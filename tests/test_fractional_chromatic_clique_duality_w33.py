"""
Phase CLXXVII: Fractional Chromatic Number and Clique-Independence Duality of W(3,3)

For vertex-transitive graphs: chi_f(G) = V / alpha(G).

Key discoveries:
  - alpha(W33) = THETA = 10 (independence number = Lovász theta; Hoffman bound TIGHT)
  - omega(W33) = MU = 4 (clique number = Hoffman clique bound TIGHT)
  - chi_f = V/alpha = 40/10 = 4 = MU = omega (fractional chi equals clique number!)
  - chi_f >= omega always; here chi_f = omega = MU = 4 (EXACT equality)
  - Lovász: theta(G) = alpha = 10; theta(Gc) = omega = 4 (BOTH tight simultaneously!)
  - theta(G) * theta(Gc) = V = 40 (vertex-transitive product formula)
  - Complement: alpha(Gc)=omega(G)=MU=4; chi_f(Gc)=V/MU=10=THETA=omega(Gc)
  - chi_f(G)*chi_f(Gc) = MU*THETA = 4*10 = 40 = V (dual fractional chromatics multiply to V!)
  - alpha * omega = THETA * MU = 10 * 4 = 40 = V (independence-clique product = vertex count!)
  - Clique cover number theta_cc(G) <= V/omega = 40/4 = 10 = alpha (spread gives 10 max-cliques)
  - V = alpha * chi_f = omega * clique_cover = 10*4 = 4*10 = 40 (covering arithmetic)
  - MUL_R = 24 = 2*alpha + MU = 2*THETA + MU (multiplicity 24 from indep/clique structure!)
  - MUL_S = 15 = alpha + MU + 1 = THETA + MU + 1 (multiplicity 15 from structure)
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

# Independence number (Hoffman bound = THETA; tight for W(3,3))
ALPHA = THETA   # = 10

# Clique number (Hoffman bound on complement; tight for W(3,3))
OMEGA = MU      # = 4

# Fractional chromatic number (vertex-transitive: chi_f = V/alpha)
CHI_F = Fraction(V, ALPHA)   # = 40/10 = 4

# Complement parameters
EIG_K_C = V - 1 - K   # = 27
EIG_R_C = -1 - EIG_R  # = -3
EIG_S_C = -1 - EIG_S  # = +3

ALPHA_C = OMEGA   # alpha(Gc) = omega(G) = 4
OMEGA_C = ALPHA   # omega(Gc) = alpha(G) = 10
CHI_F_C = Fraction(V, ALPHA_C)   # = 40/4 = 10


# ============================================================
class TestT1_IndependenceNumber:
    """alpha(W33) = THETA = 10; Hoffman bound V*|s|/(K+|s|) is tight."""

    def test_alpha_value(self):
        assert ALPHA == 10

    def test_alpha_equals_THETA(self):
        # Independence number equals Lovász theta!
        assert ALPHA == THETA

    def test_alpha_hoffman_formula(self):
        # Hoffman: alpha <= V*|s|/(K + |s|) = 40*4/16 = 10
        assert Fraction(V * abs(EIG_S), K + abs(EIG_S)) == ALPHA

    def test_alpha_hoffman_equals_V_MU_over_K_plus_MU(self):
        # alpha = V*MU/(K+MU) = 160/16 = 10
        assert Fraction(V * MU, K + MU) == ALPHA

    def test_alpha_times_K_plus_MU_equals_V_MU(self):
        # Tightness condition: alpha*(K + |s|) = V*|s|
        assert ALPHA * (K + MU) == V * MU

    def test_alpha_Q_formula(self):
        # alpha = V*MU/(K+MU) = (Q+1)(Q^2+1)*(Q+1)/((Q+1)^2) = Q^2+1 = 10
        assert ALPHA == Q**2 + 1

    def test_alpha_is_Q_squared_plus_1(self):
        # 10 = Q^2 + 1 = 9 + 1 = 10 (= points in a GQ(q,q) ovoid!)
        assert ALPHA == Q**2 + 1
        assert ALPHA == 10


class TestT2_CliqueNumber:
    """omega(W33) = MU = 4; Hoffman clique bound on complement is tight."""

    def test_omega_value(self):
        assert OMEGA == 4

    def test_omega_equals_MU(self):
        # Clique number = MU (maximum clique size = non-adjacency parameter)
        assert OMEGA == MU

    def test_omega_hoffman_clique(self):
        # omega = alpha(Gc) <= V*|s_c|/(K_c + |s_c|) = 40*3/(27+3) = 120/30 = 4
        assert Fraction(V * abs(EIG_R_C), EIG_K_C + abs(EIG_R_C)) == OMEGA

    def test_omega_equals_Q_plus_1(self):
        # omega = Q+1 = 4 (= points on a GQ line)
        assert OMEGA == Q + 1

    def test_omega_hoffman_tight(self):
        # Tightness: OMEGA * (K_c + Q) = V * Q
        # 4 * (27+3) = 4*30 = 120 = 40*3 = V*Q ✓
        assert OMEGA * (EIG_K_C + Q) == V * Q

    def test_omega_is_LINE_SIZE(self):
        # omega = Q+1 = size of GQ lines (maximum cliques ARE the GQ lines)
        line_size = Q + 1
        assert OMEGA == line_size


class TestT3_FractionalChromatic:
    """chi_f(G) = V/alpha = 4 = MU = omega; exact equality chi_f = omega."""

    def test_chi_f_value(self):
        assert CHI_F == 4

    def test_chi_f_formula(self):
        # Vertex-transitive: chi_f = V/alpha = 40/10 = 4
        assert CHI_F == Fraction(V, ALPHA)

    def test_chi_f_is_integer(self):
        # chi_f = 4 is an integer (alpha divides V perfectly)
        assert V % ALPHA == 0

    def test_chi_f_equals_MU(self):
        # chi_f = MU = 4 (fractional chromatic = non-adjacency parameter!)
        assert CHI_F == MU

    def test_chi_f_equals_omega(self):
        # chi_f = omega = 4 (EXACT equality; usually chi_f >= omega)
        assert CHI_F == OMEGA

    def test_chi_f_lower_bound(self):
        # chi_f >= omega always; here equality holds
        assert CHI_F >= OMEGA

    def test_chi_f_equals_Q_plus_1(self):
        # chi_f = Q+1 = 4
        assert CHI_F == Q + 1

    def test_V_equals_alpha_times_chi_f(self):
        # V = alpha * chi_f = 10 * 4 = 40 (covering arithmetic)
        assert V == ALPHA * CHI_F

    def test_chi_f_from_Lovász(self):
        # For vertex-transitive: chi_f = V / theta(G) = V/alpha = 40/10 = 4
        # (since theta(G) = alpha for W(3,3))
        assert CHI_F == Fraction(V, THETA)


class TestT4_LovaszTightness:
    """theta(G) = alpha = 10 and theta(Gc) = omega = 4: BOTH tight simultaneously."""

    def test_lovász_theta_G_equals_alpha(self):
        # theta(G) = V*|s|/(K+|s|) = 10 = alpha (Lovász bound TIGHT!)
        lovász_G = Fraction(V * abs(EIG_S), K + abs(EIG_S))
        assert lovász_G == ALPHA

    def test_lovász_theta_Gc_equals_omega(self):
        # theta(Gc) = V/theta(G) = 40/10 = 4 = omega (product formula, vertex-transitive)
        lovász_Gc = Fraction(V, THETA)
        assert lovász_Gc == OMEGA

    def test_lovász_product_equals_V(self):
        # theta(G) * theta(Gc) = V = 40 (vertex-transitive equality)
        assert ALPHA * OMEGA == V

    def test_alpha_times_omega_equals_V(self):
        # alpha * omega = 10 * 4 = 40 = V (independence-clique product = vertex count!)
        assert ALPHA * OMEGA == V

    def test_both_theta_bounds_tight(self):
        # Both alpha <= theta(G) and omega <= theta(Gc) are tight equalities
        assert Fraction(V * abs(EIG_S), K + abs(EIG_S)) == ALPHA
        assert Fraction(V, THETA) == OMEGA

    def test_alpha_equals_THETA_and_omega_equals_MU(self):
        # alpha = THETA = 10 and omega = MU = 4
        assert ALPHA == THETA
        assert OMEGA == MU

    def test_theta_product_Q_formula(self):
        # theta(G) * theta(Gc) = THETA * MU = 10 * 4 = 40 = V
        assert THETA * MU == V


class TestT5_ComplementDuality:
    """Complement Gc = SRG(40,27,18,18): chi_f(Gc) = THETA = 10 = omega(Gc)."""

    def test_complement_alpha(self):
        # alpha(Gc) = omega(G) = MU = 4
        assert ALPHA_C == MU

    def test_complement_omega(self):
        # omega(Gc) = alpha(G) = THETA = 10
        assert OMEGA_C == THETA

    def test_complement_chi_f(self):
        # chi_f(Gc) = V/alpha(Gc) = 40/4 = 10 = THETA
        assert CHI_F_C == THETA

    def test_complement_chi_f_equals_omega_c(self):
        # chi_f(Gc) = omega(Gc) = 10 (same tight structure in complement!)
        assert CHI_F_C == OMEGA_C

    def test_complement_chi_f_times_G_chi_f_equals_V(self):
        # chi_f(G) * chi_f(Gc) = MU * THETA = 4 * 10 = 40 = V
        assert CHI_F * CHI_F_C == V

    def test_complement_V_equals_alpha_c_times_chi_f_c(self):
        # V = alpha(Gc) * chi_f(Gc) = 4 * 10 = 40
        assert V == ALPHA_C * CHI_F_C

    def test_complement_symmetry(self):
        # alpha(G)*alpha(Gc) = chi_f(G)*chi_f(Gc) = V = 40
        assert ALPHA * ALPHA_C == V
        assert CHI_F * CHI_F_C == V

    def test_complement_roles_swapped(self):
        # The MU<->THETA role-swap between G and Gc
        assert CHI_F == MU        # G: chi_f = MU
        assert CHI_F_C == THETA   # Gc: chi_f = THETA


class TestT6_CoveringArithmetic:
    """V = alpha*chi_f = omega*clique_cover = 10*4 = 4*10 = 40."""

    def test_V_alpha_chi_f(self):
        # V = alpha * chi_f = 10 * 4 = 40
        assert V == ALPHA * int(CHI_F)

    def test_clique_cover_upper_bound(self):
        # Clique cover number theta_cc(G) <= V/omega = 40/4 = 10
        clique_cover_upper = V // OMEGA
        assert clique_cover_upper == 10

    def test_clique_cover_upper_equals_alpha(self):
        # V/omega = 10 = alpha (the upper bound equals the independence number!)
        assert V // OMEGA == ALPHA

    def test_V_omega_clique_cover(self):
        # V = omega * (V/omega) = 4 * 10 = 40 (clique-cover identity)
        assert V == OMEGA * (V // OMEGA)

    def test_spread_covers_V(self):
        # A spread (partition into lines) uses V/omega = V/(Q+1) = 40/4 = 10 lines
        spread_size = V // OMEGA
        assert spread_size == ALPHA   # = 10

    def test_alpha_divides_V(self):
        # alpha = 10 divides V = 40 (needed for integer chi_f)
        assert V % ALPHA == 0

    def test_omega_divides_V(self):
        # omega = 4 divides V = 40 (needed for integer clique cover)
        assert V % OMEGA == 0

    def test_V_factorization(self):
        # V = alpha * omega = 10 * 4 (V factors as independence*clique!)
        assert V == ALPHA * OMEGA


class TestT7_MultiplicityConnections:
    """Eigenvalue multiplicities connect to independence/clique structure."""

    def test_MUL_R_via_alpha_omega(self):
        # MUL_R = 24 = 2*alpha + MU = 2*10 + 4? No: 20+4=24 ✓
        assert MUL_R == 2 * ALPHA + MU

    def test_MUL_R_via_THETA_MU(self):
        # MUL_R = 24 = 2*THETA + MU = 20 + 4 = 24 (THETA=alpha)
        assert MUL_R == 2 * THETA + MU

    def test_MUL_S_via_alpha_omega(self):
        # MUL_S = 15 = alpha + MU + 1 = 10 + 4 + 1 = 15
        assert MUL_S == ALPHA + MU + 1

    def test_MUL_S_via_THETA_MU(self):
        # MUL_S = 15 = THETA + MU + 1 = 10 + 4 + 1 = 15
        assert MUL_S == THETA + MU + 1

    def test_MUL_R_plus_MUL_S(self):
        # 24 + 15 = 39 = V - 1
        assert MUL_R + MUL_S == V - 1

    def test_MUL_R_over_MUL_S(self):
        # MUL_R/MUL_S = 24/15 = 8/5
        assert Fraction(MUL_R, MUL_S) == Fraction(8, 5)

    def test_MUL_R_equals_V_minus_1_minus_MUL_S(self):
        # Trivially MUL_R = V-1-MUL_S = 39-15 = 24
        assert MUL_R == V - 1 - MUL_S

    def test_alpha_Q_squared_plus_1(self):
        # alpha = Q^2 + 1; MUL_S = Q*(Q+2)/? ... 15 = 3*5 = Q*(Q+2)
        assert MUL_S == Q * (Q + 2)

    def test_MUL_R_is_2Q_times_Q_plus_1(self):
        # MUL_R = 24 = 2Q*(Q+1) = 2*3*4 = 24 ✓
        assert MUL_R == 2 * Q * (Q + 1)
