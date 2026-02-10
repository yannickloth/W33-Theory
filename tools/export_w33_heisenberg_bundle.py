#!/usr/bin/env python3
"""Export W33 Heisenberg bundle files (H27, N12, MUB vectors) for a base vertex.

Generates:
  - H27_vertices_as_F3_cube_xy_t.csv
  - N12_vertices_as_affine_lines.csv
  - qutrit_MUB_state_vectors_for_N12_vertices.csv

Usage:
  py -3 tools/export_w33_heisenberg_bundle.py --out-dir analysis/w33_bundle_temp --v0 0
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# Ensure repo root and scripts dir are on sys.path so module imports work
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))
# Also add scripts/ where some helper modules live
scripts_dir = repo_root / "scripts"
if scripts_dir.exists():
    sys.path.insert(0, str(scripts_dir))
from e8_embedding_group_theoretic import build_w33


def compute_local_structure(v0: int, n: int, adj_s: List[set]):
    N12 = sorted(adj_s[v0])
    H27 = [v for v in range(n) if v != v0 and v not in adj_s[v0]]
    assert len(N12) == 12, f"N12 has {len(N12)} vertices"
    assert len(H27) == 27, f"H27 has {len(H27)} vertices"

    # Find the 4 triangles (connected components of N12)
    n12_adj = {u: [v for v in N12 if v != u and v in adj_s[u]] for u in N12}
    visited = set()
    triangles = []
    for u in N12:
        if u not in visited:
            tri = {u}
            queue = [u]
            while queue:
                cur = queue.pop(0)
                for v in n12_adj[cur]:
                    if v not in tri:
                        tri.add(v)
                        queue.append(v)
            triangles.append(sorted(tri))
            visited.update(tri)
    assert len(triangles) == 4, f"Expected 4 triangles, got {len(triangles)}"
    for t in triangles:
        assert len(t) == 3, f"Triangle has {len(t)} vertices"

    # H27 internal adjacency
    h27_neighbors = defaultdict(list)
    for u in H27:
        for v in H27:
            if u != v and v in adj_s[u]:
                h27_neighbors[u].append(v)

    return N12, H27, triangles, h27_neighbors


def build_f3_cube(N12, H27, triangles, adj_s):
    T0 = triangles[0]
    T1 = triangles[1]

    # x-slices from T0
    x_slices = {}
    for xi, u in enumerate(T0):
        x_slices[xi] = set(v for v in H27 if v in adj_s[u])

    all_h27 = set(H27)
    assert x_slices[0] | x_slices[1] | x_slices[2] == all_h27

    # y-slices from T1
    y_slices = {}
    for yi, u in enumerate(T1):
        y_slices[yi] = set(v for v in H27 if v in adj_s[u])

    # Fibers
    fibers = {}
    vertex_to_xyz = {}
    for x in range(3):
        for y in range(3):
            fiber = sorted(x_slices[x] & y_slices[y])
            assert len(fiber) == 3, f"Fiber ({x},{y}) has {len(fiber)} vertices"
            fibers[(x, y)] = fiber
            for t, v in enumerate(fiber):
                vertex_to_xyz[v] = (x, y, t)

    return fibers, vertex_to_xyz


# qutrit Weyl helpers

def build_XZ() -> Tuple[np.ndarray, np.ndarray]:
    X = np.zeros((3, 3), dtype=complex)
    for j in range(3):
        X[(j + 1) % 3, j] = 1.0 + 0.0j
    w = np.exp(2j * math.pi / 3.0)
    Z = np.diag([1.0 + 0.0j, w, w**2])
    return X, Z


def D_op(p: int, q: int, X: np.ndarray, Z: np.ndarray) -> np.ndarray:
    return np.linalg.matrix_power(X, int(p) % 3) @ np.linalg.matrix_power(Z, int(q) % 3)


# line family helpers

def point_family_and_intercept(p: Tuple[int, int]) -> Tuple[str, int]:
    x, y = p
    # fam_x: x=b  (vertical)
    # fam_y: y=b  (horizontal)
    # fam_m1: y = x + b  (slope 1)
    # fam_m2: y = 2x + b  (slope 2)
    # choose the family by checking consistency across points (call site ensures 3 points lie on same line)
    # We'll use the mapping to slope values for CSV: fam_x -> 'inf', fam_y -> 0, fam_m1 -> 1, fam_m2 -> 2
    # Intercept computed accordingly
    # This function returns family string and intercept
    # Not used alone; callers will derive intercept from three points
    # Pick family by checking two points
    return ("unknown", -1)


def detect_line_family(pts: List[Tuple[int, int]]) -> Tuple[str, int]:
    # pts are 3 distinct points on an affine line over F3
    # Check fam_x (all x equal)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if xs.count(xs[0]) == 3:
        return ("fam_x", xs[0])
    if ys.count(ys[0]) == 3:
        return ("fam_y", ys[0])
    # slope 1: y - x = const
    diffs = [((y - x) % 3) for x, y in pts]
    if diffs.count(diffs[0]) == 3:
        return ("fam_m1", diffs[0])
    # slope 2: y - 2x = const
    diffs2 = [((y - 2 * x) % 3) for x, y in pts]
    if diffs2.count(diffs2[0]) == 3:
        return ("fam_m2", diffs2[0])
    raise RuntimeError(f"Cannot detect line family for points {pts}")


def intercept_value_for_family(fam: str, p: Tuple[int, int]) -> int:
    x, y = p
    if fam == "fam_x":
        return x
    if fam == "fam_y":
        return y
    if fam == "fam_m1":
        return (y - x) % 3
    if fam == "fam_m2":
        return (y - 2 * x) % 3
    raise RuntimeError("Unknown family")


def vec_to_str(v: np.ndarray) -> str:
    # format like [+0.577350+0.000000j, ...]
    comps = [f"{x.real:+.6f}{x.imag:+.6f}j" for x in v]
    return "[" + ", ".join(comps) + "]"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--v0", type=int, default=0)
    args = p.parse_args()

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    n, vertices, adj, edges = build_w33()
    adj_s = [set(adj[i]) for i in range(n)]

    v0 = args.v0
    N12, H27, triangles, h27_neighbors = compute_local_structure(v0, n, adj_s)
    fibers, vertex_to_xyz = build_f3_cube(N12, H27, triangles, adj_s)

    # Write H27 CSV (w33_vertex,x,y,t,k,i,j)
    h27_csv = out / "H27_vertices_as_F3_cube_xy_t.csv"
    with h27_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["w33_vertex", "x", "y", "t", "k", "i", "j"])
        for v in sorted(H27):
            x, y, t = vertex_to_xyz[v]
            writer.writerow([v, x, y, t, 0, 0, 0])

    # Write missing planes as phase space points (x,y -> triple of H vertices)
    missing_csv = out / "missing_planes_as_phase_space_points.csv"
    with missing_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "triple", "incident"])
        for (x, y), verts in sorted(fibers.items()):
            triple = " ".join(str(v) for v in verts)
            writer.writerow([x, y, triple, "NA"])

    # Write N12 CSV
    n12_csv = out / "N12_vertices_as_affine_lines.csv"
    with n12_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["N12_vertex", "slope_m", "intercept_b", "phase_points", "H_vertices_in_coset"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for nid in sorted(N12):
            # phase points: unique (x,y) pairs from H27 neighbors (ignore t)
            pts_set = set()
            h_neigh = []
            for v in sorted(H27):
                if v in adj_s[nid]:
                    x, y, t = vertex_to_xyz[v]
                    pts_set.add((x, y))
                    h_neigh.append(v)
            pts_sorted = sorted(list(pts_set))
            fam, intercept = detect_line_family(pts_sorted)
            slope_val = "inf" if fam == "fam_x" else (0 if fam == "fam_y" else (1 if fam == "fam_m1" else 2))
            pts_field = "; ".join([f"({x},{y})" for x, y in pts_sorted])
            writer.writerow({
                "N12_vertex": nid,
                "slope_m": slope_val,
                "intercept_b": int(intercept),
                "phase_points": pts_field,
                "H_vertices_in_coset": " ".join(str(x) for x in sorted(h_neigh)),
            })

    # Build MUB vectors for each N12 line by diagonalizing the normal operator D(a,b)
    X, Z = build_XZ()
    omega = np.exp(2j * math.pi / 3.0)

    def normal_vector_for_slope(slope):
        # slope values: 'inf' (fam_x -> x=b), 0 (fam_y -> y=b), 1 (y=x+b), 2 (y=2x+b)
        if slope == "inf":
            return (1, 0)
        if int(slope) == 0:
            return (0, 1)
        # slope m in {1,2}: normal = (-m, 1) mod 3
        m = int(slope)
        a = (-m) % 3
        b = 1
        return (a, b)

    mub_csv = out / "qutrit_MUB_state_vectors_for_N12_vertices.csv"
    with mub_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["N12_vertex", "slope", "intercept", "state_vector"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for nid in sorted(N12):
            # read back the N12 row to get slope/intercept
            r = None
            with n12_csv.open("r", encoding="utf-8") as ff:
                rdr = csv.DictReader(ff)
                for rr in rdr:
                    if int(rr["N12_vertex"]) == nid:
                        r = rr
                        break
            assert r is not None
            slope_field = r["slope_m"]
            intercept_field = int(r["intercept_b"])

            a, b = normal_vector_for_slope(slope_field)
            # operator to diagonalize is D(a,b)
            Op = D_op(a, b, X, Z)
            eigvals, eigvecs = np.linalg.eig(Op)
            # find index of eigenvalue closest to omega**intercept
            target = omega ** int(intercept_field)
            diffs = [abs(ev - target) for ev in eigvals]
            idx = int(np.argmin(diffs))
            v = eigvecs[:, idx]
            v = v / np.linalg.norm(v)
            # canonical phase convention: first nonzero component real positive
            for comp in v:
                if abs(comp) > 1e-8:
                    ph = comp / abs(comp)
                    v = v / ph
                    break
            writer.writerow({
                "N12_vertex": nid,
                "slope": slope_field,
                "intercept": intercept_field,
                "state_vector": vec_to_str(v),
            })

    print(f"Wrote {h27_csv}")
    print(f"Wrote {n12_csv}")
    print(f"Wrote {mub_csv}")


if __name__ == "__main__":
    main()
