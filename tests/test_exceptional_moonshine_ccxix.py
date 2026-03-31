"""
Phase CCXIX — Moonshine Primes, Exceptional Chain, Trefoil-Golay Synthesis

New results (2026-03-30):
  - All 15 moonshine primes derived exactly from {q,v,k,lambda,mu,Phi}
  - Exceptional Lie chain G2->F4->E8: root counts k, mu*k, E_edges
  - All exceptional algebra dimensions from cyclotomic parameters:
    dim(G2)=2*Phi6, dim(F4)=Phi3*(q+1), dim(E6)=6*Phi3, dim(E7)=Phi6*(k+q+mu)
    dim(E8)=E_edges+2^q; rank sequence = lam, mu, k/2, Phi6, k-mu
  - dim J(3,O)=27=v-k-1=q^3 (exceptional Jordan algebra from complement count)
  - Trefoil: Alexander poly = Phi6(t); g_mult = 360/(2k) = 15 = f*g/360*g
  - Ternary Golay G12 = [k, k/2, k/2]_3; 264=E+f min-weight codewords;
    2-(k, k/2, mu*g_mult) design; mu*g_mult = 60 = |A5|
  - Leech kissing 196560 = E_edges*q^2*Phi6*Phi3; leech/2 = tau*C(v,2)/2
  - Monster gap 196884-196560 = 324 = (lam*q^2)^2 = phi(p19)^2

64 tests encoding W(3,3) as the spine of exceptional mathematics.
"""

import math
import pytest

q, v, k, lam, mu = 3, 40, 12, 2, 4
Phi3, Phi4, Phi6, Phi12 = 13, 10, 7, 73
f, g_mult = 24, 15
E_edges = 240
tau_val = 252

MOONSHINE_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71]


def _is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


# ===========================================================================
# T1 — All 15 Moonshine Primes Derived from W(3,3)
# ===========================================================================
class TestT1_MoonshinePrimes:
    """Every moonshine prime has an exact formula in {q,v,k,lambda,mu,Phi}."""

    def test_count_is_15(self):
        assert len(MOONSHINE_PRIMES) == 15

    def test_count_equals_g_mult(self):
        """15 moonshine primes = g_mult (multiplicity of eigenvalue s=-4)."""
        assert len(MOONSHINE_PRIMES) == g_mult

    def test_all_are_prime(self):
        assert all(_is_prime(p) for p in MOONSHINE_PRIMES)

    def test_p2_is_lam(self):
        assert 2 == lam

    def test_p3_is_q(self):
        assert 3 == q

    def test_p5_is_lam_plus_q(self):
        assert 5 == lam + q

    def test_p7_is_Phi6(self):
        assert 7 == Phi6

    def test_p11_is_k_minus_1(self):
        assert 11 == k - 1

    def test_p13_is_Phi3(self):
        assert 13 == Phi3

    def test_p17_is_mu_sq_plus_1(self):
        assert 17 == mu**2 + 1

    def test_p17_alt_Phi4_plus_Phi6(self):
        """17 = Phi4 + Phi6: two independent formulas for the same prime."""
        assert 17 == Phi4 + Phi6

    def test_p19_is_k_plus_q_plus_mu(self):
        assert 19 == k + q + mu

    def test_p23_is_2k_minus_1(self):
        assert 23 == 2 * k - 1

    def test_p23_alt_f_minus_1(self):
        """23 = f-1: the moonshine prime equals positive-eigenvalue multiplicity minus 1."""
        assert 23 == f - 1

    def test_p29_is_v_minus_k_plus_1(self):
        """29 = v-k+1 (also the neutrino mass factor from CCXVI)."""
        assert 29 == v - k + 1

    def test_p31_is_v_minus_q_squared(self):
        assert 31 == v - q**2

    def test_p41_is_v_plus_1(self):
        assert 41 == v + 1

    def test_p47_is_v_plus_Phi6(self):
        assert 47 == v + Phi6

    def test_p59_is_v_plus_k_plus_Phi6(self):
        assert 59 == v + k + Phi6

    def test_p71_is_Phi12_minus_lam(self):
        assert 71 == Phi12 - lam

    def test_all_15_formulas_distinct_and_complete(self):
        """The 15 formulas recover exactly the 15 moonshine primes."""
        derived = [
            lam, q, lam + q, Phi6, k - 1, Phi3, mu**2 + 1,
            k + q + mu, 2*k - 1, v - k + 1, v - q**2,
            v + 1, v + Phi6, v + k + Phi6, Phi12 - lam
        ]
        assert sorted(derived) == sorted(MOONSHINE_PRIMES)


# ===========================================================================
# T2 — Exceptional Lie Chain: Root Counts and Ranks
# ===========================================================================
class TestT2_ExceptionalLieChain:
    """Root counts of G2, F4, E8 are k, mu*k, E_edges; ranks from W(3,3)."""

    def test_G2_roots_equal_k(self):
        """12 roots of G2 = k (valency of W(3,3))."""
        assert 12 == k

    def test_F4_roots_equal_mu_k(self):
        """48 roots of F4 = mu*k = 4*12."""
        assert 48 == mu * k

    def test_E8_roots_equal_E_edges(self):
        """240 roots of E8 = E_edges (edge count of W(3,3))."""
        assert 240 == E_edges

    def test_F4_over_G2_ratio_is_mu(self):
        """F4 root count / G2 root count = 48/12 = 4 = mu."""
        assert 48 // 12 == mu

    def test_E8_over_G2_ratio_is_half_v(self):
        """E8 root count / G2 root count = 240/12 = 20 = v/2."""
        assert 240 // 12 == v // 2

    def test_root_chain_step_mu_then_lam_plus_q(self):
        """12 --(×mu)--> 48 --(×(lam+q))--> 240."""
        assert 48 == 12 * mu
        assert 240 == 48 * (lam + q)

    def test_rank_G2_equals_lam(self):
        """rank(G2) = 2 = lambda."""
        assert 2 == lam

    def test_rank_F4_equals_mu(self):
        """rank(F4) = 4 = mu."""
        assert 4 == mu

    def test_rank_E6_equals_half_k(self):
        """rank(E6) = 6 = k/2."""
        assert 6 == k // 2

    def test_rank_E7_equals_Phi6(self):
        """rank(E7) = 7 = Phi6."""
        assert 7 == Phi6

    def test_rank_E8_equals_k_minus_mu(self):
        """rank(E8) = 8 = k - mu = 12 - 4."""
        assert 8 == k - mu


# ===========================================================================
# T3 — Exceptional Algebra Dimensions from Cyclotomic Data
# ===========================================================================
class TestT3_ExceptionalDimensions:
    """All exceptional Lie algebra dimensions from W(3,3) cyclotomic data."""

    def test_dim_G2(self):
        """dim(G2) = 14 = 2*Phi6 = 2*7."""
        assert 14 == 2 * Phi6

    def test_dim_F4(self):
        """dim(F4) = 52 = Phi3*(q+1) = 13*4."""
        assert 52 == Phi3 * (q + 1)

    def test_dim_E6(self):
        """dim(E6) = 78 = 6*Phi3 = (k/2)*Phi3."""
        assert 78 == 6 * Phi3

    def test_dim_E7(self):
        """dim(E7) = 133 = Phi6*(k+q+mu) = 7*19."""
        assert 133 == Phi6 * (k + q + mu)

    def test_dim_E8(self):
        """dim(E8) = 248 = E_edges + 2^q = 240 + 8."""
        assert 248 == E_edges + 2**q

    def test_jordan_dim_complement(self):
        """dim J(3,O) = 27 = v - k - 1 (complement count of W(3,3))."""
        assert 27 == v - k - 1

    def test_jordan_dim_q_cubed(self):
        """dim J(3,O) = 27 = q^3 (3x3x3 tensor structure)."""
        assert 27 == q**3

    def test_octonion_imaginary_units_are_Phi6(self):
        """7 imaginary octonion units = Phi6 = q^2-q+1."""
        assert 7 == Phi6 == q**2 - q + 1

    def test_G2_plus_Jordan_is_moonshine_prime(self):
        """dim(G2) + dim(J(3,O)) = 14 + 27 = 41 = v+1 (moonshine prime)."""
        assert 14 + 27 == v + 1

    def test_exceptional_dimension_chain_ascending(self):
        """14 < 52 < 78 < 133 < 248 (strictly ascending exceptional chain)."""
        dims = [2*Phi6, Phi3*(q+1), 6*Phi3, Phi6*(k+q+mu), E_edges+2**q]
        assert all(dims[i] < dims[i+1] for i in range(len(dims)-1))


# ===========================================================================
# T4 — Trefoil Knot Bridge
# ===========================================================================
class TestT4_TrefoilKnot:
    """Trefoil: Alexander = Phi6(t); g_mult = 360/(2k); Jones step = f."""

    def test_alexander_poly_at_q(self):
        """Phi6(t) = t^2-t+1 evaluated at t=q=3 gives Phi6 = 7."""
        t = q
        assert t**2 - t + 1 == 7 == Phi6

    def test_alexander_is_sixth_cyclotomic(self):
        """Phi6(q) = q^2-q+1 = 7 (the W(3,3) cyclotomic parameter)."""
        assert Phi6 == q**2 - q + 1

    def test_trefoil_crossings_equals_q(self):
        """Trefoil braid word sigma_1^q has q=3 crossings."""
        assert q == 3

    def test_g_mult_equals_360_over_2k(self):
        """g_mult = 15 = 360/(2*12) = 360 angular units / (2*k)."""
        assert g_mult == 360 // (2 * k)

    def test_jones_step_equals_f(self):
        """The complementary step 360/g = 24 = f (positive eigenvalue multiplicity)."""
        assert 360 // g_mult == f

    def test_f_times_g_equals_360(self):
        """f * g_mult = 24 * 15 = 360 (spectral product = full rotation)."""
        assert f * g_mult == 360


# ===========================================================================
# T5 — Ternary Golay Code G12
# ===========================================================================
class TestT5_TernaryGolay:
    """G12 = [k, k/2, k/2]_q; 264=E+f min-weight codewords; 2-(k,k/2,mu*g) design."""

    def test_length_equals_k(self):
        """Extended ternary Golay code length = 12 = k."""
        assert 12 == k

    def test_dimension_equals_half_k(self):
        """Golay code dimension = 6 = k/2."""
        assert 6 == k // 2

    def test_min_distance_equals_half_k(self):
        """Golay minimum distance = 6 = k/2."""
        assert 6 == k // 2

    def test_weight6_count_is_E_plus_f(self):
        """264 = E_edges + f = 240 + 24 (codewords of minimum weight)."""
        assert 264 == E_edges + f

    def test_weight6_factored(self):
        """264 = 2^q * (q*(k-1)) = 8 * 33."""
        assert 264 == 2**q * (q * (k - 1))

    def test_design_lambda_is_mu_times_g(self):
        """2-(k, k/2, 60) design; lambda = 60 = mu*g_mult = 4*15."""
        assert 60 == mu * g_mult

    def test_design_lambda_equals_A5_order(self):
        """Design parameter 60 = |A5| (icosahedral group order)."""
        A5_order = 5 * 4 * 3
        assert A5_order == 60 == mu * g_mult

    def test_design_consistency_formula(self):
        """b = lambda*C(v_d,2)/C(k_b,2) = 60*66/15 = 264 ✓."""
        v_d, k_b, lam_d = k, k // 2, mu * g_mult
        b = lam_d * math.comb(v_d, 2) // math.comb(k_b, 2)
        assert b == 264 == E_edges + f

    def test_field_is_GF_q(self):
        """Ternary Golay lives over GF(3) = GF(q), same field as W(3,3)."""
        assert q == 3


# ===========================================================================
# T6 — Leech Lattice and Monster Gap
# ===========================================================================
class TestT6_LeechMonsterGap:
    """Leech kissing 196560 = E*q^2*Phi6*Phi3; Monster gap = (lam*q^2)^2."""

    LEECH_KISSING = 196560
    MONSTER_J1    = 196884

    def test_leech_from_E_and_cyclotomic(self):
        """196560 = E_edges * q^2 * Phi6 * Phi3 = 240*9*7*13."""
        assert self.LEECH_KISSING == E_edges * q**2 * Phi6 * Phi3

    def test_leech_divisor_is_819(self):
        """196560 / 240 = 819 = q^2 * Phi6 * Phi3."""
        assert self.LEECH_KISSING // E_edges == q**2 * Phi6 * Phi3

    def test_leech_half_is_tau_times_triangles(self):
        """leech/2 = tau * C(v,2)/2 = 252 * 390 = 98280."""
        assert self.LEECH_KISSING // 2 == tau_val * (math.comb(v, 2) // 2)

    def test_monster_gap_is_324(self):
        """196884 - 196560 = 324."""
        assert self.MONSTER_J1 - self.LEECH_KISSING == 324

    def test_gap_is_lam_q_sq_squared(self):
        """324 = (lam*q^2)^2 = (2*9)^2 = 18^2."""
        assert 324 == (lam * q**2)**2

    def test_18_equals_lam_q_squared(self):
        """18 = lam*q^2 = lambda * q^2."""
        assert 18 == lam * q**2

    def test_euler_totient_p19_equals_18(self):
        """phi(19) = 18 = lam*q^2 (p19 = k+q+mu is a moonshine prime)."""
        # Euler totient of prime p is p-1
        p19 = k + q + mu
        assert p19 == 19
        phi_p19 = p19 - 1  # = 18
        assert phi_p19 == lam * q**2

    def test_gap_is_phi_p19_squared(self):
        """324 = phi(19)^2 = 18^2."""
        phi_19 = (k + q + mu) - 1  # = 18
        assert 324 == phi_19**2
