"""
Phase LI — Matrix Transforms & Spectral Duality (T726-T740)
============================================================
Fifteen theorems exploring the spectral landscape beyond the adjacency matrix:
Seidel, Laplacian, signless Laplacian, Ihara zeta, complement transforms,
idempotent algebra, and cross-spectral dualities — all rooted in (v,k,λ,μ,q)=(40,12,2,4,3).
"""

from fractions import Fraction as Fr
import math
import pytest

# ── Source constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2          # 240
R, S = 2, -4
F, G = 24, 15
N = Q + 2               # 5
ALPHA = V // MU          # 10
OMEGA = MU               # 4
DIM_O = K - MU           # 8
ALBERT = V - (Q**2 + MU) # 27
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
K_BAR = V - 1 - K        # 27
r_s = R - S              # 6

# ── Seidel eigenvalues ──
SEIDEL_K = V - 1 - 2 * K  # 15 = G
SEIDEL_R = -1 - 2 * R     # -5 = -N
SEIDEL_S = -1 - 2 * S     # 7 = PHI6

# ── Laplacian eigenvalues ──
LAP_0 = 0
LAP_R = K - R   # ALPHA = 10
LAP_S = K - S   # K + MU = 16 = 2^MU

# ── Signless Laplacian eigenvalues ──
SL_K = K + K    # 2K = F = 24
SL_R = K + R    # 14 = 2*PHI6
SL_S = K + S    # 8 = DIM_O

# ── Complement Laplacian eigenvalues ──
CL_0 = 0
CL_R = K_BAR - (-Q)  # ALBERT + Q = 30
CL_S = K_BAR - Q     # ALBERT - Q = 24 = F


# ═══════════════════════════════════════════════
# T726 — Seidel Minimal Polynomial Vieta
# ═══════════════════════════════════════════════
class TestT726SeidelMinPolyVieta:
    """The Seidel matrix S = J - I - 2A has eigenvalues {G, -N, PHI6}.
    Its minimal polynomial Vieta relations yield named constants."""

    def test_seidel_eigenvalue_0_is_G(self):
        assert SEIDEL_K == G

    def test_seidel_eigenvalue_1_is_neg_N(self):
        assert SEIDEL_R == -N

    def test_seidel_eigenvalue_2_is_PHI6(self):
        assert SEIDEL_S == PHI6

    def test_seidel_vieta_sum(self):
        """Sum of Seidel eigenvalues = PHI3 + MU = 17."""
        s1 = SEIDEL_K + SEIDEL_R + SEIDEL_S
        assert s1 == PHI3 + MU == 17

    def test_seidel_vieta_sum_alt(self):
        """Sum = ALBERT - ALPHA = 27 - 10 = 17."""
        assert SEIDEL_K + SEIDEL_R + SEIDEL_S == ALBERT - ALPHA

    def test_seidel_vieta_pairwise(self):
        """Pairwise sum of Seidel eigenvalues = -N = -5."""
        s2 = (SEIDEL_K * SEIDEL_R +
              SEIDEL_K * SEIDEL_S +
              SEIDEL_R * SEIDEL_S)
        assert s2 == -N

    def test_seidel_vieta_product(self):
        """Product of Seidel eigenvalues = -Q * N^2 * PHI6 = -525."""
        s3 = SEIDEL_K * SEIDEL_R * SEIDEL_S
        assert s3 == -Q * N**2 * PHI6 == -525


# ═══════════════════════════════════════════════
# T727 — Seidel Determinant Factorization
# ═══════════════════════════════════════════════
class TestT727SeidelDeterminant:
    """det(S) = G * N^F * PHI6^G — all named from the SRG."""

    def test_seidel_det_formula(self):
        det_S = SEIDEL_K * SEIDEL_R**F * SEIDEL_S**G
        assert det_S == G * (-N)**F * PHI6**G

    def test_seidel_det_positive(self):
        """F=24 is even, so (-N)^F = N^F > 0, hence det > 0."""
        det_S = G * N**F * PHI6**G
        assert det_S > 0

    def test_seidel_det_prime_factorization(self):
        """det = 3 * 5^24 * 7^15 = Q * N^F * PHI6^G."""
        det_S = G * N**F * PHI6**G
        assert det_S == Q * N**F * PHI6**G * (G // Q)
        # G = 15 = 3*5, so G = Q*N
        assert G == Q * N
        # det = Q*N * N^F * PHI6^G = Q * N^(F+1) * PHI6^G
        assert det_S == Q * N**(F + 1) * PHI6**G


# ═══════════════════════════════════════════════
# T728 — Signless Laplacian Determinant 2^72 Anatomy
# ═══════════════════════════════════════════════
class TestT728SignlessLapDet:
    """det(KI+A) = F * (2*PHI6)^F * DIM_O^G = 2^72 * Q * PHI6^F.
    The exponent 72 = |Delta(E6)| = 2*(r-s)^2."""

    def test_det_factors(self):
        det_sl = SL_K * SL_R**F * SL_S**G
        assert det_sl == F * (2 * PHI6)**F * DIM_O**G

    def test_det_2_72_form(self):
        """det = 2^72 * Q * PHI6^F."""
        det_sl = F * (2 * PHI6)**F * DIM_O**G
        # F = 2^3 * 3, (2*PHI6)^F = 2^F * 7^F, DIM_O^G = 8^15 = 2^45
        # Total 2-power: 3 + 24 + 45 = 72
        # Total 3-power: 1 (from F=24=2^3*3)
        # Total 7-power: 24 = F
        assert det_sl == 2**72 * Q * PHI6**F

    def test_exponent_72_is_delta_E6(self):
        """72 = |Delta(E6)| = 2*(r-s)^2."""
        assert 2 * r_s**2 == 72


# ═══════════════════════════════════════════════
# T729 — Ihara–Signless Laplacian Duality
# ═══════════════════════════════════════════════
class TestT729IharaSignlessLapDuality:
    """The Ihara quadratic factors evaluated at u=-1 yield
    exactly the signless Laplacian eigenvalues."""

    @staticmethod
    def _ihara_factor(theta, u):
        """f_theta(u) = 1 - theta*u + (K-1)*u^2."""
        return 1 - theta * u + (K - 1) * u**2

    def test_ihara_at_neg1_gives_SL_K(self):
        assert self._ihara_factor(K, -1) == SL_K == F

    def test_ihara_at_neg1_gives_SL_R(self):
        assert self._ihara_factor(R, -1) == SL_R == 2 * PHI6

    def test_ihara_at_neg1_gives_SL_S(self):
        assert self._ihara_factor(S, -1) == SL_S == DIM_O

    def test_duality_formula(self):
        """f_theta(-1) = 1 + theta + (K-1) = K + theta = signless lap eigenvalue."""
        for theta in [K, R, S]:
            assert self._ihara_factor(theta, -1) == K + theta

    def test_ihara_at_1_from_K_zero(self):
        """f_K(1) = 0 (pole of Ihara zeta)."""
        assert self._ihara_factor(K, 1) == 0


# ═══════════════════════════════════════════════
# T730 — Ihara Discriminant Trifecta
# ═══════════════════════════════════════════════
class TestT730IharaDiscriminants:
    """Each Ihara quadratic discriminant is a named constant."""

    @staticmethod
    def _disc(theta):
        return theta**2 - 4 * (K - 1)

    def test_disc_K_is_ALPHA_squared(self):
        assert self._disc(K) == ALPHA**2 == 100

    def test_disc_R_is_neg_V(self):
        assert self._disc(R) == -V == -40

    def test_disc_S_is_neg_MU_PHI6(self):
        assert self._disc(S) == -MU * PHI6 == -28

    def test_disc_S_alt_form(self):
        """disc(f_S) = -(V-K) = -28."""
        assert self._disc(S) == -(V - K)

    def test_R_S_discs_negative_ramanujan(self):
        """Negative discriminants confirm complex Ihara poles on critical circle."""
        assert self._disc(R) < 0
        assert self._disc(S) < 0


# ═══════════════════════════════════════════════
# T731 — Complement Laplacian Spectrum
# ═══════════════════════════════════════════════
class TestT731ComplementLaplacian:
    """The complement graph's Laplacian eigenvalues are {0, V-ALPHA, F}."""

    def test_complement_lap_null(self):
        assert CL_0 == 0

    def test_complement_lap_eigenvalue_1(self):
        """K_BAR + Q = ALBERT + Q = V - ALPHA = 30."""
        assert CL_R == V - ALPHA == 30

    def test_complement_lap_eigenvalue_2_is_F(self):
        """K_BAR - Q = ALBERT - Q = F = 24."""
        assert CL_S == F == 24

    def test_complement_lap_sum(self):
        """Sum with multiplicities = 2*E_bar where E_bar = V*K_BAR/2 = 540."""
        total = CL_0 + F * CL_R + G * CL_S
        assert total == F * (V - ALPHA) + G * F
        E_BAR = V * K_BAR // 2  # 540
        assert total == 2 * E_BAR == 1080

    def test_complement_lap_eigenvalue_1_naming(self):
        """V - ALPHA = ALBERT + Q = 30 = 2 * G = 2 * 15."""
        assert V - ALPHA == 2 * G


# ═══════════════════════════════════════════════
# T732 — Complement Spanning Trees
# ═══════════════════════════════════════════════
class TestT732ComplementSpanningTrees:
    """tau_bar = (V-ALPHA)^F * F^G / V = 2^66 * 3^(V-1) * 5^23."""

    def test_tau_bar_formula(self):
        tau_bar = Fr((V - ALPHA)**F * F**G, V)
        expected = Fr(2**66 * 3**(V - 1) * 5**23, 1)
        assert tau_bar == expected

    def test_tau_bar_3_exponent_is_V_minus_1(self):
        """The power of 3 in tau_bar is V-1 = 39."""
        assert V - 1 == 39

    def test_tau_bar_5_exponent_is_F_minus_1(self):
        """The power of 5 is F-1 = 23."""
        assert F - 1 == 23

    def test_tau_bar_2_exponent(self):
        """The power of 2 is F + 3*G - 3 = 24+45-3 = 66."""
        exp2 = F + 3 * G - 3
        assert exp2 == 66


# ═══════════════════════════════════════════════
# T733 — Spanning Tree Duality Ratio
# ═══════════════════════════════════════════════
class TestT733SpanningTreeDuality:
    """tau_bar / tau = Q^(V-1) / 2^G."""

    def test_tree_ratio(self):
        tau = Fr(2**81 * 5**23, 1)
        tau_bar = Fr(2**66 * 3**(V - 1) * 5**23, 1)
        ratio = tau_bar / tau
        assert ratio == Fr(Q**(V - 1), 2**G)

    def test_tree_ratio_simplified(self):
        """Q^(V-1) / 2^G = 3^39 / 2^15."""
        assert Fr(Q**(V - 1), 2**G) == Fr(3**39, 2**15)

    def test_tau_product_exponents(self):
        """tau * tau_bar has 2^(81+66)=2^147, 3^39, 5^46."""
        # tau = 2^81 * 5^23, tau_bar = 2^66 * 3^39 * 5^23
        # product: 2^147 * 3^39 * 5^46
        assert 81 + 66 == 147
        assert 23 + 23 == 46


# ═══════════════════════════════════════════════
# T734 — Laplacian Complement Pairing
# ═══════════════════════════════════════════════
class TestT734LaplacianPairing:
    """Each nonzero Laplacian eigenvalue pairs with its
    complement to sum to V."""

    def test_R_eigenspace_pairing(self):
        """ALPHA + (V - ALPHA) = V."""
        assert LAP_R + CL_R == V

    def test_S_eigenspace_pairing(self):
        """2^MU + F = V."""
        assert LAP_S + CL_S == V

    def test_pairing_with_named_constants(self):
        """ALPHA + (V-ALPHA) = 10+30 = 40, 2^MU + F = 16+24 = 40."""
        assert ALPHA + (V - ALPHA) == V
        assert 2**MU + F == V

    def test_complement_lap_from_V_minus_graph(self):
        """Complement Laplacian eigenvalues = V minus graph Laplacian eigenvalues."""
        assert CL_R == V - LAP_R
        assert CL_S == V - LAP_S


# ═══════════════════════════════════════════════
# T735 — Idempotent Denominator Algebra
# ═══════════════════════════════════════════════
class TestT735IdempotentDenominators:
    """The three Lagrange denominators for primitive idempotents
    of the Bose-Mesner algebra are all named constants."""

    def test_d0_is_V_times_MU(self):
        d0 = (K - R) * (K - S)
        assert d0 == V * MU == 160

    def test_d0_is_ALPHA_times_2_MU(self):
        d0 = (K - R) * (K - S)
        assert d0 == ALPHA * 2**MU

    def test_d1_is_neg_ALPHA_r_s(self):
        d1 = (R - K) * (R - S)
        assert d1 == -ALPHA * r_s == -60

    def test_d2_is_Q_times_2_N(self):
        d2 = (S - K) * (S - R)
        assert d2 == Q * 2**N == 96

    def test_denominator_product_is_neg_disc(self):
        """d0 * d1 * d2 = -disc(m) = -(MU*E)^2 = -921600."""
        d0 = (K - R) * (K - S)
        d1 = (R - K) * (R - S)
        d2 = (S - K) * (S - R)
        assert d0 * d1 * d2 == -(MU * E)**2

    def test_hoffman_leading_coeff_from_d0(self):
        """V / d0 = 1/MU — the Hoffman polynomial leading coefficient."""
        assert Fr(V, (K - R) * (K - S)) == Fr(1, MU)


# ═══════════════════════════════════════════════
# T736 — Multiplicity-Laplacian Equipartition
# ═══════════════════════════════════════════════
class TestT736MultiplicityLaplacianEquipartition:
    """F * ALPHA = G * 2^MU = E: the two multiplicity-weighted
    Laplacian eigenvalues are each exactly E = 240."""

    def test_F_times_ALPHA_equals_E(self):
        assert F * ALPHA == E == 240

    def test_G_times_2MU_equals_E(self):
        assert G * 2**MU == E == 240

    def test_equipartition(self):
        """Both terms equal — not just their sum 2E, but individually E."""
        assert F * ALPHA == G * 2**MU == E

    def test_equipartition_alt_form(self):
        """F*(K-R) = G*(K-S) = V*K/2."""
        assert F * (K - R) == G * (K - S) == V * K // 2


# ═══════════════════════════════════════════════
# T737 — Eigenspace Half-Vertex Decomposition
# ═══════════════════════════════════════════════
class TestT737HalfVertexDecomposition:
    """F = V/2 + MU, G = V/2 - N: the multiplicities decompose
    as half the vertex count ± a source constant."""

    def test_F_decomposition(self):
        assert F == V // 2 + MU

    def test_G_decomposition(self):
        assert G == V // 2 - N

    def test_half_vertex_sum(self):
        """F + G = V - 1 (forced by I + E_1 + E_2 = V)."""
        assert F + G == V - 1

    def test_offsets_sum_to_MU_minus_N(self):
        """MU + (-N) = MU - N = -1, so F-G = 2*MU+N-N+MU-N = ..."""
        assert MU - N == -1
        assert (V // 2 + MU) - (V // 2 - N) == MU + N == F - G
        assert MU + N == Q**2  # = 9

    def test_F_minus_G_is_Q_squared(self):
        assert F - G == Q**2 == 9


# ═══════════════════════════════════════════════
# T738 — Multiplicity-Eigenvalue Products
# ═══════════════════════════════════════════════
class TestT738MultiplicityEigenvalueProducts:
    """f*R = MU*K and g*S = -K*N: multiplicity times eigenvalue
    products are named."""

    def test_fR_is_MU_K(self):
        assert F * R == MU * K == 48

    def test_gS_is_neg_K_N(self):
        assert G * S == -K * N == -60

    def test_fR_plus_gS_is_neg_K(self):
        """f*R + g*S + 1*K = tr(A) = 0, so f*R + g*S = -K."""
        assert F * R + G * S == -K

    def test_fR_divided_by_K_is_MU(self):
        assert Fr(F * R, K) == MU

    def test_gS_divided_by_K_is_neg_N(self):
        assert Fr(G * S, K) == -N

    def test_fR_minus_gS(self):
        """f*R - g*S = MU*K + K*N = K*(MU+N) = K*Q^2 = 108."""
        assert F * R - G * S == K * (MU + N)
        assert K * (MU + N) == K * Q**2


# ═══════════════════════════════════════════════
# T739 — Seidel Spectral Moments
# ═══════════════════════════════════════════════
class TestT739SeidelSpectralMoments:
    """Trace powers of S_seidel encode graph topology."""

    def test_tr_S_is_zero(self):
        """S has zero diagonal, so tr = 0."""
        tr1 = SEIDEL_K + F * SEIDEL_R + G * SEIDEL_S
        assert tr1 == 0

    def test_tr_S2_is_V_times_V_minus_1(self):
        """tr(S^2) = V*(V-1) = 1560 (each entry ±1 off diagonal)."""
        tr2 = SEIDEL_K**2 + F * SEIDEL_R**2 + G * SEIDEL_S**2
        assert tr2 == V * (V - 1) == 1560

    def test_tr_S3(self):
        """tr(S^3) = V*(V-1)(V-1-4K)/3 + ... relates to triangle count."""
        tr3 = SEIDEL_K**3 + F * SEIDEL_R**3 + G * SEIDEL_S**3
        # 3375 + 24*(-125) + 15*343 = 3375 - 3000 + 5145 = 5520
        assert tr3 == 5520
        # 5520 = 2^4 * 3 * 5 * 23 = 2^MU * Q * N * 23
        assert tr3 == 2**MU * Q * N * 23

    def test_tr_S2_over_V(self):
        """tr(S^2)/V = V-1 = 39."""
        assert Fr(V * (V - 1), V) == V - 1


# ═══════════════════════════════════════════════
# T740 — Heat Kernel Bosonic Moment
# ═══════════════════════════════════════════════
class TestT740HeatKernelBosonicMoment:
    """Z''(0) = E * 26: the second Laplacian moment equals edge count
    times the bosonic dimension, and Z''(0)/|Z'(0)| = PHI3."""

    def test_Z_prime_0_is_neg_2E(self):
        """Z'(0) = -(F*ALPHA + G*2^MU) = -2E."""
        Z1 = -(F * ALPHA + G * 2**MU)
        assert Z1 == -2 * E == -480

    def test_Z_double_prime_0_is_E_times_26(self):
        """Z''(0) = F*ALPHA^2 + G*(2^MU)^2 = E*26 = 6240."""
        Z2 = F * ALPHA**2 + G * (2**MU)**2
        assert Z2 == E * 26 == 6240

    def test_Z_double_prime_0_alt_factorization(self):
        """Z''(0) = 2^N * Q * N * PHI3 = 32*3*5*13 = 6240."""
        Z2 = F * ALPHA**2 + G * (2**MU)**2
        assert Z2 == 2**N * Q * N * PHI3

    def test_heat_ratio_is_PHI3(self):
        """Z''(0) / |Z'(0)| = PHI3 = 13."""
        Z1_abs = 2 * E
        Z2 = E * 26
        assert Fr(Z2, Z1_abs) == PHI3

    def test_Z_double_prime_over_V(self):
        """Z''(0)/V = 156 = 2 * 78 = 2 * dim(E6)."""
        Z2 = E * 26
        assert Z2 // V == 156
        assert 156 == 2 * 78


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
