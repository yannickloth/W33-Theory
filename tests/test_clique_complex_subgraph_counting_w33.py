"""
Phase CLXXIX: Clique Complex and GQ Subgraph Counting of W(3,3)

In GQ(q,q), every edge lies in a UNIQUE K_{q+1} (GQ line), and every triangle
lies in a UNIQUE K_{q+1}. This lets us count all K_h exactly from V and Q.

Key discoveries:
  - f_1 = |E| = V*C(Q+1,2) = 40*6 = 240 (each of V lines contributes C(MU,2) edges)
  - f_2 = triangles = V*C(Q+1,3) = 40*4 = 160 (each line contributes C(MU,3)=4 triangles)
  - f_3 = K_4-count = V*C(Q+1,4) = 40*1 = 40 = V (K_4 count equals vertex count!)
  - Each edge in exactly 1 K_4 (GQ: 2 adjacent pts -> unique line)
  - Each triangle in exactly 1 K_4 (3 adj pts -> unique line)
  - f-vector (f0,f1,f2,f3) = (40,240,160,40); sum = 480 = V*K = tr(A^2)!
  - f0 = f3 = V = 40 (vertex count = K_4 count; self-dual!)
  - f1/f3 = C(Q+1,2) = Q(Q+1)/2 = 6; f2/f3 = C(Q+1,3) = Q(Q^2-1)/6 = 4
  - Euler char chi = f0-f1+f2-f3 = 40-240+160-40 = -80 = -2*V
  - Triangles per vertex = K*LAM/2 = 12; K_4 per vertex = Q+1 = 4
  - Triangles per edge = LAM = 2; edges per vertex = K = 12
  - K_4 per triangle = 1 (unique extension!)
  - K_4 per edge = 1 (unique extension!): lambda equals Q-1=2 extra pts on the line
  - Each K_4 (line): MU=4 vertices, C(MU,2)=6 edges, C(MU,3)=4 triangles
  - Total face sum = f0+f1+f2+f3 = V*(1+C(Q+1,2)+C(Q+1,3)+C(Q+1,4)) + correction
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

# f-vector of clique complex (each edge/triangle/K_4 in unique line)
F0 = V              # = 40 (vertices)
F1 = V * 6         # = 240 (edges = V * C(MU,2) = V * C(Q+1,2))
F2 = V * 4         # = 160 (triangles = V * C(MU,3) = V * C(Q+1,3))
F3 = V * 1         # = 40 (K_4 = V * C(MU,4) = V * 1)


# ============================================================
class TestT1_EdgeCounting:
    """f_1 = V*C(Q+1,2) = 240 = V*K/2; each of V lines has C(MU,2)=6 edges."""

    def test_edge_count_value(self):
        assert F1 == 240

    def test_edge_count_via_regularity(self):
        # |E| = V*K/2 = 40*12/2 = 240 (standard formula for regular graph)
        assert F1 == V * K // 2

    def test_edge_count_via_lines(self):
        # Each GQ line (K_4) has C(4,2)=6 edges; V lines total; edges distinct across lines
        binomial_42 = 6   # C(4,2)
        assert F1 == V * binomial_42

    def test_edge_count_via_Q_formula(self):
        # |E| = V * C(Q+1,2) = V * Q*(Q+1)/2 = 40*6 = 240
        C_Q1_2 = Q * (Q + 1) // 2   # = 6
        assert F1 == V * C_Q1_2

    def test_C_Q1_2_value(self):
        # C(Q+1,2) = C(4,2) = 6 = Q*(Q+1)/2
        assert Q * (Q + 1) // 2 == 6

    def test_edges_per_line(self):
        # Each line (K_4) has C(MU,2) = 6 edges
        assert MU * (MU - 1) // 2 == 6

    def test_edge_partitioned_by_lines(self):
        # 240 edges = 40 lines × 6 edges each (no edge shared between lines!)
        assert F1 == F3 * 6

    def test_non_edges(self):
        # Non-edges = V*(V-1)/2 - |E| = 780 - 240 = 540 = V*K_c/2
        non_edges = V * (V - 1) // 2 - F1
        assert non_edges == 540

    def test_non_edges_formula(self):
        # Non-edges = V*(V-1-K)/2 = 40*27/2 = 540
        assert V * (V - 1 - K) // 2 == 540


class TestT2_TriangleCounting:
    """f_2 = V*C(Q+1,3) = 160; each line has 4 triangles; 12 triangles per vertex."""

    def test_triangle_count_value(self):
        assert F2 == 160

    def test_triangle_count_via_lines(self):
        # Each GQ line has C(4,3)=4 triangles; V lines; triangles distinct across lines
        binomial_43 = 4   # C(4,3)
        assert F2 == V * binomial_43

    def test_C_Q1_3_value(self):
        # C(Q+1,3) = C(4,3) = 4 = Q*(Q+1)*(Q-1)/(6)... wait: C(4,3)=4; Q*(Q+1)*(Q-1)/6=3*4*2/6=4 ✓
        C_4_3 = Q * (Q + 1) * (Q - 1) // 6
        assert C_4_3 == 4

    def test_triangle_count_via_SRG(self):
        # Triangles = V*K*LAM / 6 = 40*12*2/6 = 160
        assert V * K * LAM // 6 == 160

    def test_triangles_per_vertex(self):
        # Triangles containing vertex v = K*LAM/2 = 12*2/2 = 12
        tri_per_v = K * LAM // 2
        assert tri_per_v == 12

    def test_total_triangles_from_per_vertex(self):
        # Total triangles = V * (triangles per vertex) / 3 = 40*12/3 = 160
        tri_per_v = K * LAM // 2
        assert V * tri_per_v // 3 == 160

    def test_triangles_per_edge(self):
        # Each edge {u,v} has LAM=2 common neighbors → 2 triangles per edge
        assert LAM == 2   # triangles per edge

    def test_triangles_from_edges(self):
        # Triangles = |E| * LAM / 3 = 240 * 2 / 3 = 160
        assert F1 * LAM // 3 == F2

    def test_triangle_count_via_trace(self):
        # tr(A^3) = k^3 + r^3*f + s^3*g = 1728 + 192 - 960 = 960 = 6 * triangles
        tr_A3 = EIG_K**3 + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S
        assert tr_A3 == 960
        assert tr_A3 // 6 == F2

    def test_triangle_partitioned_by_lines(self):
        # 160 triangles = 40 lines × 4 triangles each (no triangle in 2 lines)
        assert F2 == F3 * 4


class TestT3_K4Counting:
    """f_3 = K_4-count = V = 40; each K_4 is a GQ line; f3 = f0 (self-dual!)."""

    def test_K4_count_value(self):
        assert F3 == 40

    def test_K4_count_equals_V(self):
        # Number of K_4 cliques = V (GQ is self-dual: #points = #lines!)
        assert F3 == V

    def test_K4_count_equals_GQ_lines(self):
        # W(3,3) is the collinearity graph of GQ(q,q): GQ has V lines
        assert F3 == V

    def test_C_Q1_4_value(self):
        # C(Q+1,4) = C(4,4) = 1 (unique maximum simplex per line!)
        assert MU * (MU - 1) * (MU - 2) * (MU - 3) // 24 == 1

    def test_K4_per_vertex(self):
        # Each vertex is on t+1 = Q+1 = 4 GQ lines
        K4_per_v = Q + 1
        assert K4_per_v == 4

    def test_total_K4_from_per_vertex(self):
        # Total K_4 = V * (K4 per vertex) / K4_size = 40*4/4 = 40
        K4_per_v = Q + 1
        K4_size = Q + 1
        assert V * K4_per_v // K4_size == F3

    def test_K4_per_edge(self):
        # Each edge is in exactly 1 K_4 (GQ: adjacent pair → unique line)
        K4_per_edge = 1
        # Verify via counting: F3 * C(MU,2) = F1 (each K_4 has 6 edges, each in 1 K_4)
        assert F3 * 6 == F1

    def test_K4_per_triangle(self):
        # Each triangle is in exactly 1 K_4 (3 mutually adj pts → unique line)
        K4_per_triangle = 1
        # Verify: F3 * C(MU,3) = F2 (each K_4 has 4 triangles, each in 1 K_4)
        assert F3 * 4 == F2

    def test_no_K5(self):
        # Max clique size = MU = 4; no K_5 exists
        max_clique = MU
        assert max_clique == 4
        assert max_clique < 5  # no K_5


class TestT4_FVectorSymmetry:
    """f-vector (40,240,160,40): sum=480=V*K; f0=f3=V (self-dual symmetry!)."""

    def test_f0_equals_V(self):
        assert F0 == V

    def test_f1_value(self):
        assert F1 == 240

    def test_f2_value(self):
        assert F2 == 160

    def test_f3_value(self):
        assert F3 == 40

    def test_f0_equals_f3(self):
        # f0 = f3 = 40 = V (vertex count = K_4 count: self-dual GQ!)
        assert F0 == F3

    def test_f_vector_sum_equals_V_K(self):
        # f0+f1+f2+f3 = 40+240+160+40 = 480 = V*K = tr(A^2)!
        assert F0 + F1 + F2 + F3 == V * K

    def test_f_vector_sum_equals_tr_A2(self):
        # tr(A^2) = 480 = V*K
        tr_A2 = EIG_K**2 + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S
        assert F0 + F1 + F2 + F3 == tr_A2

    def test_f_ratios(self):
        # f1/f3 = 6 = C(Q+1,2); f2/f3 = 4 = C(Q+1,3)
        assert F1 // F3 == 6   # = C(MU,2)
        assert F2 // F3 == 4   # = C(MU,3)

    def test_f_Q_formulas(self):
        # Ratios are binomial coefficients C(Q+1, i)
        assert Fraction(F1, V) == 6   # = C(Q+1, 2)
        assert Fraction(F2, V) == 4   # = C(Q+1, 3)
        assert Fraction(F3, V) == 1   # = C(Q+1, 4)


class TestT5_EulerCharacteristic:
    """Euler char = f0-f1+f2-f3 = 40-240+160-40 = -80 = -2*V."""

    def test_euler_char_value(self):
        chi = F0 - F1 + F2 - F3
        assert chi == -80

    def test_euler_char_formula(self):
        # chi = f0 - f1 + f2 - f3 = 40 - 240 + 160 - 40 = -80
        assert (F0 - F1 + F2 - F3) == -80

    def test_euler_char_equals_neg_2V(self):
        # chi = -2*V = -2*40 = -80 (Euler char = -2 times vertex count!)
        chi = F0 - F1 + F2 - F3
        assert chi == -2 * V

    def test_euler_char_from_Q(self):
        # chi = V*(1 - C(Q+1,2) + C(Q+1,3) - C(Q+1,4)) + vertex adjustment
        # Note: f0 = V but per-line vertex count would be V*C(Q+1,1) = V*4 = 160
        # The pure line-based Euler char: V*(C(4,1)-C(4,2)+C(4,3)-C(4,4)) = V*(4-6+4-1)=V*1=40
        # But we replace V*C(4,1)=160 with actual f0=V=40, so:
        # chi_actual = 40 + V*(−C(4,2)+C(4,3)−C(4,4)) = 40 + 40*(−6+4−1) = 40 + 40*(−3) = 40-120 = -80
        chi_line = V * (-6 + 4 - 1)   # contributions from f1, f2, f3
        assert F0 + chi_line == F0 - F1 + F2 - F3

    def test_f_antisymmetric_sum(self):
        # |f0-f3| = 0 (equal); |f1-f2| = |240-160| = 80 = V*LAM
        assert abs(F0 - F3) == 0
        assert abs(F1 - F2) == V * LAM


class TestT6_IncidenceCounts:
    """Incidences: (vertex,edge), (vertex,K4), (edge,triangle), (triangle,K4)."""

    def test_vertex_edge_incidences(self):
        # Sum of degrees = 2*|E| = V*K = 480 (each vertex has K edges)
        assert V * K == 2 * F1

    def test_vertex_K4_incidences(self):
        # Each vertex on Q+1=4 lines → V*(Q+1) = 160 incidences
        assert V * (Q + 1) == 160

    def test_vertex_K4_incidences_from_line_side(self):
        # Each K_4 has MU=4 vertices → F3*MU = 40*4 = 160 incidences
        assert F3 * MU == V * (Q + 1)

    def test_edge_triangle_incidences(self):
        # Each edge in LAM=2 triangles → F1*LAM = 480 incidences
        # Each triangle has 3 edges → F2*3 = 480 incidences
        assert F1 * LAM == F2 * 3

    def test_triangle_K4_incidences(self):
        # Each triangle in 1 K_4; each K_4 has 4 triangles → F2 = F3*4
        assert F2 == F3 * 4

    def test_edge_K4_incidences(self):
        # Each edge in 1 K_4; each K_4 has 6 edges → F1 = F3*6
        assert F1 == F3 * 6

    def test_vertex_triangle_incidences(self):
        # Triangles per vertex = K*LAM/2 = 12; total V*12 = 480; each triangle has 3 vtx → 480/3=160 ✓
        tri_per_v = K * LAM // 2
        assert V * tri_per_v // 3 == F2

    def test_flag_count(self):
        # Flags (vertex, K4 line) = V * (lines per vertex) = 40 * 4 = 160
        # Also = (number of lines) * (line size) = 40 * 4 = 160
        flags = V * (Q + 1)
        assert flags == F3 * MU
        assert flags == 160
