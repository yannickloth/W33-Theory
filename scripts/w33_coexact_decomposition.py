#!/usr/bin/env python3
"""
Decompose the 120-dim co-exact sector of C_1(W33) under PSp(4,3).

We know commutant_dim = 3, so there are 3 irreducible components.
This script finds their dimensions and identifies them as representations
of PSp(4,3).

Method:
  1. Restrict PSp(4,3) action to co-exact eigenspace (eigenvalue 4 of L1)
  2. Compute Casimir element C2 = (1/|G|) sum chi(g) R_g on this subspace
  3. Eigendecompose C2 to find the irreducible components

Known representations of PSp(4,3) (order 25920):
  dim 1, 5, 6, 10, 15, 20, 24, 30, 40, 45, 60, 64, 80, 81, ...
  120 = 40 + 40 + 40? or 80 + 40? or 60 + 60? etc.

Usage:
  python scripts/w33_coexact_decomposition.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from w33_homology import boundary_matrix, build_clique_complex, build_w33

from w33_h1_decomposition import (
    J_matrix,
    build_incidence_matrix,
    make_vertex_permutation,
    signed_edge_permutation,
    transvection_matrix,
)


def main():
    t0 = time.time()
    print("=" * 72)
    print("  DECOMPOSITION OF ALL HODGE SECTORS UNDER PSp(4,3)")
    print("=" * 72)

    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)

    # Build Hodge Laplacian
    B2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + B2 @ B2.T

    w, v = np.linalg.eigh(L1)
    idx = np.argsort(w)
    w, v = w[idx], v[:, idx]

    tol = 1e-6
    sectors = {
        "harmonic_0": (0.0, np.where(np.abs(w) < tol)[0]),
        "coexact_4": (4.0, np.where(np.abs(w - 4.0) < tol)[0]),
        "exact_10": (10.0, np.where(np.abs(w - 10.0) < tol)[0]),
        "exact_16": (16.0, np.where(np.abs(w - 16.0) < tol)[0]),
    }

    for name, (eig, indices) in sectors.items():
        print(f"  {name}: eigenvalue={eig}, dim={len(indices)}")

    # Build PSp(4,3) group with signed edge permutations
    print("\nEnumerating PSp(4,3)...")
    J = J_matrix()
    gen_vperms = []
    gen_signed = []
    for vert in vertices:
        M = transvection_matrix(np.array(vert, dtype=int), J)
        vp = make_vertex_permutation(M, vertices)
        gen_vperms.append(tuple(vp))
        ep, es = signed_edge_permutation(vp, edges)
        gen_signed.append((tuple(ep), tuple(es)))

    id_v = tuple(range(n))
    id_e = tuple(range(m))
    id_s = tuple([1] * m)
    visited = {id_v: (id_e, id_s)}
    queue = deque([id_v])

    while queue:
        cur_v = queue.popleft()
        cur_ep, cur_es = visited[cur_v]
        for gv, (gep, ges) in zip(gen_vperms, gen_signed):
            new_v = tuple(gv[i] for i in cur_v)
            if new_v not in visited:
                new_ep = tuple(gep[cur_ep[i]] for i in range(m))
                new_es = tuple(ges[cur_ep[i]] * cur_es[i] for i in range(m))
                visited[new_v] = (new_ep, new_es)
                queue.append(new_v)

    group_size = len(visited)
    print(f"  |PSp(4,3)| = {group_size}")

    ar = np.arange(m, dtype=int)

    # For each sector, compute the Casimir element and decompose
    results = {}
    for name, (eig, indices) in sectors.items():
        d = len(indices)
        if d == 0:
            continue

        W_sec = v[:, indices]  # m x d
        print(f"\n{'='*60}")
        print(f"  Sector: {name} (dim {d})")
        print(f"{'='*60}")

        # Compute Casimir C2 = (1/|G|) sum chi(g) R_g
        C2 = np.zeros((d, d), dtype=float)
        chi_sq_sum = 0.0
        chi_values = []

        for cur_v, (cur_ep, cur_es) in visited.items():
            cur_ep_np = np.asarray(cur_ep, dtype=int)
            cur_es_np = np.asarray(cur_es, dtype=float)

            # R_g on this sector: (W_sec^T) S_g (W_sec)
            S_g_W = W_sec[cur_ep_np, :] * cur_es_np[:, None]
            R_g = W_sec.T @ S_g_W

            chi = float(np.trace(R_g))
            chi_sq_sum += chi * chi
            chi_values.append(chi)

            C2 += chi * R_g

        C2 /= group_size
        avg_chi_sq = chi_sq_sum / group_size
        commutant_dim = int(round(avg_chi_sq))
        print(f"  commutant_dim = {commutant_dim}")
        print(f"  <|chi|^2> = {avg_chi_sq:.6f}")

        if commutant_dim == 1:
            print(f"  IRREDUCIBLE (no decomposition needed)")
            results[name] = {
                "dimension": d,
                "commutant_dim": commutant_dim,
                "irreducible": True,
                "components": [d],
            }
            continue

        # Symmetrize and eigendecompose C2
        C2_sym = (C2 + C2.T) / 2
        w_C2, v_C2 = np.linalg.eigh(C2_sym)
        idx_c = np.argsort(w_C2)
        w_C2, v_C2 = w_C2[idx_c], v_C2[:, idx_c]

        # Cluster eigenvalues
        tol_cluster = max(0.01, (w_C2[-1] - w_C2[0]) * 0.001)
        clusters = []
        current = [0]
        for i in range(1, len(w_C2)):
            if abs(w_C2[i] - w_C2[current[0]]) < tol_cluster:
                current.append(i)
            else:
                clusters.append(
                    (float(np.mean(w_C2[current])), len(current), current[:])
                )
                current = [i]
        clusters.append((float(np.mean(w_C2[current])), len(current), current[:]))

        dims = [mult for _, mult, _ in clusters]
        print(f"  C2 eigenvalue clusters: {len(clusters)}")
        for val, mult, _ in clusters:
            print(f"    eigenvalue {val:.8f}, multiplicity {mult}")
        print(f"  Decomposition: {d} = {' + '.join(map(str, dims))}")

        # Verify each component is irreducible
        print(f"  Irreducibility of each component:")
        component_info = []
        for ci, (val, mult, c_indices) in enumerate(clusters):
            Vi = v_C2[:, c_indices]

            # Map Vi back to edge space: U_i = W_sec @ Vi (m x mult)
            Ui = W_sec @ Vi

            # Compute <|chi_i|^2> for this component
            chi_sq_i = 0.0
            for cur_v, (cur_ep, cur_es) in visited.items():
                cur_ep_np = np.asarray(cur_ep, dtype=int)
                cur_es_np = np.asarray(cur_es, dtype=float)
                S_g_U = Ui[cur_ep_np, :] * cur_es_np[:, None]
                R_g_i = Ui.T @ S_g_U
                chi_i = float(np.trace(R_g_i))
                chi_sq_i += chi_i * chi_i

            chi_sq_avg_i = chi_sq_i / group_size
            is_irr = abs(chi_sq_avg_i - 1.0) < 0.1
            print(
                f"    Component {ci} (dim {mult}): <|chi|^2> = {chi_sq_avg_i:.6f} {'IRREDUCIBLE' if is_irr else 'REDUCIBLE'}"
            )
            component_info.append(
                {
                    "dimension": mult,
                    "C2_eigenvalue": float(val),
                    "chi_sq_avg": float(chi_sq_avg_i),
                    "irreducible": bool(is_irr),
                }
            )

        results[name] = {
            "dimension": d,
            "commutant_dim": commutant_dim,
            "irreducible": commutant_dim == 1,
            "components": dims,
            "decomposition": f"{d} = {' + '.join(map(str, dims))}",
            "component_details": component_info,
        }

    # Summary
    print(f"\n{'='*72}")
    print(f"  COMPLETE DECOMPOSITION SUMMARY")
    print(f"{'='*72}")

    total_components = 0
    all_dims = []
    for name in ["harmonic_0", "coexact_4", "exact_10", "exact_16"]:
        if name in results:
            r = results[name]
            total_components += r["commutant_dim"]
            all_dims.extend(r["components"])
            status = (
                "IRREDUCIBLE"
                if r["irreducible"]
                else f"{r['commutant_dim']} components: {' + '.join(map(str, r['components']))}"
            )
            print(f"  {name:15s} (dim {r['dimension']:3d}): {status}")

    print(
        f"\n  TOTAL: C_1 = 240 = {' + '.join(map(str, sorted(all_dims, reverse=True)))}"
    )
    print(f"  Number of irreducible components: {total_components}")

    # Physical interpretation
    print(f"\n  PHYSICAL INTERPRETATION:")
    for name, r in results.items():
        if not r["irreducible"] and "component_details" in r:
            for ci, comp in enumerate(r["component_details"]):
                d_i = comp["dimension"]
                print(f"    {name} component {ci} (dim {d_i}):", end="")
                # Identify known PSp(4,3) representations
                known_reps = {
                    1: "trivial",
                    5: "5-dim (standard)",
                    6: "6-dim",
                    10: "10-dim",
                    15: "15-dim (adjoint of sp(4))",
                    20: "20-dim",
                    24: "24-dim (cross-ratio)",
                    30: "30-dim",
                    40: "40-dim (vertex permutation)",
                    45: "45-dim",
                    60: "60-dim",
                    64: "64-dim",
                    80: "80-dim",
                    81: "81-dim (H1 harmonic)",
                }
                if d_i in known_reps:
                    print(f" {known_reps[d_i]}")
                else:
                    print(f" unknown (dim {d_i})")

    elapsed = time.time() - t0
    results["elapsed_seconds"] = elapsed
    results["group_size"] = group_size

    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_sector_decomposition_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            indent=2,
            default=lambda x: (
                int(x)
                if isinstance(x, (np.integer,))
                else float(x) if isinstance(x, (np.floating,)) else x
            ),
        )
    print(f"\n  Wrote: {out_path}")
    print(f"  Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
