#!/usr/bin/env python3
"""Try alternate eigenvector candidates for N12 lines with low overlap and pick the best.

Strategy:
 - Build S/T group unitaries from clifford JSON
 - For each N12 target, compute 3 eigenvectors of M = sum(D(x,y) for points on that line)
 - For each candidate, compute max overlap with transported reference vector (U * v_ref under AGL mats)
 - Replace the N12 state vector with candidate that achieves maximum overlap if improvement is significant
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def mat_mul_mod3(m2, m1):
    a2, b2, c2, d2 = m2
    a1, b1, c1, d1 = m1
    a = (a2 * a1 + b2 * c1) % 3
    b = (a2 * b1 + b2 * d1) % 3
    c = (c2 * a1 + d2 * c1) % 3
    d = (c2 * b1 + d2 * d1) % 3
    return (a, b, c, d)


def load_unitary(u_serial):
    A = np.zeros((3, 3), dtype=complex)
    for i in range(3):
        for j in range(3):
            A[i, j] = complex(u_serial[i][j]["re"] + 1j * u_serial[i][j]["im"])
    return A


def build_group_from_gens(gen_info):
    # return mat->U dict
    gens = {}
    unitaries = {}
    for g in gen_info:
        m = tuple(int(x) for x in g["matrix"])
        U = load_unitary(g["unitary"])
        gens[g["name"]] = (m, U)
        unitaries[m] = U

    id_mat = (1, 0, 0, 1)
    mat_to_unitary = {id_mat: np.eye(3, dtype=complex)}
    q = [id_mat]
    seen = {id_mat}
    while q:
        base = q.pop(0)
        U_base = mat_to_unitary[base]
        for name, (mgen, Ugen) in gens.items():
            new = mat_mul_mod3(mgen, base)
            if new not in seen:
                seen.add(new)
                mat_to_unitary[new] = Ugen @ U_base
                q.append(new)
    return mat_to_unitary


def build_XZ():
    X = np.zeros((3, 3), dtype=complex)
    for j in range(3):
        X[(j + 1) % 3, j] = 1.0 + 0.0j
    w = np.exp(2j * math.pi / 3.0)
    Z = np.diag([1.0 + 0.0j, w, w**2])
    return X, Z


def parse_vec(s: str) -> np.ndarray:
    s = s.strip()[1:-1]
    comps = [t.strip() for t in s.split(",")]
    v = np.array([complex(c) for c in comps], dtype=complex)
    v = v / np.linalg.norm(v)
    return v


def vec_to_str(v: np.ndarray) -> str:
    comps = [f"{x.real:+.6f}{x.imag:+.6f}j" for x in v]
    return "[" + ", ".join(comps) + "]"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--analysis-dir", type=Path, required=True)
    p.add_argument("--targets", type=int, nargs="*", help="N12 vertices to attempt repair")
    args = p.parse_args()

    bundle = args.bundle_dir
    analysis = args.analysis_dir

    clifford_json = analysis / "clifford_lift_on_H27_and_N12.json"
    if not clifford_json.exists():
        raise FileNotFoundError(clifford_json)

    cj = json.loads(clifford_json.read_text(encoding="utf-8"))
    gens = [g for g in cj.get("generators", []) if g["name"] in ("S", "T")]
    mat_to_U = build_group_from_gens(gens)

    X, Z = build_XZ()

    mub_csv = bundle / "qutrit_MUB_state_vectors_for_N12_vertices.csv"
    if not mub_csv.exists():
        raise FileNotFoundError(mub_csv)

    # read MUBs
    rows = []
    with mub_csv.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            rows.append(r)
    nid_to_row = {int(r["N12_vertex"]): r for r in rows}

    ref_nid = min(nid_to_row.keys())
    v_ref = parse_vec(nid_to_row[ref_nid]["state_vector"])

    # build list of target nids
    if args.targets:
        targets = args.targets
    else:
        # default: try all
        targets = sorted(nid_to_row.keys())

    # load N12 phase points to generate candidates
    n12_csv = bundle / "N12_vertices_as_affine_lines.csv"
    n12_points = {}
    with n12_csv.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            pts_field = r["phase_points"]
            pts = []
            for p in [s.strip() for s in pts_field.split(";") if s.strip()]:
                p = p.strip("() ")
                x_str, y_str = p.split(",")
                pts.append((int(x_str), int(y_str)))
            n12_points[nid] = pts

    improved = []

    for nid in targets:
        if nid not in n12_points:
            continue
        pts = n12_points[nid]
        # sum D
        M = np.zeros((3, 3), dtype=complex)
        for x, y in pts:
            M = M + np.linalg.matrix_power(X, x) @ np.linalg.matrix_power(Z, y)
        vals, vecs = np.linalg.eig(M)
        candidates = []
        for i in range(3):
            v = vecs[:, i]
            v = v / np.linalg.norm(v)
            # canonicalize phase
            for comp in v:
                if abs(comp) > 1e-8:
                    ph = comp / abs(comp)
                    v = v / ph
                    break
            candidates.append(v)

        best_cand = None
        best_overlap = 0.0
        # iterate over group matrices and translations
        for v_cand in candidates:
            max_ov = 0.0
            for mat, U in mat_to_U.items():
                for dx in range(3):
                    for dy in range(3):
                        Dm = np.linalg.matrix_power(X, dx) @ np.linalg.matrix_power(Z, dy)
                        v_im = Dm @ (U @ v_ref)
                        ov = abs(np.vdot(v_cand.conj(), v_im))
                        if ov > max_ov:
                            max_ov = ov
            if max_ov > best_overlap:
                best_overlap = max_ov
                best_cand = v_cand

        old_v = parse_vec(nid_to_row[nid]["state_vector"])
        old_best = 0.0
        for mat, U in mat_to_U.items():
            for dx in range(3):
                for dy in range(3):
                    Dm = np.linalg.matrix_power(X, dx) @ np.linalg.matrix_power(Z, dy)
                    v_im = Dm @ (U @ v_ref)
                    old_best = max(old_best, abs(np.vdot(old_v.conj(), v_im)))

        print(f"NID {nid}: old_best={old_best:.6e}, new_best={best_overlap:.6e}")

        if best_overlap > old_best + 1e-6:
            print(f"  Replacing vector for NID {nid} (improved overlap)")
            nid_to_row[nid]["state_vector"] = vec_to_str(best_cand)
            improved.append((nid, old_best, best_overlap))

    # Write back CSV if improved
    if improved:
        with mub_csv.open("w", encoding="utf-8", newline="") as f:
            fieldnames = ["N12_vertex", "slope", "intercept", "state_vector"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for nid in sorted(nid_to_row.keys()):
                writer.writerow(nid_to_row[nid])
        print("Wrote updated mub CSV (replaced candidates for some N12s)")
    else:
        print("No improvements found; mub CSV unchanged")


if __name__ == "__main__":
    main()
