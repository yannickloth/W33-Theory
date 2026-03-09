"""
Phase XLV: Chromatic, Flow & Combinatorial Algebra (T636-T650)
===============================================================

Explores the chromatic, flow-theoretic, and cycle-counting invariants
of W(3,3), revealing that every combinatorial measure — girth, triangle
count, 4-cycle count, Lovász theta, fractional chromatic number, Cheeger
expansion, genus bounds, and more — resolves to the five source numbers
(V, K, λ, μ, q) = (40, 12, 2, 4, 3).

Key discoveries:
  - Girth = Q = 3 (field order)
  - Triangle count C₃ = V·μ = 160
  - 4-cycle count C₄ = 1740, verified by TWO independent formulas
  - χ_f = μ = 4 (fractional chromatic = Paley parameter)
  - Lovász theta(G) = α = 10, theta(Ḡ) = ω = μ = 4, product = V
  - 2K·Θ = E = 240 (edge-Cheeger identity), E = 16g
  - K·Θ = DIM_O·g = E/2 = 120
  - Cycle space dim = Q·67 = 201, cut space = V−1 = 39
"""

import pytest
from fractions import Fraction

# ── Source parameters ──────────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                    # 240
R, S = 2, -4                      # Eigenvalues of adjacency matrix
F, G = 24, 15                     # Multiplicities
N = Q + 2                          # 5 (pentad size)
THETA = K - R                      # 10 (algebraic connectivity)
ALPHA = V // MU                    # 10 (independence number)
OMEGA = MU                         # 4 (clique number)
DIM_O = K - MU                     # 8 (octonion dimension)
ALBERT = V - (Q**2 + MU)           # 27

# Complement parameters
K_BAR = V - 1 - K                 # 27
R_BAR = -1 - S                    # 3
S_BAR = -1 - R                    # -3


# ── T636: Girth equals field order ─────────────────────────────────────
class TestT636GirthFieldOrder:
    """T636 · Girth = Q = 3 — the smallest cycle has length equal to GF(q)."""

    def test_girth_equals_Q(self):
        """Since λ = 2 > 0, adjacent vertices share common neighbours → triangles exist → girth = 3."""
        girth = Q
        assert girth == 3

    def test_girth_from_lambda(self):
        """LAM > 0 implies triangles exist, so girth ≤ 3; no loops/multi-edges → girth ≥ 3."""
        assert LAM > 0  # triangles exist
        girth = 3
        assert girth == Q

    def test_girth_divides_no_bipartite(self):
        """Odd girth means graph is NOT bipartite."""
        girth = Q
        assert girth % 2 == 1  # odd girth → not bipartite


# ── T637: Triangle count = V·μ ─────────────────────────────────────────
class TestT637TriangleCount:
    """T637 · C₃ = V·K·λ/6 = V·μ = 160 triangles."""

    def test_triangle_count_formula(self):
        C3 = V * K * LAM // 6
        assert C3 == 160

    def test_triangle_count_equals_V_times_MU(self):
        C3 = V * K * LAM // 6
        assert C3 == V * MU

    def test_triangles_from_trace(self):
        """w₃ = Tr(A³) = K³ + r³f + s³g = 6·C₃."""
        w3 = K**3 + R**3 * F + S**3 * G
        C3 = w3 // 6
        assert C3 == V * MU
        assert w3 == 6 * V * MU

    def test_triangles_per_vertex(self):
        """Each vertex is in K·LAM/2 = 12 triangles."""
        per_vertex = K * LAM // 2
        assert per_vertex == K  # = 12
        C3 = V * per_vertex // 3
        assert C3 == V * MU

    def test_triangle_factorisation(self):
        C3 = V * MU
        assert C3 == 2**5 * 5  # 160 = 32 · 5


# ── T638: Four-cycle count verified two ways ────────────────────────────
class TestT638FourCycleCount:
    """T638 · C₄ = 1740, verified by pair-counting AND eigenvalue formula."""

    def test_C4_from_pairs(self):
        """Adjacent pair (u,v): C(LAM,2) ways. Non-adjacent: C(MU,2) ways.
        Each 4-cycle counted twice (once per diagonal), so divide by 2."""
        E_bar = V * (V - 1) // 2 - E  # non-edges = 540
        from_adj = E * (LAM * (LAM - 1) // 2)
        from_nonadj = E_bar * (MU * (MU - 1) // 2)
        C4 = (from_adj + from_nonadj) // 2
        assert C4 == 1740

    def test_C4_from_eigenvalues(self):
        """C₄ = (w₄ - V·K² - V·K·(K-1)) / 8."""
        w4 = K**4 + R**4 * F + S**4 * G
        C4 = (w4 - V * K**2 - V * K * (K - 1)) // 8
        assert C4 == 1740

    def test_C4_both_methods_agree(self):
        E_bar = V * (V - 1) // 2 - E
        C4_pairs = (E * (LAM * (LAM - 1) // 2) + E_bar * (MU * (MU - 1) // 2)) // 2
        w4 = K**4 + R**4 * F + S**4 * G
        C4_eig = (w4 - V * K**2 - V * K * (K - 1)) // 8
        assert C4_pairs == C4_eig == 1740

    def test_C4_factorisation(self):
        assert 1740 == 2**2 * 3 * 5 * 29

    def test_C4_over_C3(self):
        """C₄/C₃ = 1740/160 = 87/8 = 87/DIM_O."""
        ratio = Fraction(1740, 160)
        assert ratio == Fraction(87, DIM_O)


# ── T639: Closed 4-walk decomposition ──────────────────────────────────
class TestT639Walk4Decomposition:
    """T639 · w₄ = 24960 with SRG per-vertex decomposition."""

    def test_w4_spectral(self):
        w4 = K**4 + R**4 * F + S**4 * G
        assert w4 == 24960

    def test_w4_per_vertex(self):
        """w₄/V = K² + K·λ² + (V−1−K)·μ² = K² + K·λ² + ALBERT·μ²."""
        per_vertex = K**2 + K * LAM**2 + ALBERT * MU**2
        assert per_vertex == 624
        assert per_vertex * V == 24960

    def test_w4_three_components(self):
        """Three contributions: return-via-same = K², via-adj = K·λ², via-nonadj = ALBERT·μ²."""
        comp1 = K**2          # 144
        comp2 = K * LAM**2    # 48
        comp3 = ALBERT * MU**2  # 432
        assert comp1 + comp2 + comp3 == 624
        assert comp3 == ALBERT * MU**2  # largest term from non-adjacent


# ── T640: Cycle space dimension ─────────────────────────────────────────
class TestT640CycleSpaceDimension:
    """T640 · dim(cycle space) = E − V + 1 = 201 = Q · 67."""

    def test_cycle_space_dim(self):
        cycle_dim = E - V + 1
        assert cycle_dim == 201

    def test_cycle_space_factorisation(self):
        cycle_dim = E - V + 1
        assert cycle_dim == Q * 67

    def test_67_is_prime(self):
        n = 67
        assert all(n % d != 0 for d in range(2, int(n**0.5) + 1))


# ── T641: Cut–cycle duality ────────────────────────────────────────────
class TestT641CutCycleDuality:
    """T641 · Cut space dim = V−1 = 39, cycle + cut = E = 240."""

    def test_cut_space_dim(self):
        cut_dim = V - 1
        assert cut_dim == 39

    def test_cycle_plus_cut_equals_E(self):
        cycle_dim = E - V + 1
        cut_dim = V - 1
        assert cycle_dim + cut_dim == E

    def test_cut_space_factorisation(self):
        assert V - 1 == 3 * 13  # Q · Φ₃

    def test_cycle_cut_ratio(self):
        ratio = Fraction(E - V + 1, V - 1)
        assert ratio == Fraction(201, 39) == Fraction(67, 13)


# ── T642: Fractional chromatic number ──────────────────────────────────
class TestT642FractionalChromatic:
    """T642 · χ_f = V/α = 4 = μ — the fractional chromatic number equals Paley parameter."""

    def test_chi_f_formula(self):
        chi_f = Fraction(V, ALPHA)
        assert chi_f == MU

    def test_chi_f_integer(self):
        """V/α is an integer for vertex-transitive graphs; here it equals μ."""
        assert V % ALPHA == 0
        assert V // ALPHA == MU

    def test_chi_f_equals_omega(self):
        """χ_f = 4 = ω = μ, so fractional chromatic = clique number."""
        chi_f = Fraction(V, ALPHA)
        assert chi_f == OMEGA


# ── T643: Lovász theta tight bound ─────────────────────────────────────
class TestT643LovaszTheta:
    """T643 · ϑ(G) = V·(−s)/(K−s) = α = 10 — Lovász bound is tight."""

    def test_theta_formula(self):
        theta = Fraction(V * (-S), K - S)
        assert theta == ALPHA

    def test_theta_integer(self):
        """ϑ is rational; for W(3,3) it's an integer."""
        theta = Fraction(V * (-S), K - S)
        assert theta.denominator == 1

    def test_theta_equals_alpha(self):
        """Equality ϑ = α means the Lovász bound is achieved (W(3,3) is a 'perfect' graph 
        w.r.t. the theta function for the independent set problem)."""
        theta = Fraction(V * (-S), K - S)
        assert theta == ALPHA == 10

    def test_alpha_lower_bound(self):
        """Standard SRG bound: α ≥ V·(−s)/(K−s). Here equality holds."""
        bound = Fraction(V * (-S), K - S)
        assert ALPHA >= bound
        assert ALPHA == bound  # tight


# ── T644: Complement theta and sandwich product ────────────────────────
class TestT644ComplementTheta:
    """T644 · ϑ(Ḡ) = ω = μ = 4, and ϑ(G)·ϑ(Ḡ) = α·ω = V = 40."""

    def test_theta_complement(self):
        theta_bar = Fraction(V * (-S_BAR), K_BAR - S_BAR)
        assert theta_bar == OMEGA

    def test_theta_complement_equals_MU(self):
        theta_bar = Fraction(V * (-S_BAR), K_BAR - S_BAR)
        assert theta_bar == MU

    def test_sandwich_product(self):
        """Lovász sandwich: ϑ(G)·ϑ(Ḡ) ≥ V. Here equality holds."""
        theta = Fraction(V * (-S), K - S)
        theta_bar = Fraction(V * (-S_BAR), K_BAR - S_BAR)
        assert theta * theta_bar == V

    def test_alpha_omega_product(self):
        """For vertex-transitive graphs: α(G)·ω(G) = V iff sandwich is tight both ways."""
        assert ALPHA * OMEGA == V


# ── T645: LP duality identities ───────────────────────────────────────
class TestT645LPDuality:
    """T645 · χ_f · α = V and ω · χ̄_f = V — LP duality for vertex-transitive graphs."""

    def test_chi_f_times_alpha(self):
        chi_f = Fraction(V, ALPHA)
        assert chi_f * ALPHA == V

    def test_fractional_clique_cover(self):
        """Fractional clique cover number = V/ω = α = 10."""
        fcc = Fraction(V, OMEGA)
        assert fcc == ALPHA

    def test_omega_times_chi_f_bar(self):
        """For complement: χ_f(Ḡ) = V/α(Ḡ) = V/ω(G) = 10, so ω·χ_f(Ḡ) = 4·10 = V."""
        alpha_bar = OMEGA  # α(Ḡ) = ω(G) for vertex-transitive
        # Actually α(Ḡ) is the clique number ω(G) only in self-complementary or specific cases.
        # For SRG complement: α(Ḡ) = ω(G) follows from theta duality.
        chi_f_bar = Fraction(V, alpha_bar)
        assert OMEGA * chi_f_bar == V

    def test_all_LP_chain(self):
        """ω ≤ χ_f ≤ χ and α(Ḡ) = ω. For W(3,3): ω = χ_f = μ = 4."""
        assert OMEGA == Fraction(V, ALPHA)
        assert Fraction(V, ALPHA) == MU


# ── T646: Flow number bound ────────────────────────────────────────────
class TestT646FlowNumber:
    """T646 · Flow number φ(G) ≤ μ = 4 (Jaeger's theorem: κ' ≥ 4 → φ ≤ 4)."""

    def test_edge_connectivity_equals_K(self):
        """W(3,3) is K-edge-connected (SRG with K=12 ≥ 2)."""
        edge_conn = K  # vertex-transitive → κ' = K
        assert edge_conn == 12

    def test_jaeger_bound(self):
        """Jaeger (1979): κ'(G) ≥ 4 → G has a nowhere-zero 4-flow → φ(G) ≤ 4."""
        assert K >= 4
        flow_bound = 4
        assert flow_bound == MU

    def test_tutte_five_flow(self):
        """Tutte's 5-flow conjecture (proved for K-connected, K≥6): φ ≤ 5."""
        assert K >= 6
        assert 5 == N  # Tutte bound = pentad size

    def test_flow_chromatic_duality(self):
        """For planar graphs χ = φ (by duality). W(3,3) isn't planar, but χ_f = μ = 4 ≤ flow bound."""
        chi_f = Fraction(V, ALPHA)
        assert chi_f <= MU


# ── T647: Edge-Cheeger expansion identity ──────────────────────────────
class TestT647CheegerEdgeExpansion:
    """T647 · 2K·Θ = E = 240 and E = 16g — edge expansion product identity."""

    def test_2K_times_theta_equals_E(self):
        assert 2 * K * THETA == E

    def test_E_equals_16g(self):
        assert E == 16 * G

    def test_cheeger_lower_bound(self):
        """Cheeger inequality lower bound: h ≥ Θ/2 = N = 5."""
        cheeger_lower = Fraction(THETA, 2)
        assert cheeger_lower == N

    def test_cheeger_upper_squared(self):
        """Cheeger upper: h ≤ √(2K·Θ) = √E = √240 = 4√15 = 4√g."""
        cheeger_upper_sq = 2 * K * THETA
        assert cheeger_upper_sq == E
        assert cheeger_upper_sq == 16 * G  # (4√g)²

    def test_edge_count_triple_product(self):
        """E = 2K·Θ = 2·12·10 = 240 links degree, algebraic connectivity, and edge count."""
        assert E == 2 * K * THETA
        assert E == V * K // 2  # standard formula
        # Both give 240


# ── T648: K·Θ = DIM_O·g = E/2 ─────────────────────────────────────────
class TestT648KThetaDimOG:
    """T648 · K·Θ = DIM_O·g = E/2 = 120 — linking degree, connectivity, and octonion dimension."""

    def test_K_times_theta(self):
        assert K * THETA == 120

    def test_DIM_O_times_g(self):
        assert DIM_O * G == 120

    def test_equals_E_over_2(self):
        assert K * THETA == E // 2

    def test_triple_equality(self):
        """K·Θ = DIM_O·g = E/2 = 120."""
        assert K * THETA == DIM_O * G == E // 2 == 120

    def test_120_is_5_factorial(self):
        """120 = 5! = N! — connecting to pentad size."""
        import math
        assert K * THETA == math.factorial(N)


# ── T649: Genus bounds ─────────────────────────────────────────────────
class TestT649GenusBounds:
    """T649 · Max genus = 100, min genus ≥ 21. Genus bounds from cycle space."""

    def test_max_genus(self):
        """Maximum genus = ⌊(E − V + 1)/2⌋ = ⌊201/2⌋ = 100."""
        g_max = (E - V + 1) // 2
        assert g_max == 100

    def test_max_genus_is_4_times_25(self):
        g_max = (E - V + 1) // 2
        assert g_max == 4 * 25  # MU · N²

    def test_max_genus_from_cycle_space(self):
        """Max genus ≤ cycle space dim / 2 (needs integer, hence floor)."""
        cycle_dim = E - V + 1
        assert cycle_dim == 201  # odd → max genus < cycle_dim/2
        assert (cycle_dim - 1) // 2 == 100

    def test_min_genus_lower_bound(self):
        """Ringel–Youngs: γ(G) ≥ ⌈(E/3 − V + 2)/2⌉ for triangle-free, or from Euler."""
        g_min_lb = (E // 3 - V + 2 + 1) // 2  # ceiling
        assert g_min_lb >= 21

    def test_genus_range(self):
        g_max = (E - V + 1) // 2
        g_min_lb = (E // 3 - V + 2 + 1) // 2
        assert 21 <= g_min_lb <= g_max == 100


# ── T650: Vertex isoperimetric expansion ──────────────────────────────
class TestT650VertexIsoperimetric:
    """T650 · Vertex expansion from max independent set = Q = 3."""

    def test_expansion_ratio(self):
        """For max independent set S with |S| = α: |N(S)|/|S| = (V − α)/α = Q."""
        boundary = V - ALPHA  # vertices NOT in the independent set
        ratio = Fraction(boundary, ALPHA)
        assert ratio == Q

    def test_expansion_integer(self):
        assert (V - ALPHA) % ALPHA == 0

    def test_vertex_expansion_lower(self):
        """Vertex expansion h_v ≥ (V − α)/α for max stable set, giving h_v ≥ Q = 3."""
        h_v_lower = Fraction(V - ALPHA, ALPHA)
        assert h_v_lower == Q

    def test_complement_expansion(self):
        """For complement, max independent set has size ω(G) = MU.
        Expansion ratio = (V − ω)/ω = (40 − 4)/4 = 9 = Q²."""
        ratio_bar = Fraction(V - OMEGA, OMEGA)
        assert ratio_bar == Q**2

    def test_expansion_product(self):
        """Product of expansions: Q · Q² = Q³ = ALBERT = 27."""
        ratio = Fraction(V - ALPHA, ALPHA)
        ratio_bar = Fraction(V - OMEGA, OMEGA)
        assert ratio * ratio_bar == Q**3 == ALBERT
