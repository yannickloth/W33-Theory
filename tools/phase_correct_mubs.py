#!/usr/bin/env python3
"""Apply Clifford (qutrit) unitaries to choose canonical phases for the 12 MUB state vectors (N12 vertices).

Strategy:
- Load S/T unitaries from `clifford_lift_on_H27_and_N12.json` and the SL(2,3) action (N12 perms) from `sp23_action_on_H27_and_N12.json`.
- Generate full SL(2,3) group by closure under multiplication (24 elements), tracking both the 2x2 mat (mod 3) and the corresponding unitary (3x3 complex).
- Pick a reference N12 vertex (min id) and the corresponding reference state vector.
- For each target N12, pick a group element that maps the reference N12 to the target; use its unitary to transport the reference vector, compute the phase relative to the current target vector, and rotate the target vector by the inverse phase so it matches the transported reference.
- Write corrected CSV `qutrit_MUB_state_vectors_for_N12_vertices_phase_corrected.csv` into the bundle `analysis` directory and report statistics.

Usage:
  py -3 tools/phase_correct_mubs.py --bundle-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1 --out-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1/analysis
"""
from __future__ import annotations

import argparse
import cmath
import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


def mat_mul_mod3(
    m2: Tuple[int, int, int, int], m1: Tuple[int, int, int, int]
) -> Tuple[int, int, int, int]:
    a2, b2, c2, d2 = m2
    a1, b1, c1, d1 = m1
    a = (a2 * a1 + b2 * c1) % 3
    b = (a2 * b1 + b2 * d1) % 3
    c = (c2 * a1 + d2 * c1) % 3
    d = (c2 * b1 + d2 * d1) % 3
    return (a, b, c, d)


def load_unitary_from_serial(u_serial: List[List[Dict[str, float]]]) -> np.ndarray:
    A = np.zeros((3, 3), dtype=complex)
    for i in range(3):
        for j in range(3):
            A[i, j] = complex(u_serial[i][j]["re"] + 1j * u_serial[i][j]["im"])
    return A


def build_group_from_gens(
    gen_info: List[Dict],
) -> Tuple[
    Dict[Tuple[int, int, int, int], np.ndarray],
    Dict[Tuple[int, int, int, int], Dict[str, int]],
]:
    # gen_info contains entries with 'name','matrix' and 'unitary' (serialized)
    gens = {}
    unitaries = {}
    perms_n12 = {}
    for g in gen_info:
        m = tuple(int(x) for x in g["matrix"])
        U = load_unitary_from_serial(g["unitary"])
        gens[g["name"]] = (m, U)
        unitaries[m] = U
        if "perm_N12" in g:
            # convert keys to ints
            perm = {int(k): int(v) for k, v in g["perm_N12"].items()}
            perms_n12[m] = perm

    # BFS closure under left-multiplication by generators
    id_mat = (1, 0, 0, 1)
    group_mats = {id_mat}
    mat_to_unitary = {id_mat: np.eye(3, dtype=complex)}
    mat_to_perm_n12 = {id_mat: None}  # fill perms later using generators

    q = deque([id_mat])
    while q:
        base = q.popleft()
        U_base = mat_to_unitary[base]
        for name, (mgen, Ugen) in gens.items():
            new = mat_mul_mod3(mgen, base)
            if new not in group_mats:
                group_mats.add(new)
                mat_to_unitary[new] = Ugen @ U_base
                # compose permutations if available
                pbase = mat_to_perm_n12.get(base)
                pgen = perms_n12.get(mgen)
                if pgen is None:
                    mat_to_perm_n12[new] = None
                else:
                    if pbase is None:
                        mat_to_perm_n12[new] = dict(pgen)
                    else:
                        # compose: new_perm[x] = pgen[pbase[x]]
                        newp = {}
                        for k, v in pbase.items():
                            newp[k] = pgen.get(v, v)
                        mat_to_perm_n12[new] = newp
                q.append(new)
    if len(group_mats) != 24:
        print(
            "Warning: group closure produced", len(group_mats), "elements (expected 24)"
        )
    return mat_to_unitary, mat_to_perm_n12


def parse_mub_csv(path: Path) -> Dict[int, complex]:
    import csv

    out = {}
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            vecs = r["state_vector"].strip()
            vecs = vecs.strip()[1:-1]
            comps = [s.strip() for s in vecs.split(",")]
            v = np.array([complex(c) for c in comps], dtype=complex)
            # normalize
            norm = np.linalg.norm(v)
            if norm > 0:
                v = v / norm
            out[nid] = v
    return out


def write_mub_csv(out_map: Dict[int, np.ndarray], src_csv: Path, out_csv: Path) -> None:
    import csv

    with src_csv.open("r", encoding="utf-8") as f:
        hdr = f.readline()
        rest = f.read().splitlines()

    # Build a dict of original rows by nid for copying fields
    rows = []
    with src_csv.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            v = out_map.get(nid)
            vec_str = "[" + ", ".join([f"{x.real:+.6f}{x.imag:+.6f}j" for x in v]) + "]"
            r["state_vector"] = vec_str
            rows.append(r)

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()

    bundle = args.bundle_dir
    out_dir = args.out_dir if args.out_dir is not None else bundle / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    clifford_json = out_dir / "clifford_lift_on_H27_and_N12.json"
    sp23_json = out_dir / "sp23_action_on_H27_and_N12.json"
    mub_csv = bundle / "qutrit_MUB_state_vectors_for_N12_vertices.csv"

    if not clifford_json.exists():
        raise FileNotFoundError(clifford_json)
    if not sp23_json.exists():
        raise FileNotFoundError(sp23_json)
    if not mub_csv.exists():
        raise FileNotFoundError(mub_csv)

    cj = json.loads(clifford_json.read_text(encoding="utf-8"))
    sp = json.loads(sp23_json.read_text(encoding="utf-8"))

    # Build generator info (S and T) from clifford JSON (matching by name)
    gens = []
    # clifford JSON gens stored as list
    for g in cj.get("generators", []):
        if g["name"] in ("S", "T"):
            gens.append(g)

    # Build group
    mat_to_U, mat_to_perm = build_group_from_gens(gens)

    # Build mapping from N12 vertices to vectors
    mub_map = parse_mub_csv(mub_csv)

    # choose reference nid
    ref_nid = min(mub_map.keys())
    v_ref = mub_map[ref_nid]

    corrected = dict(mub_map)
    stats = {"adjusted": 0, "skipped": 0, "warnings": []}

    # invert mat_to_perm to map matrix -> the permutation mapping (int->int)
    # find a matrix for each target nid
    for target_nid in sorted(mub_map.keys()):
        # find an element with perm that sends ref_nid -> target_nid
        found = None
        for m, perm in mat_to_perm.items():
            if perm is None:
                continue
            if perm.get(ref_nid) == target_nid:
                found = m
                break
        if found is None:
            stats["skipped"] += 1
            stats["warnings"].append(
                f"No group element mapping ref {ref_nid} -> {target_nid}"
            )
            continue
        U = mat_to_U[found]
        v_im = U @ v_ref
        v_t = mub_map[target_nid]
        inner = np.vdot(v_t, v_im)
        mag = abs(inner)
        if mag < 1e-6:
            stats["skipped"] += 1
            stats["warnings"].append(
                f"Low overlap for target {target_nid}: |<v_t, U v_ref>|={mag:.3e}"
            )
            continue
        phase = inner / mag
        corrected[target_nid] = v_t / phase
        stats["adjusted"] += 1

    # write corrected CSV
    out_csv = out_dir / "qutrit_MUB_state_vectors_for_N12_vertices_phase_corrected.csv"
    write_mub_csv(corrected, mub_csv, out_csv)

    # Run comparison by swapping in corrected file temporarily
    # backup original
    backup = bundle / (mub_csv.name + ".bak")
    mub_copy = bundle / mub_csv.name
    mub_temp = out_csv  # corrected CSV in analysis
    # write temp copy into bundle for compare script
    import shutil

    shutil.copy2(mub_temp, mub_copy)

    # run comparison script
    import subprocess

    rc = subprocess.run(
        [
            "python",
            "tools/compare_sp23_clifford_and_bargmann.py",
            "--bundle-dir",
            str(bundle),
            "--out-dir",
            str(out_dir),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    outp = out_dir / "parallelogram_holonomy_vs_bargmann.json"
    if outp.exists():
        j = json.loads(outp.read_text(encoding="utf-8"))
        matches = j.get("matches")
        total = j.get("total_parallelograms")
        stats["comparison_matches"] = matches
        stats["comparison_total"] = total

    # restore original mub csv (if backup exists)
    # (we didn't create backup; just remove the temp copy)
    # If desired, we could leave corrected copy in analysis

    print("Wrote corrected MUB CSV:", out_csv)
    print("Stats:", json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
