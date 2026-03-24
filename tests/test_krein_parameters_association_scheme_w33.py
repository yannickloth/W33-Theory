"""
Phase CXCI: Krein Parameters of the 2-Class Association Scheme of W(3,3)

The Bose-Mesner algebra has Hadamard product E_i ∘ E_j = (1/V) sum_l q^l_{ij} E_l.
The 9 Krein parameters q^l_{ij} (l,i,j in {0,1,2}) are all non-negative (Krein condition).

Key discoveries:
  - q^0_{11} = m_1 = 24;  q^0_{12} = 0 (Krein-orthogonal!);  q^0_{22} = m_2 = 15
  - q^1_{11} = MU*(Q^2+2)/Q = 44/3;  q^1_{12} = (2Q^2+2Q+1)/Q = 25/3;  q^1_{22} = 2*THETA/Q = 20/3
  - q^2_{11} = V/Q = 40/3;  q^2_{12} = 2*(Q+1)^2/Q = 32/3;  q^2_{22} = THETA/Q = 10/3
  - ALL denominator = Q = 3 (Krein parameters are integers / Q!)
  - q^0_{12} = 0: E_1 and E_2 are Krein-orthogonal (profound — only holds for Q-polynomial schemes!)
  - Ratio q^1_{22}/q^2_{22} = 2 (exact!);  q^2_{11}/q^2_{22} = V/THETA = 4 = MU
  - q^2_{11} = V/Q; q^2_{12} = 2*K_PLUS_MU/Q; q^2_{22} = THETA/Q — all scale by 1/Q from V,2*(Q+1)^2,THETA
  - Row 2 parameters sum: q^2_{11}+q^2_{12}+q^2_{22} = (V+2*K_PLUS_MU+THETA)/Q = (40+32+10)/3 = 82/3 ... wait
    Actually sum_j q^l_{1j} or sum over i,j is not standard
  - Numerator pattern for row l=2: V, 2(Q+1)^2, Q^2+1 = 40, 32, 10
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

MUL_K = 1
MUL_R = 24    # = m_1 (multiplicity of EIG_R=2)
MUL_S = 15    # = m_2 (multiplicity of EIG_S=-4)

THETA = 10    # = Q^2+1
K_PLUS_MU = K + MU   # = 16 = (Q+1)^2

# Primitive idempotent entries (from Phase CXC)
E0_ALL = Fraction(1, V)
E1_DIAG, E1_ADJ, E1_NONADJ = Fraction(3, 5), Fraction(1, 10), Fraction(-1, 15)
E2_DIAG, E2_ADJ, E2_NONADJ = Fraction(3, 8), Fraction(-1, 8), Fraction(1, 24)

K_C = V - 1 - K   # = 27

def krein(l_diag, l_adj, l_nonadj,
          i_diag, i_adj, i_nonadj,
          j_diag, j_adj, j_nonadj):
    """Compute q^l_{ij} = V * sum_{u,w} E_l[uw]*E_i[uw]*E_j[uw] / m_l  (normalised)."""
    triple_sum = (V * l_diag * i_diag * j_diag
                  + V * K * l_adj * i_adj * j_adj
                  + V * K_C * l_nonadj * i_nonadj * j_nonadj)
    # m_l = V * l_diag (trace of E_l = m_l, so m_l/V = E_l[diag], m_l = V*l_diag)
    m_l = V * l_diag
    return V * triple_sum / m_l

# Compute all 9 non-trivial Krein parameters
Q0_11 = krein(E0_ALL, E0_ALL, E0_ALL,
              E1_DIAG, E1_ADJ, E1_NONADJ,
              E1_DIAG, E1_ADJ, E1_NONADJ)
# Simplify: q^0_{11} = V * (1/V) * ||E_1||_F^2 = ||E_1||_F^2 = m_1
Q0_12 = krein(E0_ALL, E0_ALL, E0_ALL,
              E1_DIAG, E1_ADJ, E1_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ)
Q0_22 = krein(E0_ALL, E0_ALL, E0_ALL,
              E2_DIAG, E2_ADJ, E2_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ)

Q1_11 = krein(E1_DIAG, E1_ADJ, E1_NONADJ,
              E1_DIAG, E1_ADJ, E1_NONADJ,
              E1_DIAG, E1_ADJ, E1_NONADJ)
Q1_12 = krein(E1_DIAG, E1_ADJ, E1_NONADJ,
              E1_DIAG, E1_ADJ, E1_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ)
Q1_22 = krein(E1_DIAG, E1_ADJ, E1_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ)

Q2_11 = krein(E2_DIAG, E2_ADJ, E2_NONADJ,
              E1_DIAG, E1_ADJ, E1_NONADJ,
              E1_DIAG, E1_ADJ, E1_NONADJ)
Q2_12 = krein(E2_DIAG, E2_ADJ, E2_NONADJ,
              E1_DIAG, E1_ADJ, E1_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ)
Q2_22 = krein(E2_DIAG, E2_ADJ, E2_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ,
              E2_DIAG, E2_ADJ, E2_NONADJ)


# ============================================================
class TestT1_KreinRow0:
    """q^0_{ij}: q^0_{11}=m_1=24, q^0_{12}=0 (Krein orthogonal!), q^0_{22}=m_2=15."""

    def test_q0_11_value(self):
        assert Q0_11 == 24

    def test_q0_11_equals_m1(self):
        assert Q0_11 == MUL_R

    def test_q0_12_zero(self):
        # PROFOUND: q^0_{12} = 0 (E_1 and E_2 are Krein-orthogonal)
        assert Q0_12 == 0

    def test_q0_21_equals_q0_12(self):
        # Symmetry: q^l_{ij} = q^l_{ji}
        Q0_21 = krein(E0_ALL, E0_ALL, E0_ALL,
                      E2_DIAG, E2_ADJ, E2_NONADJ,
                      E1_DIAG, E1_ADJ, E1_NONADJ)
        assert Q0_21 == Q0_12

    def test_q0_22_value(self):
        assert Q0_22 == 15

    def test_q0_22_equals_m2(self):
        assert Q0_22 == MUL_S

    def test_q0_row_sum_nontrivial(self):
        # q^0_{11} + q^0_{12} + q^0_{22} = m_1 + m_2 = V - 1 = 39
        assert Q0_11 + Q0_12 + Q0_22 == V - 1


class TestT2_KreinRow1:
    """q^1_{11}=44/3, q^1_{12}=25/3, q^1_{22}=20/3; all denominator Q=3."""

    def test_q1_11_value(self):
        assert Q1_11 == Fraction(44, 3)

    def test_q1_12_value(self):
        assert Q1_12 == Fraction(25, 3)

    def test_q1_22_value(self):
        assert Q1_22 == Fraction(20, 3)

    def test_q1_11_Q_formula(self):
        # q^1_{11} = MU*(Q^2+2)/Q = (Q+1)*(Q^2+2)/Q = 4*11/3 = 44/3
        assert Q1_11 == Fraction(MU * (Q**2 + 2), Q)

    def test_q1_12_Q_formula(self):
        # q^1_{12} = (2Q^2+2Q+1)/Q = 25/3
        assert Q1_12 == Fraction(2 * Q**2 + 2 * Q + 1, Q)

    def test_q1_22_Q_formula(self):
        # q^1_{22} = 2*THETA/Q = 2*(Q^2+1)/Q = 20/3
        assert Q1_22 == Fraction(2 * THETA, Q)

    def test_q1_all_positive(self):
        assert Q1_11 > 0 and Q1_12 > 0 and Q1_22 > 0

    def test_q1_11_gt_q1_12_gt_q1_22(self):
        # Decreasing: 44/3 > 25/3 > 20/3
        assert Q1_11 > Q1_12 > Q1_22

    def test_q1_denominators_all_Q(self):
        # All denominators = Q = 3
        assert Q1_11.denominator == Q
        assert Q1_12.denominator == Q
        assert Q1_22.denominator == Q


class TestT3_KreinRow2:
    """q^2_{11}=40/3, q^2_{12}=32/3, q^2_{22}=10/3; all denominator Q=3."""

    def test_q2_11_value(self):
        assert Q2_11 == Fraction(40, 3)

    def test_q2_12_value(self):
        assert Q2_12 == Fraction(32, 3)

    def test_q2_22_value(self):
        assert Q2_22 == Fraction(10, 3)

    def test_q2_11_Q_formula(self):
        # q^2_{11} = V/Q = (Q+1)(Q^2+1)/Q = 40/3
        assert Q2_11 == Fraction(V, Q)

    def test_q2_12_Q_formula(self):
        # q^2_{12} = 2*(Q+1)^2/Q = 2*K_PLUS_MU/Q = 32/3
        assert Q2_12 == Fraction(2 * K_PLUS_MU, Q)

    def test_q2_22_Q_formula(self):
        # q^2_{22} = THETA/Q = (Q^2+1)/Q = 10/3
        assert Q2_22 == Fraction(THETA, Q)

    def test_q2_all_positive(self):
        assert Q2_11 > 0 and Q2_12 > 0 and Q2_22 > 0

    def test_q2_11_gt_q2_12_gt_q2_22(self):
        # 40/3 > 32/3 > 10/3
        assert Q2_11 > Q2_12 > Q2_22

    def test_q2_denominators_all_Q(self):
        assert Q2_11.denominator == Q
        assert Q2_12.denominator == Q
        assert Q2_22.denominator == Q


class TestT4_KreinSymmetry:
    """q^l_{ij} = q^l_{ji} and global non-negativity (Krein condition)."""

    def test_krein_nonneg_all(self):
        for val in [Q0_11, Q0_12, Q0_22, Q1_11, Q1_12, Q1_22, Q2_11, Q2_12, Q2_22]:
            assert val >= 0

    def test_q1_symmetry(self):
        Q1_21 = krein(E1_DIAG, E1_ADJ, E1_NONADJ,
                      E2_DIAG, E2_ADJ, E2_NONADJ,
                      E1_DIAG, E1_ADJ, E1_NONADJ)
        assert Q1_21 == Q1_12

    def test_q2_symmetry(self):
        Q2_21 = krein(E2_DIAG, E2_ADJ, E2_NONADJ,
                      E2_DIAG, E2_ADJ, E2_NONADJ,
                      E1_DIAG, E1_ADJ, E1_NONADJ)
        assert Q2_21 == Q2_12

    def test_q0_all_denominators_one(self):
        # Row 0 Krein parameters are integers
        assert Q0_11.denominator == 1
        assert Q0_12.denominator == 1
        assert Q0_22.denominator == 1


class TestT5_KreinRatioIdentities:
    """Ratios and differences between Krein parameters."""

    def test_ratio_q1_22_over_q2_22_equals_2(self):
        # q^1_{22} / q^2_{22} = (20/3)/(10/3) = 2 (exact!)
        assert Q1_22 / Q2_22 == 2

    def test_ratio_q2_11_over_q2_22_equals_MU(self):
        # q^2_{11} / q^2_{22} = (40/3)/(10/3) = 4 = MU = V/THETA
        assert Q2_11 / Q2_22 == MU

    def test_ratio_q2_11_over_q2_12(self):
        # q^2_{11} / q^2_{12} = (40/3)/(32/3) = 40/32 = 5/4 = V/K_PLUS_MU/2 = THETA/(K+1)
        assert Q2_11 / Q2_12 == Fraction(5, 4)

    def test_q1_11_minus_q1_22(self):
        # q^1_{11} - q^1_{22} = 44/3 - 20/3 = 24/3 = 8 = K-MU = Q*(Q-1) = 8
        assert Q1_11 - Q1_22 == K - MU

    def test_q2_11_minus_q2_22(self):
        # q^2_{11} - q^2_{22} = 40/3 - 10/3 = 30/3 = 10 = THETA = Q^2+1
        assert Q2_11 - Q2_22 == THETA

    def test_q1_11_plus_q2_11(self):
        # q^1_{11} + q^2_{11} = 44/3 + 40/3 = 84/3 = 28 = 2*(K+MU) - 4 = 2*K_PLUS_MU-4
        assert Q1_11 + Q2_11 == 2 * K_PLUS_MU - 4

    def test_q1_12_plus_q2_12(self):
        # q^1_{12} + q^2_{12} = 25/3 + 32/3 = 57/3 = 19 = K+MU+3 = K_PLUS_MU+3
        assert Q1_12 + Q2_12 == K_PLUS_MU + 3

    def test_q1_22_plus_q2_22(self):
        # q^1_{22} + q^2_{22} = 20/3 + 10/3 = 30/3 = 10 = THETA
        assert Q1_22 + Q2_22 == THETA

    def test_numerators_row2_are_V_2KplusMU_THETA(self):
        # Numerators of row-2 Krein params (multiplied by Q):
        # Q*q^2_{11}=V=40; Q*q^2_{12}=2*K_PLUS_MU=32; Q*q^2_{22}=THETA=10
        assert Q * Q2_11 == V
        assert Q * Q2_12 == 2 * K_PLUS_MU
        assert Q * Q2_22 == THETA


class TestT6_KreinMarginalSums:
    """Column sums and product identities linking Krein parameters to spectrum."""

    def test_q1_col1_sum(self):
        # q^0_{11} + q^1_{11} + q^2_{11} = 24 + 44/3 + 40/3 = 24 + 28 = 52
        # NOTE: 52 = A^3[adj] (walks of length 3 between adjacent vertices!)
        assert Q0_11 + Q1_11 + Q2_11 == 52

    def test_q1_col2_sum(self):
        # q^0_{12} + q^1_{12} + q^2_{12} = 0 + 25/3 + 32/3 = 57/3 = 19
        assert Q0_12 + Q1_12 + Q2_12 == 19

    def test_q1_col22_sum(self):
        # q^0_{22} + q^1_{22} + q^2_{22} = 15 + 20/3 + 10/3 = 15 + 10 = 25
        assert Q0_22 + Q1_22 + Q2_22 == 25

    def test_q1_11_times_m1(self):
        # q^1_{11} * m_1 = (44/3)*24 = 352 = 8 * 44 = 8*(Q^2+2)*MU ... = 352
        assert Q1_11 * MUL_R == Fraction(44 * 24, 3)

    def test_q2_22_times_m2(self):
        # q^2_{22} * m_2 = (10/3)*15 = 50 = 2*V+10 ... = 50
        assert Q2_22 * MUL_S == 50

    def test_q0_11_over_m0_equals_m1(self):
        # q^0_{11}/m_0 = 24/1 = 24 = m_1 (Krein parameter = multiplicity for l=0)
        assert Q0_11 / MUL_K == MUL_R

    def test_q0_22_over_m0_equals_m2(self):
        assert Q0_22 / MUL_K == MUL_S

    def test_Q1_11_numerator(self):
        # Numerator of q^1_{11} (×Q) = MU*(Q^2+2) = 4*11 = 44
        assert Q * Q1_11 == MU * (Q**2 + 2)

    def test_Q1_12_numerator(self):
        assert Q * Q1_12 == 2 * Q**2 + 2 * Q + 1

    def test_Q1_22_numerator(self):
        assert Q * Q1_22 == 2 * THETA
