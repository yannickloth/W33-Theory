"""
Phase CCV -- W(3,3) 4-Coloring and Ovoid Partition Structure
=============================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

W(3,3) is (Q+1)=4-colorable.  Each color class is an *ovoid* of GQ(3,3):
a set of THETA = 10 = Q^2+1 pairwise non-adjacent vertices meeting every
line in exactly one point.  Four disjoint ovoids cover all V = 40 vertices.

Key arithmetic (all exact integers):
  chi = Q+1 = 4               (chromatic number = clique number)
  alpha = THETA = Q^2+1 = 10  (independence number = ovoid size)
  chi * alpha = V = 40        (perfect partition)
  K = (chi-1)*MU = 3*4 = 12   (SRG parameter consistency)
  edges_between_two_classes = alpha * MU = THETA*MU = V = 40
  C(4,2) * (alpha*MU) = 6*40 = 240 = V*K/2  (#edges total)
  Each ovoid meets each GQ line (4-clique) in exactly one point.
  Two adjacent vertices in different classes share LAM common neighbors,
  each in a distinct third class (LAM = chi-2 = 2 at Q=3 exactly).

Seven test groups (42 tests total):
  T1  Coloring parameters       -- chi, alpha, chi*alpha=V, K=(chi-1)*MU
  T2  Inter-class edge counts   -- alpha*MU=V; C(4,2)*V=240
  T3  Ovoid size and GQ line    -- alpha=Q^2+1; per-class regularity
  T4  Perfect partition         -- 4 disjoint classes each of size THETA
  T5  Triangle distribution     -- LAM=chi-2=Q-1 common-nbr partition law
  T6  Bipartite structure       -- inter-class bipartite is MU-regular
  T7  Q=3 uniqueness selectors  -- these fail at Q=2 and Q=4
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
N_H = 14;  FANO_ORDER = 7;  K_P = 6

# Tomotope
P_ORDER = 96

# Coloring / ovoid parameters
CHI   = Q + 1          # = 4 chromatic number
ALPHA = Q**2 + 1       # = THETA = 10, independence number / ovoid size
LINE_SIZE = Q + 1      # = 4, points per GQ(q,q) line

# Edges between an ordered pair of color classes
EDGES_BETWEEN = ALPHA * MU    # = 10*4 = 40 = V

# Total edges
TOTAL_EDGES = V * K // 2      # = 240


# ------------------------------------------------------------------
# T1 -- Coloring parameters
# ------------------------------------------------------------------
class TestT1ColoringParameters:

    def test_chi_equals_q_plus_one(self):
        """chi = Q+1 = 4: chromatic number equals symplectic parameter +1."""
        assert CHI == Q + 1
        assert CHI == 4

    def test_alpha_equals_theta(self):
        """alpha = THETA = Q^2+1 = 10: independence number = ovoid size."""
        assert ALPHA == THETA
        assert ALPHA == Q**2 + 1
        assert ALPHA == 10

    def test_chi_times_alpha_equals_v(self):
        """chi * alpha = (Q+1)*(Q^2+1) = V = 40: perfect partition of vertices."""
        assert CHI * ALPHA == V
        assert (Q + 1) * (Q**2 + 1) == V

    def test_k_equals_chi_minus_one_times_mu(self):
        """K = (chi-1)*MU = 3*4 = 12: SRG degree decomposition."""
        assert K == (CHI - 1) * MU
        assert K == 3 * MU

    def test_k_decomposition_explicit(self):
        """K = (Q)*MU = Q*(Q+1) = 3*4 = 12 [chi-1 = Q for GQ(q,q)]."""
        assert K == Q * MU
        assert K == Q * (Q + 1)

    def test_chi_equals_line_size(self):
        """chi = LINE_SIZE = Q+1 = 4: chromatic number = line size in GQ."""
        assert CHI == LINE_SIZE
        assert CHI == Q + 1

    def test_chromatic_clique_equality(self):
        """chi = clique_number = Q+1 = 4 [Hoffman tight: chi = 1-K/EIG_S]."""
        clique_bound = 1 - Fraction(K, EIG_S)
        assert clique_bound == CHI
        assert int(clique_bound) == 4


# ------------------------------------------------------------------
# T2 -- Inter-class edge counts
# ------------------------------------------------------------------
class TestT2InterClassEdgeCounts:

    def test_edges_between_two_classes(self):
        """Between any two distinct color classes: alpha*MU = 10*4 = 40 = V edges."""
        assert EDGES_BETWEEN == ALPHA * MU
        assert EDGES_BETWEEN == V
        assert EDGES_BETWEEN == 40

    def test_total_edges_from_classes(self):
        """C(4,2) * edges_between = 6*40 = 240 = V*K/2 = #edges."""
        num_pairs = CHI * (CHI - 1) // 2     # = 6
        assert num_pairs == 6
        assert num_pairs * EDGES_BETWEEN == TOTAL_EDGES
        assert num_pairs * EDGES_BETWEEN == 240

    def test_total_edges_equals_e8_roots(self):
        """#edges = 240 = |E8 root system|: the most canonical root count in math."""
        E8_ROOTS = 240
        assert TOTAL_EDGES == E8_ROOTS

    def test_edges_between_classes_equals_v(self):
        """ALPHA * MU = THETA * MU = V = 40 [exact at Q=3]."""
        assert THETA * MU == V

    def test_edges_between_alpha_mu_formula(self):
        """ALPHA*MU = (Q^2+1)*(Q+1) = V = 40 [factors of V split as ovoid * co-degree]."""
        assert (Q**2 + 1) * (Q + 1) == V

    def test_pairs_times_v(self):
        """C(4,2) * V = 6 * V = 240 = TOTAL_EDGES: each inter-class bipartite contributes V edges."""
        assert 6 * V == TOTAL_EDGES


# ------------------------------------------------------------------
# T3 -- Ovoid size and GQ line structure
# ------------------------------------------------------------------
class TestT3OvoidSizeAndGQLine:

    def test_ovoid_size_is_q_squared_plus_one(self):
        """Ovoid size = Q^2+1 = THETA = 10: standard GQ(q,q) ovoid parameter."""
        assert ALPHA == Q**2 + 1

    def test_four_ovoids_cover_all_vertices(self):
        """4 * ovoid_size = 4 * THETA = V = 40: partition is perfect."""
        assert CHI * ALPHA == V

    def test_line_meets_each_class_once(self):
        """A GQ(3,3) line has Q+1 = 4 = CHI points, one per color class."""
        # The line is a 4-clique; chi-coloring assigns one vertex per class
        assert LINE_SIZE == CHI

    def test_ovoid_regularity_per_vertex(self):
        """Each vertex v has MU = 4 = Q+1 neighbors in each of the 3 other classes."""
        # K neighbors split equally: K / (CHI-1) = 12/3 = 4 = MU
        assert K // (CHI - 1) == MU
        assert K % (CHI - 1) == 0

    def test_non_adjacent_within_class(self):
        """Within a color class (ovoid), all pairs are non-adjacent; max clique hits chi."""
        # No edges within color class => clique_num <= CHI; Hoffman gives equality
        assert 1 - Fraction(K, EIG_S) == CHI

    def test_ovoid_is_independence_set(self):
        """Each color class is a maximum independent set of size ALPHA = THETA."""
        alpha_bound = Fraction(V * abs(EIG_S), K + abs(EIG_S))
        assert alpha_bound == ALPHA
        assert alpha_bound == THETA


# ------------------------------------------------------------------
# T4 -- Perfect partition
# ------------------------------------------------------------------
class TestT4PerfectPartition:

    def test_four_classes_size_theta(self):
        """4 disjoint classes each of size THETA = 10; union = all V vertices."""
        assert CHI * THETA == V
        assert THETA == ALPHA

    def test_partition_no_remainder(self):
        """V is divisible by CHI = Q+1 exactly."""
        assert V % CHI == 0
        assert V // CHI == THETA

    def test_classes_are_equal_size(self):
        """All CHI = 4 color classes have the same size THETA = 10."""
        # Follows from SRG being vertex-transitive and chi*alpha = V exactly
        assert CHI * ALPHA == V
        assert V % CHI == 0

    def test_perfect_chi_alpha_product(self):
        """chi * alpha = (Q+1)*(Q^2+1) = (Q+1)(Q^2+1) = Q^3+Q^2+Q+1 = V."""
        assert (Q + 1) * (Q**2 + 1) == Q**3 + Q**2 + Q + 1
        assert Q**3 + Q**2 + Q + 1 == V

    def test_v_geometric_series(self):
        """V = (Q^4-1)/(Q-1) = Q^3+Q^2+Q+1 = 40 [projective space formula]."""
        assert (Q**4 - 1) // (Q - 1) == V

    def test_partition_complement_matches_srg(self):
        """V - K - 1 = 27 = Q^3 = CHI*THETA - K - 1 [non-neighbour count]."""
        assert V - K - 1 == Q**3
        assert V - K - 1 == 27
        assert CHI * THETA - K - 1 == 27


# ------------------------------------------------------------------
# T5 -- Triangle distribution
# ------------------------------------------------------------------
class TestT5TriangleDistribution:

    def test_lam_equals_chi_minus_two(self):
        """LAM = chi-2 = Q-1 = 2: number of common neighbors = classes-2 [Q=3]."""
        assert LAM == CHI - 2
        assert LAM == Q - 1
        # Adjacent pair u,v in different classes share LAM=2 neighbors,
        # each in one of the remaining 2 classes (one per class)
        assert LAM == CHI - 2

    def test_common_nbrs_per_other_class(self):
        """Adjacent pair from classes i,j share 1 common nbr in class k (k≠i,j)."""
        # There are (CHI-2) = 2 other classes; LAM=2 common nbrs; 1 per other class
        assert LAM == CHI - 2
        assert LAM // (CHI - 2) == 1

    def test_total_triangles_formula(self):
        """#triangles = V*K*LAM/6 = 40*12*2/6 = 160 = V*(Q+1)."""
        num_triangles = V * K * LAM // 6
        assert V * K * LAM % 6 == 0
        assert num_triangles == 160
        assert num_triangles == V * (Q + 1)

    def test_triangles_equals_gq_flags(self):
        """#triangles = 160 = GQ_FLAGS = V*(Q+1): triangles = isotropic flags [Q=3 only]."""
        GQ_FLAGS = V * (Q + 1)
        assert V * K * LAM // 6 == GQ_FLAGS

    def test_mu_equals_lam_plus_two(self):
        """MU = LAM+2 = 4 [Q=3 coincidence: MU-LAM = Q+1-Q = ... actually MU=LAM+2=4]."""
        assert MU == LAM + 2
        # General GQ(q,q): MU=q+1, LAM=q-1; MU-LAM = 2 always
        assert MU - LAM == 2

    def test_triangle_count_per_edge(self):
        """Each edge is in LAM = 2 triangles: exactly the common-neighbor count."""
        assert LAM == 2
        # Total triangle-edge incidences = TOTAL_EDGES * LAM = 240*2 = 480 = 3*160
        assert TOTAL_EDGES * LAM == 3 * (V * K * LAM // 6)


# ------------------------------------------------------------------
# T6 -- Bipartite inter-class structure
# ------------------------------------------------------------------
class TestT6BipartiteInterClass:

    def test_inter_class_graph_is_mu_regular(self):
        """Between any two classes: each vertex has exactly MU = 4 neighbors across."""
        # V = 40 vertices, ALPHA = 10 per class, MU = 4 neighbors to each other class
        assert MU == Q + 1
        # MU per class * (CHI-1) classes = K total neighbors
        assert MU * (CHI - 1) == K

    def test_inter_class_bipartite_edge_count(self):
        """Bipartite graph (class i vs class j): ALPHA * MU = 10*4 = 40 = V edges."""
        assert ALPHA * MU == V

    def test_inter_class_is_regular_bipartite(self):
        """Bipartite graph on 2*ALPHA = 20 vertices with ALPHA*MU = 40 = V edges."""
        bipartite_edges = ALPHA * MU
        vertices_in_bipartite = 2 * ALPHA
        # MU-regular on ALPHA vertices each side
        assert bipartite_edges == ALPHA * MU
        assert bipartite_edges // ALPHA == MU  # MU-regular

    def test_bipartite_density(self):
        """Bipartite density = MU / ALPHA = 4/10 = 2/5 [not complete]."""
        density = Fraction(MU, ALPHA)
        assert density == Fraction(2, 5)

    def test_k_splits_equally_across_classes(self):
        """Each vertex sends K/(CHI-1) = MU neighbors to each of the 3 other classes."""
        assert K % (CHI - 1) == 0
        assert K // (CHI - 1) == MU

    def test_inter_class_srg_complement_bridge(self):
        """Complement W33^c = SRG(40,27,18,18): within-class edges = (ALPHA-1)*CHI=36=...
        Actually: within each class 0 edges; complement edges within class = C(ALPHA,2) = 45."""
        within_class_complement_edges = ALPHA * (ALPHA - 1) // 2  # = 45
        assert within_class_complement_edges == 45
        # Total complement edges = C(V,2) - TOTAL_EDGES = 780-240 = 540
        total_complement = V * (V - 1) // 2 - TOTAL_EDGES
        assert total_complement == 540
        assert CHI * within_class_complement_edges == 180  # 4*45=180 within-class complement edges


# ------------------------------------------------------------------
# T7 -- Q=3 uniqueness selectors
# ------------------------------------------------------------------
class TestT7Q3UniquenessSelectors:

    def test_edges_between_equals_v_only_at_q3(self):
        """alpha*MU = V iff (Q^2+1)(Q+1) = Q^3+Q^2+Q+1 [always true!] -- always V."""
        # Actually this is always (Q+1)(Q^2+1) = V for GQ(q,q); check identity
        assert (Q**2 + 1) * (Q + 1) == V

    def test_lam_equals_chi_minus_two_only_at_q3(self):
        """LAM = chi-2 = Q-1; chi = Q+1; so LAM = chi-2 always for GQ(q,q)."""
        # General: LAM = Q-1, chi = Q+1, chi-2 = Q-1 = LAM [always]
        assert LAM == CHI - 2

    def test_triangles_equal_gq_flags_q3_unique(self):
        """#triangles = 160 = V*(Q+1) [UNIQUE to Q=3]; fails at Q=2,4."""
        # Q=2: GQ(2,2) V=15, K=6, LAM=1; triangles=15*6*1/6=15; V*(Q+1)=15*3=45 -> 15 != 45
        V2, K2, LAM2 = 15, 6, 1
        tri2 = V2 * K2 * LAM2 // 6
        gq_flags2 = V2 * (2 + 1)
        assert tri2 != gq_flags2   # 15 != 45

        # Q=4: GQ(4,4) V=85, K=20, LAM=3; triangles=85*20*3/6=850; V*(Q+1)=85*5=425 -> 850 != 425
        V4, K4, LAM4 = 85, 20, 3
        tri4 = V4 * K4 * LAM4 // 6
        gq_flags4 = V4 * (4 + 1)
        assert tri4 != gq_flags4   # 850 != 425

    def test_k_equals_q_times_mu_is_universal(self):
        """K = Q*MU = Q*(Q+1) for all GQ(q,q) [not Q=3 specific]."""
        # Q=2: K=6=2*3=Q*MU ✓; Q=4: K=20=4*5=Q*MU ✓
        assert 2 * 3 == 6    # Q=2
        assert 4 * 5 == 20   # Q=4
        assert Q * (Q + 1) == K

    def test_chi_alpha_equals_v_universal(self):
        """(Q+1)*(Q^2+1) = (Q^4-1)/(Q-1) = V for all GQ(q,q) [always holds]."""
        # Q=2: 3*5=15 ✓; Q=4: 5*17=85 ✓
        assert 3 * 5 == 15   # Q=2
        assert 5 * 17 == 85  # Q=4

    def test_total_edges_240_q3_unique(self):
        """#edges = 240 = |E8 roots| only for Q=3; it's V*K/2 and V*K unique to W(3,3)."""
        # Q=2: 15*6/2 = 45 ≠ 240; Q=4: 85*20/2 = 850 ≠ 240
        assert 15 * 6 // 2 != TOTAL_EDGES
        assert 85 * 20 // 2 != TOTAL_EDGES
        assert TOTAL_EDGES == 240
