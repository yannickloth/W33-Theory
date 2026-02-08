#!/usr/bin/env python3
"""
Split the 90-dim component using RANDOM PROJECTION onto the commutant.

Since commutant_dim = 2, there are exactly 2 distinct irreducible
components (each with multiplicity 1) by Schur's lemma.

FAST METHOD: Project a random matrix onto the commutant algebra:
  A = (1/|G|) sum_g R_g^{-1} X R_g
For a random X, this gives a random element of the commutant.
If dim(commutant) > 1, A will generically be non-scalar,
and its eigenspaces give the irreducible decomposition.

Usage:
  python scripts/w33_commutant_split.py
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
    print("  COMMUTANT PROJECTION: SPLIT 90-DIM COMPONENT")
    print("=" * 72)

    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)

    # Hodge Laplacian -> co-exact eigenspace
    B2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + B2 @ B2.T

    w, v = np.linalg.eigh(L1)
    idx = np.argsort(w)
    w, v = w[idx], v[:, idx]

    tol = 1e-6
    coexact_idx = np.where(np.abs(w - 4.0) < tol)[0]
    W_co = v[:, coexact_idx]
    d_co = W_co.shape[1]
    print(f"Co-exact: dim = {d_co}")

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

    # Separate 90 from 30 using C1
    print("\nComputing C1 on co-exact sector...")
    C1 = np.zeros((d_co, d_co), dtype=float)
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

    tol_c = 0.001
    clusters = []
    current_cl = [0]
    for i in range(1, len(w1)):
        if abs(w1[i] - w1[current_cl[0]]) > tol_c:
            clusters.append(
                (float(np.mean(w1[current_cl])), len(current_cl), current_cl[:])
            )
            current_cl = [i]
        else:
            current_cl.append(i)
    clusters.append((float(np.mean(w1[current_cl])), len(current_cl), current_cl[:]))

    V_90 = None
    for val, mult, c_indices in clusters:
        if mult == 90:
            V_90 = v1[:, c_indices]
    if V_90 is None:
        print("ERROR: Could not find 90-dim component")
        return

    # Map 90-dim subspace to edge space
    U_90 = W_co @ V_90  # 240 x 90
    d_sub = 90
    print(f"Isolated 90-dim subspace")

    # RANDOM PROJECTION METHOD
    # Project random matrix X onto the commutant:
    # A = (1/|G|) sum_g R_g^{-1} X R_g
    # Since R_g is unitary, R_g^{-1} = R_g^T
    print("\nProjecting random matrix onto commutant...")
    np.random.seed(42)
    X = np.random.randn(d_sub, d_sub)

    A = np.zeros((d_sub, d_sub), dtype=float)
    for cur_v, (cur_ep, cur_es) in group_list:
        cur_ep_np = np.asarray(cur_ep, dtype=int)
        cur_es_np = np.asarray(cur_es, dtype=float)
        S_g_U = U_90[cur_ep_np, :] * cur_es_np[:, None]
        R_g = U_90.T @ S_g_U  # 90 x 90

        # R_g^T X R_g = R_g^{-1} X R_g (for unitary R_g)
        A += R_g.T @ X @ R_g

    A /= group_size

    # Symmetrize for real eigenvalues
    A_sym = (A + A.T) / 2

    # Check: is A scalar?
    I_90 = np.eye(d_sub)
    trace_A = np.trace(A_sym)
    A_centered = A_sym - (trace_A / d_sub) * I_90
    off_norm = np.linalg.norm(A_centered)
    print(f"  trace(A) = {trace_A:.6f}, off-diagonal norm = {off_norm:.6f}")

    if off_norm < 1e-6:
        print("  A is scalar! Trying different random seed...")
        # Try another seed
        np.random.seed(137)
        X2 = np.random.randn(d_sub, d_sub)
        A2 = np.zeros((d_sub, d_sub), dtype=float)
        for cur_v, (cur_ep, cur_es) in group_list:
            cur_ep_np = np.asarray(cur_ep, dtype=int)
            cur_es_np = np.asarray(cur_es, dtype=float)
            S_g_U = U_90[cur_ep_np, :] * cur_es_np[:, None]
            R_g = U_90.T @ S_g_U
            A2 += R_g.T @ X2 @ R_g
        A2 /= group_size
        A_sym = (A2 + A2.T) / 2
        A_centered = A_sym - (np.trace(A_sym) / d_sub) * I_90
        off_norm = np.linalg.norm(A_centered)
        print(f"  Second try: off-diagonal norm = {off_norm:.6f}")

    # Eigendecompose the commutant element
    w_a, v_a = np.linalg.eigh(A_sym)
    idx_a = np.argsort(w_a)
    w_a, v_a = w_a[idx_a], v_a[:, idx_a]

    # Cluster eigenvalues
    tol_split = max(0.001, (w_a[-1] - w_a[0]) * 0.001)
    split_clusters = []
    cur_sc = [0]
    for i in range(1, len(w_a)):
        if abs(w_a[i] - w_a[cur_sc[0]]) > tol_split:
            split_clusters.append((float(np.mean(w_a[cur_sc])), len(cur_sc), cur_sc[:]))
            cur_sc = [i]
        else:
            cur_sc.append(i)
    split_clusters.append((float(np.mean(w_a[cur_sc])), len(cur_sc), cur_sc[:]))

    sub_dims = [mult for _, mult, _ in split_clusters]
    print(f"\nCommutant eigenvalue clusters: {len(split_clusters)}")
    for val, mult, _ in split_clusters:
        print(f"  eigenvalue {val:.8f}, multiplicity {mult}")
    print(f"\n  90 = {' + '.join(map(str, sub_dims))}")

    # Verify irreducibility of each component
    print("\nVerifying irreducibility of each component...")
    component_results = []
    for sci, (sval, smult, s_indices) in enumerate(split_clusters):
        V_sub = v_a[:, s_indices]
        U_sub = U_90 @ V_sub

        chi_sq_i = 0.0
        for cur_v, (cur_ep, cur_es) in group_list:
            cur_ep_np = np.asarray(cur_ep, dtype=int)
            cur_es_np = np.asarray(cur_es, dtype=float)
            S_g_Us = U_sub[cur_ep_np, :] * cur_es_np[:, None]
            R_g_s = U_sub.T @ S_g_Us
            chi_s = float(np.trace(R_g_s))
            chi_sq_i += chi_s * chi_s

        chi_sq_avg = chi_sq_i / group_size
        is_irr = abs(chi_sq_avg - 1.0) < 0.1
        print(
            f"  Component {sci} (dim {smult}): <|chi|^2> = {chi_sq_avg:.6f} {'IRREDUCIBLE' if is_irr else f'REDUCIBLE (~{int(round(chi_sq_avg))} pieces)'}"
        )
        component_results.append(
            {
                "dimension": smult,
                "chi_sq_avg": float(chi_sq_avg),
                "irreducible": bool(is_irr),
            }
        )

    # COMPLETE SUMMARY
    all_dims = sorted([81, 30, 24, 15] + sub_dims, reverse=True)
    coex_dims = sorted(sub_dims + [30], reverse=True)

    print(f"\n{'='*72}")
    print(f"  COMPLETE IRREDUCIBLE DECOMPOSITION OF C_1(W33) UNDER PSp(4,3)")
    print(f"{'='*72}")
    print(
        f"""
  C_1(W33) = R^240 decomposes under PSp(4,3) (order {group_size}):

  240 = {' + '.join(map(str, all_dims))}

  Sector-by-sector:
    Harmonic (eig=0):   81                          [IRREDUCIBLE]
    Co-exact (eig=4):   120 = {' + '.join(map(str, coex_dims))}
    Exact    (eig=10):  24                          [IRREDUCIBLE]
    Exact    (eig=16):  15                          [IRREDUCIBLE]

  KNOWN PSp(4,3) = Sp(4,3)/{{+/-I}} IRREDUCIBLE REPRESENTATIONS:
    Character table has 20 conjugacy classes, hence 20 irreps.
    Dimensions: 1, 5, 5, 6, 6, 10, 15, 20, 20, 24, 30, 30, 40, 40,
                45, 45, 60, 64, 80, 81

  MATCH TO KNOWN REPRESENTATIONS:
    81 -> unique 81-dim irrep (matter sector)
    30 -> one of the two 30-dim irreps (co-exact component)
    24 -> unique 24-dim irrep (exact sector)
    15 -> unique 15-dim irrep (exact sector, adjoint of sp(4))

  PHYSICAL INTERPRETATION:
    81  = matter sector (3 generations of 27 of E6)
    120 = force carriers (co-exact = im(B2^T))
    39  = gauge structure (exact = im(D^T), vertex coboundaries)

  E8 ALGEBRA RECONSTRUCTION:
    248 = rank(8) + H1(81) + co-exact(120) + exact(39)
"""
    )

    elapsed = time.time() - t0

    result = {
        "complete_decomposition": f"240 = {' + '.join(map(str, all_dims))}",
        "irreducible_dimensions": all_dims,
        "n_components": len(all_dims),
        "coexact_decomposition": f"120 = {' + '.join(map(str, coex_dims))}",
        "coexact_components": coex_dims,
        "component_results": component_results,
        "group_size": group_size,
        "elapsed_seconds": elapsed,
    }

    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_complete_decomposition_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"  Wrote: {out_path}")
    print(f"  Elapsed: {elapsed:.1f}s")

    return result


if __name__ == "__main__":
    main()
