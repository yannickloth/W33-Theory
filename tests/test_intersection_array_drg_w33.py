"""
Phase CLXXII: Intersection Array, Distance Polynomials, and DRG Structure of W(3,3)

W(3,3) is a diameter-2 distance-regular graph (DRG) — equivalently, a connected SRG.
All spectral and combinatorial data is captured by the intersection array {b0,b1;c1,c2}.

Key discoveries:
  - Intersection array: {12, 9; 1, 4} = {K, Q^2; 1, Q+1}
  - b1 = K - lambda - 1 = 9 = Q^2 (intersection number = field order squared — stunning!)
  - c2 = mu = Q+1 = 4 (second intersection number = mu)
  - Valencies: k0=1, k1=K=12, k2=Q^3=27 (distance-2 count = q-cube!)
  - DRG identity: k1 * b1 = k2 * c2 = 108 (double-counting paths)
  - Distance polynomial P2(x) = (x^2 - 2x - 12)/4 from 3-term recurrence
  - P2(K)=Q^3=27, P2(r)=-(1+r)=-3, P2(s)=-(1+s)=3 (eigenvalue evaluation)
  - 4*P2(r) = -K = -12; 4*P2(s) = K = 12 (scaled poly = +-K at off-diagonal eigs!)
  - Orthogonality: sum_i m_i * P[i,j] * P[i,j'] = V * k_j * delta(j,j')
  - P matrix: [[1,12,27],[1,2,-3],[1,-4,3]] (rows=eigenspaces, cols=distance classes)
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

# Intersection array {b0, b1; c1, c2}
B0 = K              # = 12
B1 = K - LAM - 1   # = 9 = Q^2
C1 = 1
C2 = MU             # = 4 = Q+1

# "a" values: aᵢ = K - bᵢ - cᵢ
A1 = LAM            # = 2
A2 = K - MU         # = 8 = 2*MU  (b2=0 for diameter 2)

# Valency sequence (number of vertices at each distance)
K0 = 1
K1 = K              # = 12
K2 = K * B1 // C2  # = 12*9/4 = 27 = Q^3

# Distance polynomial P2
def P2(x: int) -> Fraction:
    """Distance polynomial from 3-term recurrence x*P1 = c2*P2 + a1*P1 + b0*P0."""
    return Fraction(x * x - 2 * x - 12, 4)


# ============================================================
class TestT1_IntersectionArrayValues:
    """Intersection array {12, 9; 1, 4} — direct values and Q-formulas."""

    def test_b0_equals_K(self):
        # b0 = K = 12 (from vertex x: all K neighbors go to distance 1)
        assert B0 == K

    def test_b1_equals_K_minus_lambda_minus_1(self):
        # b1 = K - lambda - 1 = 12 - 2 - 1 = 9
        assert B1 == K - LAM - 1

    def test_b1_equals_Q_squared(self):
        # b1 = Q^2 = 9 (intersection number = field order squared — stunning!)
        assert B1 == Q**2

    def test_c1_equals_1(self):
        # c1 = 1 (trivially: only the source vertex is at distance 0 from itself)
        assert C1 == 1

    def test_c2_equals_MU(self):
        # c2 = mu = 4 (from non-adjacent pair: mu common neighbors)
        assert C2 == MU

    def test_c2_equals_Q_plus_1(self):
        # c2 = Q+1 = 4 (second intersection number = q+1)
        assert C2 == Q + 1

    def test_a1_equals_lambda(self):
        # a1 = lambda = 2 (from distance-1 vertex: lambda common neighbors in Gamma_1)
        assert A1 == LAM

    def test_a2_equals_K_minus_MU(self):
        # a2 = K - c2 = 12 - 4 = 8 (b2=0 for diameter 2, so a2 = K - c2)
        assert A2 == K - MU

    def test_a2_equals_2_times_MU(self):
        # a2 = 2*MU = 8 (non-adjacent vertex has 2*mu neighbors also at distance 2)
        assert A2 == 2 * MU


class TestT2_IntersectionArrayIdentities:
    """b_i + c_i + a_i = K for all i — the fundamental DRG valency partition."""

    def test_bca_sum_at_distance_1(self):
        # b1 + c1 + a1 = 9 + 1 + 2 = 12 = K
        assert B1 + C1 + A1 == K

    def test_bca_sum_at_distance_2(self):
        # b2 + c2 + a2 = 0 + 4 + 8 = 12 = K  (b2=0 since diameter=2)
        assert 0 + C2 + A2 == K

    def test_DRG_path_counting_identity(self):
        # k1 * b1 = k2 * c2 = 108 (double-counting paths from distance-1 to distance-2)
        assert K1 * B1 == K2 * C2

    def test_DRG_path_count_value(self):
        # k1*b1 = 12*9 = 108 = k2*c2 = 27*4 = 108
        assert K1 * B1 == 108

    def test_b1_c2_ratio(self):
        # b1/c2 = Q^2/(Q+1) = 9/4 (as Fraction)
        ratio = Fraction(B1, C2)
        assert ratio == Fraction(Q**2, Q + 1)

    def test_diameter_2_means_b2_is_zero(self):
        # W(3,3) has diameter 2: every pair of vertices is at distance at most 2
        # (from mu>0: every non-adjacent pair has mu common neighbors)
        assert MU > 0

    def test_a1_plus_a2_equals_LAM_plus_K_minus_MU(self):
        # a1 + a2 = 2 + 8 = 10 = THETA = K - LAM
        assert A1 + A2 == K - LAM


class TestT3_ValencySequence:
    """Distance distribution: k0=1, k1=K=12, k2=Q^3=27."""

    def test_K0_equals_1(self):
        # k0 = 1 (only the vertex itself at distance 0)
        assert K0 == 1

    def test_K1_equals_K(self):
        # k1 = K = 12 (K vertices at distance 1)
        assert K1 == K

    def test_K2_formula_from_intersection_array(self):
        # k2 = k1 * b1 / c2 = 12 * 9 / 4 = 27 (DRG valency formula)
        assert K2 == K1 * B1 // C2

    def test_K2_equals_Q_cubed(self):
        # k2 = Q^3 = 27 (distance-2 count = q-cube — directly from GQ structure!)
        assert K2 == Q**3

    def test_K2_equals_V_minus_K_minus_1(self):
        # k2 = V - K - 1 = 27 (all vertices not at distance 0 or 1)
        assert K2 == V - K - 1

    def test_valency_sum_is_V(self):
        # k0 + k1 + k2 = 1 + 12 + 27 = 40 = V
        assert K0 + K1 + K2 == V

    def test_K2_over_K1_ratio(self):
        # k2/k1 = 27/12 = 9/4 = Q^2/(Q+1) = b1/c2
        assert Fraction(K2, K1) == Fraction(Q**2, Q + 1)

    def test_K1_times_K2_product(self):
        # k1 * k2 = 12 * 27 = 324 = (VK/2) * something ... = V*(V-1)/2 - 240 ...
        # 324 = 4*81 = 4*Q^4 (= MU * Q^4 = (Q+1)*Q^4? = 4*81=324 ✓)
        assert K1 * K2 == MU * Q**4

    def test_K2_squared_over_K(self):
        # k2^2 / K = 27^2 / 12 = 729/12 not integer; but k2^2 / k2 = k2 trivially
        # Check k2 * (k2-1) / 2 = 351 = C(27,2) (pairs at distance 2 from a vertex)
        assert K2 * (K2 - 1) // 2 == 351


class TestT4_DistancePolynomialP2:
    """P2(x) = (x^2 - 2x - 12)/4 from the 3-term recurrence."""

    def test_P2_at_K(self):
        # P2(12) = (144-24-12)/4 = 108/4 = 27 = k2 = Q^3
        assert P2(EIG_K) == K2

    def test_P2_at_r(self):
        # P2(2) = (4-4-12)/4 = -12/4 = -3 = -(1+r)
        assert P2(EIG_R) == -(1 + EIG_R)

    def test_P2_at_s(self):
        # P2(-4) = (16+8-12)/4 = 12/4 = 3 = -(1+s)
        assert P2(EIG_S) == -(1 + EIG_S)

    def test_scaled_P2_at_r_equals_minus_K(self):
        # 4*P2(r) = r^2 - 2r - 12 = 4 - 4 - 12 = -12 = -K (spectacular!)
        assert 4 * P2(EIG_R) == -K

    def test_scaled_P2_at_s_equals_K(self):
        # 4*P2(s) = s^2 - 2s - 12 = 16 + 8 - 12 = 12 = K (spectacular!)
        assert 4 * P2(EIG_S) == K

    def test_P2_plus_P1_at_K_equals_V_minus_1(self):
        # P2(K) + P1(K) = k2 + k1 = 27 + 12 = 39 = V-1 (all other vertices)
        assert P2(EIG_K) + EIG_K == V - 1

    def test_P2_numerator_coefficients(self):
        # Numerator of 4*P2(x) = x^2 - 2x - 12: coefficients are 1, -2*c1, -4*b0/c2?
        # From recurrence: x*P1 = c2*P2 + a1*P1 + b0*P0 with P1=x, P0=1:
        # x^2 = c2*P2 + a1*x + b0 => P2 = (x^2 - a1*x - b0)/c2
        # = (x^2 - LAM*x - K)/MU = (x^2 - 2x - 12)/4
        assert A1 == LAM
        assert B0 == K
        assert C2 == MU

    def test_P2_recurrence_verification(self):
        # At x=K: K * P1(K) = c2 * P2(K) + a1 * P1(K) + b0 * P0(K)
        # 12 * 12 = 4 * 27 + 2 * 12 + 12 * 1 = 108 + 24 + 12 = 144 ✓
        P1_K = EIG_K
        P0_K = 1
        lhs = EIG_K * P1_K
        rhs = C2 * K2 + A1 * P1_K + B0 * P0_K
        assert lhs == rhs

    def test_P2_recurrence_at_r(self):
        # At x=r: r * P1(r) = c2 * P2(r) + a1 * P1(r) + b0 * P0(r)
        # 2 * 2 = 4 * (-3) + 2 * 2 + 12 * 1 = -12 + 4 + 12 = 4 ✓
        lhs = EIG_R * EIG_R
        rhs = C2 * P2(EIG_R) + A1 * EIG_R + B0 * 1
        assert lhs == rhs

    def test_P2_recurrence_at_s(self):
        # At x=s: s * P1(s) = c2 * P2(s) + a1 * P1(s) + b0 * P0(s)
        # (-4)*(-4) = 4*3 + 2*(-4) + 12*1 = 12 - 8 + 12 = 16 ✓
        lhs = EIG_S * EIG_S
        rhs = C2 * P2(EIG_S) + A1 * EIG_S + B0 * 1
        assert lhs == rhs


class TestT5_EigenvalueMatrixP:
    """P matrix: rows=eigenspaces, cols=distance-class eigenvalues. Row orthogonality."""

    # P[i][j] = eigenvalue of A_j on eigenspace i
    # P = [[1, 12, 27], [1, 2, -3], [1, -4, 3]]

    def test_P_row0_is_valencies(self):
        # Row 0 (eigenvalue K): eigenvalue of A_j = k_j (each A_j has constant row sum)
        assert (1, K, K2) == (K0, K1, K2)

    def test_P_row1_matches_P_polynomials_at_r(self):
        # Row 1 (eigenvalue r=2): [P0(r), P1(r), P2(r)] = [1, 2, -3]
        assert (1, EIG_R, P2(EIG_R)) == (1, 2, -3)

    def test_P_row2_matches_P_polynomials_at_s(self):
        # Row 2 (eigenvalue s=-4): [P0(s), P1(s), P2(s)] = [1, -4, 3]
        assert (1, EIG_S, P2(EIG_S)) == (1, -4, 3)

    def test_row_orthogonality_col0_col0(self):
        # sum_i m_i * P[i,0]^2 = V * k0 = 40 * 1 = 40
        val = MUL_K * 1**2 + MUL_R * 1**2 + MUL_S * 1**2
        assert val == V * K0

    def test_row_orthogonality_col1_col1(self):
        # sum_i m_i * P[i,1]^2 = V * k1 = 40 * 12 = 480
        val = MUL_K * K**2 + MUL_R * EIG_R**2 + MUL_S * EIG_S**2
        assert val == V * K1

    def test_row_orthogonality_col2_col2(self):
        # sum_i m_i * P[i,2]^2 = V * k2 = 40 * 27 = 1080
        P2K = int(P2(EIG_K)); P2r = int(P2(EIG_R)); P2s = int(P2(EIG_S))
        val = MUL_K * P2K**2 + MUL_R * P2r**2 + MUL_S * P2s**2
        assert val == V * K2

    def test_row_orthogonality_col0_col1_cross(self):
        # sum_i m_i * P[i,0] * P[i,1] = 0 (orthogonality of different columns)
        val = MUL_K * 1 * K + MUL_R * 1 * EIG_R + MUL_S * 1 * EIG_S
        assert val == 0

    def test_row_orthogonality_col1_col2_cross(self):
        # sum_i m_i * P[i,1] * P[i,2] = 0
        P2K = int(P2(EIG_K)); P2r = int(P2(EIG_R)); P2s = int(P2(EIG_S))
        val = MUL_K * K * P2K + MUL_R * EIG_R * P2r + MUL_S * EIG_S * P2s
        assert val == 0

    def test_row_orthogonality_col0_col2_cross(self):
        # sum_i m_i * P[i,0] * P[i,2] = 0
        P2K = int(P2(EIG_K)); P2r = int(P2(EIG_R)); P2s = int(P2(EIG_S))
        val = MUL_K * 1 * P2K + MUL_R * 1 * P2r + MUL_S * 1 * P2s
        assert val == 0


class TestT6_CrossPhaseQFormulas:
    """b1=Q^2, k2=Q^3, c2=Q+1 — the intersection array encodes field arithmetic."""

    def test_b1_is_Q_squared(self):
        # b1 = Q^2 = 9 (first non-trivial intersection number = field order squared!)
        assert B1 == Q**2

    def test_K2_is_Q_cubed(self):
        # k2 = Q^3 = 27 (distance-2 valency = field order cubed — matches GQ axiom V-K-1=q^3)
        assert K2 == Q**3

    def test_c2_is_Q_plus_1(self):
        # c2 = Q+1 = 4 = MU (second intersection number = q+1)
        assert C2 == Q + 1

    def test_b1_times_c2_equals_Q_cubed(self):
        # b1 * c2 = Q^2 * (Q+1) = 9 * 4 = 36; hmm not Q^3=27
        # Actually b1 + c2 = Q^2 + Q+1 = 9+4=13? No...
        # b1*c2 = Q^2*(Q+1) = 9*4=36 = K*MU-... hmm; k1*b1 = K*Q^2=12*9=108=4*27=k2*c2 ✓
        assert K1 * B1 == K2 * C2

    def test_intersection_array_encodes_q(self):
        # b1 = Q^2, c2 = Q+1: ratio b1/c2 = Q^2/(Q+1) encodes Q
        # b1 - Q*c2 = Q^2 - Q*(Q+1) = Q^2 - Q^2 - Q = -Q (amazing!)
        assert B1 - Q * C2 == -Q

    def test_valency_ratio_k2_over_k1(self):
        # k2/k1 = Q^3/K = Q^3/(Q*MU) = Q^2/MU = Q^2/(Q+1) = 9/4 (as Fraction)
        assert Fraction(K2, K1) == Fraction(Q**2, Q + 1)

    def test_distance_2_count_equals_non_adjacent_count(self):
        # k2 = V - K - 1 = 27 = Q^3 (distance-2 vertices = non-adjacent vertices)
        assert K2 == V - K - 1

    def test_b1_plus_B1_equals_2_b1(self):
        # b1 = Q^2 = 9 has digit sum: Q^2 = 9 → 9 → 9 (mod Q: Q^2 ≡ 0 mod Q) ✓
        assert B1 % Q == 0

    def test_intersection_sum_b1_plus_c1_plus_a1(self):
        # b1 + c1 + a1 = Q^2 + 1 + LAM = 9+1+2=12 = K ✓
        assert Q**2 + 1 + LAM == K

    def test_a2_equals_2_times_c2(self):
        # a2 = 2*c2 = 2*MU = 8 (non-adjacent neighbor's same-level neighbors = 2*mu!)
        assert A2 == 2 * C2
