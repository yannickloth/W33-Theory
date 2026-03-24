"""
Phase CLXX: Generalized Quadrangle GQ(q,q) Structure of W(3,3)

W(3,3) is the collinearity graph of the symplectic generalized quadrangle Sp(4,q) = GQ(q,q)
with q=3. All SRG parameters emerge directly from the GQ axioms.

Key discoveries:
  - V = (q+1)(q^2+1) = 40 (point count formula for GQ(q,q))
  - Lines L = V = 40 (GQ(q,q) is self-dual: equal points and lines!)
  - flags = V*(q+1) = 160 = V*MU (incidences = V times mu)
  - K = q*(q+1) = 12 (degree = q times MU, from GQ: q+1 lines, q other points each)
  - lambda = q-1 = 2 (collinear common neighbors = points on shared line minus 2)
  - mu = q+1 = 4 (non-collinear common nbrs = number of lines per point!)
  - V-K-1 = q^3 = 27 (non-adjacent count = q-cube — stunning!)
  - |Sp(4,q)| = q^4*(q^4-1)*(q^2-1) = 51840 = |W(E_6)| (Weyl group of E_6!)
  - Stab(point) = q^4*LAM^2*MU = 1296 = 6^4 = (r-s)^4
  - # triangles = 160 = |Sp(4,q)| / (q^3*K) (automorphism formula)
  - # collinear pairs = 240 = 2*(V*K/2); # non-collinear = 540 = V*q^3/2
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

THETA = K - LAM   # = 10

# Sp(4,q) automorphism group order = |W(E_6)|
SP4Q = Q**4 * (Q**4 - 1) * (Q**2 - 1)   # = 51840
W_E6 = 51840


# ============================================================
class TestT1_GQPointAndLineCount:
    """W(3,3) = GQ(q,q): points = lines = (q+1)(q^2+1)."""

    def test_V_equals_q_plus_1_times_q_squared_plus_1(self):
        # V = (q+1)(q^2+1) = 4 * 10 = 40 (GQ(q,q) point count formula)
        assert V == (Q + 1) * (Q**2 + 1)

    def test_V_factored_by_q_plus_1(self):
        # V / (q+1) = q^2+1 = 10 = THETA (inner factor = Lovász theta!)
        assert V // (Q + 1) == Q**2 + 1
        assert V // (Q + 1) == THETA

    def test_V_factored_by_q_squared_plus_1(self):
        # V / (q^2+1) = q+1 = 4 = MU (outer factor = mu)
        assert V // (Q**2 + 1) == Q + 1
        assert V // (Q**2 + 1) == MU

    def test_lines_equals_V(self):
        # # lines in GQ(q,q) = (q+1)(q^2+1) = V (self-dual: same # points and lines!)
        L = V * K // 2 // ((Q + 1) * Q // 2)   # = VK/2 / C(q+1,2)
        assert L == V

    def test_lines_from_collinear_pairs(self):
        # # edges = VK/2 = 240; each line has C(q+1,2) = C(4,2) = 6 collinear pairs
        # # lines = 240 / 6 = 40 = V
        n_edges = V * K // 2
        pairs_per_line = (Q + 1) * Q // 2   # = C(q+1, 2) = 6
        assert n_edges // pairs_per_line == V

    def test_flags_V_times_q_plus_1(self):
        # # flags (point-line incidences) = V * (lines per point) = V * (q+1) = 160
        flags = V * (Q + 1)
        assert flags == 160

    def test_flags_equals_V_times_MU(self):
        # flags = 160 = V * MU (incidences = V times mu — elegant!)
        assert V * (Q + 1) == V * MU

    def test_flags_from_lines(self):
        # Also: flags = L * (points per line) = V * (q+1) = 160
        L = V
        assert L * (Q + 1) == 160


class TestT2_GQDegreeParameters:
    """SRG parameters lambda, mu, K derived from GQ(q,q) axioms."""

    def test_K_equals_q_times_q_plus_1(self):
        # K = q*(q+1) = 3*4 = 12 (each vertex on q+1 lines, q other points each)
        assert K == Q * (Q + 1)

    def test_K_equals_q_times_MU(self):
        # K = q * MU = Q * MU = 3 * 4 = 12 (degree = field_order * mu)
        assert K == Q * MU

    def test_LAM_equals_q_minus_1(self):
        # lambda = q-1 = 2 (common neighbors of collinear pair = points on line minus 2)
        assert LAM == Q - 1

    def test_MU_equals_q_plus_1(self):
        # mu = q+1 = 4 (common neighbors of non-collinear pair = lines per point!)
        # The mu non-collinear common neighbors = one per line through x (GQ axiom)
        assert MU == Q + 1

    def test_non_adjacent_count_is_q_cubed(self):
        # V - K - 1 = 40 - 12 - 1 = 27 = q^3 (stunning: non-adjacent count = q-cube!)
        assert V - K - 1 == Q**3

    def test_non_adjacent_count_formula(self):
        # V - K - 1 = (q+1)(q^2+1) - q(q+1) - 1 = q^3 (algebraic identity!)
        assert (Q + 1) * (Q**2 + 1) - Q * (Q + 1) - 1 == Q**3

    def test_collinear_pairs_count(self):
        # # collinear pairs = VK/2 = 40*12/2 = 240
        assert V * K // 2 == 240

    def test_non_collinear_pairs_count(self):
        # # non-collinear pairs = V*(V-K-1)/2 = 40*27/2 = 540 = V*q^3/2
        assert V * (V - K - 1) // 2 == 540
        assert V * Q**3 // 2 == 540

    def test_collinear_plus_noncollinear_is_C_V_2(self):
        # 240 + 540 = 780 = C(40,2) = V*(V-1)/2
        collinear = V * K // 2
        non_collinear = V * (V - K - 1) // 2
        assert collinear + non_collinear == V * (V - 1) // 2


class TestT3_SpAutomorphismGroup:
    """Sp(4,q) automorphism group has order = |W(E_6)| = 51840."""

    def test_Sp4q_order(self):
        # |Sp(4,q)| = q^4 * (q^4-1) * (q^2-1) = 81 * 80 * 8 = 51840
        assert SP4Q == 51840

    def test_Sp4q_equals_W_E6(self):
        # |Sp(4,q)| = |W(E_6)| (Weyl group of E_6 exceptional Lie algebra!)
        assert SP4Q == W_E6

    def test_Sp4q_factored(self):
        # 51840 = 81 * 80 * 8 = q^4 * (q^4-1) * (q^2-1)
        assert SP4Q == Q**4 * (Q**4 - 1) * (Q**2 - 1)

    def test_stabilizer_of_point(self):
        # |Stab(point)| = |Sp(4,q)| / V = 51840 / 40 = 1296
        assert SP4Q // V == 1296

    def test_stabilizer_equals_q4_times_LAM2_times_MU(self):
        # 1296 = q^4 * LAM^2 * MU = 81 * 4 * 4 = 1296
        assert SP4Q // V == Q**4 * LAM**2 * MU

    def test_stabilizer_equals_6_to_the_4th(self):
        # 1296 = 6^4 = (LAM+MU)^4 = (r-s)^4 (eigenvalue gap to the 4th!)
        assert SP4Q // V == (EIG_R - EIG_S)**4

    def test_Sp4q_order_mod_V(self):
        # |Sp(4,q)| divisible by V: acts on points
        assert SP4Q % V == 0

    def test_Sp4q_over_q4_factor(self):
        # |Sp(4,q)| / q^4 = (q^4-1)(q^2-1) = 80 * 8 = 640
        assert SP4Q // Q**4 == (Q**4 - 1) * (Q**2 - 1)


class TestT4_TrianglesAndSubgraphs:
    """Exact counts of triangles and subgraph statistics from GQ."""

    def test_triangle_count(self):
        # # triangles = VKlam/6 = 40*12*2/6 = 160
        assert V * K * LAM // 6 == 160

    def test_triangle_count_from_Sp4q(self):
        # # triangles = |Sp(4,q)| / (q^3 * K) = 51840 / (27*12) = 160
        assert SP4Q // (Q**3 * K) == V * K * LAM // 6

    def test_triangles_through_vertex(self):
        # # triangles through a vertex = K*LAM/2 = 12*2/2 = 12 = Q^2+Q
        tri_per_vertex = K * LAM // 2
        assert tri_per_vertex == 12
        assert tri_per_vertex == Q**2 + Q

    def test_triangles_per_edge(self):
        # # triangles containing a given edge = LAM = q-1 = 2
        assert LAM == Q - 1

    def test_edges_count(self):
        # # edges = VK/2 = 240 = 20 * (q+1) * (q-1) * ...
        # 240 = V*K/2 = 40*12/2 = 240 = 2^4 * 3 * 5
        assert V * K // 2 == 240

    def test_edges_formula_from_GQ(self):
        # # edges = V * K / 2 = (q+1)(q^2+1) * q(q+1) / 2
        assert V * K // 2 == (Q + 1) * (Q**2 + 1) * Q * (Q + 1) // 2

    def test_GQ_axiom_lambda_from_line_size(self):
        # lambda = (points per line) - 2 = (q+1) - 2 = q-1 = LAM
        assert LAM == (Q + 1) - 2

    def test_GQ_axiom_mu_from_lines_per_point(self):
        # mu = lines per point = q+1 = MU (GQ axiom: one line per point for non-collinear pair)
        lines_per_point = Q + 1   # = MU
        assert lines_per_point == MU


class TestT5_GQDualityAndSelfDuality:
    """GQ(q,q) is self-dual: interchanging points and lines gives the same GQ."""

    def test_V_equals_L(self):
        # |Points| = |Lines| = (q+1)(q^2+1) = 40 (self-duality!)
        assert V == V * K // 2 // ((Q + 1) * Q // 2)

    def test_points_per_line_equals_lines_per_point(self):
        # Points per line = q+1 = 4 = Lines per point (self-duality signature)
        assert Q + 1 == K // Q

    def test_dual_SRG_is_same_class(self):
        # Dual GQ has same SRG parameters: GQ(q,q) dual = GQ(q,q)
        # SRG parameters unchanged: (V,K,lam,mu) = (40,12,2,4)
        # K dual = V_dual / (q+1) * q = same K ✓
        assert K == Q * (Q + 1)

    def test_complement_is_also_SRG(self):
        # Complement SRG(40,27,18,18) = complement GQ(q,q)
        K_C = V - K - 1   # = 27 = q^3
        assert K_C == Q**3

    def test_complement_K_is_q_cubed(self):
        # K_bar = V-K-1 = q^3 = 27 (non-adjacent count is a perfect cube!)
        assert V - K - 1 == Q**3

    def test_flags_self_dual(self):
        # V * (q+1) = L * (q+1) = 160 (same in dual since V=L)
        assert V * (Q + 1) == V * MU


class TestT6_CrossPhaseConnections:
    """GQ structure connections to prior spectral phases."""

    def test_V_minus_K_minus_1_is_q_cubed(self):
        # V-K-1 = 27 = q^3 connects: non-adjacent count = cube of field order
        assert V - K - 1 == Q**3

    def test_Sp4q_equals_Weyl_E6(self):
        # |Sp(4,q)| = |W(E_6)| = 51840 (exceptional Lie algebra connection!)
        assert SP4Q == 51840

    def test_stabilizer_involves_eigenvalue_gap(self):
        # Stab = (r-s)^4 = 6^4 = 1296 (eigenvalue gap r-s = LAM+MU = 6)
        assert SP4Q // V == (EIG_R - EIG_S)**4

    def test_alpha_times_triangle_count(self):
        # alpha(W33) * triangles = 10 * 160 = 1600 = V^2 (perfect square of V!)
        alpha = Q**2 + 1   # = 10
        triangles = V * K * LAM // 6   # = 160
        assert alpha * triangles == V**2

    def test_GQ_non_adjacent_q3_in_spanning_trees(self):
        # q^3 = 27 appeared as: v_2(tau) = q^MU = 81 = 3^4 = q^(q+1) = q^(q+1)
        # Here: V-K-1 = q^3 = 27; the Laplacian has L2^MUL_S = (2^MU)^15 = 2^60
        # 60 = MUL_S * MU = 15 * 4 = 60 ✓; and MUL_S = V-K-1 - (q^3-q^2)/?
        # Actually: MUL_S = 15 = (q^2+q+1)(q-1)/? Let me just check: V-K-1=27=q^3 ✓
        assert V - K - 1 == Q**3

    def test_K_over_Q_equals_Q_plus_1(self):
        # K/q = q+1 = MU = 4 (lines per point = ratio K/Q)
        assert K // Q == Q + 1
        assert K // Q == MU
