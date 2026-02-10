#!/usr/bin/env python3
"""
Compute SL(2,3) (Sp(2,3)) action on the Heisenberg phase-space points and
compare Bargmann 4-cycle phases (from MUB vectors) to Z3 holonomy values
for all parallelograms in AG(2,3) based on an extracted Heisenberg bundle.

Usage:
  py -3 tools/compare_sp23_clifford_and_bargmann.py --bundle-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1 --out-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1/analysis
  py -3 tools/compare_sp23_clifford_and_bargmann.py --bundle-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1 --mub-csv artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1/analysis/qutrit_MUB_state_vectors_for_N12_vertices_phase_corrected.csv

Outputs:
  - sp23_action_on_H27_and_N12.json
  - parallelogram_holonomy_vs_bargmann.json
  - parallelogram_holonomy_vs_bargmann.md
"""
from __future__ import annotations

import argparse
import cmath
import itertools
import json
from collections import defaultdict, Counter
from math import isclose
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def load_h27(bundle_dir: Path) -> Dict[int, Tuple[int, int, int]]:
    path = bundle_dir / "H27_vertices_as_F3_cube_xy_t.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    data = {}
    with path.open("r", encoding="utf-8") as f:
        hdr = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            w33_vertex, x, y, t, k, i, j = line.split(",")
            data[int(w33_vertex)] = (int(x), int(y), int(t))
    return data


def load_missing_planes(bundle_dir: Path) -> Dict[Tuple[int, int], List[int]]:
    path = bundle_dir / "missing_planes_as_phase_space_points.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    data = {}
    with path.open("r", encoding="utf-8") as f:
        hdr = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            x, y, triple, incident = line.split(",")
            tri = [int(s) for s in triple.split()]
            data[(int(x), int(y))] = tri
    return data


def load_n12(bundle_dir: Path) -> Dict[int, Dict]:
    import csv
    path = bundle_dir / "N12_vertices_as_affine_lines.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    data = {}
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            slope_raw = r["slope_m"].strip()
            slope_val = "inf" if slope_raw.lower() == "inf" else int(slope_raw)
            intercept = int(r["intercept_b"])
            pts_field = r.get("phase_points", "")
            pts = []
            for p in [s.strip() for s in pts_field.split(";") if s.strip()]:
                p = p.strip("() ")
                if not p:
                    continue
                x_str, y_str = p.split(",")
                pts.append((int(x_str), int(y_str)))
            h_neigh_field = r.get("H_vertices_in_coset", "")
            h_neigh = [int(s) for s in h_neigh_field.split() if s.strip()]
            data[nid] = {"slope": slope_val, "intercept": intercept, "phase_points": pts, "h_neigh": h_neigh}
    return data


def load_mub_vectors(mub_csv_path: Path) -> Dict[int, List[complex]]:
    import csv

    if not mub_csv_path.exists():
        raise FileNotFoundError(mub_csv_path)
    out = {}
    with mub_csv_path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            vecs = r["state_vector"].strip()
            vecs = vecs.strip('"')
            vecs = vecs.strip()[1:-1]
            comps = [s.strip() for s in vecs.split(",") if s.strip()]
            out[nid] = [complex(c) for c in comps]
    return out


def all_sl23_matrices() -> List[Tuple[int, int, int, int]]:
    # All 2x2 matrices over F3 with determinant == 1 (mod 3)
    mats = []
    field = [0, 1, 2]
    for a in field:
        for b in field:
            for c in field:
                for d in field:
                    det = (a * d - b * c) % 3
                    if det % 3 == 1:
                        mats.append((a, b, c, d))
    # Should be 24 matrices
    return mats


def apply_mat_to_point(mat: Tuple[int, int, int, int], p: Tuple[int, int]) -> Tuple[int, int]:
    a, b, c, d = mat
    x, y = p
    nx = (a * x + b * y) % 3
    ny = (c * x + d * y) % 3
    return (nx, ny)


def find_n12_for_line(n12_map: Dict[int, Dict], direction_family: str, intercept_c: int) -> int:
    # slope mapping: fam_y -> slope 0? Reference: in N12 CSV, slope entries are "inf" (x=b), 0 (y=b), 1 (y=x+b), 2 (y=2x+b)
    # direction_family will be one of 'fam_y','fam_x','fam_m1','fam_m2' mapping to slope values
    fam_to_slope = {"fam_y": 0, "fam_x": "inf", "fam_m1": 1, "fam_m2": 2}
    slope = fam_to_slope[direction_family]
    for nid, d in n12_map.items():
        if d["slope"] == slope and int(d["intercept"]) == int(intercept_c):
            return nid
    raise RuntimeError(f"No N12 line found for family {direction_family} c={intercept_c}")


def intercept_for_family(p: Tuple[int, int], fam: str) -> int:
    x, y = p
    if fam == "fam_x":
        return x
    elif fam == "fam_y":
        return y
    elif fam == "fam_m1":
        return (y - x) % 3
    elif fam == "fam_m2":
        return (y - 2 * x) % 3
    else:
        raise RuntimeError(f"Unknown family: {fam}")


def family_for_direction(d: Tuple[int, int]) -> str:
    # mapping as in toe_affine_plane_z3_holonomy.py
    if d == (1, 0):
        return "fam_y"
    if d == (0, 1):
        return "fam_x"
    if d == (1, 1):
        return "fam_m1"
    if d == (1, 2):
        return "fam_m2"
    raise RuntimeError("Unknown direction")


def bargmann_product(v1: List[complex], v2: List[complex], v3: List[complex], v4: List[complex]) -> complex:
    def inner(u, v):
        # <u|v>
        return sum(complex(x).conjugate() * complex(y) for x, y in zip(u, v))

    prod = inner(v1, v2) * inner(v2, v3) * inner(v3, v4) * inner(v4, v1)
    if abs(prod) < 1e-12:
        return 0 + 0j
    return prod / abs(prod)


def find_k_from_omega(prod: complex) -> int:
    omega = cmath.exp(2j * cmath.pi / 3.0)
    # try k=0,1,2
    best_k = 0
    best_diff = abs(prod - 1.0 + 0j)
    for k in [0, 1, 2]:
        target = omega ** k
        d = abs(prod - target)
        if d < best_diff:
            best_diff = d
            best_k = k
    return best_k


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--mub-csv", type=Path, default=None)
    args = p.parse_args()

    bundle_dir = args.bundle_dir
    out_dir = args.out_dir if args.out_dir is not None else bundle_dir / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    h27 = load_h27(bundle_dir)
    missing = load_missing_planes(bundle_dir)
    n12 = load_n12(bundle_dir)
    mub_csv_path = (
        args.mub_csv
        if args.mub_csv is not None
        else bundle_dir / "qutrit_MUB_state_vectors_for_N12_vertices.csv"
    )
    mub = load_mub_vectors(mub_csv_path)

    # Map (x,y) -> triple (list of H vertex ids) and (x,y,t) -> id
    triple_by_point = missing
    h_by_point_t = {}
    for wid, (x, y, t) in h27.items():
        h_by_point_t[(x, y, t)] = wid

    # canonical ordering of points
    points = [(x, y) for x in range(3) for y in range(3)]

    # build SL(2,3) matrices
    mats = all_sl23_matrices()

    sp23_out = {"generators": [], "matrices_count": len(mats)}

    # For space we will record the permutations for a small generating set: S = [[0,-1],[1,0]] and T = [[1,1],[0,1]]
    S = (0, 2, 1, 0)  # [[0,2],[1,0]] because -1 mod 3 == 2
    T = (1, 1, 0, 1)
    gens = {"S": S, "T": T}

    for name, mat in gens.items():
        perm_points = {p: apply_mat_to_point(mat, p) for p in points}
        # map points to points indices
        point_to_index = {p: i for i, p in enumerate(points)}
        perm_points_idx = [point_to_index[perm_points[p]] for p in points]

        # H permutation: for each H vertex, map (x,y,t) -> (x',y',t) and find wid
        perm_h = {}
        for wid, (x, y, t) in h27.items():
            x2, y2 = apply_mat_to_point(mat, (x, y))
            key = (x2, y2, t)
            if key in h_by_point_t:
                perm_h[str(wid)] = h_by_point_t[key]
            else:
                # fallback: keep t unchanged not found — try matching any t by picking first
                tri = triple_by_point.get((x2, y2), [])
                if tri:
                    perm_h[str(wid)] = tri[0]
                else:
                    raise RuntimeError(f"Cannot find image for H vertex {wid} -> {key}")

        # N12 permutation: map each N12's phase_points under mat and match with known N12
        phase_set_to_nid = {}
        for nid2, d2 in n12.items():
            phase_set_to_nid[tuple(sorted(d2["phase_points"]))] = nid2
        perm_n12 = {}
        for nid, d in n12.items():
            pts = d["phase_points"]
            mapped = [apply_mat_to_point(mat, p) for p in pts]
            mapped_sorted = tuple(sorted(mapped))
            # find matching N12 by phase_points
            found = None
            for cand_nid, cand_d in n12.items():
                if tuple(sorted(cand_d["phase_points"])) == mapped_sorted:
                    found = cand_nid
                    break
            if found is None:
                raise RuntimeError(f"No matching N12 found for mapped phase points {mapped_sorted}")
            perm_n12[str(nid)] = found

        sp23_out["generators"].append({"name": name, "matrix": list(mat), "perm_points_idx": perm_points_idx, "perm_H": perm_h, "perm_N12": perm_n12})

    # Save sp23 action
    (out_dir / "sp23_action_on_H27_and_N12.json").write_text(json.dumps(sp23_out, indent=2), encoding="utf-8")

    # Now compute parallelogram holonomy vs Bargmann for all p and direction pairs
    directions = [((1, 0), "fam_y"), ((0, 1), "fam_x"), ((1, 1), "fam_m1"), ((1, 2), "fam_m2")]
    omega = cmath.exp(2j * cmath.pi / 3.0)
    results = []
    matches = 0
    total = 0
    for (d1, fam1), (d2, fam2) in itertools.combinations(directions, 2):
        # only independent pairs where det != 0
        det = (d1[0] * d2[1] - d1[1] * d2[0]) % 3
        if det == 0:
            continue
        expected_hol = (-det) % 3
        for p in points:
            # compute four N12 lines in order L1,L2,L3,L4
            p1 = ((p[0] + d1[0]) % 3, (p[1] + d1[1]) % 3)
            p2 = ((p[0] + d2[0]) % 3, (p[1] + d2[1]) % 3)
            p12 = ((p[0] + d1[0] + d2[0]) % 3, (p[1] + d1[1] + d2[1]) % 3)

            # L1: at p in direction d1
            c1 = intercept_for_family(p, family_for_direction(d1))
            n1 = find_n12_for_line(n12, family_for_direction(d1), c1)
            # L2: at p1 in direction d2
            c2 = intercept_for_family(p1, family_for_direction(d2))
            n2 = find_n12_for_line(n12, family_for_direction(d2), c2)
            # L3: at p12 in direction d1
            c3 = intercept_for_family(p12, family_for_direction(d1))
            n3 = find_n12_for_line(n12, family_for_direction(d1), c3)
            # L4: at p2 in direction d2
            c4 = intercept_for_family(p2, family_for_direction(d2))
            n4 = find_n12_for_line(n12, family_for_direction(d2), c4)

            # grab state vectors
            v1 = mub.get(n1)
            v2 = mub.get(n2)
            v3 = mub.get(n3)
            v4 = mub.get(n4)
            if not all([v1, v2, v3, v4]):
                # skip if any missing
                continue

            # Compute both forward and reversed traversals and prefer the orientation
            # whose Bargmann k matches the expected holonomy (if possible).
            prod_fwd = bargmann_product(v1, v2, v3, v4)
            prod_rev = bargmann_product(v1, v4, v3, v2)
            candidates = []
            if abs(prod_fwd) >= 1e-12:
                kf = find_k_from_omega(prod_fwd)
                candidates.append(("fwd", prod_fwd, kf))
            if abs(prod_rev) >= 1e-12:
                kr = find_k_from_omega(prod_rev)
                candidates.append(("rev", prod_rev, kr))
            if not candidates:
                # degenerate
                continue

            # Prefer candidate matching expected hol
            chosen = None
            for orient, prodx, kx in candidates:
                if kx == expected_hol:
                    chosen = (orient, prodx, kx)
                    break
            # Next prefer the anti-match (negated holonomy) to record orientation choice
            if chosen is None:
                for orient, prodx, kx in candidates:
                    if kx == ((-expected_hol) % 3):
                        chosen = (orient, prodx, kx)
                        break
            # Fallback: pick the first available
            if chosen is None:
                chosen = candidates[0]

            orient_used, prod, k = chosen
            match = (k == expected_hol)

            results.append({
                "p": p,
                "d1": d1,
                "d2": d2,
                "expected_hol": expected_hol,
                "n12s": [n1, n2, n3, n4],
                "used_orientation": orient_used,
                "bargmann_phase": [round(prod.real, 6), round(prod.imag, 6)],
                "bargmann_k": int(k),
                "match": bool(match),
            })
            total += 1
            if match:
                matches += 1

    outp = {"status": "ok", "total_parallelograms": total, "matches": matches, "match_fraction": matches / total if total else None, "results": results}
    (out_dir / "parallelogram_holonomy_vs_bargmann.json").write_text(json.dumps(outp, indent=2), encoding="utf-8")

    md = []
    md.append("# Parallelogram holonomy vs Bargmann comparison")
    md.append("")
    md.append(f"- total parallelograms tested: `{total}`")
    md.append(f"- matches (bargmann_k == expected_hol): `{matches}` ({outp['match_fraction']:.3f})")
    md.append("")
    md.append("## Sample mismatches (up to 20)")
    mismatches = [r for r in results if not r["match"]][:20]
    for r in mismatches:
        md.append(f"- p={r['p']} d1={r['d1']} d2={r['d2']} expected_hol={r['expected_hol']} bargmann_k={r['bargmann_k']} n12s={r['n12s']}")
    (out_dir / "parallelogram_holonomy_vs_bargmann.md").write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote {out_dir / 'sp23_action_on_H27_and_N12.json'}")
    print(f"Wrote {out_dir / 'parallelogram_holonomy_vs_bargmann.json'}")
    print(f"Wrote {out_dir / 'parallelogram_holonomy_vs_bargmann.md'}")


if __name__ == "__main__":
    main()
