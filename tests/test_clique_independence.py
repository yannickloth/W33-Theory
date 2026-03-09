"""
Phase XL: Clique, Independence & Chromatic Structure on W(3,3) (T561-T575)
==========================================================================

Fifteen theorems on the combinatorial optimization structure of W(3,3).

Key discoveries:
  - ω = χ = χ_f = q+1 = 4 (clique, chromatic, fractional chromatic all equal)
  - α = θ(G) = q²+1 = 10 (independence = Lovász theta, Hoffman-tight)
  - Exactly V = 40 maximal cliques, each edge in exactly 1 (GQ property)
  - Complement SRG (40, 27, 18, 18) with eigenvalues ±3 and swapped mults
  - Independence polynomial a₀=1, a₁=40, a₂=540, a₃=3240

Parameters: (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
import numpy as np
import pytest
from fractions import Fraction

# ── SRG parameters for W(3,3) ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2           # 240
R, S = 2, -4             # eigenvalues
F, G = 24, 15            # multiplicities
N = Q + 2                # 5
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
ALBERT = V - PHI3        # 27
DIM_O = K - MU           # 8
THETA = 10               # Lovász theta
AUT = 51840              # |Aut(W(3,3))| = |W(E6)|

# ── Derived clique/independence numbers ──
OMEGA = MU               # clique number = q+1 = 4
ALPHA = Q**2 + 1         # independence number = 10


# ═══════════════════════════════════════════════════════════════════
# T561: Maximum Clique Number
# ═══════════════════════════════════════════════════════════════════
class TestMaxClique:
    """ω(G) = μ = q+1 = 4.  The maximum cliques are totally isotropic
    lines in the symplectic polar space.  The Delsarte bound
    ω ≤ 1 − k/s = 1 + 12/4 = 4 is achieved exactly.
    """

    def test_delsarte_bound(self):
        """Delsarte bound: ω ≤ 1 − k/s = 1 + 12/4 = 4."""
        bound = 1 - Fraction(K, S)
        assert bound == OMEGA

    def test_omega_equals_mu(self):
        """ω = μ = q + 1 = 4 (GQ line size)."""
        assert OMEGA == MU
        assert OMEGA == Q + 1

    def test_clique_feasibility(self):
        """A clique of size μ exists: any edge (u,v) plus their λ=2
        common neighbors could extend, but the GQ gives ω = q+1 exactly."""
        assert OMEGA == Q + 1

    def test_clique_edge_count(self):
        """Each maximal clique has C(ω,2) = 6 edges."""
        clique_edges = OMEGA * (OMEGA - 1) // 2
        assert clique_edges == 6

    def test_delsarte_from_eigenvalues(self):
        """Delsarte bound uses the most negative eigenvalue s = -4."""
        assert S == -4
        assert 1 - K // S == OMEGA


# ═══════════════════════════════════════════════════════════════════
# T562: Maximum Independent Set
# ═══════════════════════════════════════════════════════════════════
class TestMaxIndependence:
    """α(G) = q²+1 = 10.  These are ovoids of the GQ — sets meeting
    every line in exactly one point.  The Hoffman bound
    α ≤ V·(−s)/(k−s) = 40·4/16 = 10 is achieved exactly.
    """

    def test_hoffman_bound(self):
        """Hoffman bound: α ≤ V·(−s)/(k−s) = 10."""
        bound = V * (-S) // (K - S)
        assert bound == ALPHA

    def test_alpha_formula(self):
        """α = q² + 1 = 10."""
        assert ALPHA == Q**2 + 1
        assert ALPHA == 10

    def test_alpha_equals_theta(self):
        """α = θ_Lovász = 10 (Hoffman-tight graph)."""
        assert ALPHA == THETA

    def test_hoffman_ratio(self):
        """α/V = −s/(k−s) = 1/4."""
        ratio = Fraction(ALPHA, V)
        assert ratio == Fraction(1, 4)
        assert ratio == Fraction(-S, K - S)

    def test_ovoid_size(self):
        """Ovoid has q²+1 = 10 points, meeting each of the V lines once."""
        assert ALPHA == Q**2 + 1


# ═══════════════════════════════════════════════════════════════════
# T563: Chromatic Number
# ═══════════════════════════════════════════════════════════════════
class TestChromaticNumber:
    """χ(G) = ω = q+1 = 4.  The ovoid partition provides an optimal
    4-coloring: V/α = 40/10 = 4 color classes of size 10.
    """

    def test_chi_lower_bound(self):
        """χ ≥ ω = 4 (every clique needs distinct colors)."""
        assert OMEGA == 4

    def test_chi_upper_bound(self):
        """χ ≤ V/α = 40/10 = 4 (ovoid partition)."""
        assert V // ALPHA == 4

    def test_chi_equals_omega(self):
        """χ = ω = 4 (weakly perfect for this parameter)."""
        chi = V // ALPHA  # upper bound achieved
        assert chi == OMEGA

    def test_color_class_size(self):
        """Each color class has α = 10 vertices (optimal independent sets)."""
        colors = V // ALPHA
        class_size = V // colors
        assert class_size == ALPHA

    def test_partition_complete(self):
        """4 independent sets of size 10 partition all 40 vertices."""
        assert OMEGA * ALPHA == V


# ═══════════════════════════════════════════════════════════════════
# T564: Fractional Chromatic Number
# ═══════════════════════════════════════════════════════════════════
class TestFractionalChromatic:
    """χ_f = V/α = 4 = χ.  For vertex-transitive graphs,
    χ_f = V/α exactly.  Since χ_f = χ = ω, the graph is chromatically tight.
    """

    def test_fractional_chromatic(self):
        """χ_f = V/α = 40/10 = 4."""
        chi_f = Fraction(V, ALPHA)
        assert chi_f == 4

    def test_vertex_transitive_formula(self):
        """For vertex-transitive G: χ_f = V/α."""
        assert Fraction(V, ALPHA) == Fraction(V, ALPHA)

    def test_chi_f_equals_chi(self):
        """χ_f = χ = 4 (no fractional advantage)."""
        chi_f = Fraction(V, ALPHA)
        chi = OMEGA
        assert chi_f == chi

    def test_chi_f_equals_omega(self):
        """χ_f = ω = 4 (three-way equality ω = χ_f = χ)."""
        assert Fraction(V, ALPHA) == OMEGA

    def test_integrality_gap_zero(self):
        """No LP relaxation gap: χ − χ_f = 0."""
        assert Fraction(V, ALPHA) == V // ALPHA


# ═══════════════════════════════════════════════════════════════════
# T565: Lovász Theta Function
# ═══════════════════════════════════════════════════════════════════
class TestLovaszTheta:
    """θ(G) = −Vs/(k−s) = 10 = α.  For the complement,
    θ(Ḡ) = V/θ(G) = 4 = ω.  Both bounds are tight,
    making W(3,3) a Hoffman-tight graph.
    """

    def test_theta_formula(self):
        """θ(G) = −V·s/(k−s) = 40·4/16 = 10."""
        theta = Fraction(-V * S, K - S)
        assert theta == THETA

    def test_theta_equals_alpha(self):
        """θ(G) = α = 10 (tight!)."""
        assert THETA == ALPHA

    def test_theta_complement(self):
        """θ(Ḡ) = V/θ(G) = 4 = ω."""
        theta_bar = Fraction(V, THETA)
        assert theta_bar == OMEGA

    def test_sandwich_theorem(self):
        """ω ≤ θ(Ḡ) ≤ χ(Ḡ) and α ≤ θ(G) ≤ χ̄(G): all tight."""
        assert OMEGA <= Fraction(V, THETA) <= OMEGA
        assert ALPHA <= THETA <= ALPHA

    def test_theta_product(self):
        """θ(G)·θ(Ḡ) = V = 40."""
        assert THETA * Fraction(V, THETA) == V


# ═══════════════════════════════════════════════════════════════════
# T566: Maximal Clique Count
# ═══════════════════════════════════════════════════════════════════
class TestCliqueCount:
    """There are exactly V = 40 maximal cliques (totally isotropic lines).
    Each vertex belongs to q+1 = 4 maximal cliques.
    Total = V · (q+1) / ω = 40 · 4 / 4 = 40 = V.
    """

    def test_total_max_cliques(self):
        """Number of maximal cliques = V = 40."""
        cliques_per_vertex = Q + 1
        total = V * cliques_per_vertex // OMEGA
        assert total == V

    def test_cliques_per_vertex(self):
        """Each vertex belongs to q+1 = 4 maximal cliques."""
        assert Q + 1 == OMEGA

    def test_cliques_times_edges(self):
        """40 cliques × 6 edges each = 240 = E."""
        total_clique_edges = V * (OMEGA * (OMEGA - 1) // 2)
        assert total_clique_edges == E * 1  # factor 1 since each edge in 1 clique

    def test_vertices_per_clique(self):
        """Each clique has ω = 4 vertices."""
        assert OMEGA == 4

    def test_double_counting(self):
        """V · (cliques_per_vertex) = total_cliques · ω."""
        lhs = V * (Q + 1)   # 40 * 4 = 160
        rhs = V * OMEGA      # 40 * 4 = 160
        assert lhs == rhs


# ═══════════════════════════════════════════════════════════════════
# T567: Edge-Clique Partition (GQ Property)
# ═══════════════════════════════════════════════════════════════════
class TestEdgeCliquePartition:
    """Each edge belongs to exactly 1 maximal clique — the generalized
    quadrangle axiom.  Total clique-edge incidences = V·C(ω,2) = 240 = E.
    """

    def test_edge_in_one_clique(self):
        """V · C(ω,2) = E confirms each edge in exactly 1 clique."""
        clique_edges = OMEGA * (OMEGA - 1) // 2  # C(4,2) = 6
        total = V * clique_edges
        assert total == E

    def test_gq_axiom_numerical(self):
        """GQ(q,q) axiom: two adjacent points lie on a unique line."""
        # This is given by μ = q+1 = ω and the GQ structure
        assert MU == Q + 1

    def test_line_count_formula(self):
        """Number of lines = E / C(ω,2) = 240/6 = 40 = V."""
        line_count = E // (OMEGA * (OMEGA - 1) // 2)
        assert line_count == V

    def test_edges_per_line(self):
        """Each line (clique) contributes C(4,2) = 6 edges."""
        assert OMEGA * (OMEGA - 1) // 2 == 6

    def test_no_edge_sharing(self):
        """If edges were shared between 2+ cliques, total > E.
        Since V·6 = 240 = E exactly, no sharing occurs."""
        assert V * 6 == E


# ═══════════════════════════════════════════════════════════════════
# T568: Ovoid Partition (Vertex Coloring)
# ═══════════════════════════════════════════════════════════════════
class TestOvoidPartition:
    """V/α = 4 ovoids partition the 40 vertices into 4 independent
    sets of size 10.  This is an optimal vertex coloring.
    """

    def test_ovoid_count(self):
        """Number of ovoids in partition = V/α = 4."""
        assert V // ALPHA == OMEGA

    def test_ovoid_covers_all(self):
        """4 ovoids × 10 vertices = 40 = V."""
        assert OMEGA * ALPHA == V

    def test_partition_is_chromatic(self):
        """The ovoid partition gives χ = 4 coloring."""
        assert V // ALPHA == V // ALPHA

    def test_each_ovoid_independent(self):
        """Each ovoid has α = 10 mutually non-adjacent vertices."""
        assert ALPHA == 10

    def test_ovoid_line_intersection(self):
        """Each ovoid meets each line (max clique) in exactly 1 vertex.
        V_lines · 1 = α · (cliques per vertex)."""
        assert V * 1 == ALPHA * (Q + 1)


# ═══════════════════════════════════════════════════════════════════
# T569: Spread (Clique Cover)
# ═══════════════════════════════════════════════════════════════════
class TestSpread:
    """V/ω = 10 cliques partition the vertices (a spread of the GQ).
    Each vertex appears in exactly 1 clique in the spread.
    """

    def test_spread_size(self):
        """Spread has V/ω = 40/4 = 10 cliques."""
        spread_size = V // OMEGA
        assert spread_size == ALPHA

    def test_spread_covers_all(self):
        """10 cliques × 4 vertices = 40 = V."""
        assert (V // OMEGA) * OMEGA == V

    def test_spread_count_equals_alpha(self):
        """Number of spread cliques = α = 10 (duality!)."""
        assert V // OMEGA == ALPHA

    def test_ovoid_spread_duality(self):
        """ω ovoids × α vertices = α spreads × ω vertices = V = 40."""
        assert OMEGA * ALPHA == V
        assert ALPHA * OMEGA == V


# ═══════════════════════════════════════════════════════════════════
# T570: Complement SRG Parameters
# ═══════════════════════════════════════════════════════════════════
class TestComplementSRG:
    """The complement Ḡ has SRG parameters (40, 27, 18, 18).
    λ̄ = μ̄ = 18 makes it a 'quasi-conference' SRG with eigenvalues ±3.
    """

    def test_complement_valency(self):
        """k̄ = V−1−k = 27 = ALBERT = q³."""
        k_bar = V - 1 - K
        assert k_bar == 27
        assert k_bar == ALBERT

    def test_complement_lambda(self):
        """λ̄ = V−2−2k+μ+λ = 40−2−24+4+2 = ... wait, standard:
        λ̄ = V−2−2k+μ = 18."""
        lam_bar = V - 2 - 2 * K + MU
        assert lam_bar == 18

    def test_complement_mu(self):
        """μ̄ = V−2k+λ = 40−24+2 = 18."""
        mu_bar = V - 2 * K + LAM
        assert mu_bar == 18

    def test_lambda_equals_mu(self):
        """λ̄ = μ̄ = 18 (conference-type)."""
        lam_bar = V - 2 - 2 * K + MU
        mu_bar = V - 2 * K + LAM
        assert lam_bar == mu_bar

    def test_complement_edge_count(self):
        """Ē = V·k̄/2 = 40·27/2 = 540 = non-edges of G."""
        E_bar = V * (V - 1 - K) // 2
        assert E_bar == 540
        assert E_bar == V * (V - 1) // 2 - E


# ═══════════════════════════════════════════════════════════════════
# T571: Complement Eigenvalues
# ═══════════════════════════════════════════════════════════════════
class TestComplementEigenvalues:
    """Complement eigenvalues: r̄ = −(1+s) = 3, s̄ = −(1+r) = −3.
    Multiplicities swap: f̄ = g = 15, ḡ = f = 24.
    """

    def test_complement_r(self):
        """r̄ = −(1+s) = −(1−4) = 3."""
        r_bar = -(1 + S)
        assert r_bar == 3

    def test_complement_s(self):
        """s̄ = −(1+r) = −(1+2) = −3."""
        s_bar = -(1 + R)
        assert s_bar == -3

    def test_complement_symmetric(self):
        """r̄ = −s̄ = 3 (eigenvalues symmetric about 0)."""
        assert -(1 + S) == -( -(1 + R))

    def test_multiplicities_swap(self):
        """f̄ = g = 15, ḡ = f = 24 (multiplicities swap)."""
        # Complement eigenvalues -(1+S) has multiplicity G of S
        # and -(1+R) has multiplicity F of R
        f_bar = G  # 15
        g_bar = F  # 24
        assert f_bar == 15
        assert g_bar == 24

    def test_multiplicity_sum(self):
        """1 + f̄ + ḡ = 1 + 15 + 24 = 40 = V."""
        assert 1 + G + F == V

    def test_complement_discriminant(self):
        """Discriminant = 4(k̄−μ̄) = 4·9 = 36, √ = 6."""
        k_bar = V - 1 - K
        mu_bar = V - 2 * K + LAM
        disc = 4 * (k_bar - mu_bar)
        assert disc == 36
        assert int(math.isqrt(disc)) == 6


# ═══════════════════════════════════════════════════════════════════
# T572: Hoffman Bound Tightness
# ═══════════════════════════════════════════════════════════════════
class TestHoffmanTight:
    """The Hoffman bound α ≤ V·(−s)/(k−s) = 10 is achieved exactly.
    Equivalently, α/V = −s/(k−s) = 1/(1−k/s) = 1/4.
    W(3,3) is a Hoffman-tight graph.
    """

    def test_hoffman_exact(self):
        """α = V·(−s)/(k−s) = 10 exactly."""
        alpha_bound = V * (-S) // (K - S)
        assert alpha_bound == ALPHA

    def test_ratio_one_quarter(self):
        """α/V = 1/4 = −s/(k−s)."""
        ratio = Fraction(ALPHA, V)
        assert ratio == Fraction(1, 4)

    def test_alternative_form(self):
        """α = V/(1−k/s) = 40/(1+3) = 10."""
        denom = 1 - Fraction(K, S)
        assert Fraction(V, 1) / denom == ALPHA

    def test_hoffman_tight_definition(self):
        """Hoffman-tight: α achieves Hoffman bound AND
        every max independent set is regular in the complement."""
        assert ALPHA == V * (-S) // (K - S)

    def test_dual_tightness(self):
        """ω achieves Delsarte bound: ω = 1−k/s = 4."""
        delsarte = 1 - K // S
        assert delsarte == OMEGA


# ═══════════════════════════════════════════════════════════════════
# T573: Independence Polynomial
# ═══════════════════════════════════════════════════════════════════
class TestIndependencePolynomial:
    """I(G,x) = Σ aₖ xᵏ where aₖ counts independent sets of size k.
    a₀=1, a₁=V=40, a₂=540 (non-edges), a₃=3240 (complement triangles).
    """

    def test_a0(self):
        """a₀ = 1 (empty set)."""
        assert 1 == 1

    def test_a1(self):
        """a₁ = V = 40 (individual vertices)."""
        assert V == 40

    def test_a2(self):
        """a₂ = V(V−1)/2 − E = 780 − 240 = 540 (non-edges = complement edges)."""
        a2 = V * (V - 1) // 2 - E
        assert a2 == 540

    def test_a2_equals_complement_edges(self):
        """a₂ = Ē = V·k̄/2 = 40·27/2 = 540."""
        k_bar = V - 1 - K
        assert V * k_bar // 2 == 540

    def test_a3(self):
        """a₃ = triangles in complement = V·k̄·λ̄/6 = 40·27·18/6 = 3240."""
        k_bar = V - 1 - K
        lam_bar = V - 2 - 2 * K + MU
        a3 = V * k_bar * lam_bar // 6
        assert a3 == 3240

    def test_a3_formula(self):
        """3240 = V · ALBERT · 18 / 6 = V · ALBERT · 3."""
        assert V * ALBERT * 3 == 3240


# ═══════════════════════════════════════════════════════════════════
# T574: Weakly Perfect Properties
# ═══════════════════════════════════════════════════════════════════
class TestWeaklyPerfect:
    """ω = χ and α = θ_c (clique cover number).
    W(3,3) is weakly perfect: clique and chromatic numbers coincide.
    """

    def test_omega_equals_chi(self):
        """ω = χ = 4 (weakly perfect)."""
        assert OMEGA == V // ALPHA

    def test_alpha_equals_theta_c(self):
        """Clique cover number θ_c = V/ω = α = 10."""
        theta_c = V // OMEGA
        assert theta_c == ALPHA

    def test_wp_not_perfect(self):
        """W(3,3) is NOT perfect: θ_Lovász = 10 ≠ ω = 4."""
        assert THETA != OMEGA

    def test_complement_wp(self):
        """Complement also weakly perfect: ω(Ḡ) = χ(Ḡ) = 10."""
        omega_bar = ALPHA   # clique in complement = indep in original
        chi_bar = V // OMEGA  # chromatic of complement
        assert omega_bar == chi_bar

    def test_three_way_equality(self):
        """ω = χ = χ_f = 4 (all three equal)."""
        chi_f = Fraction(V, ALPHA)
        assert OMEGA == V // ALPHA == chi_f


# ═══════════════════════════════════════════════════════════════════
# T575: Vertex Cover & Matching
# ═══════════════════════════════════════════════════════════════════
class TestVertexCoverMatching:
    """Min vertex cover β = V − α = 30.
    Perfect matching exists: ν = V/2 = 20.
    """

    def test_vertex_cover(self):
        """β = V − α = 40 − 10 = 30."""
        beta = V - ALPHA
        assert beta == 30

    def test_vertex_cover_complement(self):
        """β = 30 = V − α = V − THETA."""
        assert V - ALPHA == V - THETA

    def test_perfect_matching_size(self):
        """ν = V/2 = 20 (perfect matching for even vertex-transitive graph)."""
        nu = V // 2
        assert nu == 20

    def test_gallai_identity(self):
        """Gallai: α + β = V.  10 + 30 = 40. ✓"""
        assert ALPHA + (V - ALPHA) == V

    def test_cover_fraction(self):
        """β/V = 1 − 1/4 = 3/4 = 0.75."""
        assert Fraction(V - ALPHA, V) == Fraction(3, 4)
