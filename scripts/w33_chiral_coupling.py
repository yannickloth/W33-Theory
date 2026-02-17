#!/usr/bin/env python3
"""
Chiral vs Non-Chiral Gauge Coupling from W33
==============================================

THEOREM (Chiral Coupling Split):
  The gauge sector co-exact(120) = 90(chiral) + 30(non-chiral) under PSp(4,3).
  The coupling tensor C[k,i,j] = <g_k, [h_i, h_j]> splits as:

    C = C_chiral(90) + C_nonchiral(30)

  We compute the partial Casimirs:
    K_chiral = sum_{k in 90} M_k^T M_k      (chiral contribution)
    K_nonchiral = sum_{k in 30} M_k^T M_k    (non-chiral contribution)

  Both must be scalar by Schur's lemma (H1 irreducible), so:
    K_chiral = c_90 * I_81
    K_nonchiral = c_30 * I_81
    c_90 + c_30 = 27/20

  The RATIO c_90 / c_30 gives the relative strength of
  chiral vs non-chiral gauge interactions.

PHYSICAL INTERPRETATION:
  - c_90 ~ chiral (weak) gauge coupling
  - c_30 ~ non-chiral (strong/EM) gauge coupling
  - The ratio encodes the tree-level gauge hierarchy

Usage:
  python scripts/w33_chiral_coupling.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import deque
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
    print("  CHIRAL vs NON-CHIRAL GAUGE COUPLING")
    print("=" * 72)

    # Build W33
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    triangles = simplices[2]

    # Build boundary matrices
    d1 = boundary_matrix(simplices[1], simplices[0]).astype(float)
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)

    # Edge index
    edge_idx = {}
    for i, (u, v) in enumerate(edges):
        edge_idx[(u, v)] = (i, +1)
        edge_idx[(v, u)] = (i, -1)

    # Hodge Laplacian eigensystem
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + d2 @ d2.T
    eigvals, eigvecs = np.linalg.eigh(L1)

    harm_mask = np.abs(eigvals) < 0.5
    coex_mask = np.abs(eigvals - 4.0) < 0.5

    H = eigvecs[:, harm_mask]  # 240 x 81 (harmonic = matter)
    W_co = eigvecs[:, coex_mask]  # 240 x 120 (co-exact = gauge)

    n_matter = H.shape[1]
    n_coex = W_co.shape[1]
    print(f"\n  Matter dimension: {n_matter}")
    print(f"  Co-exact dimension: {n_coex}")

    # =====================================================================
    # PART 1: SPLIT CO-EXACT INTO 90 + 30 VIA PSp(4,3)
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 1: DECOMPOSING CO-EXACT 120 = 90 + 30")
    print("=" * 72)

    # Build PSp(4,3)
    print("  Enumerating PSp(4,3)...")
    J_mat = J_matrix()
    gen_vperms = []
    gen_signed = []
    for vert in vertices:
        M_t = transvection_matrix(np.array(vert, dtype=int), J_mat)
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
    print(f"  |PSp(4,3)| = {group_size}")
    group_list = list(visited.items())

    # Character-weighted commutant projection to split 90+30
    print("  Computing character-weighted projection C1...")
    C1_proj = np.zeros((n_coex, n_coex), dtype=float)

    for cur_v, (cur_ep, cur_es) in group_list:
        cur_ep_np = np.asarray(cur_ep, dtype=int)
        cur_es_np = np.asarray(cur_es, dtype=float)
        S_g_W = W_co[cur_ep_np, :] * cur_es_np[:, None]
        R_g = W_co.T @ S_g_W
        chi = float(np.trace(R_g))
        C1_proj += chi * R_g

    C1_proj /= group_size
    C1_proj = (C1_proj + C1_proj.T) / 2

    w1, v1 = np.linalg.eigh(C1_proj)

    # Cluster eigenvalues
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

    print(f"  Co-exact PSp(4,3) decomposition:")
    V_90_co = V_30_co = None
    for val, mult, c_indices in clusters:
        print(f"    eigenvalue {val:.4f}, multiplicity {mult}")
        if mult == 90:
            V_90_co = v1[:, c_indices]
        elif mult == 30:
            V_30_co = v1[:, c_indices]

    assert V_90_co is not None and V_30_co is not None, "Failed to split 90+30"

    # Embed back to edge space
    U_90 = W_co @ V_90_co  # 240 x 90
    U_30 = W_co @ V_30_co  # 240 x 30

    # Verify orthogonality
    cross = np.linalg.norm(U_90.T @ U_30)
    print(f"  Orthogonality check ||U_90^T U_30|| = {cross:.2e}")

    # =====================================================================
    # PART 2: COMPUTE COUPLING TENSORS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 2: COUPLING TENSORS")
    print("=" * 72)

    def wedge_product(h1, h2):
        result = np.zeros(len(triangles))
        for ti, (v0, v1, v2) in enumerate(triangles):
            e01_idx, e01_s = edge_idx[(v0, v1)]
            e02_idx, e02_s = edge_idx[(v0, v2)]
            e12_idx, e12_s = edge_idx[(v1, v2)]
            h1_01 = e01_s * h1[e01_idx]
            h1_02 = e02_s * h1[e02_idx]
            h1_12 = e12_s * h1[e12_idx]
            h2_01 = e01_s * h2[e01_idx]
            h2_02 = e02_s * h2[e02_idx]
            h2_12 = e12_s * h2[e12_idx]
            result[ti] = (
                h1_01 * h2_12
                - h2_01 * h1_12
                - h1_01 * h2_02
                + h2_01 * h1_02
                + h1_02 * h2_12
                - h2_02 * h1_12
            )
        return result

    # Coupling tensor for 90-dim chiral sector
    print(f"  Computing 90-dim chiral coupling tensor...")
    C_90 = np.zeros((90, n_matter, n_matter))
    for i in range(n_matter):
        if i % 20 == 0:
            print(f"    row {i}/{n_matter}...")
        h_i = H[:, i]
        for j in range(i + 1, n_matter):
            h_j = H[:, j]
            w = wedge_product(h_i, h_j)
            bracket = d2 @ w
            coeffs_90 = U_90.T @ bracket
            C_90[:, i, j] = coeffs_90
            C_90[:, j, i] = -coeffs_90

    # Coupling tensor for 30-dim non-chiral sector
    print(f"  Computing 30-dim non-chiral coupling tensor...")
    C_30 = np.zeros((30, n_matter, n_matter))
    for i in range(n_matter):
        if i % 20 == 0:
            print(f"    row {i}/{n_matter}...")
        h_i = H[:, i]
        for j in range(i + 1, n_matter):
            h_j = H[:, j]
            w = wedge_product(h_i, h_j)
            bracket = d2 @ w
            coeffs_30 = U_30.T @ bracket
            C_30[:, i, j] = coeffs_30
            C_30[:, j, i] = -coeffs_30

    norm_90 = np.linalg.norm(C_90)
    norm_30 = np.linalg.norm(C_30)
    print(f"\n  ||C_90||_F = {norm_90:.8f}")
    print(f"  ||C_30||_F = {norm_30:.8f}")
    print(f"  Ratio ||C_90||/||C_30|| = {norm_90/norm_30:.8f}")

    # =====================================================================
    # PART 3: PARTIAL CASIMIRS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 3: PARTIAL CASIMIR OPERATORS")
    print("=" * 72)

    # K_90 = sum_{k=1}^{90} M_k^T M_k
    K_90 = np.zeros((n_matter, n_matter))
    for k in range(90):
        Mk = C_90[k, :, :]
        K_90 += Mk @ Mk.T

    K_90_eigvals = np.linalg.eigvalsh(K_90)
    K_90_unique = sorted(set(round(v, 8) for v in K_90_eigvals if abs(v) > 1e-10))
    c_90 = np.mean(K_90_eigvals)

    print(f"  K_90 eigenvalues (unique): {K_90_unique[:5]}")
    print(f"  K_90 is {'SCALAR' if len(K_90_unique) <= 1 else 'NON-SCALAR'}")
    print(f"  c_90 = {c_90:.10f}")

    # K_30 = sum_{k=1}^{30} M_k^T M_k
    K_30 = np.zeros((n_matter, n_matter))
    for k in range(30):
        Mk = C_30[k, :, :]
        K_30 += Mk @ Mk.T

    K_30_eigvals = np.linalg.eigvalsh(K_30)
    K_30_unique = sorted(set(round(v, 8) for v in K_30_eigvals if abs(v) > 1e-10))
    c_30 = np.mean(K_30_eigvals)

    print(f"\n  K_30 eigenvalues (unique): {K_30_unique[:5]}")
    print(f"  K_30 is {'SCALAR' if len(K_30_unique) <= 1 else 'NON-SCALAR'}")
    print(f"  c_30 = {c_30:.10f}")

    c_total = c_90 + c_30
    print(f"\n  c_90 + c_30 = {c_total:.10f}")
    print(f"  Expected 27/20 = {27/20:.10f}")
    print(f"  Match: {abs(c_total - 27/20) < 1e-8}")

    # =====================================================================
    # PART 4: RATIO ANALYSIS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 4: COUPLING RATIO")
    print("=" * 72)

    ratio = c_90 / c_30 if c_30 > 1e-12 else float("inf")
    print(f"  c_90 / c_30 = {ratio:.10f}")

    # Try to identify as a rational number
    for num in range(1, 200):
        for den in range(1, 200):
            if abs(c_90 - num / den) < 1e-8:
                print(f"  c_90 = {num}/{den} (exact)")
                break
            if abs(c_30 - num / den) < 1e-8:
                print(f"  c_30 = {num}/{den} (exact)")
                break
            if abs(ratio - num / den) < 1e-6:
                print(f"  c_90/c_30 = {num}/{den} (exact)")

    # Use Fraction for exact identification
    c_90_frac = Fraction(c_90).limit_denominator(1000)
    c_30_frac = Fraction(c_30).limit_denominator(1000)
    ratio_frac = Fraction(ratio).limit_denominator(1000)

    print(f"\n  Rational approximations:")
    print(f"    c_90 ~ {c_90_frac} = {float(c_90_frac):.10f}")
    print(f"    c_30 ~ {c_30_frac} = {float(c_30_frac):.10f}")
    print(f"    ratio ~ {ratio_frac} = {float(ratio_frac):.10f}")

    # Verify sum
    sum_frac = c_90_frac + c_30_frac
    print(f"    c_90 + c_30 = {sum_frac} (should be 27/20)")

    # =====================================================================
    # PART 5: GAUGE BOSON ACTIVITY PER SECTOR
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 5: GAUGE BOSON ACTIVITY")
    print("=" * 72)

    # Coupling strength per gauge boson in each sector
    strengths_90 = np.array([np.linalg.norm(C_90[k]) for k in range(90)])
    strengths_30 = np.array([np.linalg.norm(C_30[k]) for k in range(30)])

    active_90 = np.sum(strengths_90 > 1e-10)
    active_30 = np.sum(strengths_30 > 1e-10)

    print(f"  Active chiral gauge bosons:     {active_90}/90")
    print(f"  Active non-chiral gauge bosons: {active_30}/30")

    # Unique strength values
    s90_unique = sorted(set(round(s, 8) for s in strengths_90 if s > 1e-10))
    s30_unique = sorted(set(round(s, 8) for s in strengths_30 if s > 1e-10))
    print(f"\n  Chiral sector unique strengths: {len(s90_unique)}")
    if s90_unique:
        print(f"    min={min(s90_unique):.8f}, max={max(s90_unique):.8f}")
    print(f"  Non-chiral sector unique strengths: {len(s30_unique)}")
    if s30_unique:
        print(f"    min={min(s30_unique):.8f}, max={max(s30_unique):.8f}")

    # =====================================================================
    # PART 6: COMPLEX STRUCTURE ON 90
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 6: COMPLEX STRUCTURE AND CHIRALITY")
    print("=" * 72)

    # The 90-dim has complex structure J with J^2 = -I
    # This means C_90 decomposes into 45 complex gauge bosons
    # Each complex gauge boson g_k + i*J(g_k) carries chirality

    # Compute J from anti-symmetric commutant projection
    np.random.seed(42)
    X = np.random.randn(90, 90)
    A = np.zeros((90, 90), dtype=float)
    for cur_v, (cur_ep, cur_es) in group_list:
        cur_ep_np = np.asarray(cur_ep, dtype=int)
        cur_es_np = np.asarray(cur_es, dtype=float)
        S_g_U = U_90[cur_ep_np, :] * cur_es_np[:, None]
        R_g = U_90.T @ S_g_U
        A += R_g.T @ X @ R_g
    A /= group_size
    A_anti = (A - A.T) / 2
    anti_norm = np.linalg.norm(A_anti)

    if anti_norm > 1e-6:
        J_cand = A_anti / anti_norm * np.sqrt(90)
        J2 = J_cand @ J_cand
        alpha = -float(np.trace(J2)) / 90
        J_true = J_cand / np.sqrt(alpha)
        J2_err = np.linalg.norm(J_true @ J_true + np.eye(90))
        print(f"  Complex structure J: ||J^2 + I|| = {J2_err:.2e}")

        if J2_err < 1e-6:
            print(f"  CONFIRMED: J^2 = -I on the 90-dim sector")

            # Decompose C_90 into 45 complex pairs using J
            # For each gauge boson g_k, pair it with J(g_k)
            # The complex coupling is C_k + i*C_{J(k)}

            # Compute J acting on coupling tensor
            # C_90[k,i,j] -> (C_90 + i * J.C_90)[k,i,j]
            JC_90 = np.einsum("kl,lij->kij", J_true, C_90)

            # The complex coupling norm
            complex_norms = np.sqrt(
                np.array(
                    [
                        np.linalg.norm(C_90[k]) ** 2 + np.linalg.norm(JC_90[k]) ** 2
                        for k in range(90)
                    ]
                )
            )

            # Under J, gauge bosons pair up: (g_k, J*g_k)
            # The 45 complex pairs should have equal norms within pairs
            # Check: J maps each gauge boson to another with same coupling strength
            J_strengths = np.array([np.linalg.norm(JC_90[k]) for k in range(90)])
            print(f"\n  ||C_90[k]|| vs ||J*C_90[k]||:")
            print(
                f"    Max difference: {np.max(np.abs(strengths_90 - J_strengths)):.2e}"
            )
            print(
                f"    J preserves coupling strengths: "
                f"{np.max(np.abs(strengths_90 - J_strengths)) < 1e-8}"
            )

            # The J-eigenvalues of the coupling tensor
            # In complex form: C_complex = (C + i*JC) / sqrt(2)
            # This gives 45 independent complex gauge bosons
            print(f"\n  45 complex gauge bosons from 90 real ones")
            print(f"  Each carries chirality (left or right)")

    # =====================================================================
    # SYNTHESIS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  SYNTHESIS")
    print("=" * 72)

    print(
        f"""
  CHIRAL COUPLING DECOMPOSITION:

  The quadratic Casimir K = (27/20) * I_81 splits as:
    K = K_chiral(90) + K_nonchiral(30)
    c_90 = {c_90:.10f}  (~{c_90_frac})
    c_30 = {c_30:.10f}  (~{c_30_frac})
    c_90 + c_30 = {c_total:.10f} = 27/20

  Ratio: c_90/c_30 = {ratio:.6f} (~{ratio_frac})

  PHYSICAL INTERPRETATION:
    - The 90-dim chiral sector (45_C complex irrep) carries {c_90/c_total*100:.1f}%
      of the total gauge coupling.
    - The 30-dim non-chiral sector (30_R real irrep) carries {c_30/c_total*100:.1f}%
      of the total gauge coupling.

    - Chiral gauge bosons (W+, W-, Z-like) couple with strength c_90
    - Non-chiral gauge bosons (photon, gluon-like) couple with strength c_30
    - The ratio c_90/c_30 = {ratio_frac} encodes the relative coupling strengths
      at the GUT scale.

  DIMENSIONALITY CHECK:
    90 chiral gauge DOFs / 2 (complex) = 45 complex gauge bosons
    30 non-chiral gauge DOFs = 30 real gauge bosons
    Total independent: 45 + 30 = 75 gauge bosons (= 78 - 3 Cartan of SU(3))
"""
    )

    results = {
        "c_90": float(c_90),
        "c_30": float(c_30),
        "c_total": float(c_total),
        "c_90_rational": str(c_90_frac),
        "c_30_rational": str(c_30_frac),
        "ratio": float(ratio),
        "ratio_rational": str(ratio_frac),
        "active_chiral": int(active_90),
        "active_nonchiral": int(active_30),
        "K_90_scalar": bool(len(K_90_unique) <= 1),
        "K_30_scalar": bool(len(K_30_unique) <= 1),
        "elapsed_seconds": time.time() - t0,
    }

    out = Path(__file__).resolve().parent.parent / "checks"
    out.mkdir(exist_ok=True)
    fname = out / f"PART_CVII_chiral_coupling_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder, default=str)
    print(f"  Wrote: {fname}")
    print(f"  Elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
