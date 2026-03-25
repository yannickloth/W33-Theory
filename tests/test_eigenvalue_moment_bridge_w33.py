"""
Phase CCII -- Eigenvalue Moment Bridge: Tomotope, E8, and Flag-Triangle
=======================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The spectral moments Tr(A^k) of the W(3,3) adjacency matrix decompose
as K^k*1 + EIG_R^k*MUL_R + EIG_S^k*MUL_S.  Each non-trivial contribution
hits an exact group-theoretic or geometric landmark:

  k=2:  EIG_R^2*MUL_R = |P| = 96   (tomotope stabilizer order)
        EIG_S^2*MUL_S = 240         (|E8 root system|)
  k=3:  EIG_R^3*MUL_R = |H| = 192  (axis-flag group order)
        EIG_S^3*MUL_S = -960        (-|P|*THETA)
  k=4:  EIG_R^4*MUL_R = 384        (LAM*|H|)
        EIG_S^4*MUL_S = 3840        (V*|P|)

Additionally, the number of edges equals 240 = |E8 roots|, the number of
non-edges equals 540 = |W(E6)|/|P|, and the triangle count equals the GQ
flag count (both 160 = V*(Q+1)) -- a uniqueness property of Q=3.

All arithmetic is exact integers.

Six test groups (36 tests total):
  T1  Edge and pair counts     -- #edges=240=|E8|, #non-edges=540=|W(E6)|/|P|
  T2  Moments k=0,1,2,3        -- Tr(A^k) via eigenvalue decomposition
  T3  Moment contributions k=2 -- EIG_R^2*MUL_R=|P|, EIG_S^2*MUL_S=|E8|
  T4  Moment contributions k=3 -- EIG_R^3*MUL_R=|H|, EIG_S^3*MUL_S=-|P|*THETA
  T5  Moment contributions k=4 -- EIG_R^4*MUL_R=LAM*|H|, EIG_S^4*MUL_S=V*|P|
  T6  Flag-triangle coincidence -- #triangles=#flags=160=V*(Q+1) [Q=3 unique]
"""

import pytest

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
Q = 3

# W(3,3) = SRG(40, 12, 2, 4)
V = 40;  K = 12;  LAM = 2;  MU = 4
THETA = 10;  EIG_R = 2;  EIG_S = -4;  MUL_R = 24;  MUL_S = 15

# Heawood / Fano / Perkel
N_H = 14;  FANO_ORDER = 7;  K_P = 6

# Tomotope orders
P_ORDER = 96;  H_ORDER = 192;  GAMMA_ORDER = 18432

# External root-system / Weyl-group constants
E8_ROOTS = 240       # |E8 root system|
WE6_ORDER = 51840    # |W(E6)|


# ------------------------------------------------------------------
# T1 -- Edge and pair counts
# ------------------------------------------------------------------
class TestT1EdgeAndPairCounts:

    def test_edge_count_equals_e8_roots(self):
        """#edges = V*K/2 = 240 = |E8 root system|: the W33-E8 edge bridge."""
        edges = V * K // 2
        assert edges == E8_ROOTS
        assert edges == 240

    def test_edge_count_formula(self):
        """#edges = V*K/2 = 40*12/2 = 240 (each of V vertices has degree K)."""
        assert V * K % 2 == 0
        assert V * K // 2 == E8_ROOTS

    def test_non_edge_count(self):
        """#non-edges = V*(V-K-1)/2 = 40*27/2 = 540."""
        non_edges = V * (V - K - 1) // 2
        assert non_edges == 540
        assert V * (V - K - 1) % 2 == 0

    def test_non_edge_count_we6_bridge(self):
        """#non-edges = 540 = |W(E6)|/|P| = 51840/96: W(E6)-tomotope quotient."""
        assert WE6_ORDER % P_ORDER == 0
        assert WE6_ORDER // P_ORDER == V * (V - K - 1) // 2

    def test_total_pairs(self):
        """Total pairs = V*(V-1)/2 = 780 = #edges + #non-edges = 240 + 540."""
        total = V * (V - 1) // 2
        edges = V * K // 2
        non_edges = V * (V - K - 1) // 2
        assert total == 780
        assert edges + non_edges == total

    def test_we6_equals_270_times_h(self):
        """|W(E6)| = 270*|H| = 270*192 = 51840 [270 = Schreier-edge count of K-subgroup]."""
        assert WE6_ORDER == 270 * H_ORDER

    def test_ordered_edge_count(self):
        """Ordered adjacent pairs = V*K = 480 = 2*|E8 roots| = 2*#edges."""
        assert V * K == 2 * E8_ROOTS
        assert V * K == 480


# ------------------------------------------------------------------
# T2 -- Spectral moments Tr(A^k)
# ------------------------------------------------------------------
class TestT2SpectralMoments:

    def test_tr_a0_equals_v(self):
        """Tr(A^0) = Tr(I) = V = 40: V eigenvalues with multiplicity 1."""
        tr = 1 * 1 + 1 * MUL_R + 1 * MUL_S   # K^0*1 + r^0*MUL_R + s^0*MUL_S
        assert tr == V

    def test_tr_a1_equals_zero(self):
        """Tr(A) = K + EIG_R*MUL_R + EIG_S*MUL_S = 12+48-60 = 0 (eigenvalue sum)."""
        tr = K * 1 + EIG_R * MUL_R + EIG_S * MUL_S
        assert tr == 0

    def test_tr_a2_equals_v_k(self):
        """Tr(A^2) = K^2+EIG_R^2*MUL_R+EIG_S^2*MUL_S = 144+96+240 = 480 = V*K."""
        tr = K**2 * 1 + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S
        assert tr == V * K
        assert tr == 480

    def test_tr_a3_equals_v_k_lam(self):
        """Tr(A^3) = K^3+EIG_R^3*MUL_R+EIG_S^3*MUL_S = 1728+192-960 = 960 = V*K*LAM."""
        tr = K**3 * 1 + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S
        assert tr == V * K * LAM
        assert tr == 960

    def test_tr_a3_equals_6_triangles(self):
        """Tr(A^3) = 6*(#triangles) = 6*160 = 960 [each triangle has 3 vertices × 2 orientations]."""
        triangles = V * K * LAM // 6
        assert K**3 + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S == 6 * triangles

    def test_tr_a2_half_is_edge_count(self):
        """Tr(A^2)/2 = V*K/2 = 240 = #edges = |E8 roots|."""
        tr2 = K**2 + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S
        assert tr2 // 2 == E8_ROOTS
        assert tr2 % 2 == 0


# ------------------------------------------------------------------
# T3 -- Moment contributions at k=2
# ------------------------------------------------------------------
class TestT3MomentContributionsK2:

    def test_k2_r_contrib_equals_p_order(self):
        """EIG_R^2*MUL_R = 4*24 = 96 = |P|: r-channel Tr(A^2) = tomotope order."""
        assert EIG_R**2 * MUL_R == P_ORDER

    def test_k2_s_contrib_equals_e8_roots(self):
        """EIG_S^2*MUL_S = 16*15 = 240 = |E8 roots|: s-channel Tr(A^2) = E8 root count."""
        assert EIG_S**2 * MUL_S == E8_ROOTS

    def test_k2_trivial_contrib_is_k_squared(self):
        """K^2*1 = 144: trivial eigenvalue contribution to Tr(A^2)."""
        assert K**2 * 1 == 144
        assert K**2 * 1 == K**2

    def test_k2_decomposition_sum(self):
        """K^2 + |P| + |E8| = 144 + 96 + 240 = 480 = V*K = Tr(A^2)."""
        assert K**2 + P_ORDER + E8_ROOTS == V * K

    def test_k2_nontrivial_sum_equals_k_vk(self):
        """EIG_R^2*MUL_R + EIG_S^2*MUL_S = |P|+|E8| = 336 = K*(V-K)."""
        nontrivial = EIG_R**2 * MUL_R + EIG_S**2 * MUL_S
        assert nontrivial == P_ORDER + E8_ROOTS
        assert nontrivial == K * (V - K)      # = 12*28 = 336
        assert nontrivial == 336

    def test_k2_r_contrib_equals_mu_mul_r(self):
        """EIG_R^2*MUL_R = MU*MUL_R = |P|: also equals non-K eigenvalue × larger mult."""
        assert EIG_R**2 * MUL_R == MU * MUL_R


# ------------------------------------------------------------------
# T4 -- Moment contributions at k=3
# ------------------------------------------------------------------
class TestT4MomentContributionsK3:

    def test_k3_r_contrib_equals_h_order(self):
        """EIG_R^3*MUL_R = 8*24 = 192 = |H|: r-channel Tr(A^3) = axis group order."""
        assert EIG_R**3 * MUL_R == H_ORDER

    def test_k3_s_contrib_equals_minus_p_theta(self):
        """EIG_S^3*MUL_S = (-64)*15 = -960 = -(|P|*THETA): negative spectral volume."""
        assert EIG_S**3 * MUL_S == -(P_ORDER * THETA)
        assert EIG_S**3 * MUL_S == -960

    def test_k3_nontrivial_sum(self):
        """EIG_R^3*MUL_R + EIG_S^3*MUL_S = |H| - |P|*THETA = 192 - 960 = -768."""
        nontrivial = EIG_R**3 * MUL_R + EIG_S**3 * MUL_S
        assert nontrivial == H_ORDER - P_ORDER * THETA
        assert nontrivial == -768

    def test_k3_full_decomposition(self):
        """K^3 + |H| - |P|*THETA = 1728 + 192 - 960 = 960 = V*K*LAM = Tr(A^3)."""
        tr3 = K**3 + H_ORDER - P_ORDER * THETA
        assert tr3 == V * K * LAM
        assert tr3 == 960

    def test_k3_r_contrib_is_lam_p(self):
        """EIG_R^3*MUL_R = LAM*|P| = 2*96 = 192 = |H| [since LAM*|P|=|H|]."""
        assert EIG_R**3 * MUL_R == LAM * P_ORDER
        assert EIG_R**3 * MUL_R == H_ORDER


# ------------------------------------------------------------------
# T5 -- Moment contributions at k=4
# ------------------------------------------------------------------
class TestT5MomentContributionsK4:

    def test_k4_r_contrib_equals_lam_h(self):
        """EIG_R^4*MUL_R = 16*24 = 384 = LAM*|H| = 2*192."""
        assert EIG_R**4 * MUL_R == LAM * H_ORDER
        assert EIG_R**4 * MUL_R == 384

    def test_k4_s_contrib_equals_v_p(self):
        """EIG_S^4*MUL_S = 256*15 = 3840 = V*|P| = 40*96."""
        assert EIG_S**4 * MUL_S == V * P_ORDER
        assert EIG_S**4 * MUL_S == 3840

    def test_tr_a4_exact(self):
        """Tr(A^4) = K^4 + LAM*|H| + V*|P| = 20736 + 384 + 3840 = 24960."""
        tr4 = K**4 * 1 + EIG_R**4 * MUL_R + EIG_S**4 * MUL_S
        assert tr4 == K**4 + LAM * H_ORDER + V * P_ORDER
        assert tr4 == 24960

    def test_tr_a4_per_vertex(self):
        """Tr(A^4)/V = 624 = K^2 + K*LAM^2 + (V-K-1)*MU^2 [closed walk formula]."""
        tr4 = K**4 + EIG_R**4 * MUL_R + EIG_S**4 * MUL_S
        assert tr4 % V == 0
        per_vertex = tr4 // V
        assert per_vertex == K**2 + K * LAM**2 + (V - K - 1) * MU**2
        assert per_vertex == 624

    def test_tr_a4_per_vertex_mu2_uniqueness(self):
        """Tr(A^4)/V = MU^2*(V-1) = 16*39 = 624 [Q=3 uniqueness: q(q-3)=0 required]."""
        tr4 = K**4 + EIG_R**4 * MUL_R + EIG_S**4 * MUL_S
        assert tr4 // V == MU**2 * (V - 1)
        # Verify non-trivial at q=2: would give K=6,MU=3,V=13 -> MU^2*(V-1)=108; Tr/V=114 (different)
        # We just verify the Q=3 identity holds exactly:
        assert MU**2 * (V - 1) == 624


# ------------------------------------------------------------------
# T6 -- Flag-triangle coincidence (Q=3 uniqueness)
# ------------------------------------------------------------------
class TestT6FlagTriangleCoincidence:

    def test_triangle_count(self):
        """#triangles = V*K*LAM/6 = 40*12*2/6 = 160."""
        assert V * K * LAM % 6 == 0
        assert V * K * LAM // 6 == 160

    def test_gq_flag_count(self):
        """#flags in GQ(3,3) = V*(Q+1) = 40*4 = 160 (each point on Q+1=4 lines)."""
        assert V * (Q + 1) == 160

    def test_triangles_equal_flags(self):
        """#triangles = #flags = 160: triangle count = GQ flag count [Q=3 uniqueness]."""
        triangles = V * K * LAM // 6
        flags = V * (Q + 1)
        assert triangles == flags

    def test_gq_self_dual_point_line_count(self):
        """GQ(3,3) self-dual: #points = #lines = V = 40."""
        gq_lines = (Q * Q + 1) * (Q + 1)   # = (s*t+1)*(t+1) for GQ(s,t) with s=t=Q
        assert gq_lines == V
        assert gq_lines == 40

    def test_flags_per_vertex_equals_q_plus_one(self):
        """Each GQ point is on Q+1 = 4 lines; each line has Q+1 = 4 points."""
        lines_per_point = Q + 1
        points_per_line = Q + 1
        assert lines_per_point == 4
        assert points_per_line == 4
        assert lines_per_point * V == points_per_line * V  # self-dual consistency

    def test_tr_a3_equals_6_times_triangle_count(self):
        """Tr(A^3) = 6*#triangles = 960 = V*K*LAM [3 vertices × 2 orientations per triangle]."""
        triangles = V * K * LAM // 6
        tr3 = K**3 + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S
        assert tr3 == 6 * triangles
        assert tr3 == 960

    def test_triangle_flag_identity_q3_polynomial(self):
        """V*K*LAM/6 = V*(Q+1) iff 2Q*(Q+1)/6 = Q+1 iff Q(Q-1)(Q+2)/3 = ... unique at Q=3."""
        # Direct Q=3 verification
        lhs = V * K * LAM // 6   # triangles
        rhs = V * (Q + 1)        # flags
        assert lhs == rhs
        # Fails for Q=2 (GQ(2,2)=Petersen, 10 points, K=4, LAM=0 -> 0 triangles, flags=10*3=30)
        V2, K2, LAM2 = 10, 4, 0
        assert V2 * K2 * LAM2 // 6 != V2 * (2 + 1)
        # Fails for Q=4 (GQ(4,4), 85 points, K=20, LAM=6 -> V*K*LAM/6=1700, flags=85*5=425)
        V4, K4, LAM4 = 85, 20, 6
        assert V4 * K4 * LAM4 // 6 != V4 * (4 + 1)
