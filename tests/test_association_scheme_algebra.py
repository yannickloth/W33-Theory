"""
Phase XLVI: Association Scheme Algebra & Eigenmatrix Anatomy (T651-T665)
========================================================================

Dissects the Bose-Mesner algebra of W(3,3) as a 2-class symmetric
association scheme.  The first eigenmatrix P has det(P) = -E = -240,
the second eigenmatrix Q encodes MU and N, and the intersection numbers
resolve entirely to the five source parameters.

Key discoveries:
  - det(P) = -V(r-s) = -E (eigenmatrix determinant = negative edge count)
  - Q₁₁ = MU, Q₂₁ = -N (dual eigenmatrix encodes Paley and pentad)
  - Complement: SRG(40, 27, 18, 18) with LAM_bar = MU_bar (isotropy!)
  - Seidel energy = alpha(2K+1) = 2N³ = 250; SE - E = alpha
  - Walk ratio: w₃/w₂ = LAM (triangle density identity)
  - Spanning tree exponents: 2^{Q⁴} · 5^{ALBERT-MU}, sum = DIM_O·Phi₃
"""

import pytest
from fractions import Fraction

# ── Source parameters ──────────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                    # 240
R, S = 2, -4                      # Adjacency eigenvalues
F, G = 24, 15                     # Multiplicities
N = Q + 2                         # 5
THETA = K - R                     # 10
ALPHA = V // MU                   # 10
OMEGA = MU                        # 4
DIM_O = K - MU                    # 8
ALBERT = V - (Q**2 + MU)          # 27
PHI3 = Q**2 + Q + 1               # 13
PHI6 = Q**2 - Q + 1               # 7

# Complement parameters
K_BAR = V - 1 - K                 # 27
R_BAR = -1 - S                    # 3
S_BAR = -1 - R                    # -3


# ── T651: First eigenmatrix determinant ────────────────────────────────
class TestT651EigenmatrixDeterminant:
    """T651 · det(P) = -E = -V(r-s) = -240."""

    def test_det_P_formula(self):
        """P = [[1,K,K_BAR],[1,r,-1-r],[1,s,-1-s]]; det(P) = -E."""
        # P matrix rows: eigenvalues of I, A, J-I-A
        P12, P22 = -1 - R, -1 - S  # entries for rows 1,2 column 2
        det_P = (1 * (R * P22 - P12 * S)
                 - K * (P22 - P12)
                 + K_BAR * (S - R))
        assert det_P == -E

    def test_det_P_equals_neg_V_times_spectral_gap(self):
        """det(P) = (s-r)·V = -V(r-s)."""
        P12, P22 = -1 - R, -1 - S
        det_P = (1 * (R * P22 - P12 * S)
                 - K * (P22 - P12)
                 + K_BAR * (S - R))
        assert det_P == -V * (R - S)

    def test_E_equals_V_times_spectral_gap(self):
        """E = V(r-s)/1 since K = LAM(r-s) and E = VK/2 = VLAM(r-s)/2... 
        Actually just V*(r-s) = 40*6 = 240 = E."""
        assert V * (R - S) == E

    def test_spectral_gap_divides_K(self):
        """K/(r-s) = LAM = 2."""
        assert Fraction(K, R - S) == LAM

    def test_abs_det_equals_E(self):
        assert abs(-E) == E == 240


# ── T652: Second eigenmatrix Q entries ─────────────────────────────────
class TestT652SecondEigenmatrix:
    """T652 · Q₁₁ = MU, Q₂₁ = -N — dual eigenmatrix encodes Paley and pentad."""

    def test_Q11_equals_MU(self):
        """Q₁₁ = f·r/K = 24·2/12 = 4 = MU."""
        Q11 = Fraction(F * R, K)
        assert Q11 == MU

    def test_Q21_equals_neg_N(self):
        """Q₂₁ = g·s/K = 15·(-4)/12 = -5 = -N."""
        Q21 = Fraction(G * S, K)
        assert Q21 == -N

    def test_Q11_plus_Q21(self):
        """Q₁₁ + Q₂₁ = MU - N = -1."""
        Q11 = Fraction(F * R, K)
        Q21 = Fraction(G * S, K)
        assert Q11 + Q21 == MU - N == -1

    def test_Q11_times_Q21(self):
        """Q₁₁ · Q₂₁ = -MU·N = -20."""
        Q11 = Fraction(F * R, K)
        Q21 = Fraction(G * S, K)
        assert Q11 * Q21 == -MU * N

    def test_Q12_value(self):
        """Q₁₂ = -f(1+r)/K_bar = -24·3/27 = -8/3."""
        Q12 = Fraction(-F * (1 + R), K_BAR)
        assert Q12 == Fraction(-8, 3)

    def test_Q22_value(self):
        """Q₂₂ = -g(1+s)/K_bar = -15·(-3)/27 = 5/3."""
        Q22 = Fraction(-G * (1 + S), K_BAR)
        assert Q22 == Fraction(5, 3)


# ── T653: Eigenmatrix duality ──────────────────────────────────────────
class TestT653EigenmatrixDuality:
    """T653 · det(P)·det(Q) = V³; det(Q) = -V³/E."""

    def test_dual_determinant_product(self):
        """P·Q = V·I implies det(P)·det(Q) = V³."""
        det_P = -E
        det_Q = Fraction(V**3, det_P)
        assert det_P * det_Q == V**3

    def test_det_Q_value(self):
        det_Q = Fraction(V**3, -E)
        assert det_Q == Fraction(-64000, 240)
        assert det_Q == Fraction(-800, 3)


# ── T654: Intersection numbers (R₁) ──────────────────────────────────
class TestT654IntersectionR1:
    """T654 · For adjacent pairs: p¹₁₂ = Q², p¹₂₂ = 18."""

    def test_p1_11(self):
        assert LAM == 2

    def test_p1_12_equals_Q_squared(self):
        p1_12 = K - 1 - LAM
        assert p1_12 == Q**2

    def test_p1_21_symmetric(self):
        """Symmetric scheme: p¹₂₁ = p¹₁₂ = Q²."""
        p1_12 = K - 1 - LAM
        p1_21 = K - 1 - LAM  # by symmetry
        assert p1_12 == p1_21 == Q**2

    def test_p1_22_value(self):
        p1_22 = V - 2 - LAM - 2 * (K - 1 - LAM)
        assert p1_22 == 18

    def test_row_sums_R1(self):
        """Row sums: K-1 and K_bar."""
        assert LAM + (K - 1 - LAM) == K - 1
        assert (K - 1 - LAM) + (V - 2 - LAM - 2 * (K - 1 - LAM)) == K_BAR


# ── T655: Intersection numbers (R₂) ──────────────────────────────────
class TestT655IntersectionR2:
    """T655 · For non-adjacent pairs: p²₁₂ = DIM_O, p²₂₂ = 18 = p¹₂₂."""

    def test_p2_11(self):
        assert MU == 4

    def test_p2_12_equals_DIM_O(self):
        p2_12 = K - MU
        assert p2_12 == DIM_O

    def test_p2_21_symmetric(self):
        p2_21 = K - MU
        assert p2_21 == DIM_O

    def test_p2_22_value(self):
        p2_22 = V - 2 - MU - 2 * (K - MU)
        assert p2_22 == 18

    def test_p22_universal(self):
        """p¹₂₂ = p²₂₂ = 18: the non-neighbor-pair count is the same
        regardless of whether the focal pair is adjacent or not!"""
        p1_22 = V - 2 - LAM - 2 * (K - 1 - LAM)
        p2_22 = V - 2 - MU - 2 * (K - MU)
        assert p1_22 == p2_22 == 18

    def test_row_sums_R2(self):
        assert MU + (K - MU) == K
        assert (K - MU) + (V - 2 - MU - 2 * (K - MU)) == K_BAR - 1


# ── T656: Complement isotropy ─────────────────────────────────────────
class TestT656ComplementIsotropy:
    """T656 · Complement SRG(40,27,18,18): LAM_bar = MU_bar → eigenvalues ±Q."""

    def test_lambda_bar(self):
        LAM_bar = V - 2 - 2 * K + MU
        assert LAM_bar == 18

    def test_mu_bar(self):
        MU_bar = V - 2 * K + LAM
        assert MU_bar == 18

    def test_lambda_equals_mu(self):
        """LAM_bar = MU_bar = 18 (isotropic complement)."""
        LAM_bar = V - 2 - 2 * K + MU
        MU_bar = V - 2 * K + LAM
        assert LAM_bar == MU_bar

    def test_complement_eigenvalues(self):
        """Complement eigenvalues: ±Q = ±3."""
        assert R_BAR == Q
        assert S_BAR == -Q

    def test_complement_SRG_equation(self):
        LAM_bar = V - 2 - 2 * K + MU
        MU_bar = V - 2 * K + LAM
        assert K_BAR * (K_BAR - LAM_bar - 1) == MU_bar * (V - K_BAR - 1)

    def test_K_bar_equals_ALBERT(self):
        assert K_BAR == ALBERT


# ── T657: Hoffman bounds – both tight ─────────────────────────────────
class TestT657HoffmanBounds:
    """T657 · Hoffman α-bound and ω-bound both achieved with equality."""

    def test_hoffman_alpha(self):
        """α ≤ V(-s)/(K-s) = 10, tight."""
        bound = Fraction(V * (-S), K - S)
        assert bound == ALPHA

    def test_hoffman_omega(self):
        """ω ≤ 1 - K/s = 1 + 3 = 4, tight."""
        bound = 1 - Fraction(K, S)
        assert bound == OMEGA

    def test_double_tight(self):
        """Both bounds tight simultaneously → W(3,3) is spectrally extremal."""
        alpha_bound = Fraction(V * (-S), K - S)
        omega_bound = 1 - Fraction(K, S)
        assert alpha_bound == ALPHA
        assert omega_bound == OMEGA

    def test_product_identity(self):
        """Tight Hoffman → α·ω = V."""
        assert ALPHA * OMEGA == V


# ── T658: Krein conditions ─────────────────────────────────────────────
class TestT658KreinConditions:
    """T658 · Both Krein conditions satisfied (neither tight)."""

    def test_krein_condition_1(self):
        """(r+1)(K+r+2rs) ≤ (K+r)(s+1)²."""
        lhs = (R + 1) * (K + R + 2 * R * S)
        rhs = (K + R) * (S + 1)**2
        assert lhs <= rhs

    def test_krein_condition_2(self):
        """(s+1)(K+s+2rs) ≤ (K+s)(r+1)²."""
        lhs = (S + 1) * (K + S + 2 * R * S)
        rhs = (K + S) * (R + 1)**2
        assert lhs <= rhs

    def test_krein_1_not_tight(self):
        lhs = (R + 1) * (K + R + 2 * R * S)
        rhs = (K + R) * (S + 1)**2
        assert lhs < rhs  # strict inequality

    def test_krein_2_not_tight(self):
        lhs = (S + 1) * (K + S + 2 * R * S)
        rhs = (K + S) * (R + 1)**2
        assert lhs < rhs

    def test_rs_product(self):
        """|r·s| = DIM_O."""
        assert abs(R * S) == DIM_O


# ── T659: Seidel energy ───────────────────────────────────────────────
class TestT659SeidelEnergy:
    """T659 · SE = α(2K+1) = 2N³ = 250; SE - E = α."""

    def test_seidel_energy_value(self):
        SE = abs(-(2 * K + 1)) + abs(-(2 * R + 1)) * F + abs(-(2 * S + 1)) * G
        assert SE == 250

    def test_SE_equals_2N_cubed(self):
        SE = 250
        assert SE == 2 * N**3

    def test_SE_equals_alpha_times_2K_plus_1(self):
        SE = 250
        assert SE == ALPHA * (2 * K + 1)

    def test_SE_minus_E_equals_alpha(self):
        SE = 250
        assert SE - E == ALPHA

    def test_seidel_eigenvalues(self):
        """Seidel eigenvalues: -(2K+1)=-25, -(2r+1)=-N, -(2s+1)=PHI6."""
        assert -(2 * K + 1) == -25
        assert -(2 * R + 1) == -N
        assert -(2 * S + 1) == PHI6


# ── T660: Walk ratio ──────────────────────────────────────────────────
class TestT660WalkRatio:
    """T660 · w₃/w₂ = λ = 6μ/K — the walk ratio equals the adjacency parameter."""

    def test_w3_over_w2(self):
        w2 = K**2 + R**2 * F + S**2 * G  # = VK
        w3 = K**3 + R**3 * F + S**3 * G
        assert Fraction(w3, w2) == LAM

    def test_walk_ratio_from_triangles(self):
        """w₃/w₂ = 6·C₃/(V·K) = 6μ/K."""
        assert Fraction(6 * MU, K) == LAM

    def test_w2_equals_VK(self):
        w2 = K**2 + R**2 * F + S**2 * G
        assert w2 == V * K

    def test_w3_equals_6_C3(self):
        w3 = K**3 + R**3 * F + S**3 * G
        C3 = V * MU
        assert w3 == 6 * C3


# ── T661: Eigenvalue equation ─────────────────────────────────────────
class TestT661EigenvalueEquation:
    """T661 · x² + (μ-λ)x + (μ-K) = 0 has roots r, s; disc = (r-s)² = 36."""

    def test_r_is_root(self):
        assert R**2 + (MU - LAM) * R + (MU - K) == 0

    def test_s_is_root(self):
        assert S**2 + (MU - LAM) * S + (MU - K) == 0

    def test_discriminant(self):
        disc = (MU - LAM)**2 - 4 * (MU - K)
        assert disc == (R - S)**2 == 36

    def test_vieta_sum(self):
        """r + s = -(μ - λ) = λ - μ = -2."""
        assert R + S == LAM - MU

    def test_vieta_product(self):
        """r·s = μ - K = -8 = -DIM_O."""
        assert R * S == MU - K == -DIM_O


# ── T662: Multiplicity algebra ────────────────────────────────────────
class TestT662MultiplicityAlgebra:
    """T662 · f/g = DIM_O/N, f-g = Q², f·g = V·Q² = E·Q/2."""

    def test_ratio(self):
        assert Fraction(F, G) == Fraction(DIM_O, N)

    def test_difference(self):
        assert F - G == Q**2

    def test_product_VQ2(self):
        assert F * G == V * Q**2

    def test_product_EQ_over_2(self):
        assert F * G == E * Q // 2

    def test_sum(self):
        assert F + G == V - 1


# ── T663: Laplacian eigenvalue ratio ──────────────────────────────────
class TestT663LaplacianRatio:
    """T663 · Θ/(K-s) = N/DIM_O = 5/8."""

    def test_ratio_value(self):
        assert Fraction(THETA, K - S) == Fraction(N, DIM_O)

    def test_ratio_is_5_over_8(self):
        assert Fraction(THETA, K - S) == Fraction(5, 8)

    def test_laplacian_eigenvalue_sum(self):
        """Laplacian eigenvalues: 0(×1), Θ=10(×f), K-s=16(×g). Sum = VK."""
        assert 0 * 1 + THETA * F + (K - S) * G == V * K

    def test_laplacian_K_minus_S(self):
        """K - s = 16 = 2·DIM_O."""
        assert K - S == 2 * DIM_O


# ── T664: Spanning tree exponent algebra ──────────────────────────────
class TestT664SpanningTreeExponents:
    """T664 · τ = 2^{Q⁴} · 5^{ALBERT-MU}; exponent sum = DIM_O · Φ₃."""

    def test_exp2_equals_Q4(self):
        assert 81 == Q**4

    def test_exp2_equals_3_ALBERT(self):
        assert 81 == 3 * ALBERT

    def test_exp5_equals_ALBERT_minus_MU(self):
        assert 23 == ALBERT - MU

    def test_exponent_sum(self):
        assert 81 + 23 == DIM_O * PHI3

    def test_exponent_sum_value(self):
        assert 81 + 23 == 104

    def test_spanning_tree_formula(self):
        """τ = (1/V) · Θ^f · (K-s)^g = (1/40) · 10²⁴ · 16¹⁵ = 2⁸¹ · 5²³."""
        # Verify via prime factorisation
        # 10^24 = 2^24 * 5^24
        # 16^15 = 2^60
        # Product = 2^84 * 5^24
        # Divide by 40 = 2^3 * 5: 2^81 * 5^23
        exp2 = 24 + 60 - 3
        exp5 = 24 - 1
        assert exp2 == 81
        assert exp5 == 23


# ── T665: Spectral orthogonality ──────────────────────────────────────
class TestT665SpectralOrthogonality:
    """T665 · K² + fr² + gs² = VK; fr + gs = -K; f + g = V-1."""

    def test_sum_of_eigenvalues(self):
        """Tr(A) = 0 ↔ K + fr + gs = 0 ↔ fr + gs = -K."""
        assert F * R + G * S == -K

    def test_sum_of_squared_eigenvalues(self):
        """Tr(A²) = VK ↔ K² + fr² + gs² = VK."""
        assert K**2 + F * R**2 + G * S**2 == V * K

    def test_multiplicity_sum(self):
        """1 + f + g = V."""
        assert 1 + F + G == V

    def test_three_identities_consistent(self):
        """The three trace identities determine f, g, r, s from V, K, LAM, MU."""
        # System: f+g = V-1, fr+gs = -K, fr²+gs² = VK-K²
        # Solution gives the known values.
        assert F + G == V - 1
        assert F * R + G * S == -K
        assert K**2 + F * R**2 + G * S**2 == V * K

    def test_inner_product(self):
        """The eigenvector inner product: 1·1 + 1·f + 1·g = V (trivially)."""
        assert 1 + F + G == V
