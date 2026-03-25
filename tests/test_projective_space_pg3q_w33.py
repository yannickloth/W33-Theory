"""
Phase CCIII -- Projective Space PG(3,Q) and Symplectic Incidence Bridge
=======================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The symplectic polar space Sp(4,3) lives inside PG(3,3), a projective
3-space over GF(3).  The key parameter bridge:

  |PG(3,Q)|  = V = 40  (W33 vertices = all PG(3,3) points)
  #lines PG(3,Q) = (Q^2+1)*(Q^2+Q+1) = THETA*Phi_3(Q) = 130
  #isotropic lines = V = 40  (GQ(3,3) self-dual)
  #non-isotropic lines = Q^2*THETA = 90
  #non-iso flags = V*Q^2 = MUL_R*MUL_S = 360  [Q=3 uniqueness]
  #PG flags = V*Phi_3(Q) = THETA*52 = 520  (52 = dim F4)
  #planes PG(3,Q) = V  (projective duality)

All arithmetic is exact integers.

Six test groups (37 tests total):
  T1  PG(n,Q) point counts    -- hierarchy 1,4,13,40 and Heawood-Fano bridge
  T2  Line counts PG(3,Q)     -- 130 = THETA*Phi3 = iso+noniso = 40+90
  T3  Isotropy split          -- iso/noniso lines per point (Q+1 vs Q^2)
  T4  Flag counts and F4      -- 520 = THETA*52; 360 = MUL_R*MUL_S [Q=3 only]
  T5  Projective duality      -- planes = V = 40; total subspaces = 210
  T6  Q=3 uniqueness and cross-structure
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
P_ORDER = 96;  H_ORDER = 192

# Projective space PG(n,Q) point counts [n=0..3]
PG0 = 1    # |PG(0,3)|
PG1 = 4    # |PG(1,3)| = Q+1
PG2 = 13   # |PG(2,3)| = Q^2+Q+1 = Phi_3(Q)
PG3 = 40   # |PG(3,3)| = V

# PG(3,Q) structural counts
PG3_LINES   = 130   # (Q^2+1)*(Q^2+Q+1)
ISO_LINES   = 40    # totally isotropic lines = GQ(3,3) lines = V
NONISO_LINES = 90   # non-isotropic lines = Q^2*THETA
PG3_FLAGS   = 520   # V * Phi_3(Q) = V * PG2
GQ_FLAGS    = 160   # V * (Q+1)
NONISO_FLAGS = 360  # V * Q^2 = MUL_R * MUL_S
PG3_PLANES  = 40    # = V by projective duality


# ------------------------------------------------------------------
# T1 -- PG(n,Q) point counts
# ------------------------------------------------------------------
class TestT1PGPointCounts:

    def test_pg0_is_one(self):
        """|PG(0,Q)| = 1: a projective point (trivial)."""
        assert (Q**1 - 1) // (Q - 1) == PG0
        assert PG0 == 1

    def test_pg1_equals_q_plus_one(self):
        """|PG(1,Q)| = Q+1 = 4: a projective line has Q+1 points."""
        assert (Q**2 - 1) // (Q - 1) == PG1
        assert PG1 == Q + 1

    def test_pg2_equals_phi3(self):
        """|PG(2,Q)| = Q^2+Q+1 = 13 = Phi_3(Q): projective plane point count."""
        assert (Q**3 - 1) // (Q - 1) == PG2
        assert PG2 == Q**2 + Q + 1

    def test_pg3_equals_v(self):
        """|PG(3,Q)| = Q^3+Q^2+Q+1 = 40 = V: W33 vertices = all PG(3,3) points."""
        assert (Q**4 - 1) // (Q - 1) == PG3
        assert PG3 == V

    def test_pg3_geometric_series(self):
        """|PG(3,Q)| = Q^3+Q^2+Q+1 = (Q^4-1)/(Q-1): geometric series formula."""
        assert Q**3 + Q**2 + Q + 1 == V
        assert (Q**4 - 1) // (Q - 1) == V

    def test_pg2_equals_nh_minus_one(self):
        """|PG(2,Q)| = Phi_3(Q) = 13 = N_H-1 [coincidence unique to Q=3]."""
        assert PG2 == N_H - 1
        assert PG2 == Q**2 + Q + 1
        # For q=2: |PG(2,2)| = 7 = FANO_ORDER (different coincidence!)
        assert (2**3 - 1) // (2 - 1) == FANO_ORDER

    def test_pg_hierarchy_product(self):
        """|PG(3,Q)| = |PG(1,Q)| * |PG(2,Q)| - |PG(0,Q)| ... no; check: V = PG2+PG1*(Q+1)."""
        # V = PG3 = (Q+1)(Q^2+1) = PG1 * THETA
        assert PG1 * THETA == V


# ------------------------------------------------------------------
# T2 -- Line counts PG(3,Q)
# ------------------------------------------------------------------
class TestT2LineCountsPG3Q:

    def test_pg3_line_count(self):
        """#lines in PG(3,Q) = (Q^2+1)*(Q^2+Q+1) = THETA*PG2 = 130."""
        assert (Q**2 + 1) * (Q**2 + Q + 1) == PG3_LINES
        assert PG3_LINES == 130

    def test_pg3_lines_equals_theta_phi3(self):
        """#lines = THETA * Phi_3(Q) = 10*13 = 130."""
        assert PG3_LINES == THETA * PG2

    def test_pg3_lines_equals_theta_nh_minus_one(self):
        """#lines = THETA * (N_H-1) = 10*13 = 130 [unique to Q=3]."""
        assert PG3_LINES == THETA * (N_H - 1)

    def test_pg3_lines_split_iso_noniso(self):
        """#lines = #iso + #non-iso = 40 + 90 = 130."""
        assert ISO_LINES + NONISO_LINES == PG3_LINES

    def test_noniso_lines_formula(self):
        """#non-iso lines = Q^2 * THETA = 9*10 = 90."""
        assert Q**2 * THETA == NONISO_LINES
        assert NONISO_LINES == 90

    def test_iso_lines_equals_v(self):
        """#iso (GQ) lines = V = 40: GQ(3,3) self-duality (same count as points)."""
        assert ISO_LINES == V


# ------------------------------------------------------------------
# T3 -- Isotropy split per point
# ------------------------------------------------------------------
class TestT3IsotropySplitPerPoint:

    def test_lines_through_point_total(self):
        """Lines through a point in PG(3,Q) = Phi_3(Q) = Q^2+Q+1 = 13."""
        assert Q**2 + Q + 1 == PG2
        assert PG2 == 13

    def test_iso_lines_through_point(self):
        """Isotropic lines through a GQ point = Q+1 = 4 (each point on Q+1 GQ lines)."""
        assert Q + 1 == 4

    def test_noniso_lines_through_point(self):
        """Non-iso lines through a point = Q^2 = 9 = Phi_3(Q) - (Q+1)."""
        assert Q**2 == PG2 - (Q + 1)
        assert Q**2 == 9

    def test_lines_through_point_sums(self):
        """Phi_3(Q) = (Q+1) + Q^2: iso + non-iso lines through any point."""
        assert PG2 == (Q + 1) + Q**2

    def test_noniso_flags_per_point(self):
        """Each point has Q^2 = 9 non-iso lines; V*Q^2 = 360 total non-iso flags."""
        assert V * Q**2 == NONISO_FLAGS
        assert V * Q**2 == 360

    def test_iso_flags_per_point(self):
        """Each point has Q+1 = 4 iso lines; V*(Q+1) = GQ_FLAGS = 160 iso flags."""
        assert V * (Q + 1) == GQ_FLAGS


# ------------------------------------------------------------------
# T4 -- Flag counts and F4 dimension bridge
# ------------------------------------------------------------------
class TestT4FlagCountsAndF4:

    def test_pg3_total_flags(self):
        """PG(3,Q) total flags = V * Phi_3(Q) = 40*13 = 520."""
        assert V * PG2 == PG3_FLAGS
        assert PG3_FLAGS == 520

    def test_gq_flags(self):
        """GQ(3,3) flags = V*(Q+1) = 40*4 = 160 = #triangles in W33."""
        assert V * (Q + 1) == GQ_FLAGS
        assert GQ_FLAGS == 160

    def test_noniso_flags_equals_mul_r_mul_s(self):
        """V*Q^2 = MUL_R*MUL_S = 360: non-iso flags = eigenvalue multiplicity product [Q=3 only]."""
        assert NONISO_FLAGS == MUL_R * MUL_S

    def test_flag_split(self):
        """PG flags = GQ flags + non-iso flags = 160 + 360 = 520."""
        assert GQ_FLAGS + NONISO_FLAGS == PG3_FLAGS

    def test_pg3_flags_theta_f4(self):
        """PG(3,Q) flags = THETA * 52 where 52 = dim(F4) = Phi_3(Q)*MU = 13*4."""
        dim_f4 = PG2 * MU   # = 13*4 = 52
        assert dim_f4 == 52
        assert PG3_FLAGS == THETA * dim_f4

    def test_noniso_mul_product_q3_unique(self):
        """V*Q^2 = MUL_R*MUL_S only at Q=3; fails at Q=2 and Q=4."""
        # Q=2: GQ(2,2) with V=15, Q^2=4: V*Q^2=60; MUL_R*MUL_S=9*5=45 != 60
        V2 = 15;  mul_r2, mul_s2 = 9, 5
        assert V2 * 4 != mul_r2 * mul_s2
        # Q=4: GQ(4,4) with V=85, Q^2=16: V*Q^2=1360; MUL_R*MUL_S=68*25=1700 != 1360
        V4 = 85;  mul_r4, mul_s4 = 68, 25
        assert V4 * 16 != mul_r4 * mul_s4


# ------------------------------------------------------------------
# T5 -- Projective duality
# ------------------------------------------------------------------
class TestT5ProjectiveDuality:

    def test_planes_equal_v(self):
        """#hyperplanes in PG(3,Q) = |PG(3,Q)| = V = 40 (self-dual projective space)."""
        assert PG3_PLANES == V
        assert (Q**4 - 1) // (Q - 1) == PG3_PLANES

    def test_lines_in_plane(self):
        """A plane PG(2,Q) in PG(3,Q) has Phi_3(Q) = 13 lines."""
        assert Q**2 + Q + 1 == PG2
        assert PG2 == 13

    def test_planes_through_line(self):
        """Each line in PG(3,Q) lies in Q+1 = 4 planes [pencil of planes]."""
        planes_per_line = Q + 1
        assert planes_per_line == 4
        # Verify via counting: #line-plane flags = PG3_LINES * (Q+1) = PG3_PLANES * Phi_3(Q)
        assert PG3_LINES * (Q + 1) == PG3_PLANES * PG2

    def test_total_subspace_count(self):
        """Total subspaces in PG(3,Q) = #pts + #lines + #planes = 40+130+40 = 210."""
        total = PG0 + PG1 * (PG3 // PG1) + PG3_LINES + PG3_PLANES
        # Simplified: V + PG3_LINES + V = 2V + 130 = 210
        assert V + PG3_LINES + PG3_PLANES == 210

    def test_total_210_factored(self):
        """210 = 2*3*5*7: product of first four primes [Primorial(7)]."""
        assert V + PG3_LINES + PG3_PLANES == 2 * 3 * 5 * 7
        assert 210 == 2 * 3 * 5 * 7


# ------------------------------------------------------------------
# T6 -- Q=3 uniqueness and cross-structure
# ------------------------------------------------------------------
class TestT6Q3UniquenessAndCross:

    def test_pg2_fano_unique(self):
        """|PG(2,2)| = 7 = FANO_ORDER: the Fano plane is PG(2,2) [unique to Q=2]."""
        assert (2**3 - 1) // (2 - 1) == FANO_ORDER

    def test_pg2_q3_is_nh_minus_1(self):
        """|PG(2,3)| = 13 = N_H-1 [Q=3 coincidence: Heawood vertex count minus 1]."""
        assert PG2 == N_H - 1

    def test_v_pg2_product(self):
        """V * |PG(2,Q)| = 520 = PG flags = THETA * 52 = THETA * Phi_3 * MU."""
        assert V * PG2 == PG3_FLAGS

    def test_noniso_lines_v_over_theta(self):
        """#non-iso lines / V = Q^2/THETA ... no; #non-iso / #iso = Q^2/4 = 9/4 not integer.
        Instead: #non-iso = Q^2 * THETA = 90 while #iso = V = 40."""
        assert NONISO_LINES == Q**2 * THETA
        assert ISO_LINES == V
        # Ratio
        assert NONISO_LINES * V == ISO_LINES * Q**2 * THETA

    def test_pg3_lines_over_v(self):
        """PG3_LINES / V = 130/40 = 13/4 = PG2/(Q+1) [lines per point in GQ = Q+1]."""
        from fractions import Fraction
        ratio = Fraction(PG3_LINES, V)
        assert ratio == Fraction(PG2, Q + 1)

    def test_p_order_times_pg2(self):
        """|P| * Phi_3(Q) = 96*13 = 1248 = MUL_R * MUL_S * (THETA/3) ... """
        # 1248 = 96*13 = 2^5*3*13; and 1248 = V*H_ORDER/... 40*192/... hmm
        # Actually 1248 = 4*312 = 4*8*39 = 32*39 = (V-1)*32 = (V-1)*LAM^5
        val = P_ORDER * PG2
        assert val == (V - 1) * 2**5
        assert val == 1248

    def test_noniso_and_p_times_theta(self):
        """NONISO_FLAGS = MUL_R*MUL_S = 360 = P_ORDER*THETA/(Q-1) = 96*10/... no."""
        # 360 = MUL_R*MUL_S and also 360 = MUL_R*MUL_S directly
        # Also: 360 = (V-1)*MU*... 39*4 = 156 no
        # Clean: 360 = P_ORDER * THETA / |r1r2_cox| = 96*10/... nope
        # Just verify: 360 = 3*120 = 3*V*Q = 3*40*3 = 360 [3 = Q = |r0r1| coxeter]
        assert NONISO_FLAGS == Q * V * Q
        assert NONISO_FLAGS == 360
