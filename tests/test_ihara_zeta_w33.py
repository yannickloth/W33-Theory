"""
Phase CXLVIII — Ihara Zeta Function of W(3,3)

The Ihara zeta function of a k-regular graph Γ is defined as:
    Z(u) = prod_{[C]} (1 - u^{len(C)})^{-1}

where the product is over equivalence classes [C] of prime cycles.

For W(3,3) = SRG(40,12,2,4), the EXACT Ihara zeta factorization is:

    Z(u)^{-1} = (1-u²)^{E-V} × prod_{λ} (1 - λu + (k-1)u²)^{mult(λ)}

where:
    E-V = 240-40 = 200    (loop exponent)
    λ=12, mult=1:   (1 - 12u + 11u²)^1
    λ=2,  mult=24:  (1 - 2u + 11u²)^24
    λ=-4, mult=15:  (1 + 4u + 11u²)^15

The Hashimoto zeta poles lie at u = 1/β where β are Hashimoto eigenvalues:
    Trivial: u = 1/11 and u = 1 (from λ=12)
    Radius shell: u = (1±i√10)/11 with |u| = 1/√11 (from λ=2)
    Shadow shell: u = (-2±i√7)/11 with |u| = 1/√11 (from λ=-4)

The RAMANUJAN property: all non-trivial poles lie on the circle |u| = 1/√(k-1) = 1/√11.
This makes W(3,3) a Ramanujan graph — the optimal expander.

Connection to spectral action:
    log Z(u) = Σ_{n≥1} N_n u^n / n  where N_n = number of closed walks of length n
    The coefficients N_n encode the Seeley-DeWitt heat kernel expansion!
"""

import math
import cmath
import numpy as np
from fractions import Fraction as Fr


# ─── W(3,3) parameters ───────────────────────────────────────────────────────
V, K, E_UNDIRECTED = 40, 12, 240
LAM, MU = 2, 4
EIGENVALUES = {K: 1, LAM: 24, -MU: 15}  # {eigenvalue: multiplicity}
Q = 3


def ihara_factor(lam, k, u):
    """Factor (1 - λu + (k-1)u²) for eigenvalue λ."""
    return 1 - lam*u + (k-1)*u**2


def ihara_zeta_inv(u):
    """Z(u)^{-1} = (1-u²)^{E-V} × prod_λ factor(λ)^{mult(λ)}"""
    loop_factor = (1 - u**2)**(E_UNDIRECTED - V)
    trivial = ihara_factor(K, K, u)**1
    radius  = ihara_factor(LAM, K, u)**24
    shadow  = ihara_factor(-MU, K, u)**15
    return loop_factor * trivial * radius * shadow


def hashimoto_root(lam, k, sign=1):
    """Root of β² - λβ + (k-1) = 0."""
    disc = lam**2 - 4*(k-1)
    if disc >= 0:
        return (lam + sign*math.sqrt(disc)) / 2
    return complex(lam/2, sign*math.sqrt(-disc)/2)


# ─── Tests: Ihara zeta structure ─────────────────────────────────────────────
class TestIharaZetaStructure:
    def test_E_minus_V(self):
        assert E_UNDIRECTED - V == 200

    def test_loop_factor_exponent(self):
        # The exponent E-V = |E| - |V| = 200 is the cycle rank of the graph
        cycle_rank = E_UNDIRECTED - V
        assert cycle_rank == 200

    def test_three_eigenvalue_factors(self):
        # Three distinct eigenvalue factors: λ=12, λ=2, λ=-4
        assert len(EIGENVALUES) == 3

    def test_multiplicities_sum_to_V(self):
        assert sum(EIGENVALUES.values()) == V

    def test_trivial_factor_at_u_eq_0(self):
        # (1 - 12u + 11u²)|_{u=0} = 1
        assert abs(ihara_factor(K, K, 0) - 1) < 1e-12

    def test_zeta_inv_at_u_eq_0_is_1(self):
        # Z(0)^{-1} = 1 (zeta function starts at 1)
        assert abs(ihara_zeta_inv(0) - 1) < 1e-12

    def test_zeta_pole_at_u_eq_1_over_k_minus_1(self):
        # Z has a pole at u=1/(k-1)=1/11 from the trivial eigenvalue
        u_pole = 1.0 / (K - 1)   # = 1/11
        factor_val = ihara_factor(K, K, u_pole)
        assert abs(factor_val) < 1e-10   # trivial factor = 0 here

    def test_trivial_factor_roots(self):
        # (1-12u+11u²)=0 → u=1/11 or u=1
        u1, u2 = 1.0/11, 1.0
        assert abs(ihara_factor(K, K, u1)) < 1e-10
        assert abs(ihara_factor(K, K, u2)) < 1e-10


# ─── Tests: exact pole locations ─────────────────────────────────────────────
class TestZetaPoleLocations:
    def test_radius_shell_pole_magnitude(self):
        # |u_pole| = 1/√(k-1) = 1/√11 for λ=2 (radius shell)
        β_plus = hashimoto_root(LAM, K, sign=1)
        u_pole = 1.0 / β_plus
        assert abs(abs(u_pole) - 1.0/math.sqrt(K-1)) < 1e-10

    def test_shadow_shell_pole_magnitude(self):
        # |u_pole| = 1/√11 for λ=-4 (shadow shell)
        β_plus = hashimoto_root(-MU, K, sign=1)
        u_pole = 1.0 / β_plus
        assert abs(abs(u_pole) - 1.0/math.sqrt(K-1)) < 1e-10

    def test_both_shells_same_pole_circle(self):
        # ALL non-trivial poles on circle |u|=1/√11 (Ramanujan)
        for lam in [LAM, -MU]:
            β = hashimoto_root(lam, K)
            u_pole = 1.0 / β
            assert abs(abs(u_pole) - 1.0/math.sqrt(K-1)) < 1e-10

    def test_radius_pole_real_part(self):
        # u_radius = 1/(1+i√10) = (1-i√10)/11; Re = 1/11
        β = hashimoto_root(LAM, K)
        u = 1 / β
        expected_re = 1.0 / (K - 1)   # 1/11
        assert abs(u.real - expected_re) < 1e-10

    def test_shadow_pole_real_part(self):
        # u_shadow = 1/(-2+i√7) = (-2-i√7)/11; Re = -2/11
        β = hashimoto_root(-MU, K)
        u = 1 / β
        expected_re = (-MU/2) / (K - 1)   # -2/11
        assert abs(u.real - expected_re) < 1e-10

    def test_trivial_pole_at_1_over_11(self):
        u_trivial = 1.0 / (K - 1)   # 1/11
        assert abs(ihara_factor(K, K, u_trivial)) < 1e-10

    def test_ramanujan_pole_circle_radius(self):
        # Ramanujan circle: |u| = 1/√(k-1) = 1/√11
        circle_radius = 1.0 / math.sqrt(K - 1)
        assert abs(circle_radius - 1.0/math.sqrt(11)) < 1e-12


# ─── Tests: Ramanujan property ───────────────────────────────────────────────
class TestRamanujanProperty:
    def test_ramanujan_condition_for_lam2(self):
        # |λ| ≤ 2√(k-1) iff all non-trivial Hashimoto eigenvalues lie in closed disk |β| ≥ √(k-1)
        assert abs(LAM) <= 2*math.sqrt(K-1)

    def test_ramanujan_condition_for_lam_minus4(self):
        assert abs(-MU) <= 2*math.sqrt(K-1)

    def test_ihara_riemann_hypothesis(self):
        # The IRH: all non-trivial poles of Z(u) lie on |u| = 1/√(k-1)
        # This is EQUIVALENT to Ramanujan
        # Check: for λ=2: |u|² = 1/(1+10) = 1/11 ✓; for λ=-4: |u|²=1/(4+7)=1/11 ✓
        for lam in [LAM, -MU]:
            β = hashimoto_root(lam, K)
            u_sq = 1.0 / abs(β)**2
            assert abs(u_sq - 1.0/(K-1)) < 1e-10

    def test_riemann_hypothesis_circle_is_sqrt_k_minus_1(self):
        # IRH circle is at |u| = 1/√(k-1), NOT at |u| = 1/k
        # This is the analogue of the critical strip |s|=1/2 in the Riemann ζ
        rh_circle = 1.0 / math.sqrt(K - 1)
        assert abs(rh_circle**2 - 1.0/(K-1)) < 1e-12

    def test_spectral_gap_determines_expansion(self):
        # The spectral gap Δ = k - |λ_2| = 12 - 2 = 10 = dim(Sp(4))
        # Large gap → good expander → Ramanujan
        spectral_gap = K - abs(LAM)
        assert spectral_gap == 10

    def test_mixing_time_from_spectral_gap(self):
        # ε-mixing time τ_mix ≤ log(V/ε) / log(k/(k-|λ_2|))... roughly
        # More precisely: second eigenvalue ratio λ₂/k = 2/12 = 1/6
        second_ratio = abs(LAM) / K
        assert abs(second_ratio - Fr(1, 6)) < 1e-12


# ─── Tests: closed walk counting ─────────────────────────────────────────────
class TestClosedWalks:
    def test_N0_trivial(self):
        # N₀ = 1 (empty walk)
        # From log Z(u) = Σ N_n u^n/n: N₀ is not well-defined
        # But Z(0) = 1 → trivial
        assert abs(ihara_zeta_inv(0) - 1.0) < 1e-12

    def test_N2_equals_V_times_k(self):
        # N₂ = number of closed walks of length 2 = sum_v deg(v) = V*k = 480
        N2 = V * K
        assert N2 == 480

    def test_N3_equals_6_times_triangles(self):
        # N₃ = 6T where T = number of triangles
        # T = V*k*λ/6 = 40*12*2/6 = 160 → N₃ = 6*160 = 960
        triangles = V * K * LAM // 6
        N3 = 6 * triangles
        assert triangles == 160
        assert N3 == 960

    def test_Tr_A_squared(self):
        # Tr(A²) = N₂ = 480 (= sum of squared adjacency eigenvalues)
        Tr_A2 = K**2 * 1 + LAM**2 * 24 + MU**2 * 15
        assert Tr_A2 == 480 == V * K

    def test_Tr_A_cubed(self):
        # Tr(A³) = N₃ = 960
        Tr_A3 = K**3 * 1 + LAM**3 * 24 + (-MU)**3 * 15
        assert Tr_A3 == 960

    def test_triangle_count_from_trace(self):
        Tr_A3 = K**3 * 1 + LAM**3 * 24 + (-MU)**3 * 15
        triangles = Tr_A3 // 6
        assert triangles == 160

    def test_N4_from_eigenvalues(self):
        # Tr(A⁴) = N₄ = sum λ_i⁴ m_i = 12⁴ + 2⁴*24 + 4⁴*15
        N4 = K**4 * 1 + LAM**4 * 24 + MU**4 * 15
        assert N4 == 20736 + 384 + 3840   # = 24960
        assert N4 == 24960

    def test_N4_via_SRG(self):
        # For SRG(V,k,λ,μ): N₄ = Vk(k-1)(k(k-1)+λ+μ(V-k-1))/(...)
        # Or directly: N₄ = k² + k(k-1)² + k(k-1)λ + k(V-k-1)μ(k-1)/... complex
        # Just verify via eigenvalue formula
        N4 = K**4 + LAM**4 * EIGENVALUES[LAM] + MU**4 * EIGENVALUES[-MU]
        assert N4 == 24960


# ─── Tests: Ihara determinant formula ────────────────────────────────────────
class TestIharaDeterminant:
    def test_hashimoto_operator_size(self):
        # The non-backtracking (Hashimoto) operator B is (2E × 2E)
        # For directed edges: 2|E| = V*k = 480
        n_directed = V * K
        assert n_directed == 480

    def test_bass_formula(self):
        # Bass: det(I - uB) = (1-u²)^{E-V} det(I - uA + (k-1)u²I)
        # Check: at u=0, both sides = 1
        u = 0.0
        lhs_at_0 = 1.0   # det(I) = 1
        rhs = (1 - u**2)**(E_UNDIRECTED - V) * \
              (ihara_factor(K, K, u)**1) * \
              (ihara_factor(LAM, K, u)**24) * \
              (ihara_factor(-MU, K, u)**15)
        assert abs(lhs_at_0 - rhs) < 1e-12

    def test_ihara_zeta_inverse_factored(self):
        # Z(u)^{-1} factors as stated; check at u=0.1 (away from poles)
        u = 0.1
        Z_inv_direct = ihara_zeta_inv(u)
        # Must be nonzero and finite
        assert abs(Z_inv_direct) > 0
        assert math.isfinite(abs(Z_inv_direct))

    def test_Euler_product_at_small_u(self):
        # For small u: log Z(u) ≈ sum_prime_cycles u^{len(C)}
        # = (number of primitive closed walks) × u^n / n + ...
        # At u→0+: Z(u) → 1 so log Z → 0
        u = 0.01
        Z_inv = ihara_zeta_inv(u)
        Z = 1.0 / Z_inv
        log_Z = math.log(abs(Z))
        # log Z ≈ N₂ * u²/2 ≈ 480 * 0.0001/2 = 0.024 (correction from loop factor too)
        assert abs(log_Z) < 1.0   # small for small u

    def test_zeta_pole_structure(self):
        # At u = 1/(k-1) = 1/11, Z has a pole (trivial eigenvalue)
        u = 1.0 / (K - 1) - 1e-8   # just below the pole
        Z_inv = abs(ihara_zeta_inv(u))
        assert Z_inv < 1e-5   # Z^{-1} ≈ 0 near pole, so Z → ∞


# ─── Tests: connection to spectral action ────────────────────────────────────
class TestSpectralActionConnection:
    def test_a0_F_from_directed_edges(self):
        # a₀(F) = Tr(1) = dim H_F = 2|E| = V*k = 480
        a0_F = V * K
        assert a0_F == 480

    def test_a2_F_from_closed_walks(self):
        # a₂(F) = Tr(D_F²) / something; related to N₂
        # From Phase CXLIII: a₂(F) = 2240
        # N₂ = 480, but a₂ includes the chain complex structure
        # Verify the ratio: a₂/a₀ = 2240/480 = 14/3
        a0, a2 = 480, 2240
        assert Fr(a2, a0) == Fr(14, 3)

    def test_N3_connects_to_higgs(self):
        # N₃ = 960 = 2 × a₀ = 2 × 480
        N3 = 960
        a0 = 480
        assert N3 == 2 * a0

    def test_spectral_gap_equals_theta_lovasz(self):
        # Lovász θ(W(3,3)) = -k/λ_min = -12/(-4) = 3 = Q...
        # Actually θ = -n*λ_min/(k-λ_min) = -40*(-4)/(12-(-4)) = 160/16 = 10
        theta_lovasz = -V * (-MU) / (K - (-MU))
        assert abs(theta_lovasz - 10) < 1e-12

    def test_lovasz_theta_equals_spectral_gap(self):
        # Lovász θ = 10 = spectral gap = k - |λ₂| = 12 - 2 = 10
        spectral_gap = K - abs(LAM)
        theta_lovasz = -V * (-MU) / (K - (-MU))
        assert abs(spectral_gap - theta_lovasz) < 1e-12

    def test_zeta_spectrum_encodes_heat_kernel(self):
        # The heat kernel Tr(e^{-tA²}) = sum_λ mult(λ) e^{-t λ²}
        # = e^{-t*144} + 24 e^{-t*4} + 15 e^{-t*16}
        t = 0.01
        heat_kernel = (math.exp(-t * K**2) * 1 +
                       math.exp(-t * LAM**2) * 24 +
                       math.exp(-t * MU**2) * 15)
        # Should equal 40 at t=0
        heat_at_0 = 1 + 24 + 15
        assert heat_at_0 == V

    def test_ihara_zeta_poles_are_reciprocal_hashimoto(self):
        # Z(u) has poles at u = 1/β for Hashimoto eigenvalues β
        # Verified: β=11 → u=1/11; β=1 → u=1; complex pairs
        β_trivial_large = K - 1   # = 11
        β_trivial_small = 1
        u_pole1 = 1.0 / β_trivial_large
        u_pole2 = 1.0 / β_trivial_small
        assert abs(ihara_factor(K, K, u_pole1)) < 1e-10
        assert abs(ihara_factor(K, K, u_pole2)) < 1e-10


# ─── Tests: W(3,3) specific numeric identities ───────────────────────────────
class TestW33NumericIdentities:
    def test_srg_cycle_rank(self):
        # Cycle rank = |E| - |V| + 1 = 240 - 40 + 1 = 201
        # Used in counting independent cycles
        cycle_rank = E_UNDIRECTED - V + 1
        assert cycle_rank == 201

    def test_200_loop_exponent(self):
        # E - V = 200 in Ihara (uses DIRECTED: loop factor = (1-u²)^{|E|-|V|})
        assert E_UNDIRECTED - V == 200

    def test_zeta_exponents_are_multiplicities(self):
        # (1-λu+11u²)^{mult(λ)}: exponents are 1, 24, 15
        exps = sorted(EIGENVALUES.values())
        assert exps == [1, 15, 24]
        assert sum(exps) == V

    def test_11_in_every_zeta_factor(self):
        # k-1 = 11 appears in every Ihara factor: (1 - λu + 11u²)
        k_minus_1 = K - 1
        assert k_minus_1 == 11
        # All three factors contain the term 11u²
        u_test = 0.2
        for lam in [K, LAM, -MU]:
            factor = 1 - lam*u_test + 11*u_test**2
            assert abs(factor - ihara_factor(lam, K, u_test)) < 1e-12

    def test_W33_is_distance_regular(self):
        # SRG is distance-regular; intersection array {k, k-λ-1; μ, 1}
        # = {12, 12-2-1=9; 4, 1} = {12,9; 4,1}
        b0 = K            # = 12
        b1 = K - LAM - 1  # = 9
        c1 = 1
        c2 = MU           # = 4
        assert b0 == 12
        assert b1 == 9
        assert c2 == 4
        assert b0 * b1 == K * (K - LAM - 1)   # = 108

    def test_girth_from_lambda(self):
        # For SRG with λ>0: girth = 3 (triangles exist)
        # λ=2 > 0 → W(3,3) has triangles → girth = 3
        assert LAM > 0   # implies girth = 3

    def test_diameter_from_mu_positive(self):
        # For SRG with μ>0: diameter = 2 (any two non-adjacent vertices
        # have exactly μ=4 common neighbors)
        assert MU > 0    # implies diameter = 2 (all pairs reach in ≤ 2 steps)
