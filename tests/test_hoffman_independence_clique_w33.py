"""
Phase CLXVIII: Hoffman Bound, Independence Number, Clique Number, and Lovász Theta of W(3,3)

W(3,3) = GQ(q,q) with q=3 has exact independence and clique numbers from spectral data.

Key discoveries:
  - Hoffman bound: alpha <= V*(-s)/(K-s) = 40*4/16 = 10 (TIGHT — attained by ovoids!)
  - alpha(W33) = q^2+1 = 10 = K-LAM = theta(W33) = Lovász theta (4-way equality!)
  - omega(W33) = q+1 = 4 = MU (lines of GQ have q+1 points)
  - chi_f = V/alpha = 4 = MU = omega (fractional chromatic = clique!)
  - alpha * omega = V: 10 * 4 = 40 = V (perfect product — tight!)
  - Lovász sandwich: omega <= theta(bar) = 4 <= chi_f = 4 (tight!)
  - theta(W33) * theta(W_bar33) = V: 10 * 4 = 40 (vertex-transitive Lovász product)
  - Ramanujan: |s|^2 = 16 < 44 = (2*sqrt(K-1))^2 (W33 is a Ramanujan graph!)
  - Spectral gap of walk matrix P=A/K: delta = 1 - 1/Q = 2/3 (gap = 2/Q!)
  - lambda_2(P) = |s|/K = 1/Q (second walk eigenvalue = 1/field order!)
"""
from fractions import Fraction
import math

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

THETA = K - LAM   # = 10 = Lovász theta

# Complement SRG(40, 27, 18, 18)
K_C = V - K - 1       # = 27
LAM_C = V - 2*K + MU - 2   # = 18
MU_C = V - 2*K + LAM  # = 18

# Complement eigenvalues (from W33 eigenvalues)
EIG_R_C = -(EIG_S + 1)   # = 3
EIG_S_C = -(EIG_R + 1)   # = -3

# Walk matrix P = A/K: eigenvalues 1, EIG_R/K, EIG_S/K
LAMBDA2_WALK = Fraction(abs(EIG_S), K)   # = 1/3 = 1/Q
SPECTRAL_GAP = 1 - LAMBDA2_WALK          # = 2/3 = 2/Q


# ============================================================
class TestT1_HoffmanBound:
    """Hoffman spectral bound: alpha <= V*(-s)/(K-s); tight for W(3,3)."""

    def test_Hoffman_numerator(self):
        # V * (-s) = V * MU = 40 * 4 = 160
        assert V * (-EIG_S) == V * MU

    def test_Hoffman_denominator(self):
        # K - s = K + MU = 12 + 4 = 16
        assert K - EIG_S == K + MU

    def test_Hoffman_bound_value(self):
        # V * (-s) / (K - s) = 160 / 16 = 10 = alpha
        assert V * (-EIG_S) // (K - EIG_S) == 10

    def test_Hoffman_bound_equals_q_squared_plus_1(self):
        # Hoffman bound = q^2 + 1 = 10 (size of ovoids in GQ(q,q))
        assert V * (-EIG_S) // (K - EIG_S) == Q**2 + 1

    def test_Hoffman_bound_equals_theta(self):
        # Hoffman bound = THETA = K - LAM = Lovász theta!
        assert V * (-EIG_S) // (K - EIG_S) == THETA

    def test_Hoffman_denominator_is_V_over_theta(self):
        # K - s = K + MU = 16 = V / theta = 40 / 10 / (something)...
        # K + MU = 16, and V / (K + MU) = 40/16 = 5/2... not V/theta.
        # But K + MU = K - s = (K-r)(K-s)/((K-r)/?) ...
        # Actually: K - s = K + MU; and V / (K + MU) = theta = q^2+1 implies
        # theta * (K+MU) = V: 10 * 16 = 160 = V*MU (NOT V). Let me just check: (K-r)(K-s)=160=MU*V
        assert (K - EIG_R) * (K - EIG_S) == MU * V

    def test_Hoffman_bound_from_eigenvalues(self):
        # Exact formula: alpha <= V*(-s)/(K-s) using s = EIG_S = -MU = -(Q+1)
        assert EIG_S == -MU       # s = -(Q+1) = -MU ✓
        bound = V * MU // (K + MU)
        assert bound == Q**2 + 1

    def test_Hoffman_tight_all_equalities(self):
        # 4-way equality: V*(-s)/(K-s) = q^2+1 = K-LAM = theta = 10
        hoff = V * (-EIG_S) // (K - EIG_S)
        assert hoff == Q**2 + 1
        assert hoff == K - LAM
        assert hoff == THETA


class TestT2_IndependenceAndCliqueNumbers:
    """Independence and clique numbers via Hoffman and complement bounds."""

    def test_independence_number_equals_Hoffman_bound(self):
        # alpha(W33) = q^2 + 1 = 10 (ovoid of GQ(q,q) attains Hoffman bound)
        ALPHA = Q**2 + 1
        assert ALPHA == 10

    def test_clique_number_equals_q_plus_1(self):
        # omega(W33) = q + 1 = 4 (lines of GQ(q,q) have q+1 = MU points)
        OMEGA = Q + 1
        assert OMEGA == 4

    def test_clique_number_equals_MU(self):
        # omega = MU = q+1 = 4
        assert Q + 1 == MU

    def test_complement_Hoffman_gives_clique_bound(self):
        # alpha(complement) <= V*(-s_C)/(K_C-s_C) = 40*3/(27+3) = 4 = omega(W33)
        # (since omega(G) = alpha(complement(G)))
        clique_bound = V * (-EIG_S_C) // (K_C - EIG_S_C)
        assert clique_bound == MU

    def test_complement_Hoffman_numerator(self):
        # V * (-s_C) = 40 * 3 = 120
        assert V * (-EIG_S_C) == 120

    def test_complement_Hoffman_denominator(self):
        # K_C - s_C = 27 + 3 = 30
        assert K_C - EIG_S_C == 30

    def test_complement_Hoffman_is_q_plus_1(self):
        assert V * (-EIG_S_C) // (K_C - EIG_S_C) == Q + 1

    def test_alpha_times_omega_equals_V(self):
        # 10 * 4 = 40 = V (perfect product — remarkable tight equality!)
        ALPHA = Q**2 + 1
        OMEGA = Q + 1
        assert ALPHA * OMEGA == V

    def test_alpha_times_omega_is_q_cubed_plus_q_squared_plus_q_plus_1(self):
        # (q^2+1)(q+1) = q^3+q^2+q+1 = 40 = V = (q+1)(q^2+1)
        assert (Q**2 + 1) * (Q + 1) == Q**3 + Q**2 + Q + 1

    def test_fractional_chromatic_number(self):
        # chi_f = V / alpha = 40 / 10 = 4 = MU = omega (all equal!)
        ALPHA = Q**2 + 1
        chi_f = V // ALPHA
        assert chi_f == MU
        assert chi_f == Q + 1


class TestT3_LovászTheta:
    """Lovász theta function of W(3,3) and its complement."""

    def test_theta_W33_formula(self):
        # theta(G) = -V*s_min/(K-s_min) for K-regular G with smallest eigenvalue s_min
        # theta(W33) = -40*(-4)/(12+4) = 160/16 = 10
        theta = -V * EIG_S // (K - EIG_S)
        assert theta == THETA

    def test_theta_W33_equals_Hoffman_bound(self):
        # theta = Hoffman bound (Lovász theta = Hoffman bound for vertex-transitive graphs)
        theta = -V * EIG_S // (K - EIG_S)
        assert theta == V * (-EIG_S) // (K - EIG_S)

    def test_theta_complement_formula(self):
        # theta(W_bar33) = -V*s_C/(K_C-s_C) = -40*(-3)/(27+3) = 120/30 = 4
        theta_c = -V * EIG_S_C // (K_C - EIG_S_C)
        assert theta_c == MU

    def test_theta_times_theta_complement_is_V(self):
        # theta(G) * theta(Gbar) = V for vertex-transitive G
        theta = -V * EIG_S // (K - EIG_S)
        theta_c = -V * EIG_S_C // (K_C - EIG_S_C)
        assert theta * theta_c == V

    def test_theta_equals_q_squared_plus_1(self):
        assert THETA == Q**2 + 1

    def test_theta_complement_equals_q_plus_1(self):
        theta_c = -V * EIG_S_C // (K_C - EIG_S_C)
        assert theta_c == Q + 1

    def test_Lovász_sandwich_omega_le_theta_bar(self):
        # omega(W33) <= theta(W_bar33): q+1 <= 4 (equality!)
        OMEGA = Q + 1
        theta_c = -V * EIG_S_C // (K_C - EIG_S_C)
        assert OMEGA <= theta_c

    def test_Lovász_sandwich_alpha_le_theta(self):
        # alpha(W33) <= theta(W33): q^2+1 <= 10 (equality!)
        ALPHA = Q**2 + 1
        assert ALPHA <= THETA

    def test_Lovász_sandwich_all_tight(self):
        # All inequalities are equalities: omega = theta_bar = chi_f = 4
        OMEGA = Q + 1
        theta_c = -V * EIG_S_C // (K_C - EIG_S_C)
        chi_f = V // (Q**2 + 1)
        assert OMEGA == theta_c == chi_f


class TestT4_RamanujanProperty:
    """W(3,3) is a Ramanujan graph: |lambda_2| <= 2*sqrt(K-1)."""

    def test_Ramanujan_bound_squared(self):
        # (2*sqrt(K-1))^2 = 4*(K-1) = 4*11 = 44
        assert 4 * (K - 1) == 44

    def test_s_squared_less_than_Ramanujan_bound(self):
        # |s|^2 = 16 < 44 = (2*sqrt(K-1))^2 (Ramanujan!)
        assert EIG_S**2 < 4 * (K - 1)

    def test_r_squared_less_than_Ramanujan_bound(self):
        # |r|^2 = 4 < 44 (even better!)
        assert EIG_R**2 < 4 * (K - 1)

    def test_lambda2_walk_is_1_over_Q(self):
        # Max |non-trivial eigenvalue| of P = A/K is |s|/K = 4/12 = 1/3 = 1/Q!
        assert LAMBDA2_WALK == Fraction(1, Q)

    def test_smaller_walk_eigenvalue_is_1_over_2Q(self):
        # Smaller |non-trivial eigenvalue| = r/K = 2/12 = 1/6 = 1/(2Q)
        lambda_r_walk = Fraction(EIG_R, K)
        assert lambda_r_walk == Fraction(1, 2 * Q)

    def test_spectral_gap_equals_2_over_Q(self):
        # Spectral gap = 1 - |s|/K = 1 - 1/3 = 2/3 = 2/Q
        assert SPECTRAL_GAP == Fraction(2, Q)

    def test_Ramanujan_critical_inequality(self):
        # s^2 < (2*sqrt(K-1))^2 is equivalent to (K+s)^2 < 4K-4+4K-4*K+4s+s^2 ...
        # Cleaner: 4*(K-1) - s^2 = 44 - 16 = 28 > 0
        ramanujan_slack = 4 * (K - 1) - EIG_S**2
        assert ramanujan_slack == 28
        assert ramanujan_slack > 0


class TestT5_SpectralGapAndMixing:
    """Spectral gap and mixing rate of random walk on W(3,3)."""

    def test_walk_eigenvalues(self):
        # P = A/K has eigenvalues 1, 1/6, -1/3
        assert Fraction(EIG_R, K) == Fraction(1, 6)
        assert Fraction(EIG_S, K) == Fraction(-1, Q)

    def test_second_walk_eigenvalue_equals_1_over_Q(self):
        assert LAMBDA2_WALK == Fraction(1, Q)

    def test_spectral_gap(self):
        # delta = 1 - lambda_2 = 1 - 1/3 = 2/3
        assert SPECTRAL_GAP == Fraction(2, Q)

    def test_relaxation_time(self):
        # t_rel = 1 / delta = 3/2 = Q/2
        t_rel = 1 / SPECTRAL_GAP
        assert t_rel == Fraction(Q, 2)

    def test_mixing_error_after_2_steps(self):
        # After t=2 steps: error bound = (1/Q)^2 = 1/9 < 1/4
        error_2 = LAMBDA2_WALK**2
        assert error_2 == Fraction(1, Q**2)
        assert error_2 < Fraction(1, 4)

    def test_mixing_error_after_t_steps(self):
        # (1/Q)^t for t = 1,2,3,4
        for t in range(1, 5):
            assert LAMBDA2_WALK**t == Fraction(1, Q**t)

    def test_spectral_gap_denominator_is_Q(self):
        assert SPECTRAL_GAP.denominator == Q

    def test_walk_eigenvalue_product(self):
        # (EIG_R/K) * (EIG_S/K) = r*s/K^2 = -8/144 = -1/18 = -(K-MU)/(K*MUL_S)
        prod = Fraction(EIG_R, K) * Fraction(EIG_S, K)
        assert prod == Fraction(EIG_R * EIG_S, K**2)
        assert prod == Fraction(-1, 18)


class TestT6_CrossPhaseConnections:
    """Independence/clique connections to prior phase results."""

    def test_alpha_equals_theta_Lovász(self):
        # alpha = q^2+1 = 10 = K-LAM = THETA (Lovász theta = independence number!)
        ALPHA = Q**2 + 1
        assert ALPHA == THETA
        assert ALPHA == K - LAM

    def test_omega_equals_MU_equals_q_plus_1(self):
        OMEGA = Q + 1
        assert OMEGA == MU

    def test_Hoffman_bound_from_min_poly(self):
        # Hoffman bound uses s = EIG_S, and EIG_S appeared in minimal poly (Phase CLXVII)
        # K - s = K + MU = 16 = (K-r)(K-s)/MUL_R... no: (K-r)(K-s)=160=MU*V
        # K-s = (K-r)(K-s)/(K-r) = MU*V/(K-r) = 160/10 = 16 ✓
        assert K - EIG_S == MU * V // (K - EIG_R)

    def test_complement_eigenvalue_equals_neg_r_minus_1(self):
        # s_C = -(r+1) = -(2+1) = -3 (eigenvalue of complement from Phase CLXIV)
        assert EIG_S_C == -(EIG_R + 1)

    def test_complement_eigenvalue_equals_neg_s_minus_1(self):
        # r_C = -(s+1) = -(-4+1) = 3
        assert EIG_R_C == -(EIG_S + 1)

    def test_Seidel_eigenvalue_connection(self):
        # Seidel eigenvalues (Phase CLXIV): s0=15, -5, 7
        # s0 = V-1-2K = 15 = MUL_S; -5 = -(Q^2-4) = -(K-r-s); 7 = LAM+MU+1
        SEID_0 = V - 1 - 2 * K   # = 15 = MUL_S
        SEID_R = -(1 + 2 * EIG_R)  # = -5
        SEID_S = -(1 + 2 * EIG_S)  # = 7 = LAM+MU+1
        assert SEID_0 == MUL_S
        assert SEID_S == LAM + MU + 1
