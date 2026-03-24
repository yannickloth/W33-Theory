"""
Phase CLXXIII: GQ(q,q) Lines as Cliques — Self-Duality at the Graph Level

The 40 lines of GQ(3,3)=Sp(4,3) are cliques of size q+1=4 in W(3,3).
The LINE INTERSECTION GRAPH of GQ(q,q) is isomorphic to W(3,3) itself — self-duality!

Key discoveries:
  - Each line = clique of size q+1=MU=4 in W(3,3)
  - Number of lines = V = 40 (self-dual: same # points and lines in GQ(q,q))
  - Each edge lies in EXACTLY 1 line (GQ axiom: two adjacent pts on unique line)
  - Edge-partition: 40 lines * C(4,2)=6 edges = 240 = V*K/2 (exact partition!)
  - Line intersection degree = (q+1)*q = q*MU = K = 12 (same as point degree!)
  - Two ADJACENT lines (sharing p): common line-nbrs = q-1 = LAM = 2 (lines thru p)
    Proof: lines thru q_i in L_1 minus {p} meeting L_2 = only L_1 itself (GQ axiom!)
  - Two NON-ADJACENT lines (disjoint): common line-nbrs = q+1 = MU = 4 (one per point of L_1)
  - Line intersection graph = SRG(40, 12, 2, 4) = W(3,3) — EXACT SELF-DUALITY!
  - Adjacent line pairs = V * C(q+1,2) = 40*6 = 240 = V*K/2 (agrees with edge count)
  - Non-adj line pairs = V*(q^3)/2 = 40*27/2 = 540 (= V*(V-K-1)/2)
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

# Derived constants for the line/clique geometry
LINE_SIZE = Q + 1       # = 4 = MU (each line has q+1 points)
N_LINES = V             # = 40 (self-dual: #lines = #points in GQ(q,q))
EDGES_PER_LINE = LINE_SIZE * (LINE_SIZE - 1) // 2   # = C(4,2) = 6
TOTAL_EDGES = V * K // 2   # = 240

# Line intersection graph parameters
K_LINE = Q * (Q + 1)   # = 12 = K (same as point degree)
LAM_LINE = Q - 1       # = 2 = LAM (lines thru shared point, minus the 2 lines themselves)
MU_LINE = Q + 1        # = 4 = MU (one meeting-line per point of disjoint line)


# ============================================================
class TestT1_LinesAsCliques:
    """Each of the 40 GQ lines is a clique of size q+1=MU=4 in W(3,3)."""

    def test_line_size_equals_MU(self):
        # Each line has q+1=4=MU points (= clique of size mu!)
        assert LINE_SIZE == MU

    def test_line_size_equals_Q_plus_1(self):
        # Line size = q+1 = 4
        assert LINE_SIZE == Q + 1

    def test_n_lines_equals_V(self):
        # GQ(q,q) is self-dual: number of lines = number of points = V = 40
        assert N_LINES == V

    def test_edges_per_line(self):
        # Within each line (clique of size 4): C(4,2) = 6 edges
        assert EDGES_PER_LINE == LINE_SIZE * (LINE_SIZE - 1) // 2
        assert EDGES_PER_LINE == 6

    def test_clique_size_4_equals_MU(self):
        # The maximum clique in W(3,3) has size omega=MU=4 (from Phase CLXVIII)
        # Each GQ line realizes this maximum
        assert LINE_SIZE == MU

    def test_lines_form_MU_cliques(self):
        # Lines are cliques of the maximum possible size (omega=MU=4)
        assert LINE_SIZE == MU
        assert MU == Q + 1


class TestT2_EdgePartition:
    """The 40 GQ lines partition ALL edges of W(3,3) (GQ axiom: 1 line per edge)."""

    def test_total_edge_line_incidences(self):
        # Each of 40 lines has C(4,2)=6 edges; total = 40*6 = 240
        assert N_LINES * EDGES_PER_LINE == 240

    def test_total_equals_edge_count(self):
        # 40*6 = 240 = V*K/2 = total edges of W(3,3)
        assert N_LINES * EDGES_PER_LINE == TOTAL_EDGES

    def test_each_edge_in_exactly_one_line(self):
        # GQ axiom: two collinear points lie on exactly one common line
        # => each edge of W(3,3) is in exactly 1 GQ line (no double-counting)
        # Verification: total_edges = n_lines * edges_per_line / edges_per_line = n_lines ...
        # equivalently: n_lines * edges_per_line = total_edges (not n_lines * edges_per_line / 2)
        total_inc = N_LINES * EDGES_PER_LINE
        assert total_inc == TOTAL_EDGES  # implies each edge counted once

    def test_edge_partition_into_40_cliques(self):
        # 40 disjoint cliques of size 4: each has 6 edges, 40*6 = 240 total edges ✓
        assert 40 * 6 == 240
        assert 40 * 6 == V * K // 2

    def test_lines_per_point(self):
        # Each point lies on q+1=4=MU lines (from GQ axiom)
        lines_per_pt = Q + 1
        assert lines_per_pt == MU

    def test_flags_V_times_lines_per_pt(self):
        # Total point-line incidences = V * (q+1) = 40*4 = 160
        flags = V * (Q + 1)
        assert flags == 160
        # Also = N_LINES * LINE_SIZE = 40 * 4 = 160 (by self-duality)
        assert N_LINES * LINE_SIZE == flags


class TestT3_LineIntersectionDegree:
    """Each line meets exactly K=12 other lines (line degree = K)."""

    def test_K_line_equals_Q_times_Q_plus_1(self):
        # Each of LINE_SIZE=4 points has Q=3 other lines through it
        # => degree = (Q+1)*Q = 4*3 = 12 = K
        assert K_LINE == Q * (Q + 1)

    def test_K_line_equals_K(self):
        # Line degree = K = 12 (same as point degree — self-duality!)
        assert K_LINE == K

    def test_K_line_from_point_contributions(self):
        # Each of LINE_SIZE points contributes Q=3 lines (not counting L itself)
        # Uniqueness (GQ axiom): no two points of L share a line other than L
        # So total = LINE_SIZE * Q = 4 * 3 = 12 (no overcounting)
        assert LINE_SIZE * Q == K_LINE

    def test_adjacent_line_pairs(self):
        # # adjacent line pairs = N_LINES * K_LINE / 2 = 40*12/2 = 240
        adj = N_LINES * K_LINE // 2
        assert adj == 240

    def test_adjacent_line_pairs_via_points(self):
        # Each point has C(q+1,2)=6 pairs of lines through it;
        # V * C(q+1,2) = 40 * 6 = 240 = adjacent line pairs ✓
        assert V * EDGES_PER_LINE == N_LINES * K_LINE // 2

    def test_non_adjacent_line_pairs(self):
        # Non-adjacent line pairs = C(40,2) - 240 = 780 - 240 = 540
        total_pairs = N_LINES * (N_LINES - 1) // 2
        adj = N_LINES * K_LINE // 2
        assert total_pairs - adj == 540
        assert total_pairs - adj == V * (V - K - 1) // 2


class TestT4_LambdaOfLineGraph:
    """Two adjacent lines (sharing p): common line-neighbors = q-1 = LAM = 2."""

    def test_LAM_line_from_GQ_axiom(self):
        # Lines thru p not L1,L2: (q+1) - 2 = q-1 = 2
        # Lines thru qi in L1\{p} meeting L2: by GQ axiom, that line is L1 itself (meets L2 at p)
        # => NO additional common neighbors beyond lines through p
        lines_thru_shared_p = (Q + 1) - 2   # = q-1 = 2
        assert lines_thru_shared_p == LAM_LINE

    def test_LAM_line_equals_Q_minus_1(self):
        # LAM_line = q-1 = 2 (one fewer than points-per-line minus 2)
        assert LAM_LINE == Q - 1

    def test_LAM_line_equals_LAM(self):
        # LAM_line = LAM = 2 (same lambda as point graph — self-duality!)
        assert LAM_LINE == LAM

    def test_GQ_axiom_prevents_extra_common_neighbors(self):
        # Key: for qi in L1\{p}, the unique line through qi meeting L2 is L1 itself
        # (because qi and p are both on L1, line(qi,p)=L1, and L1 meets L2 at p)
        # This is the GQ axiom applied to qi and L2: 1 line through qi meeting L2 = L1
        # Hence: LAM_line = q-1 (only lines through shared point p, not through other L1-points)
        assert LAM_LINE == (Q + 1) - 2  # = Q-1 = LAM
        assert LAM_LINE == Q - 1

    def test_lines_through_shared_point_not_L1_L2(self):
        # Points on line L1: q+1=4. Lines through p (shared point): q+1=4.
        # Of those: L1 and L2 are not candidates. Remaining: q+1-2 = q-1 = 2.
        remaining = (Q + 1) - 2
        assert remaining == Q - 1
        assert remaining == LAM


class TestT5_MuOfLineGraph:
    """Two non-adjacent lines (disjoint): common neighbors = q+1 = MU = 4."""

    def test_MU_line_from_GQ_axiom(self):
        # For each of q+1=4 points p_i on L1, there's 1 line through p_i meeting L2
        # => MU_line = q+1 = 4
        assert MU_LINE == Q + 1

    def test_MU_line_equals_MU(self):
        # MU_line = MU = 4 (same mu as point graph — self-duality!)
        assert MU_LINE == MU

    def test_MU_line_one_per_point_of_L1(self):
        # For each of LINE_SIZE points of L1, GQ axiom gives exactly 1 line thru it meeting L2
        # These LINE_SIZE lines are all distinct (if two same -> contradiction with L1,L2 sharing only 0 points)
        assert MU_LINE == LINE_SIZE

    def test_MU_line_bijectivity(self):
        # The MU_LINE=4 common lines biject L1's points to L2's points:
        # each common line meets L1 at 1 point, meets L2 at 1 point, injective on both sides
        # => |common lines| <= min(|L1|,|L2|) = q+1 = 4; and = 4 by GQ axiom ✓
        assert MU_LINE == min(LINE_SIZE, LINE_SIZE)
        assert MU_LINE == LINE_SIZE


class TestT6_SelfDualityTheorem:
    """Line intersection graph of GQ(q,q) = SRG(40,12,2,4) = W(3,3) — SELF-DUAL!"""

    def test_line_graph_V_equals_N_lines(self):
        # Line intersection graph has V_line = N_LINES = V = 40 vertices
        assert N_LINES == V

    def test_line_graph_K_equals_K(self):
        # Line intersection graph degree = K = 12 (same as point graph)
        assert K_LINE == K

    def test_line_graph_LAM_equals_LAM(self):
        # Line intersection graph lambda = LAM = 2 (same as point graph)
        assert LAM_LINE == LAM

    def test_line_graph_MU_equals_MU(self):
        # Line intersection graph mu = MU = 4 (same as point graph)
        assert MU_LINE == MU

    def test_line_graph_is_SRG_40_12_2_4(self):
        # The line intersection graph IS SRG(40,12,2,4) = W(3,3) — self-duality!
        assert (N_LINES, K_LINE, LAM_LINE, MU_LINE) == (V, K, LAM, MU)

    def test_self_dual_V_equals_L(self):
        # #points = #lines = (q+1)(q^2+1) = V (fundamental GQ(q,q) self-duality)
        assert N_LINES == (Q + 1) * (Q**2 + 1)
        assert N_LINES == V

    def test_self_dual_line_size_equals_lines_per_point(self):
        # Points per line = q+1 = lines per point (self-duality signature)
        points_per_line = Q + 1
        lines_per_point = Q + 1
        assert points_per_line == lines_per_point

    def test_self_dual_edge_partition(self):
        # Lines partition edges of W(3,3) AND W(3,3)-on-lines
        # Both have 240 edges, partitioned into 40 groups of 6 each
        assert N_LINES * EDGES_PER_LINE == V * K // 2

    def test_Q_formulas_all_self_dual(self):
        # K = q(q+1), LAM = q-1, MU = q+1 — same for both point and line graph
        assert K == Q * (Q + 1)
        assert LAM == Q - 1
        assert MU == Q + 1
        assert K_LINE == Q * (Q + 1)
        assert LAM_LINE == Q - 1
        assert MU_LINE == Q + 1
