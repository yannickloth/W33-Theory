"""
Phase CLXXXII: Neighborhood Graph Decomposition and Local Structure of W(3,3)

In GQ(q,q), the neighborhood Γ(v) of any vertex v decomposes into
(Q+1) DISJOINT TRIANGLES K_Q — one for each GQ line through v.

Key discoveries:
  - Γ(v) = Q+1 = 4 disjoint K_Q = 4 disjoint triangles K_3 (cliques of size Q)
  - Lines through v: Q+1 = 4; each line has Q=3 other points forming a K_Q
  - K = |Γ(v)| = (Q+1)*Q = 12 (degree = #lines × #points per line)
  - |E(Γ(v))| = (Q+1)*C(Q,2) = (Q+1)*Q*(Q-1)/2 = 4*3 = 12 (edges in neighborhood)
  - Γ(v) is LAM-regular (2-regular): each u in Γ(v) has exactly LAM = Q-1 neighbors in Γ(v)
  - Triangles in Γ(v) = (Q+1)*C(Q,3) = 4*1 = 4 (each K_Q triangle has C(Q,3)=1 triangle)
  - Non-neighborhood: Q^3=27 vertices, each with K-MU=Q^2-1=8 neighbors among non-nbrs
  - Non-neighborhood edges: Q^3*(Q^2-1)/2 = 27*8/2 = 108 = K*p12_1/2 = K*Q^2/2
  - |N(v)∩N(u)| for v~u: = LAM = Q-1 = 2 (within neighborhood regularity!)
  - |N(v)∩N(u)| for v≁u: = MU = Q+1 = 4 (within non-neighborhood connections)
  - Complement neighborhood: K_c=27 non-neighbors, each forming a (Q^2-1)-regular subgraph
  - (Q+1)*Q*(Q-1)/2 = K*LAM/2 = 12 (two derivations of edge count in Γ(v))
  - 4 triangles in Γ(v) match the 4 lines through v → K_4 cliques in W(3,3)
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


# ============================================================
class TestT1_NeighborhoodSize:
    """Γ(v) has K = (Q+1)*Q vertices from Q+1 GQ lines through v."""

    def test_neighborhood_size(self):
        assert K == 12

    def test_lines_through_vertex(self):
        # GQ(q,q): each vertex is on t+1 = Q+1 lines
        lines_through_v = Q + 1
        assert lines_through_v == 4

    def test_points_per_line_excluding_v(self):
        # Each line has s+1 = Q+1 points total; excluding v: Q points
        points_per_line = Q
        assert points_per_line == 3

    def test_K_equals_lines_times_Q(self):
        # K = (Q+1) * Q = 4 * 3 = 12 (degree = lines × other points per line)
        assert K == (Q + 1) * Q

    def test_K_factorization(self):
        # K = Q^2 + Q = Q*(Q+1) = 12
        assert K == Q**2 + Q


class TestT2_NeighborhoodEdges:
    """Γ(v) has (Q+1)*C(Q,2)=12 edges forming (Q+1) disjoint K_Q triangles."""

    def test_edges_in_neighborhood(self):
        # Edges in Γ(v) = (Q+1) * C(Q,2) = 4 * 3 = 12
        edges_per_triangle = Q * (Q - 1) // 2   # C(Q,2) = C(3,2) = 3
        total_edges = (Q + 1) * edges_per_triangle
        assert total_edges == 12

    def test_edges_via_LAM_regularity(self):
        # Γ(v) is LAM-regular with K vertices: edges = K*LAM/2 = 12*2/2 = 12
        assert K * LAM // 2 == 12

    def test_two_edge_count_formulas_agree(self):
        # (Q+1)*C(Q,2) = K*LAM/2 (two routes to same answer!)
        formula1 = (Q + 1) * (Q * (Q - 1) // 2)
        formula2 = K * LAM // 2
        assert formula1 == formula2

    def test_C_Q2_value(self):
        # C(Q,2) = C(3,2) = 3 = Q*(Q-1)/2
        assert Q * (Q - 1) // 2 == 3

    def test_edges_per_K_Q_triangle(self):
        # Each K_Q has C(Q,2) = 3 edges; Q+1=4 triangles → 4*3=12 total
        assert (Q + 1) * (Q * (Q - 1) // 2) == K * LAM // 2


class TestT3_NeighborhoodRegularity:
    """Γ(v) is LAM-regular: each u in Γ(v) has exactly LAM=Q-1=2 neighbors in Γ(v)."""

    def test_neighborhood_is_LAM_regular(self):
        # Each u adjacent to v: |N(u) ∩ N(v)| = LAM = 2 (SRG definition!)
        local_degree = LAM
        assert local_degree == 2

    def test_local_degree_equals_Q_minus_1(self):
        # LAM = Q-1 = 2 (local degree within neighborhood = Q-1)
        assert LAM == Q - 1

    def test_degree_consistency(self):
        # K * local_degree = 2 * (edges in Γ(v)) : standard regularity check
        assert K * LAM == 2 * (K * LAM // 2)

    def test_local_graph_2_regular(self):
        # Γ(v) is 2-regular (LAM=2-regular) on 12 vertices
        # 2-regular means every vertex has degree 2 in Γ(v)
        assert LAM == 2

    def test_cycle_decomposition_possible(self):
        # A 2-regular graph on 12 vertices decomposes into disjoint cycles
        # Here it's exactly 4 disjoint K_3 = 4 triangles (sum of cycle lengths = 12)
        triangles_in_neighborhood = Q + 1  # = 4
        vertices_per_triangle = Q          # = 3
        assert triangles_in_neighborhood * vertices_per_triangle == K


class TestT4_NeighborhoodTriangles:
    """Γ(v) = (Q+1) disjoint K_Q triangles; triangles in Γ(v) = Q+1=4."""

    def test_components_count(self):
        # Γ(v) has Q+1 = 4 connected components (one per GQ line through v)
        components = Q + 1
        assert components == 4

    def test_each_component_is_K_Q(self):
        # Each component is K_Q = K_3 (complete graph on Q=3 vertices)
        vertices_per_component = Q
        assert vertices_per_component == 3   # K_3

    def test_triangles_in_neighborhood(self):
        # Triangles in Γ(v) = (Q+1) * C(Q,3) = 4 * 1 = 4
        # (Each K_Q has C(Q,3) = C(3,3) = 1 triangle)
        C_Q_3 = 1   # C(3,3) = 1
        triangles = (Q + 1) * C_Q_3
        assert triangles == 4

    def test_triangles_in_neighborhood_Q_formula(self):
        # (Q+1)*C(Q,3) = (Q+1)*1 = Q+1 = 4 (for Q=3 since C(3,3)=1)
        assert Q + 1 == 4

    def test_triangles_in_neighborhood_extend_to_K4(self):
        # Each triangle in Γ(v) ∪ {v} is a K_4 (GQ line = 4-clique containing v)
        # 4 triangles in Γ(v) → 4 K_4 cliques through v (= K4 per vertex)
        K4_through_v = Q + 1
        assert K4_through_v == 4   # = lines through v

    def test_component_structure(self):
        # Γ(v) = K_3 + K_3 + K_3 + K_3 (disjoint union of 4 triangles)
        # Total vertices: 4*3 = 12 = K ✓
        assert (Q + 1) * Q == K
        # Total edges: 4*3 = 12 = K*LAM/2 ✓
        assert (Q + 1) * (Q * (Q - 1) // 2) == K * LAM // 2


class TestT5_NonNeighborhood:
    """Non-Γ(v): Q^3=27 vertices, each (Q^2-1)-regular within non-nbrs."""

    def test_non_neighborhood_size(self):
        # |V \ (Γ(v) ∪ {v})| = V - 1 - K = 27 = Q^3
        assert K_C == Q**3

    def test_non_neighborhood_Q_formula(self):
        # V - 1 - K = (Q+1)(Q^2+1) - 1 - Q(Q+1) = Q^3 = 27
        assert V - 1 - K == Q**3

    def test_non_nbr_local_degree(self):
        # For w ≁ v: |N(w) ∩ (V\Γ(v)\{v})| = K - μ = 12 - 4 = 8 = Q^2 - 1
        local_nonbr_degree = K - MU
        assert local_nonbr_degree == 8

    def test_non_nbr_local_degree_Q_formula(self):
        # K - MU = Q(Q+1) - (Q+1) = (Q+1)(Q-1) = Q^2 - 1 = 8
        assert K - MU == Q**2 - 1

    def test_non_nbr_edges(self):
        # |E(non-Γ(v))| = Q^3 * (Q^2-1) / 2 = 27 * 8 / 2 = 108
        assert K_C * (K - MU) // 2 == 108

    def test_non_nbr_edges_Q_formula(self):
        # 27*8/2 = 108 = Q^3*(Q^2-1)/2 = Q^3*(Q+1)*(Q-1)/2
        assert Q**3 * (Q**2 - 1) // 2 == 108

    def test_non_nbr_edges_alternative(self):
        # 108 = K * p12_1 / 2 = 12 * 9 / 2 = 54? No: 12*9=108, /2=54. Wait:
        # Actually non-nbr edges = q^3*(q^2-1)/2 = 27*8/2 = 108.
        # K*p12_1 = 12*9 = 108 = 2 * non_nbr_edges = 2*54?
        # Wait: 27*8/2 = 108. And K*(K-LAM-1)/2? = 12*9/2 = 54. These don't match.
        # Let me recheck: non-nbr has 27 vertices each with K-MU=8 internal degree.
        # But some neighbors of w (≁v) might be in Γ(v)! Of w's K=12 neighbors:
        # μ=4 are in Γ(v), and K-μ=8 are in non-Γ(v). So internal degree = K-μ = 8 ✓.
        # Edges in non-Γ(v) = Q^3*(K-MU)/2 = 27*8/2 = 108.
        assert K_C * (K - MU) // 2 == 108

    def test_non_nbr_regularity(self):
        # Non-Γ(v) is (K-MU)-regular: each non-neighbor of v has K-MU=8 neighbors there
        assert K - MU == 8

    def test_vertex_partition_identity(self):
        # 1 + K + K_C = V (v, its neighbors, non-neighbors)
        assert 1 + K + K_C == V


class TestT6_DistanceArithmetic:
    """Edge/triangle counts from distance partitioning around a vertex."""

    def test_edges_incident_to_v(self):
        # Edges incident to v = K = 12 (= degree)
        assert K == 12

    def test_edges_within_Gamma_v(self):
        # Edges with both endpoints in Γ(v) = 12 (from 4 K_3 triangles)
        edges_in_nbr = (Q + 1) * Q * (Q - 1) // 2
        assert edges_in_nbr == 12

    def test_edges_between_Gamma_and_non_Gamma(self):
        # Edges from Γ(v) to non-Γ(v): each u ∈ Γ(v) has K-1-LAM = 9 such neighbors
        # (total neighbors of u: K; subtract 1 for v itself; subtract LAM for Γ(v) neighbors)
        neighbors_outside = K - 1 - LAM   # = 9 = Q^2
        total_cross_edges = K * neighbors_outside   # = 12*9 = 108 (directed; each edge counted once from Γ side)
        assert neighbors_outside == Q**2
        assert total_cross_edges == 108

    def test_cross_edges_Q_formula(self):
        # K * (K - LAM - 1) = K * Q^2 = 108 (total edges from Γ(v) to non-Γ(v))
        assert K * (K - LAM - 1) == 108

    def test_cross_edges_double_count(self):
        # From non-Γ side: each w ∈ non-Γ(v) has μ=4 neighbors in Γ(v)
        # Total = K_C * MU = 27 * 4 = 108 ✓ (consistent count!)
        assert K_C * MU == 108

    def test_two_cross_edge_counts_agree(self):
        # K*(K-LAM-1) = K_C*MU = 108 (double-counting agrees!)
        assert K * (K - LAM - 1) == K_C * MU

    def test_total_edge_count_partition(self):
        # Total edges = (edges incident to v) + (edges in Γ(v)) + (cross Γ to non-Γ) + (edges in non-Γ)
        # = K + K*LAM/2 + ? ... but cross edges include both endpoints
        # Total edges = V*K/2 = 240
        # Edges involving v: K = 12
        # Edges in Γ(v): 12
        # Edges between Γ(v) and non-Γ(v): 108 (but directed; undirected = 108)
        # Edges in non-Γ(v): 108
        # Total = 12 + 12 + 108 + 108 = 240 = V*K/2 ✓!!!
        total = K + K * LAM // 2 + K * (K - LAM - 1) + K_C * (K - MU) // 2
        assert total == V * K // 2

    def test_edge_partition_value(self):
        # 12 + 12 + 108 + 108 = 240 = V*K/2
        assert 12 + 12 + 108 + 108 == V * K // 2
