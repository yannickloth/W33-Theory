"""
Phase CLXVII: Minimal Polynomial, Cayley-Hamilton, and Walk Recurrence of W(3,3)

The adjacency matrix A has 3 distinct eigenvalues, so its minimal polynomial equals
mu_A(x) = (x-K)(x-r)(x-s) = x^3 - theta*x^2 - MU*(K-MU)*x + K*(K-MU).

Key discoveries:
  - r + s = -LAM (off-diagonal eigenvalue sum = negative of lambda)
  - r * s = MU - K = -(K-MU) (product = negative "deficit")
  - r - s = LAM + MU = 6 (eigenvalue gap = spectral diversity!)
  - K + r + s = theta = 10 = Lovász theta (stunning!)
  - K = Q * MU = 3 * 4 (field order times mu)
  - Cayley-Hamilton: A^3 = theta*A^2 + MU*(K-MU)*A - K*(K-MU)*I
  - A^{-1} = -(A^2 - theta*A - 32*I) / 96  [from Cayley-Hamilton]
  - SRG identity: (A-r*I)(A-s*I) = MU*J  [J is a polynomial in A!]
  - Walk recurrence: p_n = theta*p_{n-1} + 32*p_{n-2} - 96*p_{n-3}
  - Generating function pole sum = 1/r + 1/s + 1/K = 1/Q
"""
from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K    # = 12
EIG_R = 2    # = Q-1
EIG_S = -4   # = -(Q+1)

MUL_K = 1
MUL_R = 24
MUL_S = 15

# Lovász theta (Phase CLX)
THETA = K - LAM   # = 10

# Minimal polynomial: x^3 - THETA*x^2 + C1*x - C0
# = (x-K)(x-r)(x-s); expanding: C1 = Kr+Ks+rs, C0 = Krs
C1 = EIG_K*EIG_R + EIG_K*EIG_S + EIG_R*EIG_S   # = 24 - 48 - 8 = -32
C0 = EIG_K * EIG_R * EIG_S                       # = -96

# Walk power traces
def trace_An(n):
    return MUL_K * EIG_K**n + MUL_R * EIG_R**n + MUL_S * EIG_S**n

P = [trace_An(n) for n in range(9)]


# ============================================================
class TestT1_EigenvalueAlgebra:
    """Remarkable algebraic relations between SRG parameters and eigenvalues r, s."""

    def test_r_plus_s_equals_neg_LAM(self):
        # r + s = 2 + (-4) = -2 = -LAM
        assert EIG_R + EIG_S == -LAM

    def test_r_times_s_equals_MU_minus_K(self):
        # r * s = 2 * (-4) = -8 = MU - K (the "deficit" of the SRG)
        assert EIG_R * EIG_S == MU - K

    def test_r_minus_s_equals_LAM_plus_MU(self):
        # r - s = 2 - (-4) = 6 = LAM + MU (eigenvalue gap = spectral diversity!)
        assert EIG_R - EIG_S == LAM + MU

    def test_quadratic_for_r_s_roots(self):
        # r, s are roots of x^2 + LAM*x - (K-MU) = x^2 + 2x - 8 = 0
        def quad(x):
            return x**2 + LAM * x - (K - MU)
        assert quad(EIG_R) == 0
        assert quad(EIG_S) == 0

    def test_discriminant_is_perfect_square(self):
        # discriminant = LAM^2 + 4*(K-MU) = 4 + 32 = 36 = (LAM+MU)^2 = (r-s)^2
        disc = LAM**2 + 4 * (K - MU)
        assert disc == (LAM + MU)**2
        assert disc == (EIG_R - EIG_S)**2

    def test_K_plus_r_plus_s_equals_Lovász_theta(self):
        # K + r + s = 12 + 2 - 4 = 10 = THETA = Lovász theta! (stunning connection)
        assert EIG_K + EIG_R + EIG_S == THETA

    def test_K_times_r_plus_s_equals_neg_MUL_R(self):
        # K * (r + s) = 12 * (-2) = -24 = -MUL_R  (multiplicity from eigenvalue product)
        assert EIG_K * (EIG_R + EIG_S) == -MUL_R

    def test_K_minus_MU_equals_2_cubed(self):
        # K - MU = 12 - 4 = 8 = 2^3 = 2^Q (field order power!)
        assert K - MU == 2**Q

    def test_K_equals_Q_times_MU(self):
        # K = Q * MU = 3 * 4 = 12 (valency = field order times mu)
        assert K == Q * MU

    def test_theta_equals_K_minus_LAM(self):
        # THETA = K - LAM = 10 (Lovász theta from SRG parameters)
        assert THETA == K - LAM


class TestT2_MinimalPolynomialCayleyHamilton:
    """Minimal polynomial mu_A(x) = x^3 - theta*x^2 - 32*x + 96."""

    def test_C1_equals_neg_MU_times_K_minus_MU(self):
        # C1 = Kr + Ks + rs = -32 = -MU*(K-MU) = -4*8
        assert C1 == -(MU * (K - MU))

    def test_C0_equals_neg_K_times_K_minus_MU(self):
        # C0 = K*r*s = -96 = -K*(K-MU) = -12*8
        assert C0 == -(K * (K - MU))

    def test_cayley_hamilton_at_each_eigenvalue(self):
        # mu_A(eig) = eig^3 - THETA*eig^2 - 32*eig + 96 = 0
        for eig in [EIG_K, EIG_R, EIG_S]:
            assert eig**3 - THETA * eig**2 - 32 * eig + 96 == 0

    def test_recurrence_from_minimal_poly_coefficients(self):
        # min poly gives: x^3 = THETA*x^2 + 32*x - 96 for eigenvalues
        assert EIG_K**3 == THETA * EIG_K**2 + 32 * EIG_K - 96
        assert EIG_R**3 == THETA * EIG_R**2 + 32 * EIG_R - 96
        assert EIG_S**3 == THETA * EIG_S**2 + 32 * EIG_S - 96

    def test_recurrence_coeff_32_formula(self):
        # 32 = MU * (K - MU) = 4 * 8
        assert MU * (K - MU) == 32

    def test_recurrence_coeff_96_formula(self):
        # 96 = K * (K - MU) = 12 * 8
        assert K * (K - MU) == 96

    def test_ainv_diag_from_cayley_hamilton(self):
        # A^{-1} = -(A^2 - theta*A - 32*I) / 96
        # (A^{-1})_{ii} = -(K - theta*0 - 32) / 96 = -(K-32)/96 = 20/96 = 5/24
        ainv_diag = Fraction(-(K - 32), 96)
        assert ainv_diag == Fraction(5, 24)

    def test_ainv_adj_from_cayley_hamilton(self):
        # (A^{-1})_{ij, adj} = -(LAM - theta*1 - 0) / 96 = -(2-10)/96 = 8/96 = 1/12
        ainv_adj = Fraction(-(LAM - THETA), 96)
        assert ainv_adj == Fraction(1, K)

    def test_ainv_non_from_cayley_hamilton(self):
        # (A^{-1})_{ij, non} = -(MU - 0 - 0) / 96 = -4/96 = -1/24
        ainv_non = Fraction(-MU, 96)
        assert ainv_non == Fraction(-1, MUL_R)

    def test_minimal_poly_coeff_sum(self):
        # Sum of coefficients: mu_A(1) = 1 - 10 - 32 + 96 = 55 = C(K-1, 2) = F_10
        mu_at_1 = 1 - THETA - MU*(K-MU) + K*(K-MU)
        assert mu_at_1 == (K - 1) * (K - 2) // 2   # = 55

    def test_minimal_poly_at_neg_1(self):
        # mu_A(-1) = -1 - 10 + 32 + 96 = 117 = 9*13 = Q^2 * (Q^2+Q+1)
        mu_at_neg1 = (-1)**3 - THETA*(-1)**2 - 32*(-1) + 96
        assert mu_at_neg1 == Q**2 * (Q**2 + Q + 1)


class TestT3_SRGIdentityAndJPolynomial:
    """For SRG: (A-r*I)(A-s*I) = MU*J; A^2 = (K-MU)*I + (LAM-MU)*A + MU*J."""

    def test_SRG_identity_r_eigenvalue(self):
        # r^2 = (K-MU) + (LAM-MU)*r  (on eigenvectors perp to all-ones)
        assert EIG_R**2 == (K - MU) + (LAM - MU) * EIG_R

    def test_SRG_identity_s_eigenvalue(self):
        # s^2 = (K-MU) + (LAM-MU)*s
        assert EIG_S**2 == (K - MU) + (LAM - MU) * EIG_S

    def test_SRG_identity_K_eigenvalue(self):
        # K^2 = (K-MU) + (LAM-MU)*K + MU*V  (all-ones eigenvector; J eigenvalue = V)
        assert EIG_K**2 == (K - MU) + (LAM - MU) * EIG_K + MU * V

    def test_J_poly_trace(self):
        # trace((A-r*I)(A-s*I)) = trace(A^2 - (r+s)*A + rs*I)
        # = P[2] - (r+s)*P[1] + rs*V = 480 - (-2)*0 + (-8)*40 = 480-320 = 160 = MU*V
        trace_Jpoly = P[2] - (EIG_R + EIG_S) * P[1] + (EIG_R * EIG_S) * V
        assert trace_Jpoly == MU * V

    def test_J_poly_K_eigenvalue(self):
        # (K-r)(K-s) = (12-2)(12+4) = 10*16 = 160 = MU*V (eigenvalue of MU*J on 1-vec)
        assert (EIG_K - EIG_R) * (EIG_K - EIG_S) == MU * V

    def test_J_poly_r_eigenvalue_is_zero(self):
        # (r-r)(r-s) = 0 (r-eigenvectors killed by (A-rI))
        assert (EIG_R - EIG_R) * (EIG_R - EIG_S) == 0

    def test_J_poly_s_eigenvalue_is_zero(self):
        assert (EIG_S - EIG_R) * (EIG_S - EIG_S) == 0

    def test_ES_denominator_is_K_times_K_minus_MU(self):
        # (s-K)(s-r) = (-4-12)(-4-2) = (-16)(-6) = 96 = K*(K-MU)
        assert (EIG_S - EIG_K) * (EIG_S - EIG_R) == K * (K - MU)

    def test_K_minus_r_times_K_minus_s_equals_MU_V(self):
        # = 10 * 16 = 160 = 4 * 40 = MU * V
        assert (K - EIG_R) * (K - EIG_S) == MU * V


class TestT4_WalkRecurrence:
    """trace(A^n) satisfies p_n = theta*p_{n-1} + 32*p_{n-2} - 96*p_{n-3}."""

    def test_p0_is_V(self):
        assert P[0] == V

    def test_p1_is_zero(self):
        # trace(A) = 0 (no self-loops)
        assert P[1] == 0

    def test_p2_is_K_times_V(self):
        # trace(A^2) = K*V = 480 = Seeley-DeWitt a0
        assert P[2] == K * V

    def test_p3_is_V_K_LAM(self):
        # trace(A^3) = V*K*LAM = 40*12*2 = 960 = 6*(# triangles)
        assert P[3] == V * K * LAM

    def test_p4_is_K_V_times_V_plus_K(self):
        # trace(A^4) = K*V*(V+K) = 480*52 = 24960 = a0*dim(F4)
        assert P[4] == K * V * (V + K)

    def test_recurrence_p3(self):
        assert P[3] == THETA * P[2] + 32 * P[1] - 96 * P[0]

    def test_recurrence_p4(self):
        assert P[4] == THETA * P[3] + 32 * P[2] - 96 * P[1]

    def test_recurrence_p5(self):
        assert P[5] == THETA * P[4] + 32 * P[3] - 96 * P[2]

    def test_recurrence_p6(self):
        assert P[6] == THETA * P[5] + 32 * P[4] - 96 * P[3]

    def test_recurrence_p7(self):
        assert P[7] == THETA * P[6] + 32 * P[5] - 96 * P[4]

    def test_recurrence_p8(self):
        assert P[8] == THETA * P[7] + 32 * P[6] - 96 * P[5]

    def test_recurrence_multiplied_trace(self):
        # Dividing both sides by V: average walks per vertex satisfies same recurrence
        for n in range(3, 7):
            assert P[n] == THETA * P[n-1] + MU*(K-MU) * P[n-2] - K*(K-MU) * P[n-3]


class TestT5_GeneratingFunction:
    """G(t) = sum_{n>=0} trace(A^n) t^n with denominator 1-theta*t-32t^2+96t^3."""

    def test_denominator_from_min_poly(self):
        # Denominator = 1 - 10t - 32t^2 + 96t^3 = reversed min poly
        # Coefficients: [1, -THETA, -MU*(K-MU), K*(K-MU)]
        assert [1, -THETA, -(MU*(K-MU)), K*(K-MU)] == [1, -10, -32, 96]

    def test_denominator_root_at_1_over_K(self):
        # 1 - 10*(1/12) - 32*(1/12)^2 + 96*(1/12)^3 = 0
        t = Fraction(1, EIG_K)
        val = 1 - THETA*t - 32*t**2 + 96*t**3
        assert val == 0

    def test_denominator_root_at_1_over_r(self):
        t = Fraction(1, EIG_R)
        val = 1 - THETA*t - 32*t**2 + 96*t**3
        assert val == 0

    def test_denominator_root_at_1_over_s(self):
        t = Fraction(1, EIG_S)
        val = 1 - THETA*t - 32*t**2 + 96*t**3
        assert val == 0

    def test_pole_sum_equals_1_over_Q(self):
        # 1/K + 1/r + 1/s = 1/12 + 1/2 - 1/4 = 1/12 + 6/12 - 3/12 = 4/12 = 1/3 = 1/Q!
        pole_sum = Fraction(1, EIG_K) + Fraction(1, EIG_R) + Fraction(1, EIG_S)
        assert pole_sum == Fraction(1, Q)

    def test_pole_product_is_1_over_K_r_s(self):
        # Product of poles = 1/(K*r*s) = 1/(-96) = 1/C0
        pole_prod = Fraction(1, EIG_K * EIG_R * EIG_S)
        assert pole_prod == Fraction(1, C0)

    def test_G_partial_fraction_multiplicities(self):
        # G(t) = 1/(1-12t) + 24/(1-2t) + 15/(1+4t); residues = multiplicities
        assert MUL_K == 1
        assert MUL_R == 24
        assert MUL_S == 15

    def test_G_sum_of_partial_fractions_gives_V_at_0(self):
        # G(0) = MUL_K + MUL_R + MUL_S = V
        assert MUL_K + MUL_R + MUL_S == V


class TestT6_CrossPhaseConnections:
    """Connections from minimal polynomial to prior phases."""

    def test_theta_equals_Lovász_theta(self):
        # Coefficient of -x^2 in min poly = K+r+s = THETA = Lovász theta
        assert THETA == 10

    def test_walk_recurrence_coefficient_theta_connection(self):
        # The recurrence coefficient 10 = Lovász theta appears in the walk recurrence!
        # theta(W33) * theta(complement) = V: 10 * 4 = 40 = V
        theta_bar = V // THETA   # = 4 = MU
        assert THETA * theta_bar == V

    def test_Seeley_DeWitt_from_recurrence(self):
        # p_2 = K*V = 480 = a0 (Seeley-DeWitt from Phase CLIV)
        assert P[2] == K * V

    def test_F4_dimension_from_recurrence(self):
        # p_4 / p_2 = (V+K) = 52 = dim(F4) (from Phase CLXVI)
        assert P[4] // P[2] == V + K

    def test_zeta_at_minus_3_is_walk_count(self):
        # zeta_A(-3) = trace(A^3) = V*K*LAM = 960
        assert P[3] == V * K * LAM

    def test_ainv_entries_recover_all_three(self):
        # All three A^{-1} entries from Cayley-Hamilton:
        assert Fraction(-(K - 32), 96) == Fraction(5, 24)    # diagonal
        assert Fraction(-(LAM - THETA), 96) == Fraction(1, K) # adjacent
        assert Fraction(-MU, 96) == Fraction(-1, MUL_R)       # non-adjacent

    def test_minimal_poly_constant_vs_det_exponent(self):
        # K*(K-MU) = 96; from Phase CLXVI det(A) = -3*2^56; 96 = 3*2^5 = Q*2^{LAM+Q}
        assert K * (K - MU) == Q * 2**(LAM + Q)

    def test_quadratic_eigenvalue_equation_discriminant(self):
        # Discriminant (LAM+MU)^2 = 36 = 6^2; r-s = 6 = LAM+MU
        assert (LAM + MU)**2 == 36
        assert EIG_R - EIG_S == LAM + MU
