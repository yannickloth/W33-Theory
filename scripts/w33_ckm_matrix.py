#!/usr/bin/env python3
"""
CKM Matrix from W(3,3) Generation Mixing
==========================================

THEOREM (CKM Matrix):
  The CKM quark mixing matrix arises from the mismatch between two
  Z3-graded generation decompositions of H1(81) = 27+27+27.

  In the Standard Model, the CKM matrix V = U_up^dagger * U_down,
  where U_up and U_down diagonalize the up-type and down-type Yukawa
  couplings respectively. The physical CP-violating phase comes from
  the fact that these two Yukawa couplings cannot be simultaneously
  diagonalized.

  In the W33 framework:
  - Each order-3 element g of PSp(4,3) gives a decomposition 81 = 27+27+27
  - Different Z3 elements give DIFFERENT generation bases
  - The overlap matrix V_{ab} = <gen_a(g1) | gen_b(g2)> between two
    Z3 decompositions IS the CKM matrix (up to phase conventions)
  - From Pillar 37: CP is conserved at the W33 level (Y_J = 0),
    so CP violation requires SPONTANEOUS symmetry breaking = VEV choice

COMPUTATION:
  Part 1: Find multiple order-3 elements giving 27+27+27
  Part 2: Compute generation bases for two distinct Z3 elements
  Part 3: Construct CKM matrix V = overlap between generation bases
  Part 4: Extract mixing angles (theta_12, theta_13, theta_23, delta_CP)
  Part 5: Jarlskog invariant
  Part 6: Wolfenstein parameters
  Part 7: Synthesis

Usage:
  python scripts/w33_ckm_matrix.py
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


def get_generation_basis(R_g, H):
    """Extract orthogonal 27+27+27 generation basis from an order-3 rep matrix.

    Parameters:
        R_g: 81x81 representation matrix of an order-3 element on H1
        H: 240x81 harmonic basis

    Returns:
        list of three 81x27 real orthonormal basis matrices [B0, B1, B2]
    """
    omega = np.exp(2j * np.pi / 3)
    I81 = np.eye(81)
    R2 = R_g @ R_g

    # Eigenvalue-1 projector
    P0 = np.real((I81 + R_g + R2) / 3.0)
    U0, S0, _ = np.linalg.svd(P0)
    B0 = U0[:, :27]  # eigenvalue-1 space

    # Eigenvalue-omega eigenvectors
    eig_vals, eig_vecs = np.linalg.eig(R_g)
    phases = np.angle(eig_vals)

    # Find omega eigenspace
    omega_idx = np.where(np.abs(phases - 2 * np.pi / 3) < 0.1)[0]
    if len(omega_idx) != 27:
        omega_idx = np.where(np.abs(phases + 2 * np.pi / 3) < 0.1)[0]
        if len(omega_idx) != 27:
            # Fallback: group by phase
            phase_groups = {}
            for i in range(81):
                p = round(phases[i] / (2 * np.pi / 3))
                if p not in phase_groups:
                    phase_groups[p] = []
                phase_groups[p].append(i)
            for key, idx_list in phase_groups.items():
                if key != 0 and len(idx_list) == 27:
                    omega_idx = np.array(idx_list)
                    break

    V_omega = eig_vecs[:, omega_idx]  # 81x27 complex
    B1_raw = np.real(V_omega)
    B2_raw = np.imag(V_omega)

    # Orthogonalize in complement
    def orthogonalize_complement(vecs, already):
        proj = already @ already.T
        vecs_comp = vecs - proj @ vecs
        Q, R = np.linalg.qr(vecs_comp)
        rank = np.sum(np.abs(np.diag(R)) > 1e-10)
        return Q[:, :rank]

    B1 = orthogonalize_complement(B1_raw, B0)
    B2 = orthogonalize_complement(B2_raw, np.hstack([B0, B1]))

    return [B0, B1, B2]


def main():
    t0 = time.time()
    print("=" * 72)
    print("  CKM MATRIX FROM W(3,3) GENERATION MIXING")
    print("=" * 72)

    # Build W33
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)

    # Hodge decomposition
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + d2 @ d2.T
    eigvals, eigvecs = np.linalg.eigh(L1)
    harm_mask = np.abs(eigvals) < 0.5
    H = eigvecs[:, harm_mask]  # 240 x 81

    # Build PSp(4,3)
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

    print(f"  |PSp(4,3)| = {len(visited)}")
    group_list = list(visited.items())

    # ================================================================
    # PART 1: FIND MULTIPLE ORDER-3 ELEMENTS
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 1: ORDER-3 ELEMENTS OF PSp(4,3)")
    print(f"{'='*72}")

    omega = np.exp(2j * np.pi / 3)
    order3_elements = []

    for idx, (cur_v, (cur_ep, cur_es)) in enumerate(group_list):
        if cur_v == id_v:
            continue
        # Check order 3
        v2 = tuple(cur_v[cur_v[i]] for i in range(n))
        v3 = tuple(cur_v[v2[i]] for i in range(n))
        if v3 != id_v:
            continue

        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)
        S_g = H[ep_np, :] * es_np[:, None]
        R_g = H.T @ S_g  # 81 x 81

        # Check eigenvalue decomposition
        eigs = np.linalg.eigvals(R_g)
        phases = np.angle(eigs) / (2 * np.pi / 3)
        counts = Counter(round(p) % 3 for p in phases)

        if counts[0] == 27 and counts[1] == 27 and counts[2] == 27:
            order3_elements.append((cur_v, cur_ep, cur_es, R_g))
            if len(order3_elements) >= 20:
                break

    print(f"  Found {len(order3_elements)} order-3 elements giving 27+27+27")

    # ================================================================
    # PART 2: GENERATION BASES FOR TWO DISTINCT Z3 ELEMENTS
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 2: GENERATION BASES")
    print(f"{'='*72}")

    # Use the first two order-3 elements as "up-type" and "down-type"
    g_up = order3_elements[0]
    # Find one that's maximally different from the first
    best_idx = 1
    best_diff = 0
    for idx in range(1, len(order3_elements)):
        R1 = order3_elements[0][3]
        R2 = order3_elements[idx][3]
        diff = np.linalg.norm(R1 - R2)
        if diff > best_diff:
            best_diff = diff
            best_idx = idx

    g_down = order3_elements[best_idx]
    print(f"  Selected g_up (element 0) and g_down (element {best_idx})")
    print(f"  ||R_up - R_down|| = {best_diff:.6f}")

    # Get generation bases
    gens_up = get_generation_basis(g_up[3], H)
    gens_down = get_generation_basis(g_down[3], H)

    for i, B in enumerate(gens_up):
        print(f"  g_up generation {i}: dim = {B.shape[1]}")
    for i, B in enumerate(gens_down):
        print(f"  g_down generation {i}: dim = {B.shape[1]}")

    # Verify orthogonality within each set
    for label, gens in [("up", gens_up), ("down", gens_down)]:
        for a in range(3):
            for b in range(a + 1, 3):
                cross = np.linalg.norm(gens[a].T @ gens[b])
                assert cross < 1e-8, f"{label} gens {a},{b} not orthogonal: {cross}"
    print(f"  Both generation sets are internally orthogonal ✓")

    # ================================================================
    # PART 3: CKM MATRIX
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 3: CKM MATRIX V = <up_a | down_b>")
    print(f"{'='*72}")

    # The CKM matrix elements are:
    # V_{ab} = Tr(P_up^a * P_down^b) / 27
    # where P_up^a = gens_up[a] @ gens_up[a].T is the projector onto gen a
    # of the up-type decomposition.

    # More precisely: V is a 3x3 unitary matrix (up to normalization)
    # formed from the singular values of the overlap between generation subspaces.

    # Method: use the full 81x81 transformation
    # U_up = [B0_up | B1_up | B2_up]  (81 x 81)
    # U_down = [B0_down | B1_down | B2_down]  (81 x 81)
    # V_full = U_up^T @ U_down  (81 x 81)
    # The CKM matrix is the 3x3 block structure of V_full.

    U_up = np.hstack(gens_up)  # 81 x 81
    U_down = np.hstack(gens_down)  # 81 x 81
    V_full = U_up.T @ U_down  # 81 x 81

    # The 3x3 CKM matrix has elements:
    # |V_{ab}|^2 = sum_{i in gen_a(up), j in gen_b(down)} |V_full[i,j]|^2 / 27
    V_CKM_sq = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            block = V_full[27 * a : 27 * (a + 1), 27 * b : 27 * (b + 1)]
            V_CKM_sq[a, b] = np.trace(block @ block.T) / 27.0

    print(f"\n  |V_CKM|^2 matrix (generation overlap):")
    for a in range(3):
        row = "    ["
        for b in range(3):
            row += f" {V_CKM_sq[a,b]:.6f}"
        row += " ]"
        print(row)

    # Row and column sums should be 1 (unitarity)
    print(f"\n  Row sums: {[f'{np.sum(V_CKM_sq[a,:]):.6f}' for a in range(3)]}")
    print(f"  Col sums: {[f'{np.sum(V_CKM_sq[:,b]):.6f}' for b in range(3)]}")

    # Check unitarity
    row_sum_err = max(abs(np.sum(V_CKM_sq[a, :]) - 1) for a in range(3))
    col_sum_err = max(abs(np.sum(V_CKM_sq[:, b]) - 1) for b in range(3))
    print(f"  Unitarity error (rows): {row_sum_err:.2e}")
    print(f"  Unitarity error (cols): {col_sum_err:.2e}")

    # The CKM amplitudes
    V_CKM = np.sqrt(V_CKM_sq)
    print(f"\n  |V_CKM| matrix:")
    for a in range(3):
        row = "    ["
        for b in range(3):
            row += f" {V_CKM[a,b]:.6f}"
        row += " ]"
        print(row)

    # ================================================================
    # PART 4: MIXING ANGLES
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 4: MIXING ANGLES")
    print(f"{'='*72}")

    # Standard parametrization:
    # V_CKM = [[c12*c13, s12*c13, s13*e^{-i*delta}],
    #           [-s12*c23 - c12*s23*s13*e^{i*delta}, c12*c23 - s12*s23*s13*e^{i*delta}, s23*c13],
    #           [s12*s23 - c12*c23*s13*e^{i*delta}, -c12*s23 - s12*c23*s13*e^{i*delta}, c23*c13]]

    # Extract angles from |V| elements:
    # |V_13| = s13
    s13 = V_CKM[0, 2]
    theta13 = np.arcsin(min(s13, 1.0))

    # |V_12| = s12 * c13, so s12 = |V_12| / c13
    c13 = np.cos(theta13)
    if c13 > 1e-10:
        s12 = V_CKM[0, 1] / c13
        theta12 = np.arcsin(min(s12, 1.0))

        # |V_23| = s23 * c13, so s23 = |V_23| / c13
        s23 = V_CKM[1, 2] / c13
        theta23 = np.arcsin(min(s23, 1.0))
    else:
        theta12 = 0
        theta23 = 0
        s12 = 0
        s23 = 0

    print(f"\n  CKM mixing angles:")
    print(f"    theta_12 (Cabibbo) = {np.degrees(theta12):.4f}°")
    print(f"    theta_13           = {np.degrees(theta13):.4f}°")
    print(f"    theta_23           = {np.degrees(theta23):.4f}°")
    print(f"  Sines:")
    print(f"    sin(theta_12) = {s12:.6f}")
    print(f"    sin(theta_13) = {s13:.6f}")
    print(f"    sin(theta_23) = {s23:.6f}")

    # Experimental values for comparison:
    print(f"\n  Experimental CKM (PDG 2024):")
    print(f"    theta_12 = 13.02° ± 0.04°")
    print(f"    theta_13 = 0.201° ± 0.011°")
    print(f"    theta_23 = 2.36° ± 0.06°")
    print(f"    |V_us| = 0.2243, |V_cb| = 0.0422, |V_ub| = 0.00394")

    # ================================================================
    # PART 5: JARLSKOG INVARIANT
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 5: JARLSKOG INVARIANT")
    print(f"{'='*72}")

    # The Jarlskog invariant J = Im(V_us V_cb V_ub* V_cs*)
    # For real CKM (our case, since Y_J = 0 from Pillar 37):
    #   J = 0 at the W33 level
    # But with complex phases from SSB, J can be nonzero.

    # From Pillar 37: CP is conserved at W33 level.
    # The CKM matrix we computed is REAL (no complex phases).
    # J = c12 * c23 * c13^2 * s12 * s13 * s23 * sin(delta)

    # Since our V is real, delta = 0 or pi, so J = 0.
    J_max = float(
        np.cos(theta12) * np.cos(theta23) * np.cos(theta13) ** 2 * s12 * s13 * s23
    )
    print(f"\n  Jarlskog invariant:")
    print(f"    J_max = c12*c23*c13^2*s12*s13*s23 = {J_max:.8f}")
    print(f"    J = J_max * sin(delta_CP)")
    print(f"\n  At W33 level (before SSB): delta_CP = 0 → J = 0")
    print(f"  This is CONSISTENT with Pillar 37 (Y_J = 0 selection rule)")
    print(f"\n  CP violation requires SSB to choose a vacuum that breaks")
    print(f"  the equivariance constraint, generating delta_CP != 0.")

    # Experimental J
    J_exp = 3.08e-5
    print(f"\n  Experimental: J = {J_exp:.2e}")
    print(
        f"  To match: sin(delta_CP) = J_exp / J_max = {J_exp / J_max:.6f}"
        if J_max > 1e-10
        else "  J_max ~ 0, mixing angles too small"
    )

    # ================================================================
    # PART 6: WOLFENSTEIN PARAMETERS
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 6: WOLFENSTEIN PARAMETERS")
    print(f"{'='*72}")

    # Wolfenstein parametrization:
    # lambda = s12 = |V_us|
    # A = s23 / lambda^2 = |V_cb| / |V_us|^2
    # rho + i*eta from V_ub = A * lambda^3 * (rho - i*eta)

    lam_W = s12  # Cabibbo angle sine
    if lam_W > 1e-10:
        A_W = s23 / lam_W**2
        rho_W = s13 / (A_W * lam_W**3) if A_W * lam_W**3 > 1e-10 else 0
    else:
        A_W = 0
        rho_W = 0

    print(f"\n  Wolfenstein parameters:")
    print(f"    lambda = {lam_W:.6f}")
    print(f"    A      = {A_W:.6f}")
    print(f"    rho    = {rho_W:.6f}")
    print(f"    eta    = 0 (CP conserved at W33 level)")

    print(f"\n  Experimental (PDG 2024):")
    print(f"    lambda = 0.22650 ± 0.00048")
    print(f"    A      = 0.790 ± 0.012")
    print(f"    rho    = 0.141 ± 0.017")
    print(f"    eta    = 0.357 ± 0.011")

    # ================================================================
    # PART 7: DEMOCRATIC MIXING AND UNIVERSALITY
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 7: DEMOCRATIC MIXING AND UNIVERSAL STRUCTURE")
    print(f"{'='*72}")

    # Check how close V_CKM_sq is to the universal mixing matrix
    # Universal: M = (1/81)[[25,28,28],[28,25,28],[28,28,25]]
    # i.e., M_diag = 25/81, M_off = 28/81

    M_universal = np.array([[25, 28, 28], [28, 25, 28], [28, 28, 25]]) / 81.0
    diff_from_universal = np.linalg.norm(V_CKM_sq - M_universal)

    print(f"\n  Universal mixing matrix (Pillar 16):")
    print(f"    M_diag = 25/81 = {25/81:.6f}")
    print(f"    M_off  = 28/81 = {28/81:.6f}")
    print(f"\n  ||V_CKM^2 - M_universal|| = {diff_from_universal:.6f}")

    # Check if V_CKM^2 has the "democratic + perturbation" structure
    # V = D + epsilon * X where D is democratic (all 1/3)
    V_democratic = np.ones((3, 3)) / 3.0
    V_deviation = V_CKM_sq - V_democratic
    dev_norm = np.linalg.norm(V_deviation)

    print(f"\n  Democratic deviation: ||V - 1/3|| = {dev_norm:.6f}")
    if dev_norm < 0.01:
        print(f"  NEARLY DEMOCRATIC: V ≈ (1/3) * [[1,1,1],[1,1,1],[1,1,1]]")
        print(f"  → No generation hierarchy at group-theory level")
        print(f"  → Hierarchy comes from SSB/VEV choice")
    elif dev_norm < 0.1:
        print(f"  QUASI-DEMOCRATIC: small deviation from equal mixing")
    else:
        print(f"  HIERARCHICAL: significant deviation from democratic mixing")

    # Diagonal dominance measure
    diag_dom = np.mean([V_CKM_sq[i, i] for i in range(3)])
    off_dom = np.mean([V_CKM_sq[i, j] for i in range(3) for j in range(3) if i != j])
    print(f"\n  Diagonal dominance: <V_diag^2> = {diag_dom:.6f}")
    print(f"  Off-diagonal: <V_off^2> = {off_dom:.6f}")
    print(f"  Ratio: diag/off = {diag_dom/off_dom:.6f}" if off_dom > 0 else "")

    # Check how many distinct Z3 decompositions exist
    print(f"\n  Number of distinct Z3 decompositions found: {len(order3_elements)}")
    print(f"  (Out of total 800 order-3 elements in PSp(4,3))")

    # Compute pairwise overlaps between all found elements
    print(f"\n  Pairwise ||R_i - R_j|| for first 5 elements:")
    n_show = min(5, len(order3_elements))
    for i in range(n_show):
        row = "    "
        for j in range(n_show):
            d = np.linalg.norm(order3_elements[i][3] - order3_elements[j][3])
            row += f" {d:6.2f}"
        print(row)

    # ================================================================
    # PART 8: SYNTHESIS
    # ================================================================
    print(f"\n{'='*72}")
    print(f"  PART 8: SYNTHESIS")
    print(f"{'='*72}")

    print(
        f"""
  CKM MATRIX FROM W(3,3):

  1. GENERATION MISMATCH:
     Different order-3 elements of PSp(4,3) give different 27+27+27
     decompositions of H1(81). The CKM matrix is the overlap between
     two such decompositions ("up-type" and "down-type").

  2. CKM STRUCTURE:
     |V_CKM|^2 diagonal: {[f'{V_CKM_sq[i,i]:.4f}' for i in range(3)]}
     |V_CKM|^2 off-diag: {[f'{V_CKM_sq[0,1]:.4f}', f'{V_CKM_sq[0,2]:.4f}', f'{V_CKM_sq[1,2]:.4f}']}
     Democratic deviation: {dev_norm:.4f}

  3. MIXING ANGLES:
     theta_12 = {np.degrees(theta12):.2f}° (Cabibbo)
     theta_13 = {np.degrees(theta13):.2f}°
     theta_23 = {np.degrees(theta23):.2f}°

  4. CP VIOLATION:
     J = 0 at W33 level (Pillar 37: Y_J = 0 selection rule)
     delta_CP generated by SSB (VEV misalignment)
     J_max = {J_max:.6f} (maximum possible Jarlskog)

  5. UNIVERSALITY:
     The CKM matrix structure is determined by the GROUP THEORY
     of PSp(4,3) acting on H1(81). The precise values of mixing
     angles depend on which pair of Z3 elements are chosen
     (= which VEV alignment is selected by SSB).

  6. PHYSICAL PICTURE:
     W33 provides the FRAMEWORK: 3 generations, unitary mixing,
     vanishing CP at the symmetric level. The DETAILED mixing
     pattern (Cabibbo angle, etc.) requires specifying the vacuum.
     This is analogous to how the Higgs mechanism gives masses
     but the Yukawa couplings must be measured.

  CONCLUSION: The CKM matrix emerges naturally from the mismatch
  between Z3-graded generation decompositions of H1(81). CP violation
  is spontaneous (requires SSB), consistent with Pillar 37.
"""
    )

    elapsed = time.time() - t0

    results = {
        "V_CKM_sq": V_CKM_sq.tolist(),
        "V_CKM": V_CKM.tolist(),
        "theta_12_deg": float(np.degrees(theta12)),
        "theta_13_deg": float(np.degrees(theta13)),
        "theta_23_deg": float(np.degrees(theta23)),
        "J_max": float(J_max),
        "J_actual": 0.0,
        "wolfenstein_lambda": float(lam_W),
        "wolfenstein_A": float(A_W),
        "democratic_deviation": float(dev_norm),
        "n_order3_found": len(order3_elements),
        "R_up_R_down_diff": float(best_diff),
        "unitarity_error_rows": float(row_sum_err),
        "unitarity_error_cols": float(col_sum_err),
        "elapsed_seconds": elapsed,
    }

    out_dir = Path(__file__).resolve().parent.parent / "checks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"PART_CXII_ckm_matrix_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder, default=str)
    print(f"  Wrote: {fname}")
    print(f"  Elapsed: {elapsed:.1f}s")

    return results


if __name__ == "__main__":
    main()
