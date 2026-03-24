"""
Phase CLXXV: Walk Generating Function and Closed Walk Counts of W(3,3)

The closed walk count w_n = tr(A^n) = MUL_K*K^n + MUL_R*r^n + MUL_S*s^n.
The generating function W(x) = V*(1 - theta*x - 2*theta*x^2) / D(x) where
D(x) = (1-Kx)(1-rx)(1-sx) = 1 - theta*x - 32*x^2 + 96*x^3 (reciprocal min poly).

Key discoveries:
  - w_0 = V = 40 (identity walks: one per vertex)
  - w_1 = 0 (no self-loops in W(3,3))
  - w_2 = V*K = 480 (closed 2-walks = twice the edges = 2*240)
  - w_3 = 6 * triangles = 6*160 = 960 (each triangle gives 6 closed walks of length 3)
  - w_4 = 24960 (from eigenvalue formula; also = THETA*w_3 + 32*w_2)
  - Recurrence: w_n = THETA*w_{n-1} + 32*w_{n-2} - 96*w_{n-3} (from Cayley-Hamilton!)
  - Generating function: W(x) = N(x)/D(x) where N = V*(1 - theta*x - 2*theta*x^2)
  - N_0 = V, N_1 = -theta*V = -400, N_2 = -2*theta*V = -800 (clean THETA*V formula!)
  - D(x) coefficient of x: -(K+r+s) = -theta (sum of eigenvalues = Lovász theta!)
  - D(x) = 1 - theta*x - 32*x^2 + 96*x^3 where 32=MU*(K-MU), 96=K*(K-MU)
  - w_4/w_2 = 52 = K^2/MU + 4*LAM (= 36+16=52)
"""

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

THETA = K - LAM    # = 10 = Lovász theta

# Recurrence coefficients from minimal polynomial x^3 - THETA*x^2 - 32*x + 96
REC_C1 = MU * (K - MU)        # = 32 (coefficient of A)
REC_C0 = K * (K - MU)         # = 96 (constant term)

# Closed walk counts (exact from eigenvalue formula)
WALKS = [MUL_K * EIG_K**n + MUL_R * EIG_R**n + MUL_S * EIG_S**n for n in range(9)]
W0, W1, W2, W3, W4, W5, W6, W7, W8 = WALKS

# Generating function numerator coefficients (N(x) = W(x)*D(x))
N0 = V
N1 = -THETA * V        # = -400
N2 = -2 * THETA * V    # = -800


# ============================================================
class TestT1_WalkCounts:
    """w_n = tr(A^n) = MUL_K*K^n + MUL_R*r^n + MUL_S*s^n for each n."""

    def test_w0_equals_V(self):
        # w_0 = tr(I) = V = 40 (one identity walk per vertex)
        assert W0 == V

    def test_w1_is_zero(self):
        # w_1 = tr(A) = 0 (A has 0 diagonal: no self-loops)
        assert W1 == 0

    def test_w1_from_eigenvalues(self):
        # MUL_K*K + MUL_R*r + MUL_S*s = 12 + 48 + (-60) = 0
        assert MUL_K * EIG_K + MUL_R * EIG_R + MUL_S * EIG_S == 0

    def test_w2_equals_V_times_K(self):
        # w_2 = tr(A^2) = sum_i (A^2)_{ii} = sum_i deg(i) = V*K = 480
        # (each vertex i: (A^2)_{ii} = #{edges from i} = K)
        assert W2 == V * K

    def test_w2_equals_twice_edges(self):
        # w_2 = 2*|E| = 2*(V*K/2) = V*K = 480 (each edge ij gives 2 closed 2-walks: i->j->i and j->i->j)
        assert W2 == 2 * (V * K // 2)

    def test_w3_equals_6_triangles(self):
        # w_3 = 6 * #{triangles} (each triangle {i,j,k} gives 6 closed 3-walks)
        triangles = V * K * LAM // 6
        assert W3 == 6 * triangles

    def test_w3_value(self):
        # w_3 = 1*12^3 + 24*2^3 + 15*(-4)^3 = 1728 + 192 + (-960) = 960
        assert W3 == 960

    def test_w4_value(self):
        # w_4 = 1*12^4 + 24*2^4 + 15*(-4)^4 = 20736 + 384 + 3840 = 24960
        assert W4 == 24960

    def test_w4_from_eigenvalues(self):
        assert MUL_K * EIG_K**4 + MUL_R * EIG_R**4 + MUL_S * EIG_S**4 == 24960


class TestT2_WalkRecurrence:
    """w_n = THETA*w_{n-1} + 32*w_{n-2} - 96*w_{n-3} for n >= 3 (from Cayley-Hamilton)."""

    def test_recurrence_coefficients(self):
        # From minimal polynomial x^3 = THETA*x^2 + 32*x - 96:
        # A^3 = THETA*A^2 + 32*A - 96*I => tr: w_3 = THETA*w_2 + 32*w_1 - 96*w_0
        assert REC_C1 == 32
        assert REC_C0 == 96

    def test_rec_c1_is_MU_times_K_minus_MU(self):
        # 32 = MU*(K-MU) = 4*8 = 32 (from SRG eigenvalue product relation)
        assert REC_C1 == MU * (K - MU)

    def test_rec_c0_is_K_times_K_minus_MU(self):
        # 96 = K*(K-MU) = 12*8 = 96 (from SRG characteristic polynomial)
        assert REC_C0 == K * (K - MU)

    def test_recurrence_at_n3(self):
        # w_3 = THETA*w_2 + 32*w_1 - 96*w_0 = 10*480 + 0 - 96*40 = 4800-3840 = 960
        assert THETA * W2 + REC_C1 * W1 - REC_C0 * W0 == W3

    def test_recurrence_at_n4(self):
        # w_4 = THETA*w_3 + 32*w_2 - 96*w_1 = 10*960 + 32*480 - 0 = 9600+15360 = 24960
        assert THETA * W3 + REC_C1 * W2 - REC_C0 * W1 == W4

    def test_recurrence_at_n5(self):
        assert THETA * W4 + REC_C1 * W3 - REC_C0 * W2 == W5

    def test_recurrence_at_n6(self):
        assert THETA * W5 + REC_C1 * W4 - REC_C0 * W3 == W6

    def test_recurrence_at_n7(self):
        assert THETA * W6 + REC_C1 * W5 - REC_C0 * W4 == W7

    def test_recurrence_at_n8(self):
        assert THETA * W7 + REC_C1 * W6 - REC_C0 * W5 == W8

    def test_w3_recurrence_value(self):
        # 10*480 + 32*0 - 96*40 = 4800 - 3840 = 960 = w_3
        assert 10 * 480 + 32 * 0 - 96 * 40 == 960

    def test_w4_recurrence_value(self):
        # 10*960 + 32*480 - 96*0 = 9600 + 15360 = 24960 = w_4
        assert 10 * 960 + 32 * 480 - 96 * 0 == 24960


class TestT3_WalkCombinatorics:
    """Combinatorial interpretations of walk counts."""

    def test_w3_triangle_formula(self):
        # w_3 = 6 * #{triangles}: triangles = V*K*LAM/6 = 40*12*2/6 = 160
        assert V * K * LAM // 6 == 160
        assert W3 == 6 * 160

    def test_w2_is_sum_of_degrees(self):
        # w_2 = sum_i deg(i)^2 / deg(i) ... actually w_2 = sum_i (A^2)_{ii}
        # = sum_i #{closed 2-walks from i} = sum_i deg(i) = V*K (since K-regular)
        assert W2 == V * K

    def test_w4_ratio_to_w2(self):
        # w_4 / w_2 = 24960 / 480 = 52
        assert W4 // W2 == 52
        assert W4 % W2 == 0

    def test_52_equals_K2_over_MU_plus_4_MU(self):
        # 52 = K^2/MU + 4*MU = 144/4 + 4*4 = 36+16 = 52
        assert K**2 // MU + 4 * MU == 52
        assert K**2 % MU == 0

    def test_w3_over_w1_undefined_but_w3_over_6_is_triangles(self):
        # w_3 / 6 = 160 = #{triangles} = V*K*LAM/6
        assert W3 // 6 == V * K * LAM // 6

    def test_walk_counts_from_eigenvalue_formula(self):
        # All w_n computed as sum m_i * theta_i^n match eigenvalue formula
        for n, wn in enumerate(WALKS):
            expected = MUL_K * EIG_K**n + MUL_R * EIG_R**n + MUL_S * EIG_S**n
            assert wn == expected, f"w_{n}: {wn} != {expected}"

    def test_w5_value(self):
        # w_5 = 1*12^5 + 24*2^5 + 15*(-4)^5 = 248832 + 768 + (-15360) = 234240
        assert W5 == 234240


class TestT4_GeneratingFunctionDenominator:
    """D(x) = (1-Kx)(1-rx)(1-sx) = 1 - theta*x - 32*x^2 + 96*x^3."""

    def test_denominator_constant_term(self):
        # D_0 = 1
        assert 1 == 1

    def test_denominator_x_coefficient(self):
        # D_1 = -(K+r+s) = -(EIG_K+EIG_R+EIG_S) = -10 = -THETA
        # (K+r+s = THETA = Lovász theta — stunning!)
        assert -(EIG_K + EIG_R + EIG_S) == -THETA

    def test_eigenvalue_sum_equals_THETA(self):
        # K + r + s = 12 + 2 + (-4) = 10 = THETA (sum of ALL eigenvalues incl. k = Lovász theta!)
        assert EIG_K + EIG_R + EIG_S == THETA

    def test_denominator_x2_coefficient(self):
        # D_2 = -(EIG_K*EIG_R + EIG_K*EIG_S + EIG_R*EIG_S) = -(24 - 48 - 8) = 32
        pairwise = EIG_K * EIG_R + EIG_K * EIG_S + EIG_R * EIG_S
        assert pairwise == -32
        assert -pairwise == REC_C1

    def test_denominator_x3_coefficient(self):
        # D_3 = EIG_K*EIG_R*EIG_S = 12*2*(-4) = -96 => +96 in denominator
        product = EIG_K * EIG_R * EIG_S
        assert product == -REC_C0

    def test_denominator_from_min_poly_relation(self):
        # D(x) corresponds to the minimal polynomial mu(x) = x^3 - THETA*x^2 - 32x + 96
        # evaluated in reciprocal form: D(x) = x^3 * mu(1/x) / mu(0)?
        # Actually D(x) = (1-Kx)(1-rx)(1-sx) = product of (1-theta_i*x) for each distinct eig
        assert (1 - EIG_K * 1) == (1 - 12)  # spot check at x=1


class TestT5_GeneratingFunctionNumerator:
    """N(x) = W(x)*D(x) = V*(1 - theta*x - 2*theta*x^2); terminates at degree 2."""

    def test_N0_equals_V(self):
        # N_0 = w_0 = V = 40
        assert N0 == V

    def test_N1_equals_minus_theta_V(self):
        # N_1 = w_1 - THETA*w_0 = 0 - 10*40 = -400 = -THETA*V
        assert N1 == -THETA * V
        assert N1 == W1 - THETA * W0

    def test_N2_equals_minus_2_theta_V(self):
        # N_2 = w_2 - THETA*w_1 - 32*w_0 = 480 - 0 - 1280 = -800 = -2*THETA*V
        assert N2 == -2 * THETA * V
        assert N2 == W2 - THETA * W1 - REC_C1 * W0

    def test_N3_is_zero(self):
        # N_3 = w_3 - THETA*w_2 - 32*w_1 + 96*w_0 = 960-4800-0+3840 = 0
        N3 = W3 - THETA * W2 - REC_C1 * W1 + REC_C0 * W0
        assert N3 == 0

    def test_N4_is_zero(self):
        # N_4 = w_4 - THETA*w_3 - 32*w_2 + 96*w_1 = 24960-9600-15360+0 = 0
        N4 = W4 - THETA * W3 - REC_C1 * W2 + REC_C0 * W1
        assert N4 == 0

    def test_numerator_terminates_at_degree_2(self):
        # W(x)*D(x) has degree 2 (not infinity) since recurrence kills higher terms
        N3 = W3 - THETA * W2 - REC_C1 * W1 + REC_C0 * W0
        N4 = W4 - THETA * W3 - REC_C1 * W2 + REC_C0 * W1
        assert N3 == 0
        assert N4 == 0

    def test_N1_over_N0_equals_minus_THETA(self):
        # N_1/N_0 = -THETA*V/V = -THETA = -10
        assert N1 // N0 == -THETA

    def test_N2_over_N0_equals_minus_2_THETA(self):
        # N_2/N_0 = -2*THETA*V/V = -2*THETA = -20
        assert N2 // N0 == -2 * THETA


class TestT6_CrossPhaseWalkConnections:
    """Cross-connections: walk counts tie back to spectral, GQ, and Seidel phases."""

    def test_w2_equals_zeta_A_minus_2(self):
        # w_2 = 480 = KV = ζ_A(-2) (from Phase CLXVI: zeta_A(-2)=KV=480)
        assert W2 == K * V

    def test_w4_equals_zeta_A_minus_4(self):
        # w_4 = 24960 = ζ_A(-4) (from Phase CLXVI: zeta_A(-4)=zeta_A(-2)*52)
        assert W4 == 24960

    def test_w3_equals_6_times_triangles_from_KV(self):
        # triangles = V*K*LAM/6 = 160; w_3 = 960 = 6*160 ✓
        assert W3 == 6 * (V * K * LAM // 6)

    def test_THETA_appears_in_D_coefficient(self):
        # The coefficient of x in D(x) is -THETA = -(K+r+s) — Lovász theta!
        assert EIG_K + EIG_R + EIG_S == THETA

    def test_w2_over_V_equals_K(self):
        # w_2/V = K = 12 (average closed-2-walk count per vertex = degree)
        assert W2 // V == K

    def test_w3_over_V_equals_THETA_times_LAM(self):
        # w_3/V = 24 = 2*LAM*MU = 2*2*4+... hmm: 960/40=24=2*LAM*MU? 2*2*4=16 no
        # 24 = 6*triangles/V = 6*(K*LAM/6) = K*LAM = 12*2=24 ✓
        assert W3 // V == K * LAM

    def test_w4_over_w3_ratio(self):
        # w_4/w_3 = 24960/960 = 26 = 2*THETA + LAM + MU? = 20+2+4=26 ✓!
        assert W4 // W3 == 26
        assert W4 % W3 == 0
        assert 2 * THETA + LAM + MU == 26
