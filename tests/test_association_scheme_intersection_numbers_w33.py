"""
Phase CLXXXI: SRG Association Scheme Intersection Numbers and Q-Formulas

The 2-class SRG association scheme has classes {I, A, J-I-A} with 7 non-trivial
intersection numbers, all expressible as Q-polynomials.

Key discoveries:
  - p_{11}^0 = K = Q(Q+1) = 12 (degree)
  - p_{11}^1 = LAM = Q-1 = 2 (triangle parameter)
  - p_{11}^2 = MU = Q+1 = 4 (square parameter)
  - p_{12}^1 = K-LAM-1 = Q^2 = 9 (non-adjacency extension)
  - p_{12}^2 = K-MU = Q^2-1 = 8 = |rs| (spectral product identity!)
  - p_{22}^0 = K_c = Q^3 = 27 (complement degree!)
  - p_{22}^1 = p_{22}^2 = Q^2*(Q-1) = 18 (complement SRG with lam=mu!)
  - Complement SRG(40,27,18,18) has lam_c = mu_c = Q^2*(Q-1) (equal parameters!)
  - K*(K-LAM-1) = K*Q^2 = 108 = MU*(V-K-1) = MU*Q^3 (SRG regularity check)
  - K_c*(K_c-lam_c-1) = Q^3*(Q^3-Q^2*(Q-1)-1) = (2Q)^3 = 216 (cube!)
  - Products: p_{11}^1 * p_{11}^2 = LAM*MU = Q^2-1 = 8 (= |rs|!)
  - Valencies: k_0=1, k_1=K=Q(Q+1), k_2=K_c=Q^3
  - Sum: k_0+k_1+k_2 = 1+Q(Q+1)+Q^3 = Q^3+Q^2+Q+1 = (Q+1)(Q^2+1) = V
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

K_C = V - 1 - K   # = 27 (complement degree)
LAM_C = V - 2 - 2 * K + MU  # = 18 (complement lambda)
MU_C = LAM_C             # = 18 (complement: lam = mu = 18)

# Intersection numbers (from SRG multiplication table A^2 = K*I + LAM*A + MU*(J-I-A))
P11_0 = K       # = 12
P11_1 = LAM     # = 2
P11_2 = MU      # = 4

P12_0 = 0       # (no contributions from I)
P12_1 = K - LAM - 1    # = 9
P12_2 = K - MU         # = 8

P22_0 = K_C            # = 27
P22_1 = MU_C           # = 18 (non-adj common neighbors of non-adj pair)
P22_2 = LAM_C          # = 18 (adj common neighbors of non-adj pair)


# ============================================================
class TestT1_Class1SelfProduct:
    """A_1^2 = K*A_0 + LAM*A_1 + MU*A_2; intersection numbers for class 1 × class 1."""

    def test_p11_0_value(self):
        # p_{11}^0 = K = 12
        assert P11_0 == 12

    def test_p11_0_equals_K(self):
        assert P11_0 == K

    def test_p11_0_Q_formula(self):
        # K = Q*(Q+1) = 3*4 = 12
        assert P11_0 == Q * (Q + 1)

    def test_p11_1_value(self):
        # p_{11}^1 = LAM = 2
        assert P11_1 == 2

    def test_p11_1_equals_LAM(self):
        assert P11_1 == LAM

    def test_p11_1_Q_formula(self):
        # LAM = Q-1 = 2
        assert P11_1 == Q - 1

    def test_p11_2_value(self):
        # p_{11}^2 = MU = 4
        assert P11_2 == 4

    def test_p11_2_equals_MU(self):
        assert P11_2 == MU

    def test_p11_2_Q_formula(self):
        # MU = Q+1 = 4
        assert P11_2 == Q + 1

    def test_p11_sum_identity(self):
        # p11_0 + p11_1 + p11_2 = K + LAM + MU = 18 = V/V * 18...
        # Also: K + LAM + MU = Q(Q+1)+(Q-1)+(Q+1) = Q^2+3Q = Q(Q+3) = 18
        assert P11_0 + P11_1 + P11_2 == Q * (Q + 3)
        assert P11_0 + P11_1 + P11_2 == 18


class TestT2_Class1Class2Product:
    """A_1*A_2 = p12_1*A_1 + p12_2*A_2; no A_0 term (off-diagonal)."""

    def test_p12_0_is_zero(self):
        # p_{12}^0 = 0 (A_1*A_2 has no diagonal contribution)
        assert P12_0 == 0

    def test_p12_1_value(self):
        # p_{12}^1 = K - LAM - 1 = 12 - 2 - 1 = 9
        assert P12_1 == 9

    def test_p12_1_equals_K_minus_LAM_minus_1(self):
        assert P12_1 == K - LAM - 1

    def test_p12_1_Q_formula(self):
        # K - LAM - 1 = Q(Q+1) - (Q-1) - 1 = Q^2+Q-Q+1-1 = Q^2 = 9
        assert P12_1 == Q**2

    def test_p12_2_value(self):
        # p_{12}^2 = K - MU = 12 - 4 = 8
        assert P12_2 == 8

    def test_p12_2_equals_K_minus_MU(self):
        assert P12_2 == K - MU

    def test_p12_2_Q_formula(self):
        # K - MU = Q(Q+1) - (Q+1) = (Q+1)(Q-1) = Q^2-1 = 8
        assert P12_2 == Q**2 - 1

    def test_p12_2_equals_LAM_times_MU(self):
        # Q^2-1 = (Q-1)(Q+1) = LAM*MU = 2*4 = 8 ✓
        assert P12_2 == LAM * MU

    def test_p12_2_equals_abs_rs(self):
        # K - MU = 8 = |r*s| = |-8| = 8 (spectral product!)
        assert P12_2 == abs(EIG_R * EIG_S)

    def test_p12_sum(self):
        # p12_1 + p12_2 = Q^2 + Q^2-1 = 2Q^2-1 = 17
        assert P12_1 + P12_2 == 2 * Q**2 - 1
        # p12_1+p12_2 = (K-λ-1)+(K-μ) = 2K-λ-μ-1 = 24-2-4-1 = 17
        assert P12_1 + P12_2 == 2 * K - LAM - MU - 1


class TestT3_Class2SelfProduct:
    """A_2^2 = K_c*A_0 + MU_c*A_1 + LAM_c*A_2; complement SRG with lam=mu."""

    def test_p22_0_value(self):
        # p_{22}^0 = K_c = 27
        assert P22_0 == 27

    def test_p22_0_equals_K_c(self):
        assert P22_0 == K_C

    def test_p22_0_Q_formula(self):
        # K_c = V-1-K = Q^3 = 27 (complement degree = Q^3!)
        assert P22_0 == Q**3

    def test_p22_1_value(self):
        # p_{22}^1 = MU_c = 18
        assert P22_1 == 18

    def test_p22_2_value(self):
        # p_{22}^2 = LAM_c = 18
        assert P22_2 == 18

    def test_lam_c_equals_mu_c(self):
        # Complement has lam_c = mu_c = 18 (every pair has same # common neighbors!)
        assert LAM_C == MU_C

    def test_p22_1_equals_p22_2(self):
        assert P22_1 == P22_2

    def test_p22_1_Q_formula(self):
        # lam_c = mu_c = Q^2*(Q-1) = 9*2 = 18 (general GQ(q,q) formula!)
        assert P22_1 == Q**2 * (Q - 1)

    def test_p22_complement_formula(self):
        # lam_c = V - 2 - 2K + MU = 40-2-24+4 = 18
        assert LAM_C == V - 2 - 2 * K + MU


class TestT4_SRGRegularityCheck:
    """SRG regularity: K*(K-LAM-1) = MU*(V-K-1); both = 108 = MU*Q^3."""

    def test_srg_regularity_identity(self):
        # K*(K-LAM-1) = MU*(V-K-1): standard SRG divisibility condition
        assert K * (K - LAM - 1) == MU * (V - K - 1)

    def test_srg_regularity_value(self):
        # = 12*9 = 108 = 4*27
        assert K * (K - LAM - 1) == 108

    def test_srg_regularity_Q_formula_1(self):
        # K*(K-LAM-1) = Q(Q+1)*Q^2 = Q^3*(Q+1) = 27*4 = 108
        assert K * P12_1 == Q**3 * (Q + 1)

    def test_srg_regularity_Q_formula_2(self):
        # MU*(V-K-1) = (Q+1)*Q^3 = Q^3*(Q+1) = 27*4 = 108 ✓
        assert MU * (V - K - 1) == Q**3 * (Q + 1)

    def test_108_equals_MU_Q3(self):
        # 108 = MU * Q^3 = 4 * 27 = 108 ✓ (non-adjacency × complement-degree)
        assert K * P12_1 == MU * Q**3

    def test_complement_regularity(self):
        # K_c*(K_c-lam_c-1) = mu_c*(V-K_c-1)
        # 27*(27-18-1) = 27*8 = 216 = 18*(40-27-1) = 18*12 = 216 ✓
        assert K_C * (K_C - LAM_C - 1) == MU_C * (V - K_C - 1)

    def test_complement_regularity_value(self):
        # = 27*8 = 216 = (2Q)^3 = 6^3 (eigenvalue gap cubed!)
        assert K_C * (K_C - LAM_C - 1) == 216

    def test_complement_regularity_cube(self):
        # 216 = (2Q)^3 = (r-s)^3 = 6^3 (remarkable!)
        assert K_C * (K_C - LAM_C - 1) == (EIG_R - EIG_S)**3

    def test_regularity_ratio(self):
        # 216 / 108 = 2 = (complement regularity) / (original regularity)
        assert K_C * (K_C - LAM_C - 1) // (K * P12_1) == 2


class TestT5_ValencyFormulas:
    """k_0=1, k_1=K, k_2=K_c; sum = V; Q-formulas for each."""

    def test_valency_sum(self):
        # k_0 + k_1 + k_2 = 1 + K + K_c = 1 + 12 + 27 = 40 = V
        assert 1 + K + K_C == V

    def test_valency_Q_formula(self):
        # 1 + Q(Q+1) + Q^3 = 1 + Q^2+Q + Q^3 = Q^3+Q^2+Q+1 = (Q+1)(Q^2+1) = V
        total = 1 + Q * (Q + 1) + Q**3
        assert total == V

    def test_valency_factored(self):
        # (Q+1)(Q^2+1) = 4*10 = 40 = V (standard GQ formula)
        assert (Q + 1) * (Q**2 + 1) == V

    def test_complement_degree_is_Q_cubed(self):
        # k_2 = K_c = Q^3 = 27
        assert K_C == Q**3

    def test_degree_is_Q_Q_plus_1(self):
        # k_1 = K = Q(Q+1) = 12
        assert K == Q * (Q + 1)


class TestT6_ProductIdentities:
    """Cross-parameter products: p11_1*p11_2 = LAM*MU = Q^2-1 = |rs|."""

    def test_lam_mu_product(self):
        # LAM*MU = (Q-1)(Q+1) = Q^2-1 = 8
        assert LAM * MU == Q**2 - 1

    def test_lam_mu_equals_p12_2(self):
        # LAM*MU = p_{12}^2 = K - MU = Q^2-1 (triple identity!)
        assert LAM * MU == P12_2

    def test_lam_mu_equals_abs_rs(self):
        # LAM*MU = |r*s| = 8 (eigenvalue product magnitude)
        assert LAM * MU == abs(EIG_R * EIG_S)

    def test_lam_mu_equals_K_minus_MU(self):
        # LAM*MU = K - MU (specific to W(3,3): k = mu*(1+lam))
        assert LAM * MU == K - MU

    def test_p12_1_equals_Q_squared(self):
        # p_{12}^1 = Q^2 = 9 (the "non-adjacent extension" = field order squared)
        assert P12_1 == Q**2

    def test_p12_product(self):
        # p12_1 * p12_2 = Q^2*(Q^2-1) = 9*8 = 72 = Q^2*LAM*MU
        assert P12_1 * P12_2 == Q**2 * (Q**2 - 1)

    def test_p12_product_value(self):
        assert P12_1 * P12_2 == 72

    def test_p22_times_complement_gap(self):
        # p22_1 * 2 = Q^2*(Q-1)*2 = 36 = (2Q)^2 = Delta
        assert P22_1 * 2 == (2 * Q)**2

    def test_intersection_sum_all(self):
        # sum of all 7 non-trivial intersection numbers (excluding p12_0=0):
        # K + LAM + MU + Q^2 + Q^2-1 + Q^3 + 2*Q^2*(Q-1)
        # = 12+2+4+9+8+27+36 = 98
        total = P11_0 + P11_1 + P11_2 + P12_1 + P12_2 + P22_0 + P22_1 + P22_2
        assert total == 98

    def test_intersection_sum_Q_formula(self):
        # 98 = K+LAM+MU + Q^2+(Q^2-1) + Q^3 + 2*Q^2*(Q-1)
        # = Q(Q+1)+(Q-1)+(Q+1) + Q^2+(Q^2-1) + Q^3 + 2Q^2(Q-1)
        # = Q^2+Q+Q-1+Q+1 + 2Q^2-1 + Q^3 + 2Q^3-2Q^2
        # = Q^2+3Q + 2Q^2-1 + Q^3 + 2Q^3-2Q^2 = 3Q^3+Q^2+3Q-1
        # = 3*27+9+9-1 = 81+9+9-1 = 98 ✓
        formula = 3 * Q**3 + Q**2 + 3 * Q - 1
        assert formula == 98
        assert P11_0 + P11_1 + P11_2 + P12_1 + P12_2 + P22_0 + P22_1 + P22_2 == formula
