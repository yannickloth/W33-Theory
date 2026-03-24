"""
Phase CLXXXVIII: Complement SRG(40,27,18,18) and Symmetric Eigenvalue Duality

The complement Gc = SRG(40,27,18,18) has lam_c = mu_c (equal parameters!),
eigenvalues ±Q = ±3, and a cascade of remarkable Q-polynomial identities.

Key discoveries:
  - Complement eigenvalues: K_c=27, r_c=+Q=3 (×15), s_c=-Q=-3 (×24)
  - lam_c = mu_c = Q^2*(Q-1) = 18 → r_c + s_c = 0 (symmetric about 0!)
  - |r_c| = |s_c| = Q = 3 (equal absolute eigenvalues; unlike original!)
  - Eigenvalue multiplicities SWAP: r_c=Q has g=15, s_c=-Q has f=24 (reversed!)
  - K_c + r_c + s_c = K_c (since r_c = -s_c → eigenvalue sum = K_c itself)
  - Complement Laplacian eigenvalues: 0, K_c+Q=30(×24), K_c-Q=24(×15)
  - K_c + Q = Q^3+Q = Q(Q^2+1) = Q*THETA = 30 (Laplacian max = Q*THETA!)
  - K_c - Q = Q^3-Q = Q(Q^2-1) = Q*(K-MU) = 24 (Laplacian min = Q*(K-MU)!)
  - (K_c+Q)*(K_c-Q) = K_c^2 - Q^2 = Q^2*(Q^4-1) = Q^2*(Q^2-1)*(Q^2+1) = 9*8*10 = 720 = 6! = (2Q)!
  - STUNNING: K_c^2 - Q^2 = (2Q)! = 6! = 720 (at Q=3: 2Q=6 so (2Q)! = 720!)
  - Complement Fiedler = K_c-Q = 24 = Q*(Q^2-1) (vs original Fiedler = Q^2+1 = 10)
  - Sum complement Laplacian = 2|E_c| = V*K_c = 1080 = 30*24 + 24*15 = 720+360
  - 30*24 = 720 (symmetric eigenvalue-mult products: 30/24 ratio = (Q^2+1)/(Q^2-1) = 5/4)
  - 24*15 = 360 (lower eigenvalue × lower mult = 360 = V*K/1.5 ... = V*K_c-720)
  - 720+360 = 1080 = V*K_c = 40*27 ✓ (half-edges = 540 = V*K_c/2)
  - Complement energy: E_c = K_c + Q*g + Q*f = 27+45+72 = 144 = K^2 (original degree squared!)
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
K_C = V - 1 - K   # = 27

# Complement SRG(40,27,18,18) parameters
V_C = V    # = 40
K_C_VAL = K_C   # = 27
LAM_C = V - 2 - 2 * K + MU   # = 18
MU_C = LAM_C    # = 18 (complement has lam = mu!)

# Complement eigenvalues (from -1-r and -1-s)
EIG_R_C = -1 - EIG_S   # = -1+4 = +3 = +Q (×MUL_S = 15)
EIG_S_C = -1 - EIG_R   # = -1-2 = -3 = -Q (×MUL_R = 24)
MUL_R_C = MUL_S   # = 15 (multiplicity of r_c=+Q)
MUL_S_C = MUL_R   # = 24 (multiplicity of s_c=-Q) — SWAPPED!

# Complement Laplacian eigenvalues
LAP_C_0 = 0
LAP_C_1 = K_C_VAL - EIG_R_C   # = 27 - 3 = 24 (×MUL_R_C = 15)
LAP_C_2 = K_C_VAL - EIG_S_C   # = 27 + 3 = 30 (×MUL_S_C = 24)


# ============================================================
class TestT1_ComplementEigenvalues:
    """r_c = +Q = 3 (×15); s_c = -Q = -3 (×24); symmetric about 0."""

    def test_r_c_value(self):
        # r_c = -1 - s = -1+4 = 3 = Q
        assert EIG_R_C == Q

    def test_s_c_value(self):
        # s_c = -1 - r = -1-2 = -3 = -Q
        assert EIG_S_C == -Q

    def test_r_c_equals_Q(self):
        assert EIG_R_C == Q

    def test_s_c_equals_neg_Q(self):
        assert EIG_S_C == -Q

    def test_eigenvalues_symmetric_about_0(self):
        # r_c + s_c = 0 (since lam_c = mu_c implies r_c = -s_c)
        assert EIG_R_C + EIG_S_C == 0

    def test_equal_absolute_eigenvalues(self):
        # |r_c| = |s_c| = Q (both have same absolute value!)
        assert abs(EIG_R_C) == abs(EIG_S_C) == Q

    def test_multiplicities_swapped(self):
        # Complement: r_c=+Q has mult 15 = MUL_S; s_c=-Q has mult 24 = MUL_R (swapped!)
        assert MUL_R_C == MUL_S   # 15 for +Q
        assert MUL_S_C == MUL_R   # 24 for -Q

    def test_complement_eigenvalue_sum_identity(self):
        # K_c + r_c + s_c = K_c + Q - Q = K_c (eigenvalue sum = K_c itself!)
        assert K_C_VAL + EIG_R_C + EIG_S_C == K_C_VAL

    def test_complement_eigenvalue_product(self):
        # r_c * s_c = Q * (-Q) = -Q^2 = -9
        assert EIG_R_C * EIG_S_C == -(Q**2)

    def test_complement_eigenvalue_diff(self):
        # r_c - s_c = Q - (-Q) = 2Q = 6 (same as original r-s = 6!)
        assert EIG_R_C - EIG_S_C == 2 * Q


class TestT2_ComplementSRGParameters:
    """SRG(40,27,18,18): V=40, K_c=27=Q^3, lam_c=mu_c=18=Q^2*(Q-1)."""

    def test_K_c_value(self):
        assert K_C_VAL == 27

    def test_K_c_Q_formula(self):
        # K_c = Q^3 = 27
        assert K_C_VAL == Q**3

    def test_LAM_C_value(self):
        assert LAM_C == 18

    def test_LAM_C_Q_formula(self):
        # lam_c = Q^2*(Q-1) = 9*2 = 18
        assert LAM_C == Q**2 * (Q - 1)

    def test_lam_c_equals_mu_c(self):
        # Complement has lam = mu (symmetric/conference-type!)
        assert LAM_C == MU_C

    def test_complement_SRG_condition(self):
        # For SRG with lam=mu: r_c+s_c = lam_c-mu_c = 0 ✓
        assert EIG_R_C + EIG_S_C == LAM_C - MU_C

    def test_complement_K_c_formula(self):
        # K_c = V-1-K = (Q+1)(Q^2+1)-1-Q(Q+1) = Q^3 ✓
        assert V - 1 - K == Q**3

    def test_complement_valency_sum(self):
        # K + K_c + 1 = V = 40
        assert K + K_C_VAL + 1 == V


class TestT3_ComplementLaplacianEigenvalues:
    """Complement Laplacian: 0, K_c-Q=24(×15), K_c+Q=30(×24)."""

    def test_lap_c_0(self):
        assert LAP_C_0 == 0

    def test_lap_c_1_value(self):
        # K_c - Q = 27 - 3 = 24
        assert LAP_C_1 == 24

    def test_lap_c_1_Q_formula(self):
        # K_c - Q = Q^3 - Q = Q(Q^2-1) = Q*(K-MU) = 3*8 = 24
        assert LAP_C_1 == Q * (Q**2 - 1)
        assert LAP_C_1 == Q * (K - MU)

    def test_lap_c_2_value(self):
        # K_c + Q = 27 + 3 = 30
        assert LAP_C_2 == 30

    def test_lap_c_2_Q_formula(self):
        # K_c + Q = Q^3 + Q = Q(Q^2+1) = Q*THETA = 3*10 = 30
        assert LAP_C_2 == Q * (Q**2 + 1)
        assert LAP_C_2 == Q * THETA

    def test_lap_c_fiedler(self):
        # Fiedler of complement = 24 = Q*(Q^2-1)
        assert LAP_C_1 == Q * (Q**2 - 1)

    def test_lap_c_product(self):
        # (K_c-Q)*(K_c+Q) = K_c^2 - Q^2 = 729-9 = 720
        assert LAP_C_1 * LAP_C_2 == K_C_VAL**2 - Q**2

    def test_lap_c_product_value(self):
        assert LAP_C_1 * LAP_C_2 == 720


class TestT4_FactorialIdentity:
    """K_c^2 - Q^2 = Q^2*(Q^2-1)*(Q^2+1) = (2Q)! = 6! = 720 at Q=3."""

    def test_K_c_sq_minus_Q_sq(self):
        # K_c^2 - Q^2 = 729 - 9 = 720
        assert K_C_VAL**2 - Q**2 == 720

    def test_720_equals_factorial_2Q(self):
        # At Q=3: 2Q = 6, (2Q)! = 6! = 720
        factorial_2Q = 1
        for i in range(1, 2 * Q + 1):
            factorial_2Q *= i
        assert factorial_2Q == 720

    def test_720_equals_6_factorial(self):
        assert 6 * 5 * 4 * 3 * 2 * 1 == 720

    def test_product_identity(self):
        # K_c^2 - Q^2 = Q^2*(Q^2-1)*(Q^2+1) = Q^2 * (K-MU) * THETA = 9*8*10 = 720
        assert Q**2 * (K - MU) * THETA == 720

    def test_Q_factors_of_720(self):
        # Q^2*(Q^2-1)*(Q^2+1) = (2Q)! (Q=3 magic!)
        assert Q**2 * (Q**2 - 1) * (Q**2 + 1) == 720

    def test_laplacian_product_is_720(self):
        # (K_c-Q)*(K_c+Q) = LAP_C_1 * LAP_C_2 = 24*30 = 720
        assert LAP_C_1 * LAP_C_2 == 720

    def test_720_triple_factorization(self):
        # 720 = 9*8*10 = Q^2 * (Q^2-1) * (Q^2+1)
        assert 9 * 8 * 10 == 720
        assert Q**2 * (Q**2 - 1) * (Q**2 + 1) == 720


class TestT5_ComplementTraceAndEnergy:
    """Complement energy = K^2 = 144; complement Laplacian trace = V*K_c."""

    def test_complement_energy(self):
        # E_c = K_c + |r_c|*MUL_R_C + |s_c|*MUL_S_C = 27+3*15+3*24 = 27+45+72 = 144
        energy_c = K_C_VAL + abs(EIG_R_C) * MUL_R_C + abs(EIG_S_C) * MUL_S_C
        assert energy_c == 144

    def test_complement_energy_equals_K_squared(self):
        # E_c = K^2 = 144 (complement energy = square of original degree!)
        energy_c = K_C_VAL + abs(EIG_R_C) * MUL_R_C + abs(EIG_S_C) * MUL_S_C
        assert energy_c == K**2

    def test_complement_laplacian_trace(self):
        # Sum of complement Laplacian eigenvalues = 2|E_c| = V*K_c = 1080
        trace_lc = LAP_C_0 * 1 + LAP_C_1 * MUL_R_C + LAP_C_2 * MUL_S_C
        assert trace_lc == V * K_C_VAL

    def test_complement_laplacian_trace_value(self):
        trace_lc = LAP_C_0 * 1 + LAP_C_1 * MUL_R_C + LAP_C_2 * MUL_S_C
        assert trace_lc == 1080

    def test_partial_laplacian_sums(self):
        # LAP_C_1 * MUL_R_C = 24*15 = 360 = V*K_c/3
        # LAP_C_2 * MUL_S_C = 30*24 = 720 = V*K_c*2/3
        assert LAP_C_1 * MUL_R_C == 360
        assert LAP_C_2 * MUL_S_C == 720
        assert LAP_C_1 * MUL_R_C + LAP_C_2 * MUL_S_C == 1080

    def test_ratio_of_partial_sums(self):
        # 720/360 = 2 (upper partial sum is exactly twice lower!)
        assert Fraction(LAP_C_2 * MUL_S_C, LAP_C_1 * MUL_R_C) == 2

    def test_laplacian_fiedler_ratio(self):
        # Fiedler_c / Fiedler_G = 24/10 = 12/5 = (Q*(Q^2-1)) / (Q^2+1)
        assert Fraction(LAP_C_1, THETA) == Fraction(12, 5)


class TestT6_OriginalComplementDuality:
    """Cross-parameter identities linking G and Gc."""

    def test_fiedler_product(self):
        # Fiedler_G * Fiedler_Gc = THETA * (K_c-Q) = 10*24 = 240 = V*K/2 = |E|
        fiedler_G = THETA
        fiedler_Gc = LAP_C_1
        assert fiedler_G * fiedler_Gc == V * K // 2

    def test_laplacian_max_product(self):
        # max_G * max_Gc = (K+MU) * (K_c+Q) = 16*30 = 480 = V*K = 2|E|
        assert (K + MU) * LAP_C_2 == V * K

    def test_laplacian_max_product_value(self):
        assert (K + MU) * LAP_C_2 == 480

    def test_complement_eigenvalue_gap_same(self):
        # r_c - s_c = 2Q = 6 = r - s (same eigenvalue gap!)
        assert EIG_R_C - EIG_S_C == EIG_R - EIG_S

    def test_eigenvalue_gap_is_2Q(self):
        # Both graphs have eigenvalue gap = 2Q = 6
        assert EIG_R - EIG_S == 2 * Q
        assert EIG_R_C - EIG_S_C == 2 * Q

    def test_K_product_complement(self):
        # K * K_c = 12*27 = 324 = Q^4+Q^2 = ... hmm: 12*27=324
        # 324 = 18^2 = lam_c^2 = mu_c^2 (remarkable!)
        assert K * K_C_VAL == LAM_C**2

    def test_K_Kc_product_is_lambda_c_squared(self):
        # K * K_c = 324 = 18^2 = lam_c^2 (!)
        assert K * K_C_VAL == 324
        assert LAM_C**2 == 324
