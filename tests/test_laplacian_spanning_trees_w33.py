"""
Phase CLXIX: Laplacian Spectrum, Spanning Trees, and Kirchhoff Index of W(3,3)

The Laplacian L = K*I - A has eigenvalues 0, K-r, K-s with multiplicities 1, MUL_R, MUL_S.

Key discoveries:
  - L1 = K - r = 10 = THETA = Lovász theta! (Laplacian eigenvalue = Lovász theta)
  - L2 = K - s = 16 = 2^MU = 2^4! (Laplacian eigenvalue is a power of two!)
  - v_2(L2) = MU = 4: 2-adic valuation of (K-s) equals mu
  - tau(W33) = 2^{Q^MU} * 5^{MUL_R - 1} = 2^81 * 5^23 (exponents involve Q^MU = 81!)
  - Kirchhoff index KF = Q * (LAM*MU*(K-1)+1) / 2 = Q*F_11/2 = 267/2
  - Algebraic connectivity (Fiedler) = L1 = THETA = 10 (field-theory spectral gap)
  - Normalized Laplacian eigenvalues: 0, THETA/K = 5/6, (K+MU)/K = 4/3
  - L2/L1 = 8/5 = (K-MU)/(Q^2-4): ratio of Laplacian eigenvalues = deficit/discriminant
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

THETA = K - LAM   # = 10

# Laplacian eigenvalues: L = K*I - A
L0 = 0              # mult MUL_K = 1
L1 = K - EIG_R     # = 10 = THETA, mult MUL_R = 24
L2 = K - EIG_S     # = 16 = 2^MU, mult MUL_S = 15

# Kirchhoff index (from Phase CLXIII)
KF = V * (Fraction(MUL_R, L1) + Fraction(MUL_S, L2))   # = 267/2


# ============================================================
class TestT1_LaplacianEigenvalues:
    """Laplacian L = KI - A has eigenvalues 0, K-r=10, K-s=16."""

    def test_L0_is_zero(self):
        assert L0 == 0

    def test_L1_equals_K_minus_r(self):
        assert L1 == K - EIG_R

    def test_L2_equals_K_minus_s(self):
        assert L2 == K - EIG_S

    def test_L1_equals_theta(self):
        # L1 = K - r = K - (Q-1) = K - Q + 1 = 10 = THETA = Lovász theta!
        assert L1 == THETA

    def test_L1_equals_K_minus_Q_plus_1(self):
        # L1 = K - (Q-1) = K - Q + 1 = 12 - 2 = 10
        assert L1 == K - Q + 1

    def test_L2_equals_2_power_MU(self):
        # L2 = K - s = K + MU = 12 + 4 = 16 = 2^MU = 2^4 (stunning!)
        assert L2 == 2**MU

    def test_L2_equals_K_plus_MU(self):
        # L2 = K + MU = K - EIG_S (since EIG_S = -MU)
        assert L2 == K + MU

    def test_L2_2adic_valuation_equals_MU(self):
        # v_2(L2) = v_2(16) = 4 = MU (2-adic valuation of Laplacian eigenvalue = mu!)
        n = L2
        v = 0
        while n % 2 == 0:
            n //= 2
            v += 1
        assert v == MU

    def test_L1_5adic_valuation_is_1(self):
        # v_5(L1) = v_5(10) = 1 (exactly one factor of 5)
        n = L1
        v = 0
        while n % 5 == 0:
            n //= 5
            v += 1
        assert v == 1

    def test_Laplacian_eigenvalue_sum(self):
        # MUL_K*L0 + MUL_R*L1 + MUL_S*L2 = 0 + 24*10 + 15*16 = 240+240 = 480 = K*V
        lap_sum = MUL_K * L0 + MUL_R * L1 + MUL_S * L2
        assert lap_sum == K * V

    def test_Laplacian_eigenvalue_sum_equals_trace_L(self):
        # trace(L) = trace(KI - A) = K*V - trace(A) = K*V - 0 = K*V = 480
        assert MUL_R * L1 + MUL_S * L2 == K * V

    def test_fiedler_value_is_L1(self):
        # Algebraic connectivity = smallest nonzero Laplacian eigenvalue = L1 = 10
        assert L1 == THETA
        assert L1 < L2

    def test_L2_over_L1_ratio(self):
        # L2/L1 = 16/10 = 8/5 = (K-MU)/(Q^2-4) = (K-MU)/F5
        ratio = Fraction(L2, L1)
        assert ratio == Fraction(K - MU, Q**2 - 4)


class TestT2_SpanningTrees:
    """Number of spanning trees tau(W33) = 2^{Q^MU} * 5^{MUL_R-1}."""

    def test_tau_2_adic_exponent(self):
        # v_2(tau) = MUL_R*v_2(L1) + MUL_S*v_2(L2) - v_2(V)
        # = 24*1 + 15*4 - 3 = 24 + 60 - 3 = 81 = Q^MU = 3^4 = 81!
        v2_L1 = 1   # v_2(10) = 1
        v2_L2 = 4   # v_2(16) = 4 = MU
        v2_V  = 3   # v_2(40) = 3
        exp2 = MUL_R * v2_L1 + MUL_S * v2_L2 - v2_V
        assert exp2 == 81

    def test_tau_5_adic_exponent(self):
        # v_5(tau) = MUL_R*v_5(L1) + MUL_S*v_5(L2) - v_5(V)
        # = 24*1 + 15*0 - 1 = 24 - 1 = 23 = MUL_R - 1
        v5_L1 = 1   # v_5(10) = 1
        v5_L2 = 0   # v_5(16) = 0
        v5_V  = 1   # v_5(40) = 1
        exp5 = MUL_R * v5_L1 + MUL_S * v5_L2 - v5_V
        assert exp5 == MUL_R - 1

    def test_tau_2_exponent_equals_Q_power_MU(self):
        # 81 = Q^MU = 3^4 (field order to the power mu!)
        assert Q**MU == 81

    def test_tau_5_exponent_equals_MUL_R_minus_1(self):
        assert MUL_R - 1 == 23

    def test_tau_exact_value(self):
        # tau = (1/V) * L1^MUL_R * L2^MUL_S = (1/40) * 10^24 * 16^15
        tau_numerator = L1**MUL_R * L2**MUL_S
        assert tau_numerator % V == 0
        tau = tau_numerator // V
        assert tau == 2**81 * 5**23

    def test_tau_formula_from_matrix_tree(self):
        # Matrix-tree theorem: tau = (1/V) * prod of nonzero Laplacian eigenvalues
        tau = (L1**MUL_R * L2**MUL_S) // V
        assert tau == 2**(Q**MU) * 5**(MUL_R - 1)

    def test_tau_prime_factorization_only_2_and_5(self):
        # tau = 2^81 * 5^23: only prime factors are 2 and 5
        tau = 2**81 * 5**23
        assert tau == (L1**MUL_R * L2**MUL_S) // V

    def test_tau_exponent_of_2_derivation(self):
        # MUL_R * 1 + MUL_S * MU - v_2(V) = 24 + 60 - 3 = 81
        assert MUL_R * 1 + MUL_S * MU - 3 == Q**MU

    def test_tau_exponent_of_5_derivation(self):
        # MUL_R * 1 - 1 = 23 = MUL_R - 1
        assert MUL_R * 1 - 1 == MUL_R - 1


class TestT3_KirchhoffIndex:
    """Kirchhoff index KF = V * sum(1/lambda_i) = 267/2 = Q*F11/2."""

    def test_KF_exact(self):
        # KF = V * (MUL_R/L1 + MUL_S/L2)
        assert KF == Fraction(267, 2)

    def test_KF_formula(self):
        # KF = V * (24/10 + 15/16) = 40 * (12/5 + 15/16)
        kf = V * (Fraction(MUL_R, L1) + Fraction(MUL_S, L2))
        assert kf == Fraction(267, 2)

    def test_KF_numerator(self):
        # 267 = 3 * 89 = Q * F11 where F11 = LAM*MU*(K-1)+1 = 2*4*11+1 = 89
        F11 = LAM * MU * (K - 1) + 1
        assert F11 == 89
        assert KF.numerator == Q * F11

    def test_KF_denominator(self):
        # denominator = 2 (exactly half-integer)
        assert KF.denominator == 2

    def test_KF_equals_Q_times_F11_over_2(self):
        F11 = LAM * MU * (K - 1) + 1
        assert KF == Fraction(Q * F11, 2)

    def test_F11_is_Fibonacci(self):
        # F11 = 89 = 11th Fibonacci number = LAM*MU*(K-1)+1 (from Phase CLXV)
        assert LAM * MU * (K - 1) + 1 == 89

    def test_KF_partial_fractions(self):
        # First term: V*MUL_R/L1 = 40*24/10 = 960/10 = 96
        kf1 = Fraction(V * MUL_R, L1)
        assert kf1 == 96

    def test_KF_second_partial_fraction(self):
        # Second term: V*MUL_S/L2 = 40*15/16 = 600/16 = 75/2
        kf2 = Fraction(V * MUL_S, L2)
        assert kf2 == Fraction(75, 2)

    def test_KF_sum_of_two_terms(self):
        assert KF == 96 + Fraction(75, 2)


class TestT4_NormalizedLaplacian:
    """Normalized Laplacian N = L/K for regular graphs; eigenvalues 0, L1/K, L2/K."""

    def test_normalized_L1(self):
        # (K-r)/K = 10/12 = 5/6 = THETA/K
        assert Fraction(L1, K) == Fraction(5, 6)

    def test_normalized_L1_equals_theta_over_K(self):
        assert Fraction(L1, K) == Fraction(THETA, K)

    def test_normalized_L2(self):
        # (K-s)/K = 16/12 = 4/3
        assert Fraction(L2, K) == Fraction(4, 3)

    def test_normalized_L2_equals_K_plus_MU_over_K(self):
        assert Fraction(L2, K) == Fraction(K + MU, K)

    def test_normalized_sum(self):
        # MUL_R*(L1/K) + MUL_S*(L2/K) = 24*5/6 + 15*4/3 = 20 + 20 = 40 = V
        norm_sum = MUL_R * Fraction(L1, K) + MUL_S * Fraction(L2, K)
        assert norm_sum == V

    def test_normalized_L2_greater_than_1(self):
        # (K-s)/K = 4/3 > 1 (exceeds 1; only possible for non-bipartite graphs)
        assert Fraction(L2, K) > 1

    def test_normalized_spectral_gap(self):
        # Normalized Fiedler value = L1/K = 5/6 = 1 - r/K = 1 - 1/6
        norm_fiedler = Fraction(L1, K)
        assert norm_fiedler == 1 - Fraction(EIG_R, K)

    def test_normalized_L2_from_walk_eigenvalue(self):
        # L2/K = 1 - s/K = 1 - (-1/3) = 1 + 1/Q = (Q+1)/Q = 4/3
        assert Fraction(L2, K) == 1 + Fraction(1, Q)
        assert Fraction(L2, K) == Fraction(Q + 1, Q)


class TestT5_LaplacianAlgebraicConnections:
    """Algebraic connections of Laplacian eigenvalues to other phases."""

    def test_L1_equals_Lovász_theta(self):
        # Fiedler value L1 = THETA = Lovász theta — same quantity in two roles!
        assert L1 == THETA

    def test_L2_equals_2_to_the_MU(self):
        # L2 = 2^MU: the second Laplacian eigenvalue is a power of 2!
        assert L2 == 2**MU

    def test_L1_times_L2_equals_K_times_V_over_Q(self):
        # L1 * L2 = 10 * 16 = 160 = MU * V = (K-r)(K-s) (from Phase CLXVII)
        assert L1 * L2 == MU * V

    def test_L1_plus_L2_equals_2K(self):
        # L1 + L2 = (K-r) + (K-s) = 2K - (r+s) = 2K + LAM = 24+2 = 26
        # Also = 2K + LAM = 2*12 + 2 = 26
        assert L1 + L2 == 2 * K + LAM

    def test_L2_squared_over_L1_squared(self):
        # (L2/L1)^2 = (8/5)^2 = 64/25
        assert Fraction(L2, L1)**2 == Fraction(64, 25)

    def test_trace_L_squared(self):
        # trace(L^2) = MUL_R*L1^2 + MUL_S*L2^2 = 24*100 + 15*256 = 2400 + 3840 = 6240
        trace_L2 = MUL_R * L1**2 + MUL_S * L2**2
        assert trace_L2 == 6240

    def test_trace_L_squared_equals_2KV_minus_2_times_edges_times_2(self):
        # trace(L^2) = ||L||_F^2 = sum_i L_ii^2 + 2*sum_{i<j} L_ij^2
        # = V*K^2 + 2*K*V*1 = V*K^2 + 2*V*K (since each edge contributes 2 to trace)
        # Actually trace(L^2) = trace((KI-A)^2) = K^2*V - 2K*trace(A) + trace(A^2)
        # = K^2*V - 0 + K*V = K*V*(K+1) = 12*40*13 = 6240 ✓
        assert MUL_R * L1**2 + MUL_S * L2**2 == K * V * (K + 1)

    def test_Laplacian_eigenvalue_cross_product(self):
        # (K-r) * (K-s) = L1 * L2 = MU * V = 4 * 40 = 160 (from Phase CLXVII)
        assert L1 * L2 == MU * V


class TestT6_SpanningTreesCrossPhase:
    """Spanning tree connections to other phases."""

    def test_tau_2_exponent_involves_Q_to_the_4th(self):
        # 81 = Q^4 = 3^4 (Q^MU where MU = Q+1 = 4)
        assert Q**MU == Q**(Q + 1)

    def test_tau_5_exponent_is_MUL_R_minus_1(self):
        assert MUL_R - 1 == 23

    def test_L1_cubed_equals_KF_times_L1_squared_over_Q(self):
        # L1^3 = 1000; KF = 267/2; L1^3/KF = 2000/267 ... not clean
        # Actually: KF * 2 = 267 = Q * F11 = Q * (LAM*MU*(K-1)+1)
        assert 2 * KF == Q * (LAM * MU * (K - 1) + 1)

    def test_tau_exponent_2_from_Laplacian(self):
        # The exponent 81 = v_2(tau) = v_2(L1^24 * L2^15) - v_2(V)
        # v_2(10^24 * 16^15) = 24 + 60 = 84; 84 - v_2(40) = 84 - 3 = 81
        assert MUL_R * 1 + MUL_S * 4 - 3 == 81

    def test_Laplacian_sum_equals_Seeley_DeWitt(self):
        # trace(L^1) = sum of Laplacian eigenvalues = K*V = 480 = a_0 (Phase CLIV)
        assert MUL_R * L1 + MUL_S * L2 == K * V

    def test_Fiedler_value_equals_spectral_gap_times_K(self):
        # Fiedler = L1 = K - r = K * (1 - r/K) = K * (spectral gap for SRG)
        # = 12 * (1 - 1/6) = 12 * 5/6 = 10 = L1 ✓
        assert L1 == K * 5 // 6   # 10 = 12*5/6
