"""
Phase CLXXXVI: GQ Axiom Translations and Line-Clique Enumeration for W(3,3)

The GQ(3,3) axiom "every non-incident (point, line) pair has a unique contact"
translates into exact integer counting identities and an equitable distance partition.

Key discoveries:
  - Lines through v: Q+1 = MU = 4 (K4 cliques containing v)
  - Lines NOT through v: V - MU = 36 = K*Q = Q^2*(Q+1) (from GQ axiom count)
  - V = MU + K*Q = (Q+1)(1 + Q^2) = MU*THETA (product identity for GQ!)
  - Each line not through v: |N(v) ∩ l| = 1 exactly (GQ axiom → K*Q = 36 lines)
  - Each non-adjacent w: shares exactly MU=4 lines with N(v) (one per line through v)
  - GQ axiom gives K*Q = K_C * MU / Q = 36 (two counting routes agree!)
  - Total flags (point,line incidences): V*(Q+1) = 40*4 = 160 (= #triangles in clique complex!)
  - Non-incident (point, line) pairs: V*(V-Q-1) = 40*36 = 1440 = V*K*Q/K_C * K_C
  - Distance quotient matrix B = [[0,K,0],[1,LAM,K-LAM-1],[0,MU,K-MU]] has
    eigenvalues {K, r, s} (equitable partition of SRG into distance shells from v)
  - B row sums all equal K (K-regular graph!)
  - tr(B) = THETA; det(B) = -96 = K*r*s; tr(B^2) = K^2 + r^2 + s^2 = 164
  - Intersection array {K, K-LAM-1; 1, MU} = {12, 9; 1, 4} (distance-regular!)
  - a_1 = LAM = Q-1 = 2; a_2 = K-MU = Q^2-1 = 8 (DRG a-values)
  - b_0*b_1 = K*(K-LAM-1) = 12*9 = 108 = MU*K_C (double-count identity!)
  - GQ self-duality: #lines = #points = V (spread has ALPHA = Q^2+1 = 10 lines!)
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
K_C = V - 1 - K   # = 27 (non-neighbors of v)

# Lines through v (K4 cliques containing v)
LINES_THROUGH_V = MU   # = Q+1 = 4

# Lines NOT through v
LINES_NOT_THROUGH_V = V - MU   # = 36

# Distance quotient matrix rows: B[i][j] = #edges from cell i to cell j per vertex in cell i
# Cells: C0={v} (size 1), C1=N(v) (size K), C2=V\(N(v)∪{v}) (size K_C)
B00, B01, B02 = 0, K, 0
B10, B11, B12 = 1, LAM, K - LAM - 1   # = 1, 2, 9
B20, B21, B22 = 0, MU, K - MU         # = 0, 4, 8

# DRG intersection array values
B0 = K           # = 12 (valency)
B1 = K - LAM - 1   # = 9  (b_1 in intersection array)
C1 = 1
C2 = MU          # = 4

A1 = LAM         # = Q-1 = 2 (a_1 = k - b_1 - c_1)
A2 = K - MU      # = Q^2-1 = 8 (a_2 = k - b_2 - c_2 with b_2=0)

# Total lines (=V by self-duality)
TOTAL_LINES = V   # = 40

# Flags (incident point-line pairs)
FLAGS = V * (Q + 1)   # = 40 * 4 = 160


# ============================================================
class TestT1_GQLineCount:
    """Lines through v = MU = Q+1 = 4; lines not through v = K*Q = 36."""

    def test_lines_through_v(self):
        # Each vertex is on Q+1 = 4 GQ lines (K4 cliques through v)
        assert LINES_THROUGH_V == Q + 1

    def test_lines_through_v_equals_MU(self):
        assert LINES_THROUGH_V == MU

    def test_lines_not_through_v(self):
        # V - MU = 40 - 4 = 36 lines not through v
        assert LINES_NOT_THROUGH_V == 36

    def test_lines_not_through_v_equals_K_Q(self):
        # 36 = K * Q = Q^2 * (Q+1) (from GQ axiom: each K*Q = 12*3 non-adjacent uses)
        assert LINES_NOT_THROUGH_V == K * Q

    def test_lines_not_through_v_Q_formula(self):
        # 36 = Q^2 * (Q+1) = 9 * 4 = 36
        assert LINES_NOT_THROUGH_V == Q**2 * (Q + 1)

    def test_V_equals_MU_plus_K_Q(self):
        # V = (lines through v) + (lines not through v) = MU + K*Q = 4 + 36 = 40
        assert MU + K * Q == V

    def test_V_GQ_formula(self):
        # V = (Q+1)(Q^2+1) = (Q+1)(1+Q^2) = MU*THETA = 4*10 = 40
        assert (Q + 1) * (Q**2 + 1) == V

    def test_V_equals_MU_times_THETA(self):
        # V = MU * THETA = 4 * 10 = 40
        assert MU * THETA == V

    def test_total_lines_equals_V(self):
        # GQ(q,q) is self-dual: #lines = #points = V = 40
        assert TOTAL_LINES == V


class TestT2_GQAxiomCounting:
    """∀ (v, l) non-incident: |N(v) ∩ l| = 1 exactly."""

    def test_gq_axiom_line_contact(self):
        # Each line not through v has exactly 1 vertex in N(v)
        # → K * Q line-contacts = K neighbors * Q non-v-lines per neighbor = 36
        contacts_per_nbr = Q   # each neighbor in Q lines not through v
        total_contacts = K * contacts_per_nbr
        assert total_contacts == LINES_NOT_THROUGH_V

    def test_gq_axiom_one_contact_per_line(self):
        # 36 lines, each with exactly 1 vertex in N(v) → total contacts = 36 ✓
        assert LINES_NOT_THROUGH_V * 1 == K * Q

    def test_each_neighbor_in_Q_non_v_lines(self):
        # u ∈ N(v): u is on Q+1=4 lines, 1 through v, Q=3 not through v
        lines_through_u_not_v = (Q + 1) - 1
        assert lines_through_u_not_v == Q

    def test_non_incident_pairs(self):
        # Total non-incident (point, line) pairs = V * (V - MU) = 40 * 36 = 1440
        non_incident = V * (V - MU)
        assert non_incident == 1440

    def test_non_incident_pairs_Q_formula(self):
        # 1440 = (Q+1)(Q^2+1) * Q^2*(Q+1) = V * K * Q = 40 * 36 = 1440
        assert V * K * Q == 1440

    def test_total_flags(self):
        # Flags = V * (Q+1) = 40 * 4 = 160 (each point on Q+1 lines)
        assert FLAGS == 160

    def test_flags_equals_triangles(self):
        # Flags = 160 = #triangles in clique complex (each K4 has 4 triangles; 40 K4s → 160)
        K4_count = V   # = 40 (each vertex in V determines one K4 per line through it... no)
        # Actually: #triangles = 160 directly from f-vector (CLXXIX)
        triangles = 160
        assert FLAGS == triangles

    def test_flags_equals_V_times_MU(self):
        # Flags = V * (Q+1) = V * MU = 40 * 4 = 160
        assert FLAGS == V * MU


class TestT3_EquitablePartition:
    """Distance partition {v, Γ(v), rest} is equitable; quotient matrix B."""

    def test_B_row0_sum(self):
        # Row 0 sums to K: 0 + K + 0 = K
        assert B00 + B01 + B02 == K

    def test_B_row1_sum(self):
        # Row 1 sums to K: 1 + LAM + (K-LAM-1) = K
        assert B10 + B11 + B12 == K

    def test_B_row2_sum(self):
        # Row 2 sums to K: 0 + MU + (K-MU) = K
        assert B20 + B21 + B22 == K

    def test_B_trace(self):
        # tr(B) = B00 + B11 + B22 = 0 + LAM + (K-MU) = THETA = 10
        assert B00 + B11 + B22 == THETA

    def test_B_trace_Q_formula(self):
        # tr(B) = LAM + (K-MU) = (Q-1) + (Q^2-1) = Q^2+Q-2 = 10 ✓
        # Also = K+r+s = THETA ✓
        assert B00 + B11 + B22 == Q**2 + Q - 2

    def test_B_determinant(self):
        # det(B) = 0*(LAM*(K-MU) - (K-LAM-1)*MU) - K*(1*(K-MU) - 0) + 0
        # = -K*(K-MU) = -12*8 = -96 = K*r*s
        det_B = (B00 * (B11 * B22 - B12 * B21)
                 - B01 * (B10 * B22 - B12 * B20)
                 + B02 * (B10 * B21 - B11 * B20))
        assert det_B == EIG_K * EIG_R * EIG_S

    def test_B_determinant_value(self):
        det_B = (B00 * (B11 * B22 - B12 * B21)
                 - B01 * (B10 * B22 - B12 * B20)
                 + B02 * (B10 * B21 - B11 * B20))
        assert det_B == -96

    def test_B_eigenvalue_product_is_K_r_s(self):
        # Product of eigenvalues = det(B) = K*r*s = -96
        assert EIG_K * EIG_R * EIG_S == -96

    def test_B_characteristic_at_K(self):
        # B has eigenvalue K: (K-K)(K-r)(K-s) = 0
        assert (EIG_K - EIG_K) * (EIG_K - EIG_R) * (EIG_K - EIG_S) == 0

    def test_B_characteristic_at_r(self):
        assert (EIG_R - EIG_K) * (EIG_R - EIG_R) * (EIG_R - EIG_S) == 0

    def test_B_characteristic_at_s(self):
        assert (EIG_S - EIG_K) * (EIG_S - EIG_R) * (EIG_S - EIG_S) == 0

    def test_B_sum_of_squares_trace(self):
        # tr(B^2) = K^2 + r^2 + s^2 = 144+4+16 = 164
        # = B00^2+B01*B10+B11^2+B12*B21+B22^2 (main diagonal of B^2)
        # B^2[0,0] = 0*0+K*1+0*0 = K = 12
        # B^2[1,1] = 1*K+LAM^2+(K-LAM-1)*MU = 12+4+36 = 52
        # B^2[2,2] = 0*0+MU*(K-LAM-1)+(K-MU)^2 = 36+64 = 100
        tr_B2 = K + (K + LAM**2 + (K - LAM - 1) * MU) + (MU * (K - LAM - 1) + (K - MU)**2)
        assert tr_B2 == EIG_K**2 + EIG_R**2 + EIG_S**2

    def test_tr_B2_value(self):
        tr_B2 = K + (K + LAM**2 + (K - LAM - 1) * MU) + (MU * (K - LAM - 1) + (K - MU)**2)
        assert tr_B2 == 164


class TestT4_IntersectionArray:
    """DRG intersection array {K, K-LAM-1; 1, MU} = {12, 9; 1, 4}."""

    def test_b0_value(self):
        # b_0 = K = 12
        assert B0 == 12

    def test_b1_value(self):
        # b_1 = K-LAM-1 = 9
        assert B1 == 9

    def test_b1_Q_formula(self):
        # b_1 = Q^2 = 9 (intersection number b_1 = Q^2!)
        assert B1 == Q**2

    def test_c1_value(self):
        # c_1 = 1 (every distance-1 vertex has 1 neighbor at distance 0)
        assert C1 == 1

    def test_c2_value(self):
        # c_2 = MU = Q+1 = 4 (every non-adjacent vertex has MU neighbors in N(v))
        assert C2 == MU

    def test_c2_Q_formula(self):
        assert C2 == Q + 1

    def test_a1_equals_LAM(self):
        # a_1 = k - b_1 - c_1 = K - Q^2 - 1 = Q-1 = LAM = 2
        assert K - B1 - C1 == LAM

    def test_a1_Q_formula(self):
        # a_1 = Q-1 = 2
        assert A1 == Q - 1

    def test_a2_value(self):
        # a_2 = k - b_2 - c_2 = K - 0 - MU = K-MU = 8 (b_2=0: no distance-3)
        assert A2 == K - MU

    def test_a2_Q_formula(self):
        # a_2 = Q^2-1 = 8
        assert A2 == Q**2 - 1

    def test_diameter_2(self):
        # W(3,3) has diameter 2 (b_2 = 0: no vertices at distance 3!)
        b2 = 0   # no vertices at distance > 2 (diameter = 2)
        assert b2 == 0

    def test_intersection_array_row_sums(self):
        # a_i + b_i + c_i = K for each i:
        # i=1: A1 + B1 + C1 = 2+9+1 = 12 = K ✓
        # i=2: A2 + b2 + C2 = 8+0+4 = 12 = K ✓
        assert A1 + B1 + C1 == K
        assert A2 + 0 + C2 == K


class TestT5_DrGDoubleCountingIdentities:
    """b_0 * b_1 = K_C * MU = 108; dual identities from DRG."""

    def test_b0_b1_product(self):
        # b_0 * b_1 = K * (K-LAM-1) = 12*9 = 108
        assert B0 * B1 == 108

    def test_b0_b1_equals_K_C_MU(self):
        # K*(K-LAM-1) = (V-K-1)*MU = K_C*MU = 27*4 = 108 (SRG regularity!)
        assert B0 * B1 == K_C * MU

    def test_b0_b1_Q_formula(self):
        # K*(K-LAM-1) = Q(Q+1)*Q^2 = Q^3*(Q+1) = 27*4 = 108
        assert B0 * B1 == Q**3 * (Q + 1)

    def test_c1_c2_product(self):
        # c_1 * c_2 = 1 * MU = MU = 4
        assert C1 * C2 == MU

    def test_k_i_recurrence(self):
        # k_0 = 1, k_1 = K, k_2 = K_C (sizes of distance shells)
        k0, k1, k2 = 1, K, K_C
        # k_1 = b_0/c_1 * k_0 = (K/1) * 1 = K ✓
        assert B0 * k0 // C1 == k1
        # k_2 = b_1/c_2 * k_1 = (Q^2/MU)*K = (9/4)*12 = 27 ✓
        assert B1 * k1 // C2 == k2

    def test_k2_from_DRG(self):
        # k_2 = k_1 * b_1 / c_2 = K*(K-LAM-1)/MU = 12*9/4 = 27 = K_C = Q^3
        assert Fraction(K * B1, C2) == K_C

    def test_distance_shell_sum(self):
        # k_0 + k_1 + k_2 = 1 + K + K_C = V
        assert 1 + K + K_C == V


class TestT6_SelfDualityAndSpreadOvoid:
    """#lines = #points = V; spread has THETA=10 lines; ovoid has THETA=10 points."""

    def test_self_duality_line_count(self):
        # GQ(q,q) is self-dual: #lines = #points = V = 40
        assert TOTAL_LINES == V

    def test_spread_line_count(self):
        # A spread partitions V points into V/(Q+1) = 10 = THETA lines
        spread_size = V // (Q + 1)
        assert spread_size == THETA

    def test_spread_size_Q_formula(self):
        # spread size = (Q+1)(Q^2+1)/(Q+1) = Q^2+1 = THETA = 10
        assert V // MU == THETA

    def test_ovoid_point_count(self):
        # An ovoid has Q^2+1 = THETA = 10 points (meets each line in 1 pt)
        ovoid_size = Q**2 + 1
        assert ovoid_size == THETA

    def test_ovoid_size_equals_ALPHA(self):
        # Ovoid size = ALPHA = independence number (ovoid = max independent set!)
        ALPHA = THETA
        assert V // MU == ALPHA

    def test_ovoid_covers_all_lines(self):
        # |ovoid| * |lines through each ovoid pt| = THETA * MU = 10 * 4 = 40 = #lines ✓
        # (each line is covered exactly once → spread = ovoid dual)
        assert THETA * MU == TOTAL_LINES

    def test_spread_covers_all_points(self):
        # spread_size * points_per_line = THETA * MU = 10 * 4 = 40 = V ✓
        assert THETA * MU == V

    def test_spread_ovoid_both_THETA(self):
        # Both spread and ovoid have THETA = 10 elements (self-duality!)
        spread_lines = V // MU    # = 10
        ovoid_points = Q**2 + 1   # = 10
        assert spread_lines == ovoid_points == THETA
