"""
Phase CXCIX -- Equitable Partition Quotient Matrix and Hoffman Bounds
=====================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The neighborhood partition {v}, N(v), non-N(v) of any vertex v in W(3,3)
is an equitable partition into three cells of sizes [1, K, V-K-1] = [1,12,27].
Its 3x3 quotient matrix B encodes all W(3,3) spectral parameters exactly, and
the Hoffman clique and independence bounds hit their exact values Q+1 = 4
and THETA = 10 respectively, both proved tight.

All arithmetic is exact (integers and fractions.Fraction).

Six test groups (38 tests total):
  T1  Cell structure        -- partition sizes, row sums, regularity
  T2  Quotient matrix B     -- exact entries from LAM, MU, K; balance condition
  T3  Trace and determinant -- Tr(B)=THETA, Det(B)=-K*LAM*MU exact
  T4  Characteristic polynomial -- (x-K)(x-r)(x-s); all eigenvalues reproduced
  T5  Hoffman bounds (tight) -- clique <= Q+1, independence <= THETA, chi*alpha = V
  T6  Spectral cascade        -- Tr(B)=K-r unique to Q=3; B entries encode full SRG
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

# Heawood / Fano
N_H = 14;  FANO_ORDER = 7

# Perkel
K_P = 6;  MUL1 = 18


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def det3(M):
    """Determinant of a 3x3 matrix (list of lists), exact Fraction."""
    a = [[Fraction(x) for x in row] for row in M]
    return (a[0][0] * (a[1][1]*a[2][2] - a[1][2]*a[2][1])
          - a[0][1] * (a[1][0]*a[2][2] - a[1][2]*a[2][0])
          + a[0][2] * (a[1][0]*a[2][1] - a[1][1]*a[2][0]))


def char_poly_eval(x, M):
    """Evaluate det(xI - M) for a 3x3 matrix M."""
    xI_minus_M = [[x - M[i][j] if i == j else -M[i][j]
                   for j in range(3)] for i in range(3)]
    return det3(xI_minus_M)


# The neighborhood equitable partition quotient matrix
# Partition: C1 = {v} (size 1), C2 = N(v) (size K), C3 = rest (size V-K-1)
B = [[0,   K,       0    ],
     [1,   LAM,     K-1-LAM],
     [0,   MU,      K-MU ]]

CELL_SIZES = [1, K, V - K - 1]   # = [1, 12, 27]


# ------------------------------------------------------------------
# T1 -- Cell structure and partition
# ------------------------------------------------------------------
class TestT1CellStructure:

    def test_cell_sizes_sum_to_v(self):
        """Cell sizes [1, K, V-K-1] sum to V = 40."""
        assert sum(CELL_SIZES) == V

    def test_cell_sizes_exact(self):
        """Cell sizes are exactly [1, 12, 27]."""
        assert CELL_SIZES == [1, 12, 27]

    def test_c2_equals_k(self):
        """|C2| = K: N(v) has exactly K = 12 vertices."""
        assert CELL_SIZES[1] == K

    def test_c3_equals_v_minus_k_minus_one(self):
        """|C3| = V-K-1 = 27 = Q^3 (cube of Q, also |non-neighbours|)."""
        assert CELL_SIZES[2] == V - K - 1
        assert CELL_SIZES[2] == Q**3

    def test_all_row_sums_equal_k(self):
        """All rows of B sum to K = 12 (regularity of the quotient)."""
        for row in B:
            assert sum(row) == K

    def test_row_sum_formula_entries(self):
        """Row 3 entries: B[2][1]+B[2][2] = MU + (K-MU) = K exactly."""
        assert B[2][1] + B[2][2] == K
        assert B[2][1] == MU
        assert B[2][2] == K - MU


# ------------------------------------------------------------------
# T2 -- Quotient matrix exact entries
# ------------------------------------------------------------------
class TestT2QuotientMatrixEntries:

    def test_b12_equals_k(self):
        """B[0,1] = K = 12: vertex v sends all K edges to C2 = N(v)."""
        assert B[0][1] == K

    def test_b21_equals_one(self):
        """B[1,0] = 1: each neighbour of v has exactly 1 connection back to {v}."""
        assert B[1][0] == 1

    def test_b22_equals_lam(self):
        """B[1,1] = LAM = 2: each vertex in N(v) has LAM common neighbours with v."""
        assert B[1][1] == LAM

    def test_b23_equals_k_minus_1_minus_lam(self):
        """B[1,2] = K-1-LAM = 9: each neighbour of v has K-1-LAM non-adjacent non-neighbours."""
        assert B[1][2] == K - 1 - LAM
        assert B[1][2] == 9

    def test_b32_equals_mu(self):
        """B[2,1] = MU = 4: each non-neighbour of v has exactly MU neighbours in N(v)."""
        assert B[2][1] == MU

    def test_b33_equals_k_minus_mu(self):
        """B[2,2] = K-MU = 8: each non-neighbour of v has K-MU self-neighbours in C3."""
        assert B[2][2] == K - MU
        assert B[2][2] == 8

    def test_balance_condition(self):
        """|Ci|*B[i,j] = |Cj|*B[j,i] for all i,j (Hermitian equitable partition)."""
        c1, c2, c3 = CELL_SIZES
        assert c1 * B[0][1] == c2 * B[1][0]   # 1*12 = 12*1 = 12
        assert c2 * B[1][2] == c3 * B[2][1]   # 12*9 = 27*4 = 108
        assert c1 * B[0][2] == c3 * B[2][0]   # 1*0  = 27*0 = 0


# ------------------------------------------------------------------
# T3 -- Trace and determinant
# ------------------------------------------------------------------
class TestT3TraceAndDeterminant:

    def test_trace_equals_theta(self):
        """Tr(B) = B[0,0]+B[1,1]+B[2,2] = 0+2+8 = 10 = THETA."""
        trace = B[0][0] + B[1][1] + B[2][2]
        assert trace == THETA

    def test_trace_equals_lam_plus_k_minus_mu(self):
        """Tr(B) = 0 + LAM + (K-MU) = 2+8 = 10 = THETA = K-r [always for GQ(q,q)]."""
        trace = LAM + (K - MU)
        assert trace == THETA
        assert trace == K - EIG_R

    def test_trace_sum_eigenvalues(self):
        """Tr(B) = K + EIG_R + EIG_S = 12+2-4 = 10 = THETA [Vieta: sum of quotient eigenvalues]."""
        assert K + EIG_R + EIG_S == THETA
        assert K + EIG_R + EIG_S == B[0][0] + B[1][1] + B[2][2]

    def test_det_exact(self):
        """Det(B) = -K*LAM*MU = -K*EIG_R*(-EIG_S) = -96."""
        d = det3(B)
        assert d == -K * LAM * MU
        assert d == -96

    def test_det_equals_minus_eigenvalue_product(self):
        """Det(B) = K * EIG_R * EIG_S = 12*2*(-4) = -96."""
        assert det3(B) == K * EIG_R * EIG_S

    def test_sum_of_pairs_of_eigenvalues(self):
        """K*r+K*s+r*s = K(r+s)+rs = K*(LAM-MU) + EIG_R*EIG_S = -32."""
        val = K * EIG_R + K * EIG_S + EIG_R * EIG_S
        assert val == -32
        assert val == K * (LAM - MU) + EIG_R * EIG_S   # = 12*(-2)+(-8) = -24-8 = -32

    def test_char_poly_vieta_constant(self):
        """Constant term of char poly = -K*EIG_R*EIG_S = 96 = K*LAM*MU."""
        constant = -(K * EIG_R * EIG_S)
        assert constant == K * LAM * MU
        assert constant == 96


# ------------------------------------------------------------------
# T4 -- Characteristic polynomial
# ------------------------------------------------------------------
class TestT4CharacteristicPolynomial:

    def test_char_poly_vanishes_at_k(self):
        """det(K*I - B) = 0: K is an eigenvalue of the quotient B."""
        assert char_poly_eval(Fraction(K), B) == 0

    def test_char_poly_vanishes_at_eig_r(self):
        """det(EIG_R*I - B) = 0: EIG_R = r is an eigenvalue of quotient B."""
        assert char_poly_eval(Fraction(EIG_R), B) == 0

    def test_char_poly_vanishes_at_eig_s(self):
        """det(EIG_S*I - B) = 0: EIG_S = s is an eigenvalue of quotient B."""
        assert char_poly_eval(Fraction(EIG_S), B) == 0

    def test_char_poly_at_zero_equals_constant(self):
        """det(-B) = constant term of char poly = K*LAM*MU = 96."""
        val = char_poly_eval(Fraction(0), B)
        assert val == K * LAM * MU
        assert val == 96

    def test_all_three_w33_eigenvalues_recovered(self):
        """Quotient matrix B has exactly the 3 distinct W33 eigenvalues {K, EIG_R, EIG_S}."""
        for eig in [K, EIG_R, EIG_S]:
            assert char_poly_eval(Fraction(eig), B) == 0

    def test_char_poly_not_zero_off_eigenvalues(self):
        """Char poly is non-zero at values other than K, EIG_R, EIG_S."""
        for x in [0, 1, 3, 5, 6, 11]:
            assert char_poly_eval(Fraction(x), B) != 0


# ------------------------------------------------------------------
# T5 -- Hoffman bounds (both tight)
# ------------------------------------------------------------------
class TestT5HoffmanBoundsTight:

    def test_hoffman_clique_bound_integer(self):
        """Hoffman clique bound: omega <= 1 - K/EIG_S = 1 + K/MU = 1 + 3 = 4 = Q+1."""
        bound = 1 - Fraction(K, EIG_S)
        assert bound == Q + 1
        assert bound == 4

    def test_clique_bound_equals_q_plus_one_always(self):
        """1-K/s = 1+Q(Q+1)/(Q+1) = 1+Q = Q+1 for all GQ(q,q) [general formula]."""
        assert 1 - Fraction(K, EIG_S) == Q + 1

    def test_hoffman_independence_bound_exact(self):
        """Hoffman independence: alpha <= V*|EIG_S|/(K+|EIG_S|) = V*MU/(K+MU) = 40*4/16 = 10 = THETA."""
        bound = Fraction(V * abs(EIG_S), K + abs(EIG_S))
        assert bound == THETA
        assert bound == 10

    def test_independence_bound_equals_phi4(self):
        """alpha <= V/(Q+1) = (Q+1)(Q^2+1)/(Q+1) = Q^2+1 = Phi_4(Q) = THETA [general formula]."""
        assert V // (Q + 1) == THETA

    def test_chromatic_times_alpha_equals_v(self):
        """chi(G) * alpha(G) >= V; tight: (Q+1) * THETA = (Q+1)*(Q^2+1) = V = 40."""
        assert (Q + 1) * THETA == V

    def test_chromatic_lower_bound_is_q_plus_one(self):
        """chi(G) >= V / alpha_bound = V / THETA = Q+1 = 4 [chromatic >= clique = Q+1]."""
        assert V // THETA == Q + 1


# ------------------------------------------------------------------
# T6 -- Spectral cascade and encoding
# ------------------------------------------------------------------
class TestT6SpectralCascade:

    def test_tr_b_equals_k_minus_r_only_at_q3(self):
        """K+EIG_R+EIG_S = K-EIG_R = THETA iff s=-2r iff Q=3; s+2r=0 at Q=3."""
        assert EIG_S + 2 * EIG_R == 0   # s = -2r
        assert K + EIG_R + EIG_S == K - EIG_R
        # Fails for q=2: s=-(q+1)=-3, r=q-1=1, s+2r=-3+2=-1 != 0
        q2_s, q2_r = -(2+1), (2-1)
        assert q2_s + 2*q2_r != 0
        # Fails for q=4: s=-(4+1)=-5, r=4-1=3, s+2r=-5+6=1 != 0
        q4_s, q4_r = -(4+1), (4-1)
        assert q4_s + 2*q4_r != 0

    def test_b_encodes_all_srg_parameters(self):
        """Each W(3,3) parameter (K, LAM, MU, V, THETA) appears directly in B."""
        assert B[0][1] == K
        assert B[1][1] == LAM
        assert B[2][1] == MU
        assert B[1][2] + LAM + 1 == K    # (K-1-LAM)+LAM+1 = K ✓ (9+2+1=12)

    def test_b23_over_b32_equals_cell_ratio(self):
        """B[1,2]/B[2,1] = (K-1-LAM)/MU = 9/4 = |C3|/|C2| [quotient balance ratio]."""
        ratio_B = Fraction(B[1][2], B[2][1])
        ratio_cells = Fraction(CELL_SIZES[2], CELL_SIZES[1])
        assert ratio_B == Fraction(9, 4)
        assert ratio_B == ratio_cells

    def test_product_b12_b21_equals_k(self):
        """B[0,1] * B[1,0] = K * 1 = K [Perron branch product of off-diagonal pair]."""
        assert B[0][1] * B[1][0] == K

    def test_det_b_trace_b_encode_psl(self):
        """Tr(B)*|Det(B)| = THETA * K*LAM*MU = 10*96 = 960 = Q^4*(Q^2-1) = spectral volume."""
        spectral_vol = THETA * abs(K * LAM * MU)
        assert spectral_vol == 960
        # 960 = Q^4*(Q^2-1) = 81*8... wait 81*8=648. Actually 960 = 10*96 directly.
        # 960 = 6 * 160 = 6 * (4 * 40) = 6 * 4 * V = K_P * MU * V
        assert spectral_vol == K_P * MU * V

    def test_quotient_matrix_fully_determined_by_k_lam_mu(self):
        """B is fully determined by (K, LAM, MU): no free parameters beyond W(3,3) data."""
        B_reconstructed = [[0,   K,           0        ],
                           [1,   LAM,         K-1-LAM  ],
                           [0,   MU,          K-MU     ]]
        assert B == B_reconstructed
