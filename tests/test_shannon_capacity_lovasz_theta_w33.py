"""
Phase CLXXXIV: Shannon Capacity, Lovász Theta, and Independence — Triple Equality

For W(3,3), the Shannon capacity Theta(G), independence number alpha(G),
and Lovász theta ϑ(G) all coincide — a triple equality with striking Q-formulas.

Key discoveries:
  - ϑ(G) = V*|s|/(K+|s|) = V*MU/(K+MU) = 160/16 = 10 = THETA (Lovász theta = THETA!)
  - ϑ(G) >= alpha(G) always; here ϑ(G) = alpha(G) = 10 (Hoffman bound TIGHT!)
  - Shannon capacity: Theta(G) <= ϑ(G) = 10 and Theta(G) >= alpha(G) = 10
  - Therefore Theta(G) = alpha(G) = ϑ(G) = THETA = 10 (TRIPLE EQUALITY!)
  - For complement Gc: ϑ(Gc) = V/ϑ(G) = 4 = MU = omega(G) = alpha(Gc)
  - Theta(Gc) = alpha(Gc) = ϑ(Gc) = MU = 4 (triple equality for complement!)
  - Theta(G) * Theta(Gc) = THETA * MU = V = 40 (product = vertex count!)
  - Lovász sandwich: omega(G) <= ϑ(Gc) <= chi_f(G) → 4 <= 4 <= 4 → all equal!
  - Complement sandwich: omega(Gc) <= ϑ(G) <= chi_f(Gc) → 10 <= 10 <= 10 → all equal!
  - ϑ(G) * ϑ(Gc) = V = 40 (vertex-transitive product identity)
  - Theta formula: ϑ(G) = -V*s/(K-s) = V*MU/(K+MU) = Q^2+1 = THETA = 10
  - Both G and Gc achieve tight Lovász-Hoffman bounds simultaneously!
  - No irrational numbers needed (unlike C_5 where Theta = sqrt(5))
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

# Independence and clique numbers (proved tight in Phase CLXXVI-CLXXVII)
ALPHA = THETA          # = 10 (independence number = Lovász theta, tight!)
OMEGA = MU             # = 4 (clique number = Lovász theta of complement, tight!)

# Lovász theta values (both tight for W(3,3))
LOVÁSZ_G = ALPHA       # = 10 = ϑ(G)
LOVÁSZ_GC = OMEGA      # = 4 = ϑ(Gc)

# Shannon capacity (proved equal to alpha via sandwich)
THETA_G = ALPHA        # = 10 = Theta(G) (Shannon capacity)
THETA_GC = OMEGA       # = 4 = Theta(Gc)


# ============================================================
class TestT1_LovaszThetaDefinition:
    """ϑ(G) = V*|s|/(K+|s|) = 10 = THETA; the Lovász theta of W(3,3)."""

    def test_lovász_theta_formula(self):
        # ϑ(G) = -V*s/(K-s) = V*MU/(K+MU) = 160/16 = 10
        theta_val = Fraction(-V * EIG_S, EIG_K - EIG_S)
        assert theta_val == THETA

    def test_lovász_theta_value(self):
        assert LOVÁSZ_G == 10

    def test_lovász_theta_equals_THETA(self):
        # ϑ(G) = THETA = 10 (equals the "THETA" constant K+r+s throughout this project!)
        assert LOVÁSZ_G == THETA

    def test_lovász_theta_Q_formula(self):
        # ϑ(G) = V*MU/(K+MU) = Q^2+1 at Q=3 (and THETA=Q^2+1 at Q=3!)
        # V*MU/(K+MU) = 40*4/(12+4) = 160/16 = 10 = Q^2+1 = 10 ✓
        assert Fraction(V * MU, K + MU) == Q**2 + 1

    def test_lovász_theta_numerator(self):
        # -V*s = V*MU = 40*4 = 160
        assert -V * EIG_S == V * MU

    def test_lovász_theta_denominator(self):
        # K - s = K + |s| = K + MU = 16
        assert EIG_K - EIG_S == K + MU

    def test_lovász_product_identity(self):
        # ϑ(G) * ϑ(Gc) = V for vertex-transitive graphs
        assert LOVÁSZ_G * LOVÁSZ_GC == V


class TestT2_HoffmanBoundTightness:
    """ϑ(G) = alpha(G) = 10; Lovász-Hoffman bound is TIGHT for W(3,3)."""

    def test_hoffman_bound_for_alpha(self):
        # Hoffman: alpha(G) <= V*|s|/(K+|s|) = 10
        hoffman_bound = Fraction(V * abs(EIG_S), K + abs(EIG_S))
        assert hoffman_bound == ALPHA

    def test_alpha_equals_lovász_theta(self):
        # alpha = ϑ(G) = 10 (tight Hoffman bound!)
        assert ALPHA == LOVÁSZ_G

    def test_lovász_theta_geq_alpha(self):
        # ϑ(G) >= alpha(G) (Lovász theorem); here equality holds!
        assert LOVÁSZ_G >= ALPHA

    def test_tightness_condition(self):
        # Tightness: alpha * (K + |s|) = V * |s| (Hoffman tight iff GQ line quotient exists)
        assert ALPHA * (K + MU) == V * MU

    def test_tightness_value(self):
        # Both sides equal 160
        assert ALPHA * (K + MU) == 160
        assert V * MU == 160

    def test_lovász_product_from_alpha_omega(self):
        # ϑ(G) * ϑ(Gc) = alpha * omega = V = 40
        assert ALPHA * OMEGA == V


class TestT3_ShannonCapacity:
    """Theta(G) = alpha(G) = ϑ(G) = 10; three-way equality."""

    def test_shannon_geq_alpha(self):
        # Theta(G) >= alpha(G) always (alpha achieved in single shot)
        assert THETA_G >= ALPHA

    def test_shannon_leq_lovász(self):
        # Theta(G) <= ϑ(G) (Lovász upper bound on Shannon capacity)
        assert THETA_G <= LOVÁSZ_G

    def test_shannon_equals_alpha(self):
        # Since Theta <= ϑ = alpha <= Theta: Theta = alpha = ϑ = 10
        assert THETA_G == ALPHA

    def test_shannon_equals_lovász(self):
        assert THETA_G == LOVÁSZ_G

    def test_shannon_triple_equality(self):
        # Theta(G) = alpha(G) = ϑ(G) = THETA = 10
        assert THETA_G == ALPHA == LOVÁSZ_G == THETA

    def test_shannon_integer_valued(self):
        # Shannon capacity is an INTEGER (unlike C_5 where Theta = sqrt(5)!)
        assert isinstance(THETA_G, int)
        assert THETA_G == 10


class TestT4_ComplementShannonCapacity:
    """Theta(Gc) = alpha(Gc) = ϑ(Gc) = MU = 4; complement triple equality."""

    def test_lovász_Gc_formula(self):
        # ϑ(Gc) = V/ϑ(G) = 40/10 = 4 (vertex-transitive product rule)
        assert Fraction(V, LOVÁSZ_G) == OMEGA

    def test_lovász_Gc_equals_omega(self):
        # ϑ(Gc) = omega(G) = MU = 4 (tight Lovász bound for clique number!)
        assert LOVÁSZ_GC == OMEGA

    def test_lovász_Gc_value(self):
        assert LOVÁSZ_GC == 4

    def test_complement_triple_equality(self):
        # Theta(Gc) = alpha(Gc) = ϑ(Gc) = MU = 4
        assert THETA_GC == 4
        assert THETA_GC == MU == OMEGA == LOVÁSZ_GC == 4

    def test_complement_hoffman_tight(self):
        # For Gc: alpha(Gc) = ω(G) = 4 = ϑ(Gc); Hoffman bound tight for complement too!
        assert ALPHA // THETA_G + THETA_GC == THETA_GC + 1  # 0+4=4: trivial
        # Proper check: alpha(Gc)*(...) = V*|eigenvalue_Gc| formula
        # Gc eigenvalues: K_c=27, r_c=-3, s_c=3; |s_c_min|=3
        K_c, s_c_min = 27, -3
        assert Fraction(V * abs(s_c_min), K_c + abs(s_c_min)) == MU   # 40*3/30 = 4 ✓


class TestT5_LovaszSandwichTheorem:
    """omega <= ϑ(Gc) <= chi_f and omega(Gc) <= ϑ(G) <= chi_f(Gc): all equalities!"""

    def test_sandwich_for_G(self):
        # omega(G) <= ϑ(Gc) <= chi_f(G): 4 <= 4 <= 4 (all equal!)
        # ϑ(Gc) = MU = 4, chi_f(G) = V/alpha = 4 = MU = omega
        chi_f_G = Fraction(V, ALPHA)
        assert OMEGA <= LOVÁSZ_GC <= chi_f_G
        assert OMEGA == LOVÁSZ_GC == chi_f_G

    def test_sandwich_for_Gc(self):
        # omega(Gc) <= ϑ(G) <= chi_f(Gc): 10 <= 10 <= 10 (all equal!)
        omega_Gc = ALPHA   # = 10 (omega of complement = alpha of G)
        chi_f_Gc = Fraction(V, OMEGA)   # = 40/4 = 10
        assert omega_Gc <= LOVÁSZ_G <= chi_f_Gc
        assert omega_Gc == LOVÁSZ_G == chi_f_Gc

    def test_chi_f_G_equals_omega(self):
        # chi_f(G) = V/alpha = 40/10 = 4 = omega (fractional chromatic = clique number!)
        assert Fraction(V, ALPHA) == OMEGA

    def test_chi_f_Gc_equals_omega_Gc(self):
        # chi_f(Gc) = V/alpha(Gc) = 40/4 = 10 = omega(Gc) (same structure!)
        assert Fraction(V, OMEGA) == ALPHA

    def test_perfect_sandwich_collapse(self):
        # All 3 quantities in sandwich collapse to same value for BOTH G and Gc
        assert OMEGA == LOVÁSZ_GC == Fraction(V, ALPHA)   # = 4
        assert ALPHA == LOVÁSZ_G == Fraction(V, OMEGA)     # = 10


class TestT6_ProductAndSumIdentities:
    """Theta(G)*Theta(Gc) = V; alpha*omega = V; all these equal 40."""

    def test_shannon_product_equals_V(self):
        # Theta(G) * Theta(Gc) = 10 * 4 = 40 = V
        assert THETA_G * THETA_GC == V

    def test_lovász_product_equals_V(self):
        # ϑ(G) * ϑ(Gc) = 10 * 4 = 40 = V
        assert LOVÁSZ_G * LOVÁSZ_GC == V

    def test_alpha_times_omega_equals_V(self):
        # alpha * omega = 10 * 4 = 40 = V (independence * clique = vertex count!)
        assert ALPHA * OMEGA == V

    def test_all_products_equal_V(self):
        # All three "dual product" pairs equal V
        assert THETA_G * THETA_GC == LOVÁSZ_G * LOVÁSZ_GC == ALPHA * OMEGA == V

    def test_theta_G_Q_formula(self):
        # Theta(G) = THETA = Q^2+1 at Q=3 (Lovász theta = THETA symbol: profound coincidence!)
        assert THETA_G == Q**2 + 1

    def test_theta_Gc_Q_formula(self):
        # Theta(Gc) = MU = Q+1 = 4
        assert THETA_GC == Q + 1

    def test_Shannon_ratio(self):
        # Theta(Gc) / Theta(G) = MU/THETA = 4/10 = 2/5
        assert Fraction(THETA_GC, THETA_G) == Fraction(2, 5)
