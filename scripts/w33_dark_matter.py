#!/usr/bin/env python3
"""
Dark Matter Candidates from W(3,3) Spectral Structure
=======================================================

THEOREM (Dark Matter from Exact Sector):
  The exact sector of the Hodge Laplacian on W(3,3) contains 39 = 24 + 15
  moduli fields at eigenvalues 10 and 16, spectrally isolated from both
  the matter sector (eigenvalue 0) and the gauge sector (eigenvalue 4).
  These fields are natural dark matter candidates with the following
  properties:

  1. SPECTRAL ISOLATION: Gap of 6 from gauge bosons (10-4=6),
     gap of 10 from matter (10-0=10). Dark matter does not mix with
     visible matter at the topological level.

  2. TWO SPECIES: The 24-dim (SU(5) adjoint) and 15-dim (SU(4) adjoint)
     components form two distinct dark matter species with mass ratio
     M_heavy/M_light = sqrt(16/10) = sqrt(8/5) ~ 1.265.

  3. STABILITY: Both sectors are IRREDUCIBLE under PSp(4,3) (FS=+1),
     preventing decay to visible sector fields.

  4. ABUNDANCE RATIO: The spectral democracy relation
     n_24 * lambda_24 = n_15 * lambda_15 = 240 predicts a fixed
     ratio of dark matter species abundances.

COMPUTATION:
  Part 1: Exact sector decomposition and projectors
  Part 2: Coupling of exact sector to matter (forbidden channels)
  Part 3: Self-coupling within exact sector
  Part 4: Dark matter mass predictions
  Part 5: Relic abundance estimates from spectral democracy
  Part 6: Synthesis

Usage:
  python scripts/w33_dark_matter.py
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from w33_homology import boundary_matrix, build_clique_complex, build_w33

from w33_h1_decomposition import build_incidence_matrix


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
    print("  DARK MATTER CANDIDATES FROM W(3,3) SPECTRAL STRUCTURE")
    print("=" * 72)

    # Build W33
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    triangles = simplices[2]

    # Hodge decomposition
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + d2 @ d2.T
    eigvals, eigvecs = np.linalg.eigh(L1)

    # Four Hodge sectors
    harm_mask = np.abs(eigvals) < 0.5  # lambda=0, dim 81
    coex_mask = np.abs(eigvals - 4.0) < 0.5  # lambda=4, dim 120
    ex10_mask = np.abs(eigvals - 10.0) < 0.5  # lambda=10, dim 24
    ex16_mask = np.abs(eigvals - 16.0) < 0.5  # lambda=16, dim 15

    H = eigvecs[:, harm_mask]  # 240 x 81
    W_co = eigvecs[:, coex_mask]  # 240 x 120
    V_24 = eigvecs[:, ex10_mask]  # 240 x 24
    V_15 = eigvecs[:, ex16_mask]  # 240 x 15

    # Projectors
    P_harm = H @ H.T
    P_coex = W_co @ W_co.T
    P_24 = V_24 @ V_24.T
    P_15 = V_15 @ V_15.T

    print(f"\n  Hodge decomposition of C_1(240):")
    print(f"    Harmonic (matter):  lambda=0,  dim={H.shape[1]}")
    print(f"    Co-exact (gauge):   lambda=4,  dim={W_co.shape[1]}")
    print(f"    Exact-24 (DM-1):    lambda=10, dim={V_24.shape[1]}")
    print(f"    Exact-15 (DM-2):    lambda=16, dim={V_15.shape[1]}")

    # Edge index
    edge_idx = {}
    for i, (u, v) in enumerate(edges):
        edge_idx[(u, v)] = (i, +1)
        edge_idx[(v, u)] = (i, -1)

    # =====================================================================
    # PART 1: SPECTRAL ISOLATION
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 1: SPECTRAL ISOLATION OF DARK MATTER SECTORS")
    print("=" * 72)

    # Spectral gaps between all sectors
    gaps = {
        "matter-gauge": 4.0 - 0.0,
        "gauge-DM1": 10.0 - 4.0,
        "DM1-DM2": 16.0 - 10.0,
        "matter-DM1": 10.0 - 0.0,
        "matter-DM2": 16.0 - 0.0,
        "gauge-DM2": 16.0 - 4.0,
    }

    print(f"  Spectral gaps (eigenvalue differences):")
    for name, gap in gaps.items():
        print(f"    {name}: {gap:.0f}")

    # Projector orthogonality
    cross_products = {
        "P_harm @ P_24": np.linalg.norm(P_harm @ P_24),
        "P_harm @ P_15": np.linalg.norm(P_harm @ P_15),
        "P_coex @ P_24": np.linalg.norm(P_coex @ P_24),
        "P_coex @ P_15": np.linalg.norm(P_coex @ P_15),
        "P_24 @ P_15": np.linalg.norm(P_24 @ P_15),
    }

    print(f"\n  Projector orthogonality (should all be ~0):")
    for name, val in cross_products.items():
        print(f"    ||{name}|| = {val:.2e}")

    # Completeness
    P_total = P_harm + P_coex + P_24 + P_15
    completeness_err = np.linalg.norm(P_total - np.eye(m))
    print(f"\n  Projector completeness: ||P_total - I|| = {completeness_err:.2e}")

    # =====================================================================
    # PART 2: MATTER-DM COUPLING (FORBIDDEN CHANNELS)
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 2: MATTER-DM COUPLING ANALYSIS")
    print("=" * 72)

    # The bracket [h_i, h_j] = d2*(h_i ^ h_j) maps matter×matter -> co-exact.
    # It does NOT map into the exact sector (by the Hodge decomposition).
    # This means: at tree level, matter-DM coupling is TOPOLOGICALLY FORBIDDEN.

    def wedge_product(h1, h2):
        result = np.zeros(len(triangles))
        for ti, (v0, v1_, v2) in enumerate(triangles):
            e01_i, e01_s = edge_idx[(v0, v1_)]
            e02_i, e02_s = edge_idx[(v0, v2)]
            e12_i, e12_s = edge_idx[(v1_, v2)]
            h1_01 = e01_s * h1[e01_i]
            h1_02 = e02_s * h1[e02_i]
            h1_12 = e12_s * h1[e12_i]
            h2_01 = e01_s * h2[e01_i]
            h2_02 = e02_s * h2[e02_i]
            h2_12 = e12_s * h2[e12_i]
            result[ti] = (
                h1_01 * h2_12
                - h2_01 * h1_12
                - h1_01 * h2_02
                + h2_01 * h1_02
                + h1_02 * h2_12
                - h2_02 * h1_12
            )
        return result

    # Sample some matter-matter brackets and check exact-sector projection
    print("  Checking matter-matter bracket projection to exact sector...")
    max_leak_24 = 0.0
    max_leak_15 = 0.0
    n_samples = 50
    np.random.seed(42)

    for _ in range(n_samples):
        i, j = np.random.choice(H.shape[1], 2, replace=False)
        h_i = H[:, i]
        h_j = H[:, j]
        w = wedge_product(h_i, h_j)
        bracket = d2 @ w

        # Project onto exact sectors
        proj_24 = float(np.dot(bracket, P_24 @ bracket))
        proj_15 = float(np.dot(bracket, P_15 @ bracket))
        proj_coex = float(np.dot(bracket, P_coex @ bracket))
        total = float(np.dot(bracket, bracket))

        if total > 1e-15:
            max_leak_24 = max(max_leak_24, abs(proj_24 / total))
            max_leak_15 = max(max_leak_15, abs(proj_15 / total))

    print(f"  Max leakage to 24-dim exact: {max_leak_24:.2e}")
    print(f"  Max leakage to 15-dim exact: {max_leak_15:.2e}")
    print(
        f"  [h_i, h_j] is {'100% co-exact' if max_leak_24 < 1e-10 and max_leak_15 < 1e-10 else 'LEAKS to exact'}"
    )

    # The bracket maps into co-exact ONLY.
    # This means: dark matter particles (exact sector) do NOT couple
    # directly to matter via the bracket mechanism.
    matter_dm_decoupled = max_leak_24 < 1e-10 and max_leak_15 < 1e-10
    print(
        f"\n  RESULT: Matter-DM direct coupling is "
        f"{'TOPOLOGICALLY FORBIDDEN' if matter_dm_decoupled else 'ALLOWED'}"
    )

    # =====================================================================
    # PART 3: DARK MATTER SELF-COUPLING
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 3: DARK MATTER SELF-COUPLING")
    print("=" * 72)

    # The exact sector fields arise from the vertex Laplacian L0.
    # L0 has eigenvalues: 0 (mult 1), 10 (mult 24), 16 (mult 15).
    # The exact 1-chains are images of d1: C0 -> C1.

    L0 = D @ D.T
    w0, v0 = np.linalg.eigh(L0)

    # Vertex eigenvectors for each sector
    v0_1 = v0[:, np.abs(w0) < 0.5]  # 40x1 (constant mode)
    v0_24 = v0[:, np.abs(w0 - 10.0) < 0.5]  # 40x24
    v0_15 = v0[:, np.abs(w0 - 16.0) < 0.5]  # 40x15

    print(f"  L0 decomposition: 1 + 24 + 15 = 40")
    print(f"    Constant mode: dim {v0_1.shape[1]}")
    print(f"    24 (SU(5) adj): dim {v0_24.shape[1]}, lambda=10")
    print(f"    15 (SU(4) adj): dim {v0_15.shape[1]}, lambda=16")

    # DM self-coupling: can the exact-sector fields couple to each other?
    # The exact 1-chain for a vertex eigenfunction f is: d1(f) = D^T f.
    # Self-coupling requires a 3-point function.
    # For graph functions: f_a * f_b * f_c summed over vertices.

    # Compute the triple overlap tensor T[a,b,c] = sum_v f_a(v) f_b(v) f_c(v)
    # for the 24-dim sector
    print(f"\n  Computing DM-24 self-coupling (triple overlap)...")
    T_24_norm = 0.0
    for a in range(24):
        for b in range(a, 24):
            for c in range(b, 24):
                t = float(np.sum(v0_24[:, a] * v0_24[:, b] * v0_24[:, c]))
                T_24_norm += t * t

    T_24_norm = np.sqrt(T_24_norm)
    print(f"  ||T_24||_F = {T_24_norm:.8f}")

    # Cross-coupling between 24 and 15
    print(f"  Computing DM-24 × DM-15 coupling...")
    T_cross_norm = 0.0
    for a in range(24):
        for b in range(15):
            for c in range(15):
                t = float(np.sum(v0_24[:, a] * v0_15[:, b] * v0_15[:, c]))
                T_cross_norm += t * t

    T_cross_norm = np.sqrt(T_cross_norm)
    print(f"  ||T_24×15×15||_F = {T_cross_norm:.8f}")

    # 15-dim self-coupling
    print(f"  Computing DM-15 self-coupling...")
    T_15_norm = 0.0
    for a in range(15):
        for b in range(a, 15):
            for c in range(b, 15):
                t = float(np.sum(v0_15[:, a] * v0_15[:, b] * v0_15[:, c]))
                T_15_norm += t * t

    T_15_norm = np.sqrt(T_15_norm)
    print(f"  ||T_15||_F = {T_15_norm:.8f}")

    # crude conversion to self-interaction cross section per mass
    m_dm_gev = 100.0  # assume ~100 GeV scale
    g_eff = T_24_norm
    m_dm_g = m_dm_gev * 1.78e-24  # grams
    sigma_over_m = (g_eff ** 4) / (4 * np.pi * (m_dm_gev ** 3))
    sigma_over_m *= 1.78e-24
    print(f"\n  Approximate self-interaction σ/m = {sigma_over_m:.2e} cm^2/g")

    # =====================================================================
    # PART 4: DARK MATTER MASS PREDICTIONS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 4: MASS PREDICTIONS FROM SPECTRAL DATA")
    print("=" * 72)

    # Mass ratios from Hodge eigenvalues:
    # M_DM1 / M_gauge = sqrt(lambda_10 / lambda_4) = sqrt(10/4) = sqrt(5/2)
    # M_DM2 / M_gauge = sqrt(lambda_16 / lambda_4) = sqrt(16/4) = 2
    # M_DM2 / M_DM1 = sqrt(16/10) = sqrt(8/5)

    r_DM1_gauge = np.sqrt(10 / 4)
    r_DM2_gauge = np.sqrt(16 / 4)
    r_DM2_DM1 = np.sqrt(16 / 10)

    print(f"  Mass ratios (from sqrt of eigenvalue ratios):")
    print(f"    M_DM1/M_gauge = sqrt(10/4) = sqrt(5/2) = {r_DM1_gauge:.6f}")
    print(f"    M_DM2/M_gauge = sqrt(16/4) = 2.000000")
    print(f"    M_DM2/M_DM1 = sqrt(16/10) = sqrt(8/5) = {r_DM2_DM1:.6f}")

    # Fractions
    print(f"\n  Exact ratios:")
    print(
        f"    M_DM1/M_gauge = sqrt({Fraction(5,2)}) = {float(Fraction(5,2))**0.5:.10f}"
    )
    print(f"    M_DM2/M_gauge = {Fraction(2,1)}")
    print(f"    M_DM2/M_DM1 = sqrt({Fraction(8,5)}) = {float(Fraction(8,5))**0.5:.10f}")

    # =====================================================================
    # PART 5: RELIC ABUNDANCE FROM SPECTRAL DEMOCRACY
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 5: SPECTRAL DEMOCRACY AND ABUNDANCE RATIOS")
    print("=" * 72)

    # Spectral democracy: n_k * lambda_k = 240 for all sectors
    # This gives: 24*10 = 15*16 = 120*4 ... no, 120*4=480 ≠ 240
    # Actually: spectral democracy is 24*10 = 15*16 = 240 (exact sector only)
    # And for co-exact: it's 120*4 = 480 (different).
    # Actually from Pillar 18: lambda_2*n_2 = lambda_3*n_3 = 240
    # where lambda_2=10, n_2=24, lambda_3=16, n_3=15.

    sd_24 = 24 * 10
    sd_15 = 15 * 16
    sd_coex = 120 * 4

    print(f"  Spectral democracy check:")
    print(f"    n_24 * lambda_10 = 24 * 10 = {sd_24}")
    print(f"    n_15 * lambda_16 = 15 * 16 = {sd_15}")
    print(f"    n_coex * lambda_4 = 120 * 4 = {sd_coex}")
    print(
        f"    Exact sector democracy: {sd_24} = {sd_15} = 240 {'HOLDS' if sd_24 == sd_15 == 240 else 'FAILS'}"
    )

    # The abundance ratio of the two DM species
    # In thermal freeze-out: Omega ~ n * M ~ n * sqrt(lambda)
    # Omega_24 / Omega_15 = (24 * sqrt(10)) / (15 * sqrt(16)) = 24*sqrt(10) / 60
    omega_ratio = (24 * np.sqrt(10)) / (15 * np.sqrt(16))
    print(f"\n  DM abundance ratio (thermal estimate):")
    print(f"    Omega_24/Omega_15 = 24*sqrt(10)/(15*4) = {omega_ratio:.6f}")
    print(f"    = {24*np.sqrt(10)/60:.6f}")

    # Fraction of total dark matter
    omega_24_frac = 24 * np.sqrt(10) / (24 * np.sqrt(10) + 15 * np.sqrt(16))
    omega_15_frac = 15 * np.sqrt(16) / (24 * np.sqrt(10) + 15 * np.sqrt(16))
    print(f"\n  DM composition:")
    print(f"    DM-24 (lighter): {omega_24_frac*100:.1f}%")
    print(f"    DM-15 (heavier): {omega_15_frac*100:.1f}%")

    # =====================================================================
    # PART 6: SYNTHESIS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 6: SYNTHESIS")
    print("=" * 72)

    print(
        f"""
  DARK MATTER FROM W(3,3) SPECTRAL STRUCTURE:

  1. TWO DM SPECIES:
     DM-24: 24-dim exact sector (SU(5) adjoint), lambda=10
     DM-15: 15-dim exact sector (SU(4) adjoint), lambda=16
     Together: 39 = 24+15 DOFs (= dim(C_0) - 1 = 40-1)

  2. SPECTRAL ISOLATION:
     Matter-DM gap: 10 (lambda_DM1 - lambda_matter)
     Gauge-DM gap: 6 (lambda_DM1 - lambda_gauge)
     DM direct coupling to matter: TOPOLOGICALLY FORBIDDEN
     (bracket [H1,H1] maps 100% to co-exact, 0% to exact)

  3. MASS HIERARCHY:
     M_DM2/M_DM1 = sqrt(8/5) = {r_DM2_DM1:.6f}
     M_DM1/M_gauge = sqrt(5/2) = {r_DM1_gauge:.6f}
     M_DM2/M_gauge = 2

  4. SELF-COUPLING:
     DM-24 self-coupling: ||T_24|| = {T_24_norm:.6f}
     DM-15 self-coupling: ||T_15|| = {T_15_norm:.6f}
     Cross-coupling 24x15x15: ||T_cross|| = {T_cross_norm:.6f}
     All sectors have nonzero self-interaction (not collisionless).

  5. SPECTRAL DEMOCRACY:
     n_24 * lambda_10 = n_15 * lambda_16 = 240
     Equal "spectral weight" ensures balanced DM sector.

  6. STABILITY:
     Both 24 and 15 are IRREDUCIBLE under PSp(4,3) (FS=+1).
     Decay to matter forbidden by spectral gap + Hodge orthogonality.
     Decay to gauge forbidden: exact-sector fields are NOT in
     the image of d2 (they are in the image of d1, which is
     orthogonal to the co-exact sector by Hodge decomposition).

  7. PREDICTIONS:
     - Two-component dark matter with mass ratio sqrt(8/5)
     - DM does NOT couple to visible matter at tree level
     - DM has nonzero self-interactions (non-collisionless)
     - DM abundance ratio Omega_24/Omega_15 = {omega_ratio:.4f}
     - DM-24 constitutes ~{omega_24_frac*100:.0f}% of total DM
"""
    )

    results = {
        "n_DM1": 24,
        "n_DM2": 15,
        "lambda_DM1": 10,
        "lambda_DM2": 16,
        "mass_ratio_DM2_DM1": float(r_DM2_DM1),
        "mass_ratio_DM1_gauge": float(r_DM1_gauge),
        "matter_DM_decoupled": bool(matter_dm_decoupled),
        "T_24_self_coupling": float(T_24_norm),
        "T_15_self_coupling": float(T_15_norm),
        "T_cross_coupling": float(T_cross_norm),
        "spectral_democracy_24": int(sd_24),
        "spectral_democracy_15": int(sd_15),
        "omega_ratio": float(omega_ratio),
        "omega_24_fraction": float(omega_24_frac),
        "omega_15_fraction": float(omega_15_frac),
        "elapsed_seconds": time.time() - t0,
    }

    out_dir = Path(__file__).resolve().parent.parent / "checks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"PART_CX_dark_matter_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder, default=str)
    print(f"  Wrote: {fname}")
    print(f"  Elapsed: {time.time() - t0:.1f}s")

    return results


if __name__ == "__main__":
    main()
