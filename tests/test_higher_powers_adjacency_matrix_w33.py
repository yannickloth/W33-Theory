"""
Phase CLXXXIX: Higher Powers of Adjacency Matrix and Constant Entry Values

For a vertex-transitive SRG, A^k has only 3 distinct entries (diagonal, adjacent, non-adjacent),
all computable by the minimal polynomial recurrence. A striking constant emerges at A^3.

Key discoveries:
  - A^2: entries K=12(diag), LAM=2(adj), MU=4(non-adj) — defines SRG!
  - A^3: entries K*LAM=24(diag), 52(adj), THETA*MU=V=40(non-adj) — A^3[non-adj]=V!!
  - A^3[non-adj] = THETA*MU = (Q^2+1)*(Q+1) = V (walks of length 3 between non-adj = V!)
  - A^3[adj] = 2*LAM*Phi_3(Q) where Phi_3(Q)=Q^2+Q+1=13 (cyclotomic!); 2*2*13=52
  - A^3[diag] = K*LAM = Q*(Q^2-1) = 24 (closed 3-walks per vertex)
  - A^4: entries 624(diag), 488(adj), 528(non-adj); all computed from recurrence
  - A^4[non-adj] = THETA*V + MINPOLY_C1*MU = 400+128 = 528 = K*MU*(Q^2+2) = 528
  - A^4[diag] = THETA*K*LAM + MINPOLY_C1*K = 240+384 = 624 = 16*39 = MU^2*Q*Phi_3(Q)
  - Trace consistency: tr(A^3) = V*24 = 960; tr(A^4) = V*624 = 24960 (from power sums)
  - A^3[non-adj] - A^3[adj] = 40-52 = -12 = -K (difference of off-diagonal entries = -K!)
  - Sum check: V*24 + 2*|E|*52 + (V^2-V-2*|E|)*40 = K^3*V (all-walks identity)
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
MINPOLY_C1 = -(EIG_K * EIG_R + EIG_K * EIG_S + EIG_R * EIG_S)   # = 32

# Cyclotomic polynomial Phi_3(Q) = Q^2+Q+1
PHI3 = Q**2 + Q + 1   # = 13

# A^k entry values (vertex-transitive: only 3 distinct entries per power k)
# A^2
A2_DIAG = K       # = 12
A2_ADJ = LAM      # = 2
A2_NONADJ = MU    # = 4

# A^3 (from recurrence: A^3 = THETA*A^2 + MINPOLY_C1*A - 96*I)
A3_DIAG = THETA * A2_DIAG + MINPOLY_C1 * 0 - 96 * 1   # = 120+0-96 = 24
A3_ADJ = THETA * A2_ADJ + MINPOLY_C1 * 1 - 96 * 0     # = 20+32 = 52
A3_NONADJ = THETA * A2_NONADJ + MINPOLY_C1 * 0 - 96 * 0  # = 40

# A^4 (from recurrence: A^4 = THETA*A^3 + MINPOLY_C1*A^2 - 96*A)
A4_DIAG = THETA * A3_DIAG + MINPOLY_C1 * A2_DIAG - 96 * 0    # = 240+384 = 624
A4_ADJ = THETA * A3_ADJ + MINPOLY_C1 * A2_ADJ - 96 * 1       # = 520+64-96 = 488
A4_NONADJ = THETA * A3_NONADJ + MINPOLY_C1 * A2_NONADJ - 96 * 0  # = 400+128 = 528

EDGES = V * K // 2   # = 240


# ============================================================
class TestT1_A2Entries:
    """A^2 entries: K(diag), LAM(adj), MU(non-adj) — the SRG definition."""

    def test_A2_diagonal(self):
        # (A^2)[i,i] = K (number of closed 2-walks at i = degree)
        assert A2_DIAG == K

    def test_A2_adjacent(self):
        # (A^2)[i,j] for i~j = LAM (common neighbors of adjacent pair)
        assert A2_ADJ == LAM

    def test_A2_nonadjacent(self):
        # (A^2)[i,j] for i≁j, i≠j = MU (common neighbors of non-adjacent pair)
        assert A2_NONADJ == MU

    def test_A2_trace(self):
        # tr(A^2) = V * K = 40*12 = 480 (from V diagonal entries each = K)
        assert V * A2_DIAG == 480

    def test_A2_row_sum_at_i(self):
        # Sum of row i of A^2 = K (all-ones eigenvector with eigenvalue K)
        # = A^2[i,i] + sum_{j~i} A^2[i,j] + sum_{j≁i} A^2[i,j]
        # = K + K*LAM + K_C*MU = 12+24+108 = 144 = K^2 ✓
        K_C = V - 1 - K
        row_sum = A2_DIAG + K * A2_ADJ + K_C * A2_NONADJ
        assert row_sum == K**2

    def test_A2_Q_formulas(self):
        assert A2_DIAG == Q * (Q + 1)
        assert A2_ADJ == Q - 1
        assert A2_NONADJ == Q + 1


class TestT2_A3Entries:
    """A^3 entries: K*LAM=24(diag), 52(adj), THETA*MU=V=40(non-adj)."""

    def test_A3_diagonal(self):
        # (A^3)[i,i] = K*LAM = 24 (closed 3-walks at i = triangles through i × 2)
        assert A3_DIAG == K * LAM

    def test_A3_diagonal_Q_formula(self):
        # K*LAM = Q(Q+1)(Q-1) = Q*(Q^2-1) = 3*8 = 24
        assert A3_DIAG == Q * (Q**2 - 1)

    def test_A3_adjacent(self):
        # (A^3)[i,j] for i~j = 52
        assert A3_ADJ == 52

    def test_A3_adjacent_cyclotomic(self):
        # A^3[adj] = 2*LAM*Phi_3(Q) = 2*2*13 = 52 (Phi_3 = cyclotomic!)
        assert A3_ADJ == 2 * LAM * PHI3

    def test_A3_adjacent_Q_formula(self):
        # A^3[adj] = 2*(Q-1)*(Q^2+Q+1) = 2*2*13 = 52
        assert A3_ADJ == 2 * (Q - 1) * (Q**2 + Q + 1)

    def test_A3_nonadjacent(self):
        # (A^3)[i,j] for i≁j, i≠j = THETA*MU = 40 = V !!!
        assert A3_NONADJ == 40

    def test_A3_nonadjacent_equals_V(self):
        # PROFOUND: A^3[non-adj] = V = 40 (walks of length 3 between non-adj = vertex count!)
        assert A3_NONADJ == V

    def test_A3_nonadjacent_equals_THETA_MU(self):
        # THETA*MU = (Q^2+1)*(Q+1) = V = 40 (the GQ formula!)
        assert A3_NONADJ == THETA * MU

    def test_A3_nonadjacent_Q_formula(self):
        # (Q^2+1)*(Q+1) = Q^3+Q^2+Q+1 = V
        assert A3_NONADJ == (Q**2 + 1) * (Q + 1)

    def test_A3_trace(self):
        # tr(A^3) = V * A3_DIAG = 40 * 24 = 960
        assert V * A3_DIAG == 960


class TestT3_A3Identities:
    """Key A^3 identities: difference=-K, ratio ALPHA, sum relations."""

    def test_A3_nonadj_minus_adj(self):
        # A^3[non-adj] - A^3[adj] = 40 - 52 = -12 = -K
        assert A3_NONADJ - A3_ADJ == -K

    def test_A3_nonadj_over_A2_nonadj(self):
        # A^3[non-adj] / A^2[non-adj] = V/MU = ALPHA = THETA = 10
        assert Fraction(A3_NONADJ, A2_NONADJ) == THETA

    def test_A3_adj_over_A2_adj(self):
        # A^3[adj] / A^2[adj] = 52/2 = 26 = 2*Phi_3(Q) = 2*13
        assert A3_ADJ // A2_ADJ == 26
        assert A3_ADJ // A2_ADJ == 2 * PHI3

    def test_A3_diag_over_A2_diag(self):
        # A^3[diag] / A^2[diag] = 24/12 = 2 = LAM
        assert A3_DIAG // A2_DIAG == LAM

    def test_A3_nonadj_plus_adj(self):
        # A^3[non-adj] + A^3[adj] = 40+52 = 92 = 4*23
        # Also: THETA*(LAM+MU) + MINPOLY_C1 = 10*6+32 = 92 ✓
        assert A3_NONADJ + A3_ADJ == THETA * (LAM + MU) + MINPOLY_C1

    def test_A3_sum_recurrence(self):
        # From A^3 = THETA*A^2 + MINPOLY_C1*A - 96*I, verify all three entries
        assert A3_DIAG == THETA * A2_DIAG - 96
        assert A3_ADJ == THETA * A2_ADJ + MINPOLY_C1
        assert A3_NONADJ == THETA * A2_NONADJ


class TestT4_A4Entries:
    """A^4 entries: 624(diag), 488(adj), 528(non-adj)."""

    def test_A4_diagonal(self):
        assert A4_DIAG == 624

    def test_A4_diagonal_Q_formula(self):
        # 624 = THETA*K*LAM + MINPOLY_C1*K = 10*24+32*12 = 240+384 = 624
        assert A4_DIAG == THETA * A3_DIAG + MINPOLY_C1 * A2_DIAG

    def test_A4_diagonal_factored(self):
        # 624 = MU^2 * Q * Phi_3(Q) = 16*3*13 = 624
        assert A4_DIAG == MU**2 * Q * PHI3

    def test_A4_adjacent(self):
        assert A4_ADJ == 488

    def test_A4_adjacent_Q_formula(self):
        # 488 = THETA*52 + MINPOLY_C1*2 - 96 = 520+64-96 = 488
        assert A4_ADJ == THETA * A3_ADJ + MINPOLY_C1 * A2_ADJ - 96

    def test_A4_nonadjacent(self):
        assert A4_NONADJ == 528

    def test_A4_nonadjacent_Q_formula(self):
        # 528 = THETA*40 + MINPOLY_C1*4 = 400+128 = 528
        assert A4_NONADJ == THETA * A3_NONADJ + MINPOLY_C1 * A2_NONADJ

    def test_A4_nonadjacent_factored(self):
        # 528 = K * MU * (Q^2+2) = 12*4*11 = 528
        assert A4_NONADJ == K * MU * (Q**2 + 2)

    def test_A4_trace(self):
        # tr(A^4) = V * A4_DIAG = 40*624 = 24960
        assert V * A4_DIAG == 24960


class TestT5_PowerSumConsistency:
    """tr(A^k) = p_k = V * A^k[diag]; entries sum = K^k * V."""

    def test_p3_from_entries(self):
        # tr(A^3) = V * A3[diag] = 960
        assert V * A3_DIAG == 960

    def test_p4_from_entries(self):
        # tr(A^4) = V * A4[diag] = 24960
        assert V * A4_DIAG == 24960

    def test_all_A3_entries_sum(self):
        # sum of all V^2 entries of A^3 = K^3 * V (A^3 * all-ones = K^3 * all-ones for K-regular)
        # Total = V*A3_diag + 2*|E|*A3_adj + (V^2-V-2|E|)*A3_nonadj
        K_C = V - 1 - K
        total = V * A3_DIAG + 2 * EDGES * A3_ADJ + (V * K_C) * A3_NONADJ
        assert total == K**3 * V

    def test_all_A3_entries_value(self):
        K_C = V - 1 - K
        total = V * A3_DIAG + 2 * EDGES * A3_ADJ + (V * K_C) * A3_NONADJ
        assert total == 69120   # = K^3 * V = 1728*40

    def test_all_A4_entries_sum(self):
        # sum of all V^2 entries = K^4 * V
        K_C = V - 1 - K
        total = V * A4_DIAG + 2 * EDGES * A4_ADJ + (V * K_C) * A4_NONADJ
        assert total == K**4 * V


class TestT6_EntriesAtEigenvalues:
    """Entry formulas reproduce eigenvalues: A^k[i,i] = (sum_j lambda_j^k * P_{ij}^2) / V."""

    def test_eigenvalue_sum_A3_gives_diag(self):
        # A^3[i,i] = (K^3*1 + r^3*f + s^3*g)/V per vertex (power sum / V = per-vertex walks)
        p3_per_vertex = (EIG_K**3 * MUL_K + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S) // V
        assert p3_per_vertex == A3_DIAG

    def test_eigenvalue_sum_A4_gives_diag(self):
        p4_per_vertex = (EIG_K**4 * MUL_K + EIG_R**4 * MUL_R + EIG_S**4 * MUL_S) // V
        assert p4_per_vertex == A4_DIAG

    def test_A3_Phi3_connection(self):
        # Phi_3(Q) = Q^2+Q+1 = 13 appears in A^3[adj] = 2*LAM*Phi_3
        assert PHI3 == Q**2 + Q + 1
        assert PHI3 == 13
        assert A3_ADJ == 2 * LAM * PHI3

    def test_A3_nonadj_is_GQ_vertex_count(self):
        # A^3[non-adj] = (q+1)(q^2+1) = V (the GQ vertex count formula!)
        assert A3_NONADJ == (Q + 1) * (Q**2 + 1)

    def test_A3_differences(self):
        # A^3[diag] - A^3[adj] = 24-52 = -28 = -2*MU*(Q+1-1) ... = -4*7 = -28
        # Also: = K*LAM - THETA*LAM - MINPOLY_C1 = 24-20-32 = -28
        assert A3_DIAG - A3_ADJ == -28
        # And: A^3[diag] - A^3[non-adj] = 24-40 = -16 = -MU^2 = -(Q+1)^2
        assert A3_DIAG - A3_NONADJ == -(Q + 1)**2
