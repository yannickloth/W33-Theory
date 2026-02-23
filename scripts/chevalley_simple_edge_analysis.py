#!/usr/bin/env python3
"""Utility to inspect the eight simple roots/edges recorded by the
`w33_algebra_qca` Chevalley-invariant computation.

This script reads the JSON produced by the QCA run and computes a few
additional invariants that might be useful for identifying gauge sectors
or understanding the geometry.

Outputs:
  * Cartan matrix recovered from orbit coefficients (should match
    standard E8 Cartan).
  * W33 graph distances between each pair of simple-edge endpoints.
  * Summary table listing grade, i27,i3, phase, and other simple data.

Run with:
    python scripts/chevalley_simple_edge_analysis.py

"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import List, Tuple

import numpy as np

# import W33 building routines from the main script
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
from w33_algebra_qca import build_w33_geometry, hodge_laplacian_1


def cartan_from_orbits(roots: List[Tuple[int, ...]]) -> np.ndarray:
    """Compute the Cartan matrix via simple-root coefficient inner products."""
    C = _cartan_unit_e8_sage_order()
    m = len(roots)
    A = np.zeros((m, m), dtype=int)
    for i in range(m):
        for j in range(m):
            # use the standard formula a_i . a_j = sum_k,l a_i[k] C[k,l] a_j[l]
            A[i, j] = int(sum(roots[i][k] * int(C[k, l]) * roots[j][l]
                              for k in range(8) for l in range(8)))
    return A


def w33_graph_distances(edges: List[Tuple[int, int]]) -> np.ndarray:
    """Distance matrix on the 40-vertex W33 graph built from collinearity."""
    n = 40
    adj = np.zeros((n, n), dtype=int)
    for u, v in edges:
        adj[u, v] = adj[v, u] = 1
    # Floyd–Warshall or BFS
    dist = np.full((n, n), 999, dtype=int)
    for i in range(n):
        dist[i, i] = 0
    for u, v in edges:
        dist[u, v] = dist[v, u] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
    return dist


# We reimport helpers from the main script for convenience
from w33_algebra_qca import _cartan_unit_e8_sage_order


def main():
    data_path = Path("data/w33_algebra_qca.json")
    if not data_path.exists():
        print(f"Run w33_algebra_qca.py first to create {data_path}")
        return

    data = json.loads(data_path.read_text(encoding="utf-8"))
    simples = data.get("chevalley", {}).get("simple_edges", [])
    if not simples:
        print("No simple edge data found in JSON")
        return

    roots = [tuple(e["root_orbit"]) for e in simples]
    C = cartan_from_orbits(roots)
    print("Cartan matrix extracted from simple roots:")
    print(C)
    rowsum = C.sum(axis=1)
    print("Row sums (2 minus number of neighbours):", rowsum.tolist())

    # build W33 geometry and distance matrix
    pts, edges, adj, triangles, J = build_w33_geometry()
    dist = w33_graph_distances(edges)

    print("\nPairwise W33 distances between simple-edge vertices (a,b) -> min distance:")
    for info in simples:
        u, v = info["edge"]
        print(f" edge {u}-{v}: distance {dist[u,v]}")

    # also produce a full matrix between edges
    print("\nDistance matrix between simple edges (min distance between any endpoints):")
    m = len(simples)
    D = np.zeros((m, m), dtype=int)
    for i in range(m):
        u1, v1 = simples[i]["edge"]
        for j in range(m):
            u2, v2 = simples[j]["edge"]
            D[i, j] = min(dist[u1, u2], dist[u1, v2], dist[v1, u2], dist[v1, v2])
    print(D)

    print("\nSimple-edge summary:")
    for info in simples:
        print(f"i={info['i']} grade={info['grade']} i27={info.get('i27')} i3={info.get('i3')} phase={info['phase_z6']}")
    
    # group edges by grade
    by_grade = {}
    for info in simples:
        by_grade.setdefault(info['grade'], []).append(info['i'])
    print("\nEdges grouped by grade:")
    for grade, idxs in by_grade.items():
        print(f"  {grade}: indices {idxs}")
    
    # attach row-degree of each simple to summary
    print("\nSimple-root degrees (number of simple neighbours):")
    for i, deg in enumerate(2 - rowsum):
        print(f"  root {i}: degree {int(deg)}")
    # ------------------------------------------------------------------
    # project simple-edge basis vectors onto the three H1 subspaces
    # ------------------------------------------------------------------
    projections = []
    h1_path = Path("data/h1_subspaces.json")
    if h1_path.exists():
        h1 = json.loads(h1_path.read_text(encoding="utf-8"))
        gram_mats = [np.array(G, dtype=float) for G in h1.get("gram_matrices", [])]
        bases = [np.array(B, dtype=float) for B in h1.get("subspace_bases", [])]

        # rebuild W33 edges to know dimension and mapping
        pts, edges, adj, triangles, J = build_w33_geometry()
        m = len(edges)
        edge_map = { (u,v):k for k,(u,v) in enumerate(edges) }
        edge_map.update({(v,u):k for k,(u,v) in enumerate(edges)})

        # compute H1 harmonic basis (eigenvectors of L1 with ev ≈ 0)
        L1, d1, d2, edge_map2 = hodge_laplacian_1(len(pts), edges, triangles)
        eigvals, eigvecs = np.linalg.eigh(L1.astype(float))
        tol = 0.5
        harm_mask = np.abs(eigvals) < tol
        harmonic = eigvecs[:, harm_mask]  # shape (m, 81)

        # compute projection norm for every W33 edge basis vector
        edge_vals = []  # per-edge list of subspace values
        for k in range(m):
            c = harmonic[k, :]  # coordinates in H1 harmonic basis
            row = []
            for B, G in zip(bases, gram_mats):
                ci = B @ c           # map into the 27-dim subspace
                row.append(float(ci @ (G @ ci)))
            edge_vals.append(row)

        # now summarise for each simple vertex pair (u,v)
        stats_list = []
        for info in simples:
            u, vtx = info["edge"]
            incident_idxs = [idx for idx, (a, b) in enumerate(edges) if a in (u, vtx) or b in (u, vtx)]
            stats = []
            vars_ = []
            for si in range(len(gram_mats)):
                vals = [edge_vals[idx][si] for idx in incident_idxs]
                if vals:
                    meanv = float(np.mean(vals))
                    maxv = float(np.max(vals))
                    varv = float(np.var(vals))
                else:
                    meanv = maxv = varv = 0.0
                stats.append((meanv, maxv))
                vars_.append(varv)
            # triangle count incident
            tri_count = sum(1 for tri in triangles if u in tri or vtx in tri)
            # distance to all other simple edges (min endpoint distance)
            dist_list = []
            for j, other in enumerate(simples):
                if other is info:
                    continue
                u2, v2 = other['edge']
                dist_list.append(min(dist[u, u2], dist[u, v2], dist[vtx, u2], dist[vtx, v2]))
            dmean = float(np.mean(dist_list))
            stats_list.append({
                "i": info["i"],
                "incident_stats": stats,
                "incident_variance": vars_,
                "triangles": tri_count,
                "mean_dist_to_simples": dmean,
                "grade": info["grade"],
            })
        projections = stats_list
        print("\nSimple-vertex pair stats (mean,max per subspace, variance, triangle count, avg simple dist):")
        for p in projections:
            print(f"  root {p['i']} grade={p['grade']} tri={p['triangles']} dist={p['mean_dist_to_simples']:.2f} stats={p['incident_stats']} var={p['incident_variance']}")
        # additionally compute grade-average of means for correlation
        grade_avgs = {}
        frob_weights = data.get("theorem4_5", {}).get("frob_weights", [])
        for p in projections:
            g = p['grade']
            grade_avgs.setdefault(g, []).append([s[0] for s in p['incident_stats']])
        print("\nGrade-average mean projections per subspace:")
        avg_list = []
        grades = []
        for g, arr in grade_avgs.items():
            arr = np.array(arr)
            avg = arr.mean(axis=0)
            grades.append(g)
            avg_list.append(avg)
            print(f"  {g}: {avg.tolist()}")
        if frob_weights:
            print(f"  compare frobenius weights: {frob_weights}")
            # correlation between subspace0 avg and first Frobenius weight
            sub0 = np.array([a[0] for a in avg_list])
            fw0 = np.array(frob_weights)[:len(sub0)]
            # match ordering grades (g1,g2,g0_e6 maybe) - simply compute pearson
            if len(sub0) == len(fw0):
                corr = np.corrcoef(sub0, fw0)[0,1]
                print(f"  Pearson corr (subspace0 vs fw): {corr:.3f}")
        # save both edge_vals and simple projections
        outp = Path("data/simple_edge_projections.json")
        with open(outp, "w") as f:
            json.dump({"edge_vals": edge_vals, "simple_stats": projections}, f, indent=2)
        print(f"  Projection results saved to {outp}")
    else:
        print("\n  (h1_subspaces.json not found; cannot compute projections)")
if __name__ == "__main__":
    main()
