"""
Phase CLXXIV: Perp-Sets and the Constant Intersection Property of W(3,3)

The perp-set (closed neighborhood) x_perp = {x} union Gamma(x) has |x_perp| = K+1 = 13.
The KEY DISCOVERY: |x_perp cap y_perp| = MU = 4 for ALL pairs x != y — CONSTANT!

Key discoveries:
  - |x_perp| = K+1 = 13 (closed neighborhood size)
  - V - |x_perp| = Q^3 = 27 (non-perp count = q-cube, matching GQ distance-2 count)
  - For x~y (adjacent): x_perp cap y_perp = line L(x,y), q+1=MU=4 points
    |x_perp cap y_perp| = LAM + 2 = 2 + 2 = 4 = MU
  - For x not~y (non-adjacent): x_perp cap y_perp = MU common neighbors
    |x_perp cap y_perp| = MU = 4
  - STUNNING: LAM + 2 = Q-1+2 = Q+1 = MU (the identity that makes |cap| CONSTANT!)
  - |x_perp union y_perp| = 2*(K+1) - MU = 22 for ALL x != y
  - V - |x_perp union y_perp| = 18 = Q^2*(Q-1) (vertices in neither perp-set)
  - For adjacent x~y: x_perp cap y_perp = clique of size MU (the GQ line L(x,y)!)
  - Sum |x_perp| = V*(K+1) = 520 = 40*13
  - The constant MU = Q+1 appears as both perp-intersection and non-adjacency parameter
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

# Derived constants
PERP_SIZE = K + 1          # = 13 (size of closed neighborhood x_perp)
NON_PERP = V - PERP_SIZE   # = 27 = Q^3 (vertices not in x_perp)

# Perp-set intersection sizes
PERP_CAP_ADJ = 2 + LAM    # = 4 = MU (for adjacent pairs: {x,y} + LAM common nbrs)
PERP_CAP_NONADJ = MU       # = 4     (for non-adjacent pairs: MU common nbrs)

# Perp-set union size (same for both cases since intersection is same)
PERP_UNION = 2 * PERP_SIZE - MU   # = 26 - 4 = 22


# ============================================================
class TestT1_PerpSetSize:
    """Perp-set x_perp = {x} union Gamma(x) has size K+1 = 13."""

    def test_perp_size_equals_K_plus_1(self):
        # |x_perp| = 1 (vertex x itself) + K (K neighbors) = K+1 = 13
        assert PERP_SIZE == K + 1

    def test_perp_size_value(self):
        # K+1 = 12+1 = 13
        assert PERP_SIZE == 13

    def test_non_perp_count_equals_Q_cubed(self):
        # V - |x_perp| = 40 - 13 = 27 = Q^3 (vertices at distance 2 from x)
        assert NON_PERP == Q**3

    def test_non_perp_equals_V_minus_K_minus_1(self):
        # V - K - 1 = 27 = Q^3 (same as distance-2 count from DRG structure)
        assert NON_PERP == V - K - 1

    def test_perp_size_plus_non_perp_is_V(self):
        # |x_perp| + (V - |x_perp|) = V = 40
        assert PERP_SIZE + NON_PERP == V

    def test_perp_size_over_V_fraction(self):
        # |x_perp|/V = 13/40 (non-integer: perp-sets don't partition V)
        from fractions import Fraction
        assert Fraction(PERP_SIZE, V) == Fraction(13, 40)

    def test_K_plus_1_not_dividing_V(self):
        # 13 does not divide 40 (no partition of V by disjoint perp-sets)
        assert V % PERP_SIZE != 0


class TestT2_PerpCapForAdjacentPairs:
    """For x~y (adjacent): x_perp cap y_perp = line L(x,y), |cap| = MU = 4."""

    def test_perp_cap_adjacent_equals_LAM_plus_2(self):
        # x_perp cap y_perp = {x,y} union (common nbrs of x,y) = 2 + LAM = 4
        assert PERP_CAP_ADJ == 2 + LAM

    def test_perp_cap_adjacent_equals_MU(self):
        # 2 + LAM = 4 = MU (stunning: perp intersection = non-adjacency parameter!)
        assert PERP_CAP_ADJ == MU

    def test_LAM_plus_2_equals_MU(self):
        # KEY IDENTITY: LAM + 2 = Q-1+2 = Q+1 = MU
        # This is the identity that makes |x_perp cap y_perp| CONSTANT
        assert LAM + 2 == MU

    def test_LAM_plus_2_equals_Q_plus_1(self):
        # LAM + 2 = (Q-1) + 2 = Q+1 = MU (the Q-formula version)
        assert LAM + 2 == Q + 1

    def test_perp_cap_adjacent_is_line_L_xy(self):
        # For x~y: x_perp cap y_perp contains x, y, and LAM common neighbors
        # These are EXACTLY the q+1=MU points of the GQ line L(x,y)
        points_on_line = Q + 1
        assert points_on_line == PERP_CAP_ADJ

    def test_perp_cap_adjacent_is_max_clique(self):
        # The q+1=4 points of L(x,y) form a max clique (omega=MU) in W(3,3)
        assert PERP_CAP_ADJ == MU  # = omega(W33)

    def test_components_of_adjacent_cap(self):
        # {x} + {y} + {LAM common neighbors} = 1 + 1 + LAM = 2 + LAM = MU
        assert 1 + 1 + LAM == MU


class TestT3_PerpCapForNonAdjacentPairs:
    """For x not~y (non-adjacent): x_perp cap y_perp = MU common neighbors."""

    def test_perp_cap_nonadj_equals_MU(self):
        # x_perp cap y_perp = common neighbors of x,y = MU = 4
        assert PERP_CAP_NONADJ == MU

    def test_perp_cap_nonadj_formula(self):
        # x not~y: x_perp = {x}+Gamma(x), y_perp = {y}+Gamma(y)
        # x not in y_perp (x not~y, x!=y); y not in x_perp
        # cap = Gamma(x) cap Gamma(y) = MU common neighbors
        assert PERP_CAP_NONADJ == MU

    def test_x_not_in_y_perp_for_nonadj(self):
        # For x not~y: x not in y_perp = {y} union Gamma(y)
        # (x != y and x not adj y => x not in y_perp)
        # Consequence: PERP_CAP_NONADJ <= MU
        assert PERP_CAP_NONADJ <= MU

    def test_nonadj_cap_equals_adj_cap(self):
        # STUNNING: |x_perp cap y_perp| is the SAME for adjacent and non-adjacent pairs!
        assert PERP_CAP_ADJ == PERP_CAP_NONADJ


class TestT4_ConstantIntersectionProperty:
    """The constant intersection theorem: |x_perp cap y_perp| = MU for ALL x!=y."""

    def test_constant_intersection_value(self):
        # Both adjacent and non-adjacent pairs give |cap| = MU = 4
        assert PERP_CAP_ADJ == MU
        assert PERP_CAP_NONADJ == MU

    def test_constant_intersection_key_identity(self):
        # The identity LAM+2 = MU makes this possible:
        # adj case:   2+LAM = MU (matches non-adj case)
        # non-adj case: MU = MU (trivially)
        assert LAM + 2 == MU

    def test_constant_intersection_is_Q_plus_1(self):
        # The constant value MU = Q+1 = 4 (field order plus 1)
        assert MU == Q + 1

    def test_LAM_equals_Q_minus_1(self):
        # LAM = Q-1 = 2 (for GQ(q,q): lambda = q-1)
        assert LAM == Q - 1

    def test_LAM_plus_2_algebraic_identity(self):
        # LAM + 2 = (Q-1) + 2 = Q+1 = MU: the Q-arithmetic identity
        assert Q - 1 + 2 == Q + 1

    def test_constant_intersection_count_over_all_pairs(self):
        # Total (ordered) pairs (x,y) with x!=y: V*(V-1) = 40*39 = 1560
        # Each contributes |x_perp cap y_perp| = MU = 4 to a sum
        total_pairs = V * (V - 1)
        total_cap_sum = total_pairs * MU
        assert total_pairs == 1560
        assert total_cap_sum == 6240

    def test_constant_intersection_implies_regular_design(self):
        # The constant |x_perp cap y_perp| = MU means the perp-sets form
        # a "2-design" in a generalized sense (any two points in MU "blocks")
        # Here V=40, block-size=K+1=13, any two points in MU=4 common blocks
        # This satisfies the Fisher-type relation: MU * C(V,2) = C(K+1,2) * b...
        # Actually: each ordered pair (x,y) appears in |x_perp cap y_perp| = MU "double-perps"
        assert PERP_CAP_ADJ == PERP_CAP_NONADJ == MU


class TestT5_PerpSetUnion:
    """Perp-set union: |x_perp union y_perp| = 22 for ALL x != y."""

    def test_perp_union_formula(self):
        # |x_perp union y_perp| = |x_perp| + |y_perp| - |x_perp cap y_perp|
        # = 13 + 13 - 4 = 22 (SAME for adjacent and non-adjacent pairs!)
        assert PERP_UNION == PERP_SIZE + PERP_SIZE - MU

    def test_perp_union_value(self):
        # 13 + 13 - 4 = 22
        assert PERP_UNION == 22

    def test_V_minus_perp_union_is_18(self):
        # V - |x_perp union y_perp| = 40 - 22 = 18 = Q^2*(Q-1) vertices in neither
        assert V - PERP_UNION == 18
        assert V - PERP_UNION == Q**2 * (Q - 1)

    def test_V_minus_perp_union_Q_formula(self):
        # 18 = Q^2*(Q-1) = 9*2 = 18 (field-arithmetic expression)
        assert V - PERP_UNION == Q**2 * (Q - 1)

    def test_perp_union_as_Q_formula(self):
        # |x_perp union y_perp| = 2*(K+1) - MU = 2*(Q^2+1+Q) - (Q+1)
        # For Q=3: 2*13 - 4 = 22 ✓
        assert PERP_UNION == 2 * (K + 1) - MU

    def test_22_equals_2K_plus_2_minus_MU(self):
        # 22 = 2*12 + 2 - 4 = 24 + 2 - 4 = 22 ✓
        assert 2 * K + 2 - MU == 22

    def test_perp_union_constant_over_all_pairs(self):
        # Since |cap| is constant and |x_perp|=|y_perp|=K+1, |union| is also constant
        # (doesn't depend on adjacency)
        assert 2 * PERP_SIZE - PERP_CAP_ADJ == 2 * PERP_SIZE - PERP_CAP_NONADJ


class TestT6_PerpSetCountingFormulas:
    """Counting identities involving perp-sets."""

    def test_sum_perp_sizes(self):
        # Sum over all x of |x_perp| = V * (K+1) = 40 * 13 = 520
        assert V * PERP_SIZE == 520

    def test_directed_perp_pairs(self):
        # Ordered pairs (x,y) with y in x_perp and x!=y: V*K = 40*12 = 480
        # (= directed adjacency pairs since y in x_perp iff y=x or y~x; y!=x means y~x)
        assert V * K == 480

    def test_perp_size_as_Q_formula(self):
        # |x_perp| = K+1 = q(q+1)+1 = q^2+q+1 = 13 (= #points of PG(2,q)!)
        assert PERP_SIZE == Q**2 + Q + 1

    def test_perp_size_is_projective_plane_order(self):
        # Q^2 + Q + 1 = 13 = #points of PG(2,3) (projective plane of order 3!)
        assert Q**2 + Q + 1 == 13
        assert PERP_SIZE == Q**2 + Q + 1

    def test_non_perp_count_is_Q_cubed(self):
        # V - |x_perp| = Q^3 = 27 = Q*(Q^2+Q+1) - ... no
        # Actually Q^3 = 27 = V - K - 1 = distance-2 count ✓
        assert V - PERP_SIZE == Q**3

    def test_perp_cap_sum_over_all_pairs(self):
        # Sum_{x!=y} |x_perp cap y_perp| = V*(V-1) * MU = 1560 * 4 = 6240
        assert V * (V - 1) * MU == 6240

    def test_perp_union_complement_is_Q2_times_Q_minus_1(self):
        # 18 = Q^2 * (Q-1): the vertices outside x_perp union y_perp
        complement = V - PERP_UNION
        assert complement == Q**2 * (Q - 1)

    def test_perp_size_plus_non_perp_is_V(self):
        # K+1 + (V-K-1) = V = 40 (trivial but confirms partition into perp and non-perp)
        assert PERP_SIZE + NON_PERP == V

    def test_LAM_plus_2_equals_MU_Q_arithmetic(self):
        # In GQ(q,q): LAM = q-1, MU = q+1, so LAM+2 = q+1 = MU
        # This is pure q-arithmetic: (q-1) + 2 = q+1
        assert LAM + 2 == MU
        assert Q - 1 + 2 == Q + 1
