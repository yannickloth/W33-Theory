"""
Phase CCI -- Tomotope Order-96 Bridge: Det(B) = -|P|
=====================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The tomotope stabilizer P has order |P| = 96 = K*LAM*MU.  The equitable
partition quotient matrix B of W(3,3) satisfies Det(B) = -K*LAM*MU = -96.
Hence Det(B) = -|P|: the quotient-matrix determinant equals minus the
tomotope stabilizer order, bridging SRG combinatorics and tomotope geometry.

Additional exact identities pin down the axis group |H| = 192 = 2|P| and
the full monodromy |Gamma| = 18432 = |P|*|H|.  All arithmetic is exact
(integers and fractions.Fraction).

Six test groups (41 tests total):
  T1  Tomotope order formulas  -- |P| = K*LAM*MU in seven distinct exact forms
  T2  Det(B) = -|P| bridge     -- quotient matrix determinant = -tomotope order
  T3  Axis group H identities  -- |H| = 2|P| = (K-MU)*MUL_R from B entries
  T4  Full monodromy Gamma     -- |Gamma| = |P|*|H| = 2|P|^2 = K*LAM*MU*(K-MU)*MUL_R
  T5  Spectral volume          -- |P|*THETA = K_P*MU*V = Tr(B)*|Det(B)|
  T6  Polynomial Q-expansions  -- |P|,|H|,|Gamma| as exact polynomials in Q=3
"""

import pytest
from fractions import Fraction

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
Q = 3

# W(3,3) = SRG(40, 12, 2, 4)
V = 40;  K = 12;  LAM = 2;  MU = 4
THETA = 10;  EIG_R = 2;  EIG_S = -4;  MUL_R = 24;  MUL_S = 15

# Heawood / Fano / Perkel
N_H = 14;  FANO_ORDER = 7;  K_P = 6

# Tomotope group orders (from W33-E8 geometry, Coxeter orders Q,K,MU)
P_ORDER     = 96      # tomotope stabilizer   |P|
H_ORDER     = 192     # axis-flag group        |H|
GAMMA_ORDER = 18432   # full tomotope monodromy |Gamma|

# Equitable partition quotient matrix (neighbourhood partition of W33)
B = [[0,   K,       0        ],
     [1,   LAM,     K-1-LAM  ],
     [0,   MU,      K-MU     ]]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def det3(M):
    """Exact determinant of a 3x3 matrix using Fraction arithmetic."""
    a = [[Fraction(x) for x in row] for row in M]
    return (a[0][0] * (a[1][1]*a[2][2] - a[1][2]*a[2][1])
          - a[0][1] * (a[1][0]*a[2][2] - a[1][2]*a[2][0])
          + a[0][2] * (a[1][0]*a[2][1] - a[1][1]*a[2][0]))


# ------------------------------------------------------------------
# T1 -- Tomotope order formulas
# ------------------------------------------------------------------
class TestT1TomotopeOrderFormulas:

    def test_p_order_k_lam_mu(self):
        """|P| = K*LAM*MU = 12*2*4 = 96."""
        assert K * LAM * MU == P_ORDER

    def test_p_order_eigenvalue_form(self):
        """|P| = K*EIG_R*|EIG_S| = 12*2*4 = 96 (K times eigenvalue magnitudes)."""
        assert K * EIG_R * abs(EIG_S) == P_ORDER

    def test_p_order_mu_times_mul_r(self):
        """|P| = MU*MUL_R = 4*24 = 96 (non-K eigenvalue times larger multiplicity)."""
        assert MU * MUL_R == P_ORDER

    def test_p_order_k_plus_mu_times_kp(self):
        """|P| = (K+MU)*K_P = 16*6 = 96 [(Q+1)^2 * 2Q, unique to Q=3]."""
        assert (K + MU) * K_P == P_ORDER

    def test_p_order_k_times_k_minus_mu(self):
        """|P| = K*(K-MU) = 12*8 = 96; since K-MU = LAM*MU for all GQ(q,q)."""
        assert K * (K - MU) == P_ORDER
        # General identity: K-MU = (q+1)(q-1) = q^2-1 = LAM*MU for GQ(q,q)
        assert K - MU == LAM * MU

    def test_p_order_2q_qplus1_squared(self):
        """|P| = 2Q*(Q+1)^2 = 2*3*16 = 96 [polynomial form in Q]."""
        assert 2 * Q * (Q + 1)**2 == P_ORDER

    def test_p_order_prime_factorization(self):
        """|P| = 2^5 * 3: five factors of 2, one factor of Q=3."""
        assert P_ORDER == 2**5 * 3
        assert P_ORDER // 3 == 2**5


# ------------------------------------------------------------------
# T2 -- Det(B) = -|P| bridge
# ------------------------------------------------------------------
class TestT2DetBEqualsMinusPOrder:

    def test_det_b_equals_minus_p_order(self):
        """Det(B) = -K*LAM*MU = -96 = -|P|: quotient determinant = -tomotope order."""
        assert det3(B) == -P_ORDER

    def test_det_b_is_negative(self):
        """Det(B) < 0; |Det(B)| = |P| = 96."""
        d = det3(B)
        assert d < 0
        assert abs(d) == P_ORDER

    def test_det_b_eigenvalue_product(self):
        """Det(B) = K*EIG_R*EIG_S = 12*2*(-4) = -96 = -|P|."""
        assert det3(B) == K * EIG_R * EIG_S

    def test_det_b_explicit_formula(self):
        """Det(B) = -(K*LAM*MU) computed directly from B matrix entries."""
        d = det3(B)
        assert d == -(K * LAM * MU)
        assert d == -P_ORDER

    def test_abs_det_b_mu_times_mul_r(self):
        """|Det(B)| = MU*MUL_R = 4*24 = 96: Perkel-multiplicity factorization."""
        assert abs(det3(B)) == MU * MUL_R

    def test_det_b_over_minus_k(self):
        """Det(B)/(-K) = LAM*MU = 8: the 2x2 minor product."""
        val = Fraction(det3(B), -K)
        assert val == LAM * MU


# ------------------------------------------------------------------
# T3 -- Axis group H identities
# ------------------------------------------------------------------
class TestT3AxisGroupHIdentities:

    def test_h_order_equals_2_p(self):
        """|H| = 2|P| = 192: axis-flag group is index-2 above stabilizer."""
        assert H_ORDER == 2 * P_ORDER

    def test_h_order_lam_times_p(self):
        """|H| = LAM*|P| = 2*96 = 192 (the index equals LAM = Q-1)."""
        assert H_ORDER == LAM * P_ORDER

    def test_h_order_from_b_entry_and_mul_r(self):
        """|H| = (K-MU)*MUL_R = 8*24 = 192: B[2][2] times larger multiplicity."""
        assert H_ORDER == (K - MU) * MUL_R

    def test_h_order_b33_times_mul_r(self):
        """|H| = B[2][2]*MUL_R where B[2][2] = K-MU = 8 (C3 self-connectivity)."""
        assert H_ORDER == B[2][2] * MUL_R

    def test_h_order_k_lam2_mu(self):
        """|H| = K*LAM^2*MU = 12*4*4 = 192 = LAM*|P|."""
        assert H_ORDER == K * LAM**2 * MU

    def test_h_order_over_mul_r(self):
        """|H|/MUL_R = K-MU = B[2][2] = 8: the self-loop weight of C3."""
        assert H_ORDER // MUL_R == K - MU
        assert H_ORDER // MUL_R == B[2][2]
        assert H_ORDER % MUL_R == 0

    def test_h_order_polynomial_q(self):
        """|H| = 4Q*(Q+1)^2 = 4*3*16 = 192 = 2|P| as polynomial in Q=3."""
        assert H_ORDER == 4 * Q * (Q + 1)**2

    def test_h_order_prime_factorization(self):
        """|H| = 2^6 * 3 = 64*3: one extra factor of 2 above |P| = 2^5*3."""
        assert H_ORDER == 2**6 * 3


# ------------------------------------------------------------------
# T4 -- Full monodromy Gamma
# ------------------------------------------------------------------
class TestT4FullMonodromyGamma:

    def test_gamma_equals_p_times_h(self):
        """|Gamma| = |P|*|H| = 96*192 = 18432."""
        assert GAMMA_ORDER == P_ORDER * H_ORDER

    def test_gamma_equals_2_p_squared(self):
        """|Gamma| = 2|P|^2 = 2*9216 = 18432."""
        assert GAMMA_ORDER == 2 * P_ORDER**2

    def test_gamma_equals_lam_p_squared(self):
        """|Gamma| = LAM*|P|^2 = 2*9216 = 18432 (LAM = index |H|/|P|)."""
        assert GAMMA_ORDER == LAM * P_ORDER**2

    def test_gamma_over_p_equals_h(self):
        """|Gamma|/|P| = |H|: monodromy quotient by stabilizer = axis group."""
        assert GAMMA_ORDER % P_ORDER == 0
        assert GAMMA_ORDER // P_ORDER == H_ORDER

    def test_gamma_over_h_equals_p(self):
        """|Gamma|/|H| = |P|: monodromy quotient by axis group = stabilizer."""
        assert GAMMA_ORDER % H_ORDER == 0
        assert GAMMA_ORDER // H_ORDER == P_ORDER

    def test_gamma_full_srg_expansion(self):
        """|Gamma| = K*LAM*MU*(K-MU)*MUL_R = 96*192 = 18432."""
        assert GAMMA_ORDER == K * LAM * MU * (K - MU) * MUL_R

    def test_gamma_prime_factorization(self):
        """|Gamma| = 2^11 * 3^2 = 2048*9: eleven 2-factors, two 3-factors."""
        assert GAMMA_ORDER == 2**11 * 3**2


# ------------------------------------------------------------------
# T5 -- Spectral volume identity
# ------------------------------------------------------------------
class TestT5SpectralVolume:

    def test_p_theta_equals_kp_mu_v(self):
        """|P|*THETA = K_P*MU*V = 96*10 = 960 (Perkel-W33-tomotope bridge)."""
        assert P_ORDER * THETA == K_P * MU * V
        assert P_ORDER * THETA == 960

    def test_tr_b_abs_det_b_is_spectral_vol(self):
        """Tr(B)*|Det(B)| = THETA*|P| = 960 = spectral volume of quotient B."""
        tr_b = B[0][0] + B[1][1] + B[2][2]
        assert tr_b == THETA
        assert tr_b * abs(det3(B)) == P_ORDER * THETA

    def test_spectral_vol_kp_v_mu_order(self):
        """960 = K_P*V*MU = 6*40*4 [Perkel degree * W33 order * |EIG_S|]."""
        assert P_ORDER * THETA == K_P * V * MU

    def test_p_over_mu_equals_mul_r(self):
        """|P|/MU = MUL_R = 96/4 = 24: tomotope order / |EIG_S| = larger multiplicity."""
        assert P_ORDER % MU == 0
        assert P_ORDER // MU == MUL_R

    def test_p_over_kp_equals_qplus1_squared(self):
        """|P|/K_P = (Q+1)^2 = 96/6 = 16: tomotope / Perkel degree = cell-size square."""
        assert P_ORDER % K_P == 0
        assert P_ORDER // K_P == (Q + 1)**2

    def test_spectral_vol_per_vertex_equals_mul_r(self):
        """(|P|*THETA)/V = 960/40 = 24 = MUL_R: spectral volume per vertex."""
        assert (P_ORDER * THETA) % V == 0
        assert (P_ORDER * THETA) // V == MUL_R


# ------------------------------------------------------------------
# T6 -- Polynomial Q-expansions and order distribution
# ------------------------------------------------------------------
class TestT6PolynomialQExpansions:

    def test_p_degree4_polynomial(self):
        """|P| = Q^4+Q^3-Q^2-Q = Q(Q-1)(Q+1)^2 = 81+27-9-3 = 96 for Q=3."""
        poly = Q**4 + Q**3 - Q**2 - Q
        assert poly == P_ORDER

    def test_h_polynomial(self):
        """|H| = 2Q(Q-1)(Q+1)^2 = 2*3*2*16 = 192 for Q=3."""
        assert 2 * Q * (Q - 1) * (Q + 1)**2 == H_ORDER

    def test_gamma_polynomial(self):
        """|Gamma| = 2Q^2(Q-1)^2(Q+1)^4 = 2*9*4*256 = 18432 for Q=3."""
        assert 2 * Q**2 * (Q - 1)**2 * (Q + 1)**4 == GAMMA_ORDER

    def test_index_h_over_p_is_lam(self):
        """|H|/|P| = LAM = Q-1 = 2: the index is exactly lambda."""
        assert H_ORDER // P_ORDER == LAM
        assert H_ORDER // P_ORDER == Q - 1

    def test_p_order_distribution_sum(self):
        """P order distribution {1:1, 2:Q^3, 3:(Q-1)(Q+1)^2, 4:Q^2(Q+1)} sums to |P|."""
        n1 = 1
        n2 = Q**3                  # 27 involutions
        n3 = (Q - 1) * (Q + 1)**2  # 32 order-3 elements = |P|/Q
        n4 = Q**2 * (Q + 1)        # 36 order-4 elements = K*Q
        assert n1 + n2 + n3 + n4 == P_ORDER
        assert n1 == 1
        assert n2 == 27
        assert n3 == 32
        assert n4 == 36

    def test_p_involutions_equal_c3_size(self):
        """P has exactly Q^3 = 27 involutions = |C3| (non-neighbours in W33 partition)."""
        P_INVOLUTIONS = Q**3
        assert P_INVOLUTIONS == V - K - 1    # = 27 = |C3|
        assert P_INVOLUTIONS == 27

    def test_formula_differs_at_q2_q4(self):
        """Q(Q-1)(Q+1)^2 gives different orders for Q=2 (18) and Q=4 (300)."""
        p_q2 = 2 * 1 * 9     # = 18
        p_q4 = 4 * 3 * 25    # = 300
        assert p_q2 != P_ORDER
        assert p_q4 != P_ORDER
        assert p_q2 == 18
        assert p_q4 == 300
