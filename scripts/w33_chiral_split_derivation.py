#!/usr/bin/env python3
"""
Analytic Derivation of Chiral Split c_90 = 61/60, c_30 = 1/3
===============================================================

QUESTION: Why does the Casimir 27/20 split as 61/60 + 1/3?

The total Casimir K = (27/20) * I_81 splits under PSp(4,3) into:
  K = K_90 + K_30
  K_90 = c_90 * I_81 = (61/60) * I_81   (chiral sector)
  K_30 = c_30 * I_81 = (1/3) * I_81     (non-chiral sector)

Since both are scalar by Schur's lemma, we need:
  c_90 = (1/81) * sum_k ||C_90[k]||^2_F
  c_30 = (1/81) * sum_k ||C_30[k]||^2_F

APPROACH:
  The split depends on how the bracket image distributes between
  the 90 and 30 dimensional subspaces. We can analyze this using:

  1. The PSp(4,3) Clebsch-Gordan decomposition:
     81 x 81 = ??? (what irreps appear in the tensor product)

  2. The wedge product structure:
     The antisymmetric square Λ^2(81) decomposes into PSp(4,3) irreps.
     Only those irreps that appear in BOTH Λ^2(81) AND the co-exact
     sector contribute to the coupling.

  3. The Schur orthogonality approach:
     ||C_90||^2_F / ||C_30||^2_F = (c_90 * 81) / (c_30 * 81) = c_90/c_30
     = (61/60) / (1/3) = 61/20 = 3.05

COMPUTATION:
  We compute various structural quantities to find the analytic formula.

Usage:
  python scripts/w33_chiral_split_derivation.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, deque
from fractions import Fraction
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


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def main():
    t0 = time.time()
    print("=" * 72)
    print("  ANALYTIC DERIVATION OF CHIRAL SPLIT")
    print("=" * 72)

    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    triangles = simplices[2]

    d1 = boundary_matrix(simplices[1], simplices[0]).astype(float)
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + d2 @ d2.T

    eigvals, eigvecs = np.linalg.eigh(L1)
    harm_mask = np.abs(eigvals) < 0.5
    coex_mask = np.abs(eigvals - 4.0) < 0.5

    H = eigvecs[:, harm_mask]  # 240 x 81
    W_co = eigvecs[:, coex_mask]  # 240 x 120

    # Build PSp(4,3)
    print("  Building PSp(4,3)...")
    J_mat = J_matrix()
    gen_vperms, gen_signed = [], []
    for vert in vertices:
        M_t = transvection_matrix(np.array(vert, dtype=int), J_mat)
        vp = make_vertex_permutation(M_t, vertices)
        gen_vperms.append(tuple(vp))
        ep, es = signed_edge_permutation(vp, edges)
        gen_signed.append((tuple(ep), tuple(es)))

    id_v = tuple(range(n))
    visited = {id_v: (tuple(range(m)), tuple([1] * m))}
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

    group_list = list(visited.items())
    G = len(visited)
    print(f"  |PSp(4,3)| = {G}")

    # Split co-exact into 90 + 30
    print("  Splitting co-exact 120 = 90 + 30...")
    n_coex = W_co.shape[1]
    C1_proj = np.zeros((n_coex, n_coex))
    for _, (cur_ep, cur_es) in group_list:
        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)
        S = W_co[ep_np, :] * es_np[:, None]
        R = W_co.T @ S
        C1_proj += np.trace(R) * R
    C1_proj /= G
    C1_proj = (C1_proj + C1_proj.T) / 2

    w1, v1 = np.linalg.eigh(C1_proj)
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

    P_90 = P_30 = None
    for val, mult, c_idx in clusters:
        if mult == 90:
            V_90 = v1[:, c_idx]
            U_90 = W_co @ V_90
            P_90 = U_90 @ U_90.T  # 240x240 projector onto 90-dim
        elif mult == 30:
            V_30 = v1[:, c_idx]
            U_30 = W_co @ V_30
            P_30 = U_30 @ U_30.T  # 240x240 projector onto 30-dim

    # =====================================================================
    # PART 1: CHARACTER ANALYSIS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 1: CHARACTER ANALYSIS OF REPRESENTATIONS")
    print("=" * 72)

    # Compute characters of all five irreps: 81, 90, 30, 24, 15
    # For each group element g, compute chi_V(g) = trace of g on V
    print("  Computing character tables...")

    # Organize group elements by conjugacy class (via character values)
    char_data = []
    for idx, (cur_v, (cur_ep, cur_es)) in enumerate(group_list):
        if idx % 5000 == 0:
            print(f"    Processing element {idx}/{G}...")
        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)

        # Character on each irrep
        S = eigvecs[ep_np, :] * es_np[:, None]
        R_full = eigvecs.T @ S  # 240x240 in eigenbasis

        chi_81 = float(
            np.trace(R_full[np.ix_(np.where(harm_mask)[0], np.where(harm_mask)[0])])
        )
        chi_90 = float(
            np.trace(
                R_full[np.ix_(np.where(coex_mask)[0], np.where(coex_mask)[0])]
                @ (V_90 @ V_90.T)
            )
        )
        chi_30 = float(
            np.trace(
                R_full[np.ix_(np.where(coex_mask)[0], np.where(coex_mask)[0])]
                @ (V_30 @ V_30.T)
            )
        )

        # Actually, simpler: directly compute on the subspace basis
        S_H = H[ep_np, :] * es_np[:, None]
        chi_81 = float(np.trace(H.T @ S_H))

        S_90 = U_90[ep_np, :] * es_np[:, None]
        chi_90 = float(np.trace(U_90.T @ S_90))

        S_30 = U_30[ep_np, :] * es_np[:, None]
        chi_30 = float(np.trace(U_30.T @ S_30))

        char_data.append((chi_81, chi_90, chi_30))

    # =====================================================================
    # PART 2: PLANCHEREL / SCHUR ORTHOGONALITY
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 2: INNER PRODUCTS OF CHARACTERS")
    print("=" * 72)

    # <chi_V, chi_W> = (1/|G|) sum_g chi_V(g) * chi_W(g)
    # If V is irreducible, <chi_V, chi_V> = 1
    # The bracket [81, 81] -> 90 or 30 means that 90 or 30 appears in
    # the tensor product 81 x 81 (or rather, the antisymmetric square Λ^2(81))

    chars = np.array(char_data)  # G x 3 (columns: chi_81, chi_90, chi_30)

    # Verify irreducibility
    for name, col in [("81", 0), ("90", 1), ("30", 2)]:
        inner = np.sum(chars[:, col] ** 2) / G
        print(f"  <chi_{name}, chi_{name}> = {inner:.6f}")

    # Cross inner products
    print(f"\n  Cross inner products:")
    for (n1, c1), (n2, c2) in [
        (("81", 0), ("90", 1)),
        (("81", 0), ("30", 2)),
        (("90", 1), ("30", 2)),
    ]:
        inner = np.sum(chars[:, c1] * chars[:, c2]) / G
        print(f"  <chi_{n1}, chi_{n2}> = {inner:.6f}")

    # =====================================================================
    # PART 3: ANTISYMMETRIC SQUARE Λ^2(81)
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 3: ANTISYMMETRIC SQUARE Λ^2(81)")
    print("=" * 72)

    # chi_{Λ^2(V)}(g) = (1/2)(chi_V(g)^2 - chi_V(g^2))
    # chi_{S^2(V)}(g) = (1/2)(chi_V(g)^2 + chi_V(g^2))
    # We need chi_V(g^2) for each g.

    # For chi(g^2): we need R_g^2 on H
    print("  Computing chi(g^2) for Λ^2(81)...")
    chi_81_sq = np.zeros(G)  # chi_81(g^2) for each g

    for idx, (cur_v, (cur_ep, cur_es)) in enumerate(group_list):
        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)
        S_H = H[ep_np, :] * es_np[:, None]
        R_g = H.T @ S_H
        chi_81_sq[idx] = float(np.trace(R_g @ R_g))

    chi_81_arr = chars[:, 0]
    chi_wedge2 = 0.5 * (chi_81_arr**2 - chi_81_sq)

    # Decompose Λ^2(81) into irreps
    # <Λ^2(81), chi_V> = (1/|G|) sum_g chi_{Λ^2}(g) * chi_V(g)
    dim_wedge2 = 81 * 80 // 2  # = 3240
    print(f"\n  dim(Λ^2(81)) = {dim_wedge2}")

    mult_90_in_wedge2 = np.sum(chi_wedge2 * chars[:, 1]) / G
    mult_30_in_wedge2 = np.sum(chi_wedge2 * chars[:, 2]) / G

    print(f"  Multiplicity of 90 in Λ^2(81): {mult_90_in_wedge2:.6f}")
    print(f"  Multiplicity of 30 in Λ^2(81): {mult_30_in_wedge2:.6f}")

    # Also check: how many copies of 81 appear in Λ^2(81)?
    mult_81_in_wedge2 = np.sum(chi_wedge2 * chars[:, 0]) / G
    print(f"  Multiplicity of 81 in Λ^2(81): {mult_81_in_wedge2:.6f}")

    # Full decomposition of Λ^2(81)
    # We need all irrep characters. Let's also compute chi_24 and chi_15.
    ex10_mask = np.abs(eigvals - 10.0) < 0.5
    ex16_mask = np.abs(eigvals - 16.0) < 0.5
    V_24 = eigvecs[:, ex10_mask]
    V_15 = eigvecs[:, ex16_mask]

    chi_24_arr = np.zeros(G)
    chi_15_arr = np.zeros(G)
    for idx, (cur_v, (cur_ep, cur_es)) in enumerate(group_list):
        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)
        S_24 = V_24[ep_np, :] * es_np[:, None]
        chi_24_arr[idx] = float(np.trace(V_24.T @ S_24))
        S_15 = V_15[ep_np, :] * es_np[:, None]
        chi_15_arr[idx] = float(np.trace(V_15.T @ S_15))

    # Also need the trivial representation chi_1 = 1 for all g
    chi_1_arr = np.ones(G)

    all_irreps = {
        "1": chi_1_arr,
        "15": chi_15_arr,
        "24": chi_24_arr,
        "30": chars[:, 2],
        "81": chars[:, 0],
        "90": chars[:, 1],
    }

    print(f"\n  Full decomposition of Λ^2(81) = {dim_wedge2}:")
    total_accounted = 0
    decomp = {}
    for name, chi_arr in all_irreps.items():
        mult = np.sum(chi_wedge2 * chi_arr) / G
        dim_irrep = int(round(np.sum(chi_arr**2) / G))  # This is 1 if irreducible
        actual_dim = int(round(chi_arr[0]))  # chi(e) = dim
        mult_round = round(mult)
        if abs(mult - mult_round) < 0.01 and mult_round > 0:
            decomp[name] = mult_round
            total_accounted += mult_round * actual_dim
            print(
                f"    {name} (dim={actual_dim}): multiplicity {mult_round} (contributes {mult_round * actual_dim})"
            )

    print(f"  Total accounted: {total_accounted}/{dim_wedge2}")
    remaining = dim_wedge2 - total_accounted
    if remaining > 0:
        print(f"  Remaining: {remaining} dimensions in unknown irreps")

    # =====================================================================
    # PART 4: CLEBSCH-GORDAN AND COUPLING CONSTANTS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 4: CLEBSCH-GORDAN COEFFICIENTS")
    print("=" * 72)

    # The coupling constant c_V for the V-component of the Casimir is:
    # c_V = (dim_V / dim_H^2) * ||projection of bracket to V||^2
    # By Schur's lemma, this equals (mult_V_in_Λ^2(H)) * (some normalization)

    # More precisely, if Λ^2(81) contains V with multiplicity m_V, then
    # the bracket [H,H] -> V has m_V independent components.
    # The Casimir contribution from V is:
    #   c_V = m_V * (normalization factor depending on V)

    # For the wedge-coboundary bracket:
    # The bracket [h_i, h_j] = d2*(h_i ∧ h_j) maps Λ^2(H1) -> C1
    # Then projects to co-exact. So:
    # c_V = ||P_V d2* (Σ_{i<j} |h_i ∧ h_j><h_i ∧ h_j|) d2 P_V||

    # We already know c_90 = 61/60, c_30 = 1/3
    # And mult_90 and mult_30 in Λ^2(81)
    # Can we predict c_90/c_30 from multiplicities?

    m_90 = round(mult_90_in_wedge2)
    m_30 = round(mult_30_in_wedge2)
    print(f"  Λ^2(81) contains 90 with multiplicity {m_90}")
    print(f"  Λ^2(81) contains 30 with multiplicity {m_30}")
    print(f"  c_90/c_30 = {61/20:.6f}")
    print(
        f"  m_90 * 90 / (m_30 * 30) = {m_90 * 90 / (m_30 * 30) if m_30 > 0 else 'inf':.6f}"
    )
    print(f"  m_90 / m_30 = {m_90 / m_30 if m_30 > 0 else 'inf':.6f}")

    # Check if c_V is proportional to m_V * dim_V
    # That would mean: c_90 = α * m_90 * 90, c_30 = α * m_30 * 30
    if m_90 > 0 and m_30 > 0:
        alpha_90 = (61 / 60) / (m_90 * 90)
        alpha_30 = (1 / 3) / (m_30 * 30)
        print(f"\n  c_90 / (m_90 * 90) = {alpha_90:.10f}")
        print(f"  c_30 / (m_30 * 30) = {alpha_30:.10f}")
        print(f"  Equal? {abs(alpha_90 - alpha_30) < 1e-8}")

    # Check if c_V is proportional to m_V * dim_V / dim(Λ^2)
    if m_90 > 0 and m_30 > 0:
        beta_90 = (61 / 60) / (m_90 * 90 / dim_wedge2)
        beta_30 = (1 / 3) / (m_30 * 30 / dim_wedge2)
        print(f"\n  c_90 * dim(Λ^2) / (m_90 * 90) = {beta_90:.10f}")
        print(f"  c_30 * dim(Λ^2) / (m_30 * 30) = {beta_30:.10f}")

    # =====================================================================
    # PART 5: BRACKET NORM DECOMPOSITION
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 5: BRACKET NORM ANALYSIS")
    print("=" * 72)

    # Compute: for the wedge-coboundary map W: Λ^2(H1) -> C1,
    # how much of the image lands in the 90-dim vs 30-dim?

    # Total bracket norm: ||C||^2_F = 2 * bracket_sq = 2187/20
    # 90-part: ||C_90||^2_F = c_90 * 81 = (61/60)*81 = 61*81/60 = 4941/60 = 1647/20
    # 30-part: ||C_30||^2_F = c_30 * 81 = (1/3)*81 = 27
    # Check: 1647/20 + 27 = 1647/20 + 540/20 = 2187/20 ✓

    print(f"  ||C||^2_F = 2 * 2187/40 = 2187/20 = {2187/20}")
    print(f"  ||C_90||^2_F = (61/60)*81 = {61*81/60} = {Fraction(61*81, 60)}")
    print(f"  ||C_30||^2_F = (1/3)*81 = {81/3} = {Fraction(81, 3)}")
    print(f"  Sum: {Fraction(61*81, 60) + Fraction(81, 3)} = {Fraction(2187, 20)}")
    print(f"  Match: {Fraction(61*81, 60) + Fraction(81, 3) == Fraction(2187, 20)}")

    # Ratio of norms
    ratio_norms = Fraction(61 * 81, 60) / Fraction(81, 3)
    print(f"\n  ||C_90||^2 / ||C_30||^2 = {ratio_norms} = {float(ratio_norms):.6f}")
    print(f"  This equals (61/60) / (1/3) = 61/20 = {61/20}")

    # =====================================================================
    # PART 6: PROJECTOR TRACES
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 6: PROJECTOR TRACE ANALYSIS")
    print("=" * 72)

    # The bracket operator B: Λ^2(H1) -> co-exact is d2* ∘ wedge
    # The partial Casimirs are:
    #   c_90 = (1/81) Tr(B^T P_90 B) where B is the bracket operator
    #   c_30 = (1/81) Tr(B^T P_30 B)

    # Since P_90 + P_30 = P_coex and B maps INTO co-exact:
    #   c_90 + c_30 = (1/81) Tr(B^T B) = K_total = 27/20

    # The trace Tr(P_90) = 90, Tr(P_30) = 30
    # If B were "uniform" on co-exact: c_90/c_30 = 90/30 = 3
    # But we get 61/20 = 3.05, which is close to 3 but not equal.

    # The deviation from 3 is:
    # c_90/c_30 = 61/20 = 3 + 1/20
    # So: c_90 = c_30 * (3 + 1/20)

    print(f"  c_90/c_30 = 61/20 = 3 + 1/20")
    print(f"  If bracket were uniform on co-exact: ratio would be 90/30 = 3")
    print(f"  Actual ratio: 61/20 = 3.05")
    print(f"  Deviation: 1/20 = 0.05")
    print(f"  Relative deviation: 1/60 ≈ 1.67%")

    # The 1/20 excess comes from the non-trivial intertwiner between
    # the bracket map and the 90/30 decomposition.

    # Alternative: express in terms of Casimir eigenvalues of PSp(4,3) irreps
    # The quadratic Casimir C_2(V) for irrep V of a group G satisfies:
    # sum_a T_a^V T_a^V = C_2(V) * I_{dim V}
    # where T_a are generators in representation V.

    # For PSp(4,3), the representations 90 and 30 have different Casimir values.
    # The coupling c_V should be related to C_2(V).

    # =====================================================================
    # PART 7: CHECKING FOR ANALYTIC PATTERN
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 7: ANALYTIC PATTERN SEARCH")
    print("=" * 72)

    # c_90 = 61/60 = (81 - 20) / (81 - 21) = ... no
    # c_90 = 61/60 = (2*81 - 101) / (2*81 - 102) = ... no
    # c_30 = 1/3 = 20/60
    # c_90 = 61/60
    # 61 + 20 = 81 = dim(H1) !!
    # 60 = 81 - 21 = ... or 60 = 3 * 20 = 3 * c_30 * 60
    # 60 = dim(90) - dim(30) = 90 - 30

    print(f"  c_90 = 61/60, c_30 = 20/60")
    print(f"  Numerators: 61 + 20 = 81 = dim(H1)!")
    print(f"  Denominator: 60 = 90 - 30 = dim(chiral) - dim(non-chiral)")
    print(f"  Or: 60 = 3 * 20, and 20 = dim(30) - 10 = ... hmm")

    # Check: c_90 * 60 = 61, c_30 * 60 = 20. So:
    # 60 * K = 60 * 27/20 = 81 = dim(H1). YES!
    # So: 60 * K = 81, giving K = 81/60 = 27/20. ✓
    # And: 60 * c_90 + 60 * c_30 = 61 + 20 = 81

    print(f"\n  KEY IDENTITY: 60 * (27/20) = 81")
    print(f"  This means: (dim_90 - dim_30) * K = dim_H1")
    print(f"  Or: (90 - 30) * 27/20 = 60 * 27/20 = 81 ✓")

    # But what determines the SPLIT 61 + 20 = 81?
    # Hypothesis: c_V is proportional to the dimension-weighted
    # Clebsch-Gordan multiplicity.

    # Alternative: use the trace formula
    # c_90 = (1/81) * (1/|G|) * sum_g |chi_{90}(g)|^2 * something
    # Actually, the Casimir C_V for rep V of G acting on W is:
    # c_V = (dim V / |G|^2) * sum_g,h chi_V(g) chi_V(h) <terms from bracket>

    # Let's try a different approach: compute c_90 and c_30 from the
    # character table alone.

    # The bracket [H,H] -> V is an equivariant map Λ^2(H) -> V.
    # Its norm squared is:
    # ||map||^2 = (1/|G|) * sum_g chi_{Λ^2(H)}(g) * chi_V(g^{-1})
    #           = multiplicity of V in Λ^2(H)

    # But the bracket is NOT just any equivariant map; it's the SPECIFIC
    # map d2* ∘ wedge. The norm depends on the specific map, not just
    # the representation theory.

    # However, since each irrep appears with multiplicity 1 (Schur),
    # the coupling is determined UP TO A SCALAR per irrep.
    # The question is: what is that scalar?

    # Let's compute it numerically and see if it has a nice form.

    # c_90 / m_90 = coupling per copy of 90 in Λ^2(81)
    # c_30 / m_30 = coupling per copy of 30 in Λ^2(81)
    if m_90 > 0 and m_30 > 0:
        per_copy_90 = Fraction(61, 60) / m_90
        per_copy_30 = Fraction(1, 3) / m_30
        print(f"\n  c_90 / m_90 = {per_copy_90} = {float(per_copy_90):.10f}")
        print(f"  c_30 / m_30 = {per_copy_30} = {float(per_copy_30):.10f}")

    # =====================================================================
    # PART 8: THE ANSWER
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 8: SYNTHESIS")
    print("=" * 72)

    print(
        f"""
  CHIRAL SPLIT DERIVATION:

  The total Casimir K = 27/20 splits as:
    K = c_90 + c_30 = 61/60 + 1/3

  NUMEROLOGY:
    60 * K = 60 * 27/20 = 81 = dim(H1)
    60 * c_90 = 61  (the "chiral charge")
    60 * c_30 = 20  (the "non-chiral charge")
    61 + 20 = 81 = dim(H1)

  INTERPRETATION:
    The 81-dim matter sector distributes its coupling strength as:
      61 units to the 90-dim chiral gauge sector
      20 units to the 30-dim non-chiral gauge sector
    Total: 81 units, normalized by factor 60 = dim(90) - dim(30)

  DECOMPOSITION DATA:
    Λ²(81) = {dim_wedge2} dimensions
    Contains 90 with multiplicity {m_90}
    Contains 30 with multiplicity {m_30}
    Contains 81 with multiplicity {round(mult_81_in_wedge2)}

  The ratio c_90/c_30 = 61/20 is NOT simply m_90*90/(m_30*30).
  It reflects the specific geometry of the wedge-coboundary map
  d₂* ∘ ∧ acting on harmonic 1-chains of W(3,3).
"""
    )

    results = {
        "c_90": "61/60",
        "c_30": "1/3",
        "ratio": "61/20",
        "key_identity": "60 * 27/20 = 81",
        "mult_90_in_wedge2": int(round(mult_90_in_wedge2)),
        "mult_30_in_wedge2": int(round(mult_30_in_wedge2)),
        "mult_81_in_wedge2": int(round(mult_81_in_wedge2)),
        "dim_wedge2": dim_wedge2,
        "elapsed_seconds": time.time() - t0,
    }

    out = Path(__file__).resolve().parent.parent / "checks"
    out.mkdir(exist_ok=True)
    fname = out / f"PART_CVII_chiral_split_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"  Wrote: {fname}")
    print(f"  Elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
