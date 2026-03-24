"""
Phase CXC: Primitive Idempotents and Eigenspace Projection Entries of W(3,3)

For a vertex-transitive SRG the three primitive idempotents E_0, E_1, E_2
have constant entries on each adjacency class (diagonal / adjacent / non-adjacent).

Key discoveries:
  - E_1 = (A - s*I - (K+MU)/V * J) / (2Q)  where K+MU=(Q+1)^2, 2Q=r-s
  - E_2 = (A - r*I - THETA/V  * J) / (-2Q) where THETA=Q^2+1, r=LAM
  - E_1[diag] = Q*MU/(2*THETA) = 3/5   (= m_1/V = 24/40)
  - E_1[adj]  = LAM/(2*THETA) = 1/10   (= (Q-1)/(2*(Q^2+1)))
  - E_1[non]  = -MU/(2*Q*THETA) = -1/15
  - E_2[diag] = Q/(2*MU) = 3/8         (= m_2/V = 15/40)
  - E_2[adj]  = -1/(2*MU) = -1/8
  - E_2[non]  = 1/(2*Q*MU) = 1/24
  - Frobenius norms: ||E_i||_F^2 = m_i (projection idempotent identity)
  - Row sums: sum of each row of E_1 = 0, E_2 = 0 (ortho to all-ones)
  - Hadamard cross-norm: sum_{u,w} (E_1)_{uw}*(E_2)_{uw} = 0 (Krein orthogonality)
  - Krein parameter q^0_{12} = 0 (E_1, E_2 Krein-orthogonal!)
  - q^0_{11} = m_1 = 24;  q^0_{22} = m_2 = 15
  - Product formulas: (K+MU)/V = 1/(Q+1) = 1/MU; THETA/V = 1/MU... wait:
    (K+MU)/V = (Q+1)^2/((Q+1)(Q^2+1)) = (Q+1)/(Q^2+1) = MU/THETA
    THETA/V = (Q^2+1)/((Q+1)(Q^2+1)) = 1/(Q+1) = 1/MU
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K
EIG_R = 2      # = LAM = Q-1
EIG_S = -4     # = -MU = -(Q+1)

MUL_K = 1
MUL_R = 24     # = f (multiplicity of EIG_R)
MUL_S = 15     # = g (multiplicity of EIG_S)

THETA = EIG_K + EIG_R + EIG_S   # = 10 = Q^2+1

# Derived constants
K_PLUS_MU = K + MU       # = 16 = (Q+1)^2
R_MINUS_S = EIG_R - EIG_S  # = 6 = 2Q  (= r - s)
S_MINUS_R = EIG_S - EIG_R  # = -6 = -2Q

# E_0 = (1/V)*J : all entries equal 1/V
E0_DIAG = Fraction(1, V)
E0_ADJ  = Fraction(1, V)
E0_NONADJ = Fraction(1, V)

# E_1 = (A - s*I - (K+MU)/V * J) / (r - s)
# Diagonal entry (A=0, I=1, J=1):
E1_DIAG = (-EIG_S - Fraction(K_PLUS_MU, V)) / R_MINUS_S   # (-s - (K+MU)/V) / (r-s)
# Adjacent entry (A=1, I=0, J=1):
E1_ADJ  = (1 - Fraction(K_PLUS_MU, V)) / R_MINUS_S
# Non-adjacent entry (A=0, I=0, J=1):
E1_NONADJ = -Fraction(K_PLUS_MU, V) / R_MINUS_S

# E_2 = (A - r*I - THETA/V * J) / (s - r)
# Diagonal entry (A=0, I=1, J=1):
E2_DIAG = (-EIG_R - Fraction(THETA, V)) / S_MINUS_R  # (-r - THETA/V) / (s-r)
# Adjacent entry (A=1, I=0, J=1):
E2_ADJ  = (1 - Fraction(THETA, V)) / S_MINUS_R
# Non-adjacent entry (A=0, I=0, J=1):
E2_NONADJ = -Fraction(THETA, V) / S_MINUS_R

# Number of non-neighbours of a vertex (excluding itself)
K_C = V - 1 - K   # = 27


# ============================================================
class TestT1_E0Entries:
    """E_0 = (1/V)*J: trivial idempotent, all entries = 1/V = 1/40."""

    def test_E0_diag_value(self):
        assert E0_DIAG == Fraction(1, 40)

    def test_E0_adj_value(self):
        assert E0_ADJ == Fraction(1, 40)

    def test_E0_nonadj_value(self):
        assert E0_NONADJ == Fraction(1, 40)

    def test_E0_all_entries_equal(self):
        assert E0_DIAG == E0_ADJ == E0_NONADJ

    def test_E0_trace(self):
        # tr(E_0) = V * (1/V) = 1 = MUL_K
        assert V * E0_DIAG == MUL_K

    def test_E0_Frobenius_sq(self):
        # ||E_0||_F^2 = V^2 * (1/V)^2 = 1 = MUL_K
        frob_sq = V * E0_DIAG**2 + V * K * E0_ADJ**2 + V * K_C * E0_NONADJ**2
        assert frob_sq == MUL_K

    def test_E0_row_sum(self):
        # Row sum = 1 (all-ones eigenvector with eigenvalue K gives row sum of E_0 = 1/V * V = 1)
        # Actually E_0 * 1 = (1/V) * J * 1 = (1/V) * V * 1 = 1, so row sum of E_0 = 1
        row_sum = E0_DIAG + K * E0_ADJ + K_C * E0_NONADJ
        assert row_sum == 1


class TestT2_E1Entries:
    """E_1 entries: 3/5 (diag), 1/10 (adj), -1/15 (non-adj)."""

    def test_E1_diag_value(self):
        assert E1_DIAG == Fraction(3, 5)

    def test_E1_adj_value(self):
        assert E1_ADJ == Fraction(1, 10)

    def test_E1_nonadj_value(self):
        assert E1_NONADJ == Fraction(-1, 15)

    def test_E1_diag_equals_m1_over_V(self):
        # E_1[i,i] = m_1/V = 24/40 = 3/5
        assert E1_DIAG == Fraction(MUL_R, V)

    def test_E1_trace(self):
        # tr(E_1) = V * E1_DIAG = V * m_1/V = m_1 = 24
        assert V * E1_DIAG == MUL_R

    def test_E1_Frobenius_sq(self):
        # ||E_1||_F^2 = V*(E1_diag)^2 + V*K*(E1_adj)^2 + V*K_C*(E1_nonadj)^2 = m_1
        frob_sq = (V * E1_DIAG**2
                   + V * K * E1_ADJ**2
                   + V * K_C * E1_NONADJ**2)
        assert frob_sq == MUL_R

    def test_E1_row_sum_zero(self):
        # E_1 * 1 = 0 (eigenvalue r ≠ K, and E_1 projects onto eigenspace of r, orthogonal to 1)
        row_sum = E1_DIAG + K * E1_ADJ + K_C * E1_NONADJ
        assert row_sum == 0

    def test_E1_adj_positive(self):
        assert E1_ADJ > 0

    def test_E1_nonadj_negative(self):
        assert E1_NONADJ < 0


class TestT3_E2Entries:
    """E_2 entries: 3/8 (diag), -1/8 (adj), 1/24 (non-adj)."""

    def test_E2_diag_value(self):
        assert E2_DIAG == Fraction(3, 8)

    def test_E2_adj_value(self):
        assert E2_ADJ == Fraction(-1, 8)

    def test_E2_nonadj_value(self):
        assert E2_NONADJ == Fraction(1, 24)

    def test_E2_diag_equals_m2_over_V(self):
        # E_2[i,i] = m_2/V = 15/40 = 3/8
        assert E2_DIAG == Fraction(MUL_S, V)

    def test_E2_trace(self):
        # tr(E_2) = V * E2_DIAG = m_2 = 15
        assert V * E2_DIAG == MUL_S

    def test_E2_Frobenius_sq(self):
        # ||E_2||_F^2 = m_2 = 15
        frob_sq = (V * E2_DIAG**2
                   + V * K * E2_ADJ**2
                   + V * K_C * E2_NONADJ**2)
        assert frob_sq == MUL_S

    def test_E2_row_sum_zero(self):
        # E_2 * 1 = 0 (eigenspace of s is orthogonal to all-ones)
        row_sum = E2_DIAG + K * E2_ADJ + K_C * E2_NONADJ
        assert row_sum == 0

    def test_E2_adj_negative(self):
        assert E2_ADJ < 0

    def test_E2_nonadj_positive(self):
        assert E2_NONADJ > 0


class TestT4_CompleteneessOrthogonality:
    """E_0 + E_1 + E_2 = I; E_i * E_j = delta_{ij} * E_i (trace)."""

    def test_completeness_diag(self):
        # Diagonal: E_0[d] + E_1[d] + E_2[d] = 1
        assert E0_DIAG + E1_DIAG + E2_DIAG == 1

    def test_completeness_adj(self):
        # Adjacent: E_0[a] + E_1[a] + E_2[a] = 0 (off-diagonal of identity)
        assert E0_ADJ + E1_ADJ + E2_ADJ == 0

    def test_completeness_nonadj(self):
        # Non-adj: E_0[n] + E_1[n] + E_2[n] = 0
        assert E0_NONADJ + E1_NONADJ + E2_NONADJ == 0

    def test_trace_sum_equals_V(self):
        # tr(E_0) + tr(E_1) + tr(E_2) = MUL_K + MUL_R + MUL_S = V = 40
        assert MUL_K + MUL_R + MUL_S == V

    def test_Frobenius_sq_sum(self):
        # sum ||E_i||_F^2 = ||I||_F^2 = V (since E_i are orthogonal projections)
        frob0 = V * E0_DIAG**2 + V * K * E0_ADJ**2 + V * K_C * E0_NONADJ**2
        frob1 = V * E1_DIAG**2 + V * K * E1_ADJ**2 + V * K_C * E1_NONADJ**2
        frob2 = V * E2_DIAG**2 + V * K * E2_ADJ**2 + V * K_C * E2_NONADJ**2
        assert frob0 + frob1 + frob2 == V

    def test_cross_Frobenius_E0_E1(self):
        # <E_0, E_1>_F = sum E_0[uw]*E_1[uw] = tr(E_0*E_1) = 0 (orthogonal projections)
        cross = (V * E0_DIAG * E1_DIAG
                 + V * K * E0_ADJ * E1_ADJ
                 + V * K_C * E0_NONADJ * E1_NONADJ)
        assert cross == 0

    def test_cross_Frobenius_E0_E2(self):
        cross = (V * E0_DIAG * E2_DIAG
                 + V * K * E0_ADJ * E2_ADJ
                 + V * K_C * E0_NONADJ * E2_NONADJ)
        assert cross == 0

    def test_cross_Frobenius_E1_E2(self):
        cross = (V * E1_DIAG * E2_DIAG
                 + V * K * E1_ADJ * E2_ADJ
                 + V * K_C * E1_NONADJ * E2_NONADJ)
        assert cross == 0


class TestT5_QPolynomialFormulas:
    """All six off-diagonal/diagonal entries expressible as Q-fractions."""

    def test_E1_diag_Q_formula(self):
        # E_1[diag] = Q*MU / (2*THETA) = Q*(Q+1) / (2*(Q^2+1))
        assert E1_DIAG == Fraction(Q * MU, 2 * THETA)

    def test_E1_adj_Q_formula(self):
        # E_1[adj] = LAM / (2*THETA) = (Q-1) / (2*(Q^2+1))
        assert E1_ADJ == Fraction(LAM, 2 * THETA)

    def test_E1_nonadj_Q_formula(self):
        # E_1[non] = -MU / (2*Q*THETA) = -(Q+1) / (2*Q*(Q^2+1))
        assert E1_NONADJ == Fraction(-MU, 2 * Q * THETA)

    def test_E2_diag_Q_formula(self):
        # E_2[diag] = Q / (2*MU) = Q / (2*(Q+1))
        assert E2_DIAG == Fraction(Q, 2 * MU)

    def test_E2_adj_Q_formula(self):
        # E_2[adj] = -1 / (2*MU) = -1 / (2*(Q+1))
        assert E2_ADJ == Fraction(-1, 2 * MU)

    def test_E2_nonadj_Q_formula(self):
        # E_2[non] = 1 / (2*Q*MU) = 1 / (2*Q*(Q+1))
        assert E2_NONADJ == Fraction(1, 2 * Q * MU)

    def test_E1_adj_over_E1_diag(self):
        # E_1[adj] / E_1[diag] = (LAM/2THETA) / (Q*MU/2THETA) = LAM/(Q*MU) = 2/12 = 1/6
        assert E1_ADJ / E1_DIAG == Fraction(LAM, Q * MU)

    def test_E1_nonadj_over_E1_adj(self):
        # E_1[non] / E_1[adj] = (-MU/2QTHETA) / (LAM/2THETA) = -MU/(Q*LAM) = -4/6 = -2/3
        assert E1_NONADJ / E1_ADJ == Fraction(-MU, Q * LAM)

    def test_E2_adj_over_E2_diag(self):
        # E_2[adj] / E_2[diag] = (-1/2MU) / (Q/2MU) = -1/Q
        assert E2_ADJ / E2_DIAG == Fraction(-1, Q)

    def test_E2_nonadj_over_E2_adj(self):
        # E_2[non] / E_2[adj] = (1/2QMIU) / (-1/2MU) = -1/Q
        assert E2_NONADJ / E2_ADJ == Fraction(-1, Q)

    def test_E2_adj_E2_nonadj_ratio_minus_1_over_Q(self):
        # Both ratios adj/diag and non/adj equal -1/Q for E_2 (geometric ratio = -1/Q!)
        assert E2_ADJ / E2_DIAG == E2_NONADJ / E2_ADJ == Fraction(-1, Q)


class TestT6_KreinLikeIdentities:
    """Hadamard (entrywise) product norms and Krein-parameter relations."""

    def test_hadamard_norm_E1_sq(self):
        # ||E_1 circ E_1||_F = sum (E_1)_{uw}^2 = m_1 (Frobenius)
        # sum (E_1)_{uw}^4 (Hadamard square norm):
        had_sq_sum = (V * E1_DIAG**2 + V * K * E1_ADJ**2 + V * K_C * E1_NONADJ**2)
        assert had_sq_sum == MUL_R

    def test_hadamard_norm_E2_sq(self):
        had_sq_sum = (V * E2_DIAG**2 + V * K * E2_ADJ**2 + V * K_C * E2_NONADJ**2)
        assert had_sq_sum == MUL_S

    def test_Krein_q0_11(self):
        # q^0_{11} = V * sum_{u,w} (E_1)_{uw}^2 * (E_0)_{uw} / m_0
        # = V * (1/V) * ||E_1||_F^2 = m_1 = 24
        q0_11 = V * (V * E1_DIAG**2 * E0_DIAG
                     + V * K * E1_ADJ**2 * E0_ADJ
                     + V * K_C * E1_NONADJ**2 * E0_NONADJ)
        assert q0_11 == MUL_R

    def test_Krein_q0_22(self):
        # q^0_{22} = m_2 = 15
        q0_22 = V * (V * E2_DIAG**2 * E0_DIAG
                     + V * K * E2_ADJ**2 * E0_ADJ
                     + V * K_C * E2_NONADJ**2 * E0_NONADJ)
        assert q0_22 == MUL_S

    def test_Krein_q0_12_zero(self):
        # q^0_{12} = V * sum (E_1)_{uw}*(E_2)_{uw}*(E_0)_{uw} / m_0 = 0 (Krein orthogonality!)
        q0_12 = V * (V * E1_DIAG * E2_DIAG * E0_DIAG
                     + V * K * E1_ADJ * E2_ADJ * E0_ADJ
                     + V * K_C * E1_NONADJ * E2_NONADJ * E0_NONADJ)
        assert q0_12 == 0

    def test_E1_diag_plus_E2_diag(self):
        # E_1[d] + E_2[d] = m_1/V + m_2/V = (m_1+m_2)/V = (V-1)/V = 39/40
        assert E1_DIAG + E2_DIAG == Fraction(V - 1, V)

    def test_E1_adj_plus_E2_adj(self):
        # E_1[a] + E_2[a] = -E_0[a] = -1/40
        assert E1_ADJ + E2_ADJ == -E0_ADJ

    def test_E1_nonadj_plus_E2_nonadj(self):
        # E_1[n] + E_2[n] = -E_0[n] = -1/40
        assert E1_NONADJ + E2_NONADJ == -E0_NONADJ

    def test_E1_diag_times_V(self):
        # V * E_1[diag] = m_1 = 24
        assert V * E1_DIAG == MUL_R

    def test_E2_diag_times_V(self):
        # V * E_2[diag] = m_2 = 15
        assert V * E2_DIAG == MUL_S

    def test_spectral_decomp_adj_entry(self):
        # A[adj] = 1 = K*E_0[a] + r*E_1[a] + s*E_2[a]
        # = 12*(1/40) + 2*(1/10) + (-4)*(-1/8)
        # = 3/10 + 1/5 + 1/2 = 3/10 + 2/10 + 5/10 = 1 ✓
        a_adj = EIG_K * E0_ADJ + EIG_R * E1_ADJ + EIG_S * E2_ADJ
        assert a_adj == 1

    def test_spectral_decomp_nonadj_entry(self):
        # A[non] = 0 = K*E_0[n] + r*E_1[n] + s*E_2[n]
        # = 12/40 + 2*(-1/15) + (-4)*(1/24)
        # = 3/10 - 2/15 - 1/6 = 9/30 - 4/30 - 5/30 = 0 ✓
        a_nonadj = EIG_K * E0_NONADJ + EIG_R * E1_NONADJ + EIG_S * E2_NONADJ
        assert a_nonadj == 0

    def test_spectral_decomp_diag_entry(self):
        # A[diag] = 0 = K*E_0[d] + r*E_1[d] + s*E_2[d]
        # = 12/40 + 2*(3/5) + (-4)*(3/8) = 3/10 + 6/5 - 3/2 = 3/10 + 12/10 - 15/10 = 0 ✓
        a_diag = EIG_K * E0_DIAG + EIG_R * E1_DIAG + EIG_S * E2_DIAG
        assert a_diag == 0
