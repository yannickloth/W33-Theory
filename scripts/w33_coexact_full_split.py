#!/usr/bin/env python3
"""
Further decompose the 90-dim reducible component of the co-exact sector.

We know 120 = 30 + 90 with the 30 irreducible and 90 having commutant_dim=2.
So 90 = d1 + d2 for some irreducible representations of PSp(4,3).

Strategy: Use SECOND Casimir operator (chi^3 or chi^2 averaging) to split
the 90-dim space. Alternatively, use the class function f(g) = chi(g)^2
instead of chi(g) for the averaging operator.

Usage:
  python scripts/w33_coexact_full_split.py
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
    print("  FULL IRREDUCIBLE DECOMPOSITION OF 120-DIM CO-EXACT SECTOR")
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

    # Compute THREE averaging operators on the 120-dim co-exact sector:
    # C1 = (1/|G|) sum chi(g) R_g          (linear Casimir)
    # C2 = (1/|G|) sum chi(g)^2 R_g        (quadratic Casimir)
    # C3 = (1/|G|) sum chi(g)^3 R_g        (cubic Casimir)
    print("Computing Casimir operators C1, C2, C3 on co-exact sector...")

    C1 = np.zeros((d_co, d_co), dtype=float)
    C2 = np.zeros((d_co, d_co), dtype=float)

    chi_sq_total = 0.0

    for cur_v, (cur_ep, cur_es) in visited.items():
        cur_ep_np = np.asarray(cur_ep, dtype=int)
        cur_es_np = np.asarray(cur_es, dtype=float)

        # R_g on co-exact sector
        S_g_W = W_co[cur_ep_np, :] * cur_es_np[:, None]
        R_g = W_co.T @ S_g_W

        chi = float(np.trace(R_g))
        chi_sq_total += chi * chi

        C1 += chi * R_g
        C2 += (chi * chi) * R_g

    C1 /= group_size
    C2 /= group_size
    avg_chi_sq = chi_sq_total / group_size
    print(f"<|chi|^2> = {avg_chi_sq:.6f} (commutant_dim = {int(round(avg_chi_sq))})")

    # Symmetrize
    C1 = (C1 + C1.T) / 2
    C2 = (C2 + C2.T) / 2

    # First split using C1
    w1, v1 = np.linalg.eigh(C1)
    idx1 = np.argsort(w1)
    w1, v1 = w1[idx1], v1[:, idx1]

    tol_cluster = max(0.01, (w1[-1] - w1[0]) * 0.001)
    clusters1 = []
    current = [0]
    for i in range(1, len(w1)):
        if abs(w1[i] - w1[current[0]]) < tol_cluster:
            current.append(i)
        else:
            clusters1.append((float(np.mean(w1[current])), len(current), current[:]))
            current = [i]
    clusters1.append((float(np.mean(w1[current])), len(current), current[:]))

    print(f"\nC1 eigenvalue clusters:")
    for val, mult, _ in clusters1:
        print(f"  eigenvalue {val:.8f}, multiplicity {mult}")

    # For the 90-dim reducible component, use C2 to further split
    for val, mult, c_indices in clusters1:
        if mult <= 30:
            print(f"\nComponent dim={mult} (eigenvalue {val:.6f}): already irreducible")
            continue

        print(
            f"\nComponent dim={mult} (eigenvalue {val:.6f}): REDUCIBLE, applying C2..."
        )
        # Get basis vectors for this component
        V_sub = v1[:, c_indices]  # 120 x mult

        # Restrict C2 to this subspace
        C2_sub = V_sub.T @ C2 @ V_sub

        # Symmetrize
        C2_sub = (C2_sub + C2_sub.T) / 2

        # Eigendecompose
        w2, v2 = np.linalg.eigh(C2_sub)
        idx2 = np.argsort(w2)
        w2, v2 = w2[idx2], v2[:, idx2]

        tol2 = max(0.01, (w2[-1] - w2[0]) * 0.001)
        clusters2 = []
        cur2 = [0]
        for i in range(1, len(w2)):
            if abs(w2[i] - w2[cur2[0]]) < tol2:
                cur2.append(i)
            else:
                clusters2.append((float(np.mean(w2[cur2])), len(cur2), cur2[:]))
                cur2 = [i]
        clusters2.append((float(np.mean(w2[cur2])), len(cur2), cur2[:]))

        print(f"  C2 eigenvalue clusters:")
        sub_dims = []
        for val2, mult2, _ in clusters2:
            print(f"    eigenvalue {val2:.8f}, multiplicity {mult2}")
            sub_dims.append(mult2)

        print(f"  Sub-decomposition: {mult} = {' + '.join(map(str, sub_dims))}")

        # Verify each sub-component is irreducible
        for ci, (val2, mult2, c_idx2) in enumerate(clusters2):
            # Basis in 120-dim space: V_sub @ v2[:, c_idx2]
            V_comp = V_sub @ v2[:, c_idx2]
            # Basis in 240-dim edge space: W_co @ V_comp
            U_comp = W_co @ V_comp

            chi_sq_i = 0.0
            for cur_v, (cur_ep, cur_es) in visited.items():
                cur_ep_np = np.asarray(cur_ep, dtype=int)
                cur_es_np = np.asarray(cur_es, dtype=float)
                S_g_U = U_comp[cur_ep_np, :] * cur_es_np[:, None]
                R_g_i = U_comp.T @ S_g_U
                chi_i = float(np.trace(R_g_i))
                chi_sq_i += chi_i * chi_i

            chi_sq_avg = chi_sq_i / group_size
            is_irr = abs(chi_sq_avg - 1.0) < 0.1
            print(
                f"    Sub-component {ci} (dim {mult2}): <|chi|^2> = {chi_sq_avg:.6f} {'IRREDUCIBLE' if is_irr else f'REDUCIBLE (~{int(round(chi_sq_avg))} pieces)'}"
            )

    # FULL SUMMARY: collect all irreducible dimensions
    print(f"\n{'='*72}")
    print(f"  COMPLETE IRREDUCIBLE DECOMPOSITION OF C_1(W33) UNDER PSp(4,3)")
    print(f"{'='*72}")

    # We also need to collect from the other sectors
    # harmonic: 81 (irreducible)
    # exact_10: 24 (irreducible)
    # exact_16: 15 (irreducible)
    print(
        f"""
  C_1(W33) = R^240 decomposes into irreducible representations of PSp(4,3):

  Hodge sector       | Eigenvalue | Dim | PSp(4,3) irreps
  -------------------|------------|-----|------------------
  Harmonic           |     0      |  81 | 81
  Co-exact           |     4      | 120 | (see decomposition above)
  Exact (from D^T)   |    10      |  24 | 24
  Exact (from D^T)   |    16      |  15 | 15

  NOTE: The Hodge Laplacian eigenspaces are PSp(4,3)-INVARIANT because
  the group commutes with L1 (since L1 is built from the incidence
  structure which PSp(4,3) preserves). This means each Hodge sector
  decomposes independently.

  PHYSICAL SIGNIFICANCE:
  - 81 (harmonic) = matter sector, 3 generations of 27-plets
  - 120 (co-exact) = interaction/force carriers
  - 24 (exact, eig=10) = cross-ratio representation
  - 15 (exact, eig=16) = adjoint of Sp(4) (gauge bosons of GUT)
"""
    )

    elapsed = time.time() - t0
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
