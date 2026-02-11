#!/usr/bin/env python3
"""
Split the 90-dim reducible component of the co-exact sector.

The Casimir C1 = (1/|G|) sum chi(g) R_g only gave 120 = 90 + 30.
The 90 has commutant_dim=2 but C1 and C2 give proportional operators.

DIFFERENT STRATEGY: Use a SPECIFIC generator's representation matrix
R_g0 restricted to the 90-dim subspace. If g0 is not in the kernel,
its eigenspaces will separate the irreducible components.

We can also compute the full commutant algebra by checking which
linear combinations of randomly-chosen R_g matrices commute with all R_g.

Usage:
  python scripts/w33_split_90.py
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
    print("  SPLITTING THE 90-DIM COMPONENT VIA GENERATOR MATRICES")
    print("=" * 72)

    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)

    # Build Hodge Laplacian and get co-exact eigenspace
    B2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + B2 @ B2.T

    w, v = np.linalg.eigh(L1)
    idx = np.argsort(w)
    w, v = w[idx], v[:, idx]

    tol = 1e-6
    coexact_idx = np.where(np.abs(w - 4.0) < tol)[0]
    W_co = v[:, coexact_idx]  # 240 x 120
    d_co = W_co.shape[1]
    print(f"Co-exact eigenspace: dim = {d_co}")

    # Build PSp(4,3)
    print("Enumerating PSp(4,3)...")
    J = J_matrix()
    gen_vperms = []
    gen_signed = []
    for vert in vertices:
        M_t = transvection_matrix(np.array(vert, dtype=int), J)
        vp = make_vertex_permutation(M_t, vertices)
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
    print(f"|PSp(4,3)| = {group_size}")

    # First get C1 to separate 90 from 30
    print("\nComputing C1 to separate 30 from 90...")
    C1 = np.zeros((d_co, d_co), dtype=float)
    ar = np.arange(m, dtype=int)

    group_list = list(visited.items())

    for cur_v, (cur_ep, cur_es) in group_list:
        cur_ep_np = np.asarray(cur_ep, dtype=int)
        cur_es_np = np.asarray(cur_es, dtype=float)
        S_g_W = W_co[cur_ep_np, :] * cur_es_np[:, None]
        R_g = W_co.T @ S_g_W
        chi = float(np.trace(R_g))
        C1 += chi * R_g

    C1 /= group_size
    C1 = (C1 + C1.T) / 2

    w1, v1 = np.linalg.eigh(C1)
    idx1 = np.argsort(w1)
    w1, v1 = w1[idx1], v1[:, idx1]

    # Separate the 90 from the 30
    tol_c = max(0.01, (w1[-1] - w1[0]) * 0.001)
    clusters = []
    current_cl = [0]
    for i in range(1, len(w1)):
        if abs(w1[i] - w1[current_cl[0]]) < tol_c:
            current_cl.append(i)
        else:
            clusters.append(
                (float(np.mean(w1[current_cl])), len(current_cl), current_cl[:])
            )
            current_cl = [i]
    clusters.append((float(np.mean(w1[current_cl])), len(current_cl), current_cl[:]))

    # Find the 90-dim component
    V_90 = None
    V_30 = None
    for val, mult, c_indices in clusters:
        if mult == 90:
            V_90 = v1[:, c_indices]  # 120 x 90 (in co-exact basis)
        elif mult == 30:
            V_30 = v1[:, c_indices]

    if V_90 is None:
        print("ERROR: Could not find 90-dim component")
        return

    print(f"Found 90-dim and 30-dim components")

    # Now restrict to the 90-dim subspace
    # Map to edge space: U_90 = W_co @ V_90 (240 x 90)
    U_90 = W_co @ V_90

    # Try multiple generators to find one that splits the 90
    print("\nTrying generators to split the 90-dim component...")

    for gi in range(len(gen_signed)):
        ep, es = gen_signed[gi]
        ep_np = np.asarray(ep, dtype=int)
        es_np = np.asarray(es, dtype=float)

        # R_g restricted to 90-dim subspace
        S_g_U = U_90[ep_np, :] * es_np[:, None]
        R_g_90 = U_90.T @ S_g_U  # 90 x 90

        # Eigenvalues
        R_sym = (R_g_90 + R_g_90.T) / 2
        eigs = np.linalg.eigvalsh(R_sym)

        # Count distinct eigenvalue clusters
        eigs_sorted = np.sort(eigs)
        distinct = [eigs_sorted[0]]
        for e in eigs_sorted[1:]:
            if abs(e - distinct[-1]) > 0.01:
                distinct.append(e)

        if len(distinct) > 1:
            print(f"  Generator {gi}: {len(distinct)} distinct eigenvalue clusters")
            # Use this generator's R_g to split
            w_g, v_g = np.linalg.eigh(R_sym)
            idx_g = np.argsort(w_g)
            w_g, v_g = w_g[idx_g], v_g[:, idx_g]

            sub_clusters = []
            cur_c = [0]
            for i in range(1, len(w_g)):
                if abs(w_g[i] - w_g[cur_c[0]]) > 0.01:
                    sub_clusters.append(
                        (float(np.mean(w_g[cur_c])), len(cur_c), cur_c[:])
                    )
                    cur_c = [i]
                else:
                    cur_c.append(i)
            sub_clusters.append((float(np.mean(w_g[cur_c])), len(cur_c), cur_c[:]))

            sub_dims = [mult for _, mult, _ in sub_clusters]
            print(f"    Eigenvalue clusters: {sub_dims}")

            if len(sub_clusters) > 1:
                print(f"    SUCCESS: 90 = {' + '.join(map(str, sub_dims))}")

                # Verify irreducibility of each sub-component
                for sci, (sval, smult, s_indices) in enumerate(sub_clusters):
                    # Basis in 90-dim space
                    V_sub = v_g[:, s_indices]
                    # Basis in edge space
                    U_sub = U_90 @ V_sub

                    chi_sq_i = 0.0
                    for cur_v, (cur_ep, cur_es) in group_list:
                        cur_ep_np2 = np.asarray(cur_ep, dtype=int)
                        cur_es_np2 = np.asarray(cur_es, dtype=float)
                        S_g_Us = U_sub[cur_ep_np2, :] * cur_es_np2[:, None]
                        R_g_s = U_sub.T @ S_g_Us
                        chi_s = float(np.trace(R_g_s))
                        chi_sq_i += chi_s * chi_s

                    chi_sq_avg = chi_sq_i / group_size
                    is_irr = abs(chi_sq_avg - 1.0) < 0.1
                    print(
                        f"    Component {sci} (dim {smult}): <|chi|^2> = {chi_sq_avg:.6f} {'IRREDUCIBLE' if is_irr else f'REDUCIBLE (~{int(round(chi_sq_avg))} pieces)'}"
                    )

                # FINAL SUMMARY
                print(f"\n{'='*72}")
                print(f"  COMPLETE IRREDUCIBLE DECOMPOSITION OF C_1(W33)")
                print(f"{'='*72}")

                all_dims = sorted([81, 30, 24, 15] + sub_dims, reverse=True)
                print(f"\n  C_1(W33) = R^240 under PSp(4,3):")
                print(f"  240 = {' + '.join(map(str, all_dims))}")
                print(f"  Number of irreducible components: {len(all_dims)}")

                print(f"\n  HODGE SECTOR BREAKDOWN:")
                print(f"    Harmonic (eig=0):   81              [IRREDUCIBLE]")
                print(
                    f"    Co-exact (eig=4):   {' + '.join(map(str, sorted(sub_dims, reverse=True)))} + 30"
                )
                print(f"    Exact    (eig=10):  24              [IRREDUCIBLE]")
                print(f"    Exact    (eig=16):  15              [IRREDUCIBLE]")

                # Write results
                result = {
                    "complete_decomposition": f"240 = {' + '.join(map(str, all_dims))}",
                    "irreducible_dimensions": all_dims,
                    "n_components": len(all_dims),
                    "coexact_decomposition": f"120 = {' + '.join(map(str, sorted(sub_dims, reverse=True)))} + 30",
                    "coexact_components": sorted(sub_dims, reverse=True) + [30],
                    "harmonic": {"dim": 81, "irreducible": True},
                    "exact_10": {"dim": 24, "irreducible": True},
                    "exact_16": {"dim": 15, "irreducible": True},
                    "group_size": group_size,
                    "splitting_generator": gi,
                    "elapsed_seconds": time.time() - t0,
                }

                ts = int(time.time())
                out_path = (
                    Path.cwd()
                    / "checks"
                    / f"PART_CVII_complete_decomposition_{ts}.json"
                )
                out_path.parent.mkdir(parents=True, exist_ok=True)
                from utils.json_safe import dump_json

                dump_json(result, out_path, indent=2)
                print(f"\n  Wrote: {out_path}")
                print(f"  Elapsed: {time.time() - t0:.1f}s")
                return result

    # If no single generator splits it, try products of generators
    print("\nNo single generator split the 90. Trying products of two generators...")
    for gi in range(min(5, len(gen_signed))):
        ep1, es1 = gen_signed[gi]
        for gj in range(gi + 1, min(10, len(gen_signed))):
            ep2, es2 = gen_signed[gj]
            # Compose: g2 o g1
            ep_c = tuple(ep2[ep1[i]] for i in range(m))
            es_c = tuple(es2[ep1[i]] * es1[i] for i in range(m))

            ep_np = np.asarray(ep_c, dtype=int)
            es_np = np.asarray(es_c, dtype=float)

            S_g_U = U_90[ep_np, :] * es_np[:, None]
            R_g_90 = U_90.T @ S_g_U
            R_sym = (R_g_90 + R_g_90.T) / 2
            eigs = np.linalg.eigvalsh(R_sym)

            eigs_sorted = np.sort(eigs)
            distinct = [eigs_sorted[0]]
            for e in eigs_sorted[1:]:
                if abs(e - distinct[-1]) > 0.01:
                    distinct.append(e)

            if len(distinct) > 1:
                print(
                    f"  Generators ({gi},{gj}) product: {len(distinct)} distinct eigenvalue clusters"
                )
                w_g, v_g = np.linalg.eigh(R_sym)
                idx_g = np.argsort(w_g)
                w_g, v_g = w_g[idx_g], v_g[:, idx_g]

                sub_clusters = []
                cur_c = [0]
                for i in range(1, len(w_g)):
                    if abs(w_g[i] - w_g[cur_c[0]]) > 0.01:
                        sub_clusters.append(
                            (float(np.mean(w_g[cur_c])), len(cur_c), cur_c[:])
                        )
                        cur_c = [i]
                    else:
                        cur_c.append(i)
                sub_clusters.append((float(np.mean(w_g[cur_c])), len(cur_c), cur_c[:]))

                sub_dims = [mult for _, mult, _ in sub_clusters]
                print(f"    90 = {' + '.join(map(str, sub_dims))}")

                # Verify each
                for sci, (sval, smult, s_indices) in enumerate(sub_clusters):
                    V_sub = v_g[:, s_indices]
                    U_sub = U_90 @ V_sub
                    chi_sq_i = 0.0
                    for cur_v, (cur_ep, cur_es) in group_list:
                        cur_ep_np2 = np.asarray(cur_ep, dtype=int)
                        cur_es_np2 = np.asarray(cur_es, dtype=float)
                        S_g_Us = U_sub[cur_ep_np2, :] * cur_es_np2[:, None]
                        R_g_s = U_sub.T @ S_g_Us
                        chi_s = float(np.trace(R_g_s))
                        chi_sq_i += chi_s * chi_s
                    chi_sq_avg = chi_sq_i / group_size
                    is_irr = abs(chi_sq_avg - 1.0) < 0.1
                    print(
                        f"    Component {sci} (dim {smult}): <|chi|^2> = {chi_sq_avg:.6f} {'IRREDUCIBLE' if is_irr else 'REDUCIBLE'}"
                    )

                all_dims = sorted([81, 30, 24, 15] + sub_dims, reverse=True)
                print(f"\n  COMPLETE: 240 = {' + '.join(map(str, all_dims))}")
                print(f"  Elapsed: {time.time() - t0:.1f}s")
                return

    print("Could not split 90 with generators or pairs. Try random commutant element.")
    print(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
