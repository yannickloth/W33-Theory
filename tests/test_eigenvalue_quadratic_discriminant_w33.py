"""
Phase CLXXVIII: Eigenvalue Quadratic and Discriminant Identities of W(3,3)

The non-trivial eigenvalues r,s of any SRG(v,k,lam,mu) satisfy a QUADRATIC
rooted in the SRG parameters, with striking Q-formulas for GQ(q,q).

Key discoveries:
  - (x-r)(x-s) = x^2 - (lam-mu)*x - lam*mu  (eigenvalue quadratic!)
  - r + s = lam - mu = -2 (sum of non-trivial eigenvalues = lam - mu)
  - r * s = mu - k = -lam*mu = -(Q^2-1) = -8 (product = mu-k, always for GQ(q,q)!)
  - Discriminant Delta = (lam+mu)^2 = (2Q)^2 = 36 (discriminant = square of lam+mu!)
  - r - s = 2Q = lam+mu = 6 (eigenvalue gap = 2q for ALL GQ(q,q))
  - k - lam - mu = Q*(Q-1) = 6 = r - s  (Q=3 MAGIC: gap equals k-lam-mu!)
  - r^2 + s^2 = (lam-mu)^2 + 2*(k-mu) = 4 + 16 = 20
  - r^2 * s^2 = lam^2 * mu^2 = (Q^2-1)^2 = 64
  - k*r*s = -k*(Q^2-1) = -96 = -K^3/18
  - k = mu*(1+lam) = MU*(1+LAM) = 4*3 = 12 (holds for all GQ(q,q)!)
  - lam+mu = 2Q = r-s (lam+mu = eigenvalue gap, holds for all GQ(q,q)!)
  - Quadratic factor: x^2 + 2x - 8 = (x-2)(x+4) over integers
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K
EIG_R = 2
EIG_S = -4

MUL_K = 1
MUL_R = 24
MUL_S = 15

THETA = EIG_K + EIG_R + EIG_S   # = 10


# ============================================================
class TestT1_EigenvalueQuadratic:
    """(x-r)(x-s) = x^2 - (lam-mu)*x - lam*mu; coefficients from SRG params."""

    def test_quadratic_sum_coefficient(self):
        # The quadratic x^2 - (r+s)*x + r*s has -(r+s) = -(lam-mu) = mu-lam = 2
        assert -(EIG_R + EIG_S) == MU - LAM

    def test_quadratic_product_coefficient(self):
        # r*s = -lam*mu = -2*4 = -8
        assert EIG_R * EIG_S == -LAM * MU

    def test_quadratic_sum_equals_lam_minus_mu(self):
        # r + s = lam - mu = 2 - 4 = -2
        assert EIG_R + EIG_S == LAM - MU

    def test_quadratic_factors_correctly(self):
        # x^2 - (lam-mu)*x - lam*mu evaluated at r and s gives 0
        def quad(x):
            return x**2 - (LAM - MU)*x - LAM*MU
        assert quad(EIG_R) == 0
        assert quad(EIG_S) == 0

    def test_quadratic_constant_term(self):
        # Constant term = -lam*mu = -8
        assert -LAM * MU == -8

    def test_quadratic_linear_coefficient(self):
        # Linear coefficient = -(lam - mu) = mu - lam = 2
        assert -(LAM - MU) == 2

    def test_quadratic_is_x2_plus_2x_minus_8(self):
        # x^2 - (lam-mu)*x - lam*mu = x^2 + 2x - 8
        # Coefficients [1, +(mu-lam), -lam*mu] = [1, 2, -8]
        assert MU - LAM == 2
        assert LAM * MU == 8

    def test_vieta_r_times_s(self):
        # Vieta: r*s = -lam*mu = -8
        assert EIG_R * EIG_S == -LAM * MU
        assert EIG_R * EIG_S == -8

    def test_vieta_r_plus_s(self):
        # Vieta: r+s = lam-mu = -2
        assert EIG_R + EIG_S == LAM - MU
        assert EIG_R + EIG_S == -2


class TestT2_ProductIdentities:
    """r*s = mu-k = -lam*mu = -(Q^2-1) = -8; holds for all GQ(q,q)."""

    def test_rs_equals_mu_minus_k(self):
        # r*s = mu - k = 4 - 12 = -8 (general SRG formula: rs = mu - k)
        assert EIG_R * EIG_S == MU - K

    def test_mu_minus_k_equals_neg_lam_mu(self):
        # mu - k = -lam*mu for GQ(q,q): k = mu*(1+lam) → mu - k = -lam*mu ✓
        assert MU - K == -LAM * MU

    def test_k_equals_mu_times_1_plus_lam(self):
        # k = mu*(1+lam) = (q+1)*q = q^2+q = 12; holds for ALL GQ(q,q)!
        assert K == MU * (1 + LAM)

    def test_k_equals_mu_times_Q(self):
        # k = mu * Q = (Q+1)*Q = Q^2+Q = 12 (since lam = Q-1, 1+lam = Q)
        assert K == MU * Q

    def test_rs_equals_neg_Q_squared_minus_1(self):
        # r*s = -(Q^2-1) = -(9-1) = -8 (general for GQ(q,q)!)
        assert EIG_R * EIG_S == -(Q**2 - 1)

    def test_rs_equals_neg_lam_mu(self):
        # r*s = -lam*mu; and lam*mu = (Q-1)(Q+1) = Q^2-1 = 8 ✓
        assert EIG_R * EIG_S == -LAM * MU

    def test_lam_mu_equals_Q_squared_minus_1(self):
        # lam*mu = (Q-1)*(Q+1) = Q^2 - 1 = 8 (a difference of squares!)
        assert LAM * MU == Q**2 - 1

    def test_rs_Q_formula(self):
        # r*s = -(Q-1)(Q+1) = -(Q^2-1) = -8
        assert EIG_R * EIG_S == -(Q - 1) * (Q + 1)

    def test_abs_rs_equals_K_minus_MU(self):
        # |r*s| = 8 = k - mu = 12 - 4 = 8 ✓
        assert abs(EIG_R * EIG_S) == K - MU


class TestT3_SumIdentities:
    """r+s = lam-mu = -(mu-lam) = -2; sum of non-trivial eigenvalues."""

    def test_r_plus_s_value(self):
        assert EIG_R + EIG_S == -2

    def test_r_plus_s_equals_lam_minus_mu(self):
        # r+s = lam - mu = 2 - 4 = -2
        assert EIG_R + EIG_S == LAM - MU

    def test_r_plus_s_is_negative(self):
        # lam - mu < 0 for GQ(q,q): lam = q-1 < q+1 = mu
        assert EIG_R + EIG_S < 0

    def test_r_plus_s_plus_k_equals_THETA(self):
        # k + r + s = 12 + 2 - 4 = 10 = THETA
        assert EIG_K + EIG_R + EIG_S == THETA

    def test_r_plus_s_Q_formula(self):
        # r+s = lam-mu = (Q-1)-(Q+1) = -2 (always = -2 for GQ(q,q)!)
        assert EIG_R + EIG_S == (Q - 1) - (Q + 1)

    def test_r_plus_s_always_minus_2_for_GQ(self):
        # For ANY GQ(q,q): r+s = (q-1)-(q+1) = -2 (universal constant!)
        assert LAM - MU == -2

    def test_all_eigenvalues_sum_to_zero(self):
        # MUL_K*k + MUL_R*r + MUL_S*s = 0 (trace of A = 0)
        assert MUL_K * EIG_K + MUL_R * EIG_R + MUL_S * EIG_S == 0


class TestT4_Discriminant:
    """Delta = (lam+mu)^2 = (2Q)^2 = 36; discriminant of eigenvalue quadratic."""

    def test_discriminant_value(self):
        # Delta = (lam-mu)^2 + 4*(k-mu) = 4 + 32 = 36
        delta = (LAM - MU)**2 + 4 * (K - MU)
        assert delta == 36

    def test_discriminant_equals_lam_plus_mu_squared(self):
        # Delta = (lam+mu)^2 = 6^2 = 36 (CLEAN FORM!)
        assert (LAM - MU)**2 + 4 * (K - MU) == (LAM + MU)**2

    def test_lam_plus_mu_squared(self):
        # (lam+mu)^2 = 6^2 = 36
        assert (LAM + MU)**2 == 36

    def test_discriminant_equals_2Q_squared(self):
        # Delta = (2Q)^2 = 36
        assert (LAM + MU)**2 == (2 * Q)**2

    def test_lam_plus_mu_equals_2Q(self):
        # lam + mu = (Q-1)+(Q+1) = 2Q = 6 (for ALL GQ(q,q)!)
        assert LAM + MU == 2 * Q

    def test_sqrt_discriminant_equals_lam_plus_mu(self):
        # sqrt(Delta) = lam + mu = 2Q = 6 (eigenvalue gap = lam+mu!)
        import math
        delta = (LAM - MU)**2 + 4 * (K - MU)
        assert int(math.isqrt(delta)) == LAM + MU

    def test_eigenvalue_reconstruction_from_discriminant(self):
        # r = (lam-mu + sqrt(Delta)) / 2 = (-2 + 6)/2 = 2
        # s = (lam-mu - sqrt(Delta)) / 2 = (-2 - 6)/2 = -4
        delta_sqrt = LAM + MU  # = 6 = sqrt(Delta)
        r_reconstructed = Fraction(LAM - MU + delta_sqrt, 2)
        s_reconstructed = Fraction(LAM - MU - delta_sqrt, 2)
        assert r_reconstructed == EIG_R
        assert s_reconstructed == EIG_S

    def test_discriminant_mod_4(self):
        # Delta = 36; Delta mod 4 = 0 (ensures integer eigenvalues)
        assert 36 % 4 == 0


class TestT5_EigenvalueGap:
    """r - s = 2Q = 6 = lam+mu for ALL GQ(q,q)."""

    def test_gap_value(self):
        # r - s = 2 - (-4) = 6
        assert EIG_R - EIG_S == 6

    def test_gap_equals_2Q(self):
        # r - s = 2Q = 6 (eigenvalue gap = 2*field_order for GQ(q,q)!)
        assert EIG_R - EIG_S == 2 * Q

    def test_gap_equals_lam_plus_mu(self):
        # r - s = lam + mu = 2 + 4 = 6 (for ALL GQ(q,q): lam+mu = 2q)
        assert EIG_R - EIG_S == LAM + MU

    def test_gap_equals_sqrt_discriminant(self):
        # r - s = sqrt(Delta) = lam + mu = 6
        assert EIG_R - EIG_S == LAM + MU

    def test_gap_Q_formula(self):
        # r - s = (Q-1) - (-(Q+1)) = Q-1+Q+1 = 2Q = 6
        assert EIG_R - EIG_S == (Q - 1) - (-(Q + 1))


class TestT6_MagicQ3Identity:
    """At Q=3: r-s = k-lam-mu = 6 (UNIQUE to Q=3 among GQ(q,q)!)."""

    def test_k_minus_lam_minus_mu_value(self):
        # k - lam - mu = 12 - 2 - 4 = 6
        assert K - LAM - MU == 6

    def test_k_minus_lam_minus_mu_Q_formula(self):
        # k - lam - mu = q(q+1) - (q-1) - (q+1) = q^2-q = Q*(Q-1) = 6
        assert K - LAM - MU == Q * (Q - 1)

    def test_Q_times_Q_minus_1_equals_2Q_at_Q3(self):
        # Q*(Q-1) = 2Q iff Q-1 = 2 iff Q = 3 (MAGIC: only at Q=3!)
        assert Q * (Q - 1) == 2 * Q   # 6 = 6 ✓ (specific to Q=3)

    def test_gap_equals_k_minus_lam_minus_mu(self):
        # r - s = k - lam - mu = 6 (only true at Q=3!)
        assert EIG_R - EIG_S == K - LAM - MU

    def test_Q3_magic_polynomial_identity(self):
        # At Q=3: Q*(Q-1) = 2*Q → simplifies to Q-1=2 → Q=3
        # Numerically: 3*2 = 2*3 = 6 ✓
        assert Q * (Q - 1) == 2 * Q

    def test_eigenvalue_gap_as_three_different_expressions(self):
        # All equal 6: r-s, 2Q, lam+mu, k-lam-mu (Q=3 only for last)
        gap = 6
        assert EIG_R - EIG_S == gap
        assert 2 * Q == gap
        assert LAM + MU == gap
        assert K - LAM - MU == gap


class TestT7_HigherEigenvalueFormulas:
    """r^2, s^2, r^2+s^2, and products k*r*s."""

    def test_r_squared(self):
        assert EIG_R**2 == 4

    def test_s_squared(self):
        assert EIG_S**2 == 16

    def test_r_squared_equals_LAM_squared(self):
        # r^2 = LAM^2 = 4 (since r = LAM!)
        assert EIG_R**2 == LAM**2

    def test_s_squared_equals_MU_squared(self):
        # s^2 = MU^2 = 16 (since |s| = MU!)
        assert EIG_S**2 == MU**2

    def test_r_sq_plus_s_sq(self):
        # r^2 + s^2 = 4 + 16 = 20
        assert EIG_R**2 + EIG_S**2 == 20

    def test_r_sq_plus_s_sq_formula(self):
        # r^2 + s^2 = (r+s)^2 - 2*r*s = (-2)^2 - 2*(-8) = 4 + 16 = 20
        assert (EIG_R + EIG_S)**2 - 2 * EIG_R * EIG_S == 20

    def test_r_sq_plus_s_sq_equals_lam_sq_plus_mu_sq(self):
        # r^2+s^2 = LAM^2+MU^2 = 4+16 = 20 (since r=LAM, |s|=MU!)
        assert EIG_R**2 + EIG_S**2 == LAM**2 + MU**2

    def test_k_times_r_times_s(self):
        # k*r*s = 12*2*(-4) = -96
        assert EIG_K * EIG_R * EIG_S == -96

    def test_k_r_s_equals_neg_k_Q2_minus_1(self):
        # k*r*s = -k*(Q^2-1) = -12*8 = -96
        assert EIG_K * EIG_R * EIG_S == -K * (Q**2 - 1)

    def test_r_squared_times_s_squared(self):
        # (r*s)^2 = (-8)^2 = 64 = (Q^2-1)^2 = 64
        assert (EIG_R * EIG_S)**2 == (Q**2 - 1)**2

    def test_r_cubed_plus_s_cubed(self):
        # r^3 + s^3 = (r+s)^3 - 3*r*s*(r+s) = (-2)^3 - 3*(-8)*(-2) = -8 - 48 = -56
        assert EIG_R**3 + EIG_S**3 == (EIG_R + EIG_S)**3 - 3 * EIG_R * EIG_S * (EIG_R + EIG_S)

    def test_r_cubed_plus_s_cubed_value(self):
        # r^3 + s^3 = 8 + (-64) = -56
        assert EIG_R**3 + EIG_S**3 == -56


class TestT8_EigenvalueVsSRGParams:
    """Cross-identities connecting eigenvalues and SRG parameters."""

    def test_r_equals_lam(self):
        assert EIG_R == LAM

    def test_abs_s_equals_mu(self):
        assert abs(EIG_S) == MU

    def test_r_s_encodes_lam_mu(self):
        # Given r and s, recover lam and mu:
        # lam = r, mu = -s (specific to W(3,3) where r = lam, s = -mu)
        assert LAM == EIG_R
        assert MU == -EIG_S

    def test_lam_mu_Q_formulas(self):
        # lam = Q-1, mu = Q+1; r = lam = Q-1, s = -mu = -(Q+1)
        assert LAM == Q - 1
        assert MU == Q + 1
        assert EIG_R == Q - 1
        assert EIG_S == -(Q + 1)

    def test_eigenvalue_ratio(self):
        # s/r = -4/2 = -2 = -MU/LAM = -(Q+1)/(Q-1)
        assert Fraction(EIG_S, EIG_R) == Fraction(-MU, LAM)

    def test_eigenvalue_ratio_Q_formula(self):
        # s/r = -(Q+1)/(Q-1) = -4/2 = -2
        assert Fraction(EIG_S, EIG_R) == Fraction(-(Q + 1), Q - 1)

    def test_k_r_s_in_terms_of_Q(self):
        # k = Q(Q+1), r = Q-1, s = -(Q+1)
        assert K == Q * (Q + 1)
        assert EIG_R == Q - 1
        assert EIG_S == -(Q + 1)

    def test_power_sum_p3(self):
        # p3 = tr(A^3)/6 = number of triangles; p3 = (1/6)*sum_i lambda_i^3
        # sum lambda_i^3 = k^3 + r^3*f + s^3*g = 1728 + 8*24 + (-64)*15
        # = 1728 + 192 - 960 = 960
        p3_times_6 = EIG_K**3 + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S
        assert p3_times_6 == 1728 + 8 * 24 + (-64) * 15
        assert p3_times_6 == 960
        # Number of triangles = 960/6 = 160
        assert p3_times_6 % 6 == 0
        assert p3_times_6 // 6 == 160
