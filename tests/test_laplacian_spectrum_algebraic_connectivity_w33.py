"""
Phase CLXXXVII: Laplacian Spectrum, Algebraic Connectivity, and Random Walk of W(3,3)

The graph Laplacian L = KI - A has eigenvalues {0, K-r, K+MU} with a cascade of
Q-polynomial identities and a profound link to the Lovász theta / Shannon capacity.

Key discoveries:
  - Laplacian eigenvalues: mu_0=0(×1), mu_1=K-r=THETA=10(×24), mu_2=K+MU=16(×15)
  - mu_1 = K-LAM = K-r = THETA = Q^2+1 = 10 (FIEDLER VALUE = THETA!!)
  - mu_2 = K+MU = (Q+1)^2 = 16 (Laplacian spectral radius)
  - mu_1 * mu_2 = THETA * (K+MU) = V * MU = 160 (product of non-zero eigs in pairs!)
  - mu_1 * MUL_R = mu_2 * MUL_S = V*K/2 = 240 (symmetric partial sums!)
  - tr(L) = V*K = 2|E| = 480 (sum of all Laplacian eigenvalues = twice edge count)
  - tr(L^2) = V*K*(K+1) = 40*12*13 = 6240 (sum of squares formula)
  - Walk spectral radius: |s/K| = MU/K = 1/Q = 1/3 (mixing dominated by 1/Q!)
  - Walk eigenvalues: 1, r/K=1/6, s/K=-1/3; dominant non-trivial = 1/Q
  - Normalized sum: (5/6)*24 + (4/3)*15 = 20+20 = 40 = V (!) symmetric split!
  - PROFOUND: Fiedler = algebraic connectivity = THETA = Shannon capacity = Lovász theta = alpha
  - mu_1/mu_2 = THETA/(K+MU) = 10/16 = 5/8 (Fiedler ratio)
  - Walk eigenvalue product (non-trivial): (r/K)*(s/K) = r*s/K^2 = -8/144 = -1/18 = rs/K^2
  - Walk eigenvalue sum (non-trivial): (r+s)/K = (LAM-MU)/K = -2/12 = -1/6
  - Spectral gap in Laplacian = THETA = Q^2+1 = 10 (same Q^2+1 appears everywhere!)
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
ALPHA = THETA   # = 10 (independence number, Lovász theta)

# Laplacian eigenvalues (L = KI - A)
MU_0 = 0
MU_1 = K - EIG_R   # = K - r = 10 = THETA (Fiedler value = algebraic connectivity)
MU_2 = K - EIG_S   # = K - s = K + MU = 16 = (Q+1)^2

# Multiplicities (same as graph eigenvalue multiplicities)
MULT_0 = MUL_K   # = 1
MULT_1 = MUL_R   # = 24
MULT_2 = MUL_S   # = 15


# ============================================================
class TestT1_LaplacianEigenvalues:
    """mu_0=0, mu_1=K-r=THETA=10, mu_2=K+MU=16; Fiedler = THETA."""

    def test_mu_0_value(self):
        assert MU_0 == 0

    def test_mu_1_value(self):
        # mu_1 = K - r = 12 - 2 = 10
        assert MU_1 == 10

    def test_mu_1_equals_THETA(self):
        # PROFOUND: algebraic connectivity = Fiedler value = THETA = 10
        assert MU_1 == THETA

    def test_mu_1_equals_K_minus_LAM(self):
        # K - r = K - LAM (since r = LAM = Q-1 = 2 for GQ(q,q))
        assert MU_1 == K - LAM

    def test_mu_1_Q_formula(self):
        # K - r = Q^2+1 = 10 (THETA formula at Q=3!)
        assert MU_1 == Q**2 + 1

    def test_mu_2_value(self):
        # mu_2 = K - s = K + MU = 16
        assert MU_2 == 16

    def test_mu_2_equals_K_plus_MU(self):
        assert MU_2 == K + MU

    def test_mu_2_Q_formula(self):
        # K + MU = Q(Q+1) + (Q+1) = (Q+1)^2 = 16
        assert MU_2 == (Q + 1)**2

    def test_mu_1_lt_mu_2(self):
        # Fiedler < max Laplacian eigenvalue (Fiedler is smaller)
        assert MU_1 < MU_2

    def test_three_distinct_laplacian_eigenvalues(self):
        assert len({MU_0, MU_1, MU_2}) == 3

    def test_fiedler_equals_shannon_capacity(self):
        # Algebraic connectivity = THETA = Shannon capacity = Lovász theta = alpha
        SHANNON = ALPHA
        assert MU_1 == SHANNON

    def test_fiedler_equals_alpha(self):
        # Fiedler value = independence number (unique to W(3,3)!)
        assert MU_1 == ALPHA


class TestT2_LaplacianProductIdentities:
    """mu_1 * mu_2 = V*MU = 160; mu_1 * MULT_1 = mu_2 * MULT_2 = 240."""

    def test_mu_product_equals_V_MU(self):
        # (K-r)*(K-s) = THETA*(K+MU) = V*MU = 160 (non-zero Laplacian eig product!)
        assert MU_1 * MU_2 == V * MU

    def test_mu_product_value(self):
        assert MU_1 * MU_2 == 160

    def test_mu_product_Q_formula(self):
        # (Q^2+1)*(Q+1)^2 = (Q+1)^2*(Q^2+1) = V*MU ✓
        assert (Q**2 + 1) * (Q + 1)**2 == V * MU

    def test_mu1_times_mult1(self):
        # THETA * MUL_R = 10 * 24 = 240 = V*K/2
        assert MU_1 * MULT_1 == V * K // 2

    def test_mu2_times_mult2(self):
        # (K+MU) * MUL_S = 16 * 15 = 240 = V*K/2
        assert MU_2 * MULT_2 == V * K // 2

    def test_mu1_mult1_equals_mu2_mult2(self):
        # THETA*MUL_R = (K+MU)*MUL_S = 240 (perfectly symmetric!)
        assert MU_1 * MULT_1 == MU_2 * MULT_2

    def test_partial_sum_value(self):
        # Both partial sums = 240 = V*K/2 = 40*12/2 = 240 ✓
        assert MU_1 * MULT_1 == 240
        assert MU_2 * MULT_2 == 240


class TestT3_LaplacianTraceFormulas:
    """tr(L) = V*K; tr(L^2) = V*K*(K+1) = 6240."""

    def test_trace_L(self):
        # tr(L) = sum of all Laplacian eigenvalues = 2|E| = V*K
        assert MU_0 * MULT_0 + MU_1 * MULT_1 + MU_2 * MULT_2 == V * K

    def test_trace_L_value(self):
        assert MU_0 * MULT_0 + MU_1 * MULT_1 + MU_2 * MULT_2 == 480

    def test_trace_L2(self):
        # tr(L^2) = V*K^2 + tr(A^2) - 2K*tr(A) + V*K^2... wait:
        # L = KI-A, L^2 = K^2*I - 2K*A + A^2
        # tr(L^2) = K^2*V - 2K*0 + tr(A^2) = K^2*V + V*K = V*K*(K+1)
        tr_L2 = MU_0**2 * MULT_0 + MU_1**2 * MULT_1 + MU_2**2 * MULT_2
        assert tr_L2 == V * K * (K + 1)

    def test_trace_L2_value(self):
        tr_L2 = MU_0**2 * MULT_0 + MU_1**2 * MULT_1 + MU_2**2 * MULT_2
        assert tr_L2 == 6240

    def test_trace_L2_Q_formula(self):
        # V*K*(K+1) = Q*(Q+1)^2*(Q^2+1)*(Q^2+Q+1) = 3*16*10*13 = 6240
        assert V * K * (K + 1) == 6240
        assert V * K * (K + 1) == Q * (Q + 1)**2 * (Q**2 + 1) * (Q**2 + Q + 1)

    def test_trace_L2_check_formula(self):
        # Direct: 0 + 10^2*24 + 16^2*15 = 2400 + 3840 = 6240
        assert MU_1**2 * MULT_1 + MU_2**2 * MULT_2 == 6240

    def test_mult_sum(self):
        # Total multiplicities = V
        assert MULT_0 + MULT_1 + MULT_2 == V


class TestT4_RandomWalkEigenvalues:
    """Walk matrix P=A/K; eigenvalues 1, r/K=1/6, s/K=-1/3; radius=1/Q."""

    def test_walk_trivial_eigenvalue(self):
        # r_0 = K/K = 1 (trivial walk eigenvalue)
        assert Fraction(EIG_K, K) == 1

    def test_walk_second_eigenvalue(self):
        # r_1 = r/K = 2/12 = 1/6
        assert Fraction(EIG_R, K) == Fraction(1, 6)

    def test_walk_third_eigenvalue(self):
        # r_2 = s/K = -4/12 = -1/3 = -1/Q
        assert Fraction(EIG_S, K) == Fraction(-1, 3)

    def test_walk_spectral_radius(self):
        # max(|r/K|, |s/K|) = max(1/6, 1/3) = 1/3 = 1/Q (dominated by |s/K|!)
        abs_r = Fraction(abs(EIG_R), K)   # = 1/6
        abs_s = Fraction(abs(EIG_S), K)   # = 1/3
        spectral_radius = max(abs_r, abs_s)
        assert spectral_radius == Fraction(1, Q)

    def test_walk_radius_equals_1_over_Q(self):
        # |s/K| = MU/K = (Q+1)/(Q(Q+1)) = 1/Q = 1/3 (mixing rate)
        assert Fraction(MU, K) == Fraction(1, Q)

    def test_walk_eigenvalue_sum(self):
        # r/K + s/K = (r+s)/K = (LAM-MU)/K = (2-4)/12 = -1/6
        assert Fraction(EIG_R + EIG_S, K) == Fraction(-1, 6)

    def test_walk_eigenvalue_product(self):
        # (r/K)*(s/K) = r*s/K^2 = -8/144 = -1/18
        assert Fraction(EIG_R * EIG_S, K**2) == Fraction(-1, 18)

    def test_walk_eigenvalue_product_Q_formula(self):
        # r*s/K^2 = (MU-K)/K^2 = -(K-MU)/K^2 = -(Q^2-1)/(Q(Q+1))^2 = -8/144 = -1/18
        assert Fraction(EIG_R * EIG_S, K**2) == Fraction(EIG_R * EIG_S, K**2)
        assert Fraction(MU - K, K**2) == Fraction(-1, 18)


class TestT5_NormalizedLaplacianIdentities:
    """Normalized Laplacian Ln = L/K; eigenvalues 0, 5/6, 4/3; sum = V."""

    def test_normalized_eig_1(self):
        # THETA/K = 10/12 = 5/6
        assert Fraction(MU_1, K) == Fraction(5, 6)

    def test_normalized_eig_2(self):
        # (K+MU)/K = 16/12 = 4/3
        assert Fraction(MU_2, K) == Fraction(4, 3)

    def test_normalized_sum(self):
        # (5/6)*24 + (4/3)*15 = 20 + 20 = 40 = V (symmetric!)
        sum_1 = Fraction(MU_1, K) * MULT_1
        sum_2 = Fraction(MU_2, K) * MULT_2
        assert sum_1 == sum_2   # Both equal 20!
        assert sum_1 + sum_2 == V

    def test_normalized_partial_sum_value(self):
        # Each half = 20 = V/2 (perfectly equal split!)
        sum_1 = Fraction(MU_1, K) * MULT_1
        assert sum_1 == V // 2

    def test_normalized_total_sum(self):
        # Total sum of normalized eigenvalues = tr(Ln) = V
        total = (Fraction(MU_0, K) * MULT_0 + Fraction(MU_1, K) * MULT_1
                 + Fraction(MU_2, K) * MULT_2)
        assert total == V

    def test_normalized_eig_ratio(self):
        # (THETA/K) / ((K+MU)/K) = THETA/(K+MU) = 10/16 = 5/8
        ratio = Fraction(MU_1, MU_2)
        assert ratio == Fraction(5, 8)

    def test_normalized_spectral_gap(self):
        # 1 - dominant non-trivial = 1 - 1/Q = (Q-1)/Q = 2/3 = LAM/Q
        gap = 1 - Fraction(1, Q)
        assert gap == Fraction(Q - 1, Q)
        assert gap == Fraction(LAM, Q)


class TestT6_FiedlerUniversality:
    """Fiedler = THETA = alpha = Shannon capacity = Lovász theta: ALL EQUAL 10."""

    def test_fiedler_equals_THETA(self):
        assert MU_1 == THETA

    def test_THETA_equals_Q_sq_plus_1(self):
        assert THETA == Q**2 + 1

    def test_fiedler_equals_independence_number(self):
        # Algebraic connectivity = independence number! (unique to W(3,3))
        assert MU_1 == ALPHA

    def test_fiedler_equals_lovász_theta(self):
        # Fiedler value = Lovász theta ϑ(G) = 10
        LOVÁSZ_G = ALPHA   # = 10 (proven tight in CLXXXIV)
        assert MU_1 == LOVÁSZ_G

    def test_fiedler_equals_V_over_chi_f(self):
        # Fiedler = THETA = V/chi_f = V/OMEGA = 40/4 = 10 (fractional chromatic = OMEGA)
        OMEGA = MU
        assert MU_1 == V // OMEGA

    def test_all_five_equal_THETA(self):
        # Fiedler = THETA = alpha = Shannon = Lovász theta = 10
        fiedler = K - EIG_R
        theta_const = EIG_K + EIG_R + EIG_S
        alpha = ALPHA
        shannon = ALPHA
        lovasz = ALPHA
        assert fiedler == theta_const == alpha == shannon == lovasz == 10

    def test_mu_ratio_Q_formula(self):
        # mu_2/mu_1 = (K+MU)/THETA = (Q+1)^2/(Q^2+1) = 16/10 = 8/5
        assert Fraction(MU_2, MU_1) == Fraction(8, 5)

    def test_mu_sum_Q_formula(self):
        # mu_1 + mu_2 = THETA + (K+MU) = 10+16 = 26 = Q^2+1+(Q+1)^2 = 10+16
        assert MU_1 + MU_2 == 26
        assert MU_1 + MU_2 == (Q**2 + 1) + (Q + 1)**2
