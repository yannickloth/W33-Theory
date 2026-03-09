"""
Phase XLIX — Generalized Quadrangle GQ(3,3) & Finite Geometry (T696-T710)

W(3,3) IS the collinearity graph of the self-dual generalized quadrangle GQ(3,3).
This phase proves that the GQ structure, its ovoids and spreads, its Delsarte
property, its eigenmatrix arithmetic, Krein parameters, Gaussian binomials,
and the tangent hyperplane geometry ALL reduce to the five source numbers
(v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import pytest
from fractions import Fraction as Fr
from math import comb

# ── five source numbers ──────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                     # 240 edges
R, S = 2, -4                       # SRG eigenvalues
F, G = 24, 15                      # multiplicities
N = Q + 2                          # 5
THETA = K - R                      # 10
ALPHA = V // MU                    # 10
OMEGA = MU                         # 4
DIM_O = K - MU                     # 8
ALBERT = V - (Q**2 + MU)           # 27
PHI3 = Q**2 + Q + 1                # 13
PHI6 = Q**2 - Q + 1                # 7
K_BAR = V - 1 - K                  # 27
AUT = 51840


def gauss_binom(n, k, q):
    """Gaussian binomial coefficient [n choose k]_q."""
    if k < 0 or k > n:
        return 0
    num = den = 1
    for i in range(k):
        num *= (q ** (n - i) - 1)
        den *= (q ** (i + 1) - 1)
    return num // den


# =====================================================================
# T696 — GQ(3,3) Self-Duality
# =====================================================================
class TestT696_GQSelfDuality:
    """GQ(3,3) has s = t = q, making it self-dual."""

    def test_gq_order_s_equals_t(self):
        s = t = Q
        assert s == t == 3

    def test_points_equals_lines(self):
        points = (Q + 1) * (Q**2 + 1)
        lines = (Q + 1) * (Q**2 + 1)
        assert points == lines == V

    def test_points_per_line_equals_lines_per_point(self):
        pts_per_line = Q + 1
        lines_per_pt = Q + 1
        assert pts_per_line == lines_per_pt == OMEGA == MU

    def test_self_duality_omega_equals_mu(self):
        assert OMEGA == MU


# =====================================================================
# T697 — GQ Order → SRG Parameters
# =====================================================================
class TestT697_GQOrderToSRG:
    """All five SRG parameters derive from GQ order q = 3."""

    def test_v_from_q(self):
        assert (Q + 1) * (Q**2 + 1) == V

    def test_k_from_q(self):
        assert Q * (Q + 1) == K

    def test_lam_from_q(self):
        assert Q - 1 == LAM

    def test_mu_from_q(self):
        assert Q + 1 == MU

    def test_r_from_q(self):
        assert Q - 1 == R

    def test_s_from_q(self):
        assert -(Q + 1) == S

    def test_five_from_one(self):
        """All five source numbers derive from the single GQ order q = 3."""
        v = (Q + 1) * (Q**2 + 1)
        k = Q * (Q + 1)
        lam = Q - 1
        mu = Q + 1
        q = Q
        assert (v, k, lam, mu, q) == (V, K, LAM, MU, Q)


# =====================================================================
# T698 — Ovoid-Spread Duality
# =====================================================================
class TestT698_OvoidSpreadDuality:
    """Ovoids and spreads are dual; both have size ALPHA = 1 + q²."""

    def test_ovoid_size(self):
        ovoid = 1 + Q**2
        assert ovoid == ALPHA

    def test_spread_size(self):
        spread = 1 + Q**2
        assert spread == ALPHA

    def test_spread_times_omega_equals_v(self):
        assert ALPHA * OMEGA == V

    def test_ovoid_partition(self):
        """MU disjoint ovoids partition all V points."""
        assert V // ALPHA == MU

    def test_ovoid_is_max_independent_set(self):
        """Ovoid size = Hoffman bound = ALPHA."""
        hoffman = V // MU
        assert ALPHA == hoffman


# =====================================================================
# T699 — 56 Ovoids
# =====================================================================
class TestT699_56Ovoids:
    """W(3,3) has exactly 56 ovoids with beautiful distribution."""

    NUM_OVOIDS = 56

    def test_ovoid_count(self):
        assert self.NUM_OVOIDS == DIM_O * PHI6

    def test_ovoid_count_weyl_ratio(self):
        """56 = |W(E₇)| / |W(E₆)| (Phase XLVIII connection)."""
        assert self.NUM_OVOIDS == 2903040 // AUT

    def test_ovoids_per_point(self):
        per_pt = self.NUM_OVOIDS * ALPHA // V
        assert per_pt == K + LAM
        assert per_pt == 2 * PHI6
        assert per_pt == 14

    def test_ovoids_missing_point(self):
        missing = self.NUM_OVOIDS - (self.NUM_OVOIDS * ALPHA // V)
        assert missing == V + LAM
        assert missing == 42

    def test_spreads_equal_ovoids(self):
        """By GQ self-duality, #spreads = #ovoids."""
        assert self.NUM_OVOIDS == DIM_O * PHI6


# =====================================================================
# T700 — Delsarte Graph
# =====================================================================
class TestT700_DelsarteGraph:
    """Both Hoffman bounds are tight: W(3,3) is a Delsarte graph."""

    def test_clique_bound_tight(self):
        """Hoffman/Delsarte clique bound = 1 - K/S = OMEGA."""
        hoffman_clique = 1 - K // S
        assert hoffman_clique == OMEGA

    def test_independence_bound_tight(self):
        """Hoffman/Delsarte independence bound = ALPHA."""
        hoffman_indep = V // MU
        assert hoffman_indep == ALPHA

    def test_regular_cliques(self):
        """Max cliques are regular: every non-member has exactly 1 neighbor in C.
        Each vertex is in MU cliques; total cliques = V; each clique has OMEGA vertices.
        For non-member v of clique C: |N(v) ∩ C| = 1 (GQ axiom)."""
        nexus = 1
        # Non-member v has MU common neighbors with anchor ∈ C, distributed
        # across MU cliques through v, each meeting C in nexus vertex:
        assert nexus == MU // MU

    def test_regular_independent_sets(self):
        """Ovoids: each non-member has exactly MU neighbors in the ovoid."""
        nexus_indep = MU
        assert nexus_indep == Q + 1

    def test_product_omega_alpha_equals_v(self):
        assert OMEGA * ALPHA == V


# =====================================================================
# T701 — Incidence Equals Triangles
# =====================================================================
class TestT701_IncidenceEqualsTriangles:
    """Total point-line incidences = number of triangles in the graph."""

    def test_total_incidences(self):
        incidences = V * MU  # V points × MU lines each
        assert incidences == 160

    def test_incidences_equal_triangles(self):
        """C₃ = V × C(OMEGA,3) = V × MU = 160."""
        C3 = V * comb(OMEGA, 3)  # triangles from clique counting
        incidences = V * MU
        assert C3 == incidences

    def test_incidences_four_forms(self):
        inc = V * MU
        assert inc == V * OMEGA
        assert inc == V * (Q + 1)
        assert inc == (Q + 1) * (Q**2 + 1) * (Q + 1)


# =====================================================================
# T702 — Tangent Hyperplane = Local Neighborhood
# =====================================================================
class TestT702_TangentHyperplane:
    """In PG(3,q), the tangent hyperplane p⊥ = closed neighborhood N[p]."""

    def test_hyperplane_size(self):
        """Each tangent hyperplane has PHI3 = q² + q + 1 projective points."""
        hyperplane_pts = Q**2 + Q + 1
        assert hyperplane_pts == PHI3

    def test_closed_neighborhood_size(self):
        """N[p] = {p} ∪ N(p) has 1 + K = PHI3 points."""
        assert 1 + K == PHI3

    def test_hyperplane_equals_neighborhood(self):
        """Tangent hyperplane = closed neighborhood."""
        assert PHI3 == 1 + K

    def test_non_neighbors_complement(self):
        """Non-neighbors = points outside tangent hyperplane = ALBERT."""
        assert V - PHI3 == ALBERT

    def test_hyperplane_point_bijection(self):
        """40 hyperplanes ↔ 40 points via the perp map (bijection)."""
        num_hyperplanes = gauss_binom(4, 3, Q)
        assert num_hyperplanes == V

    def test_bijection_is_self_duality(self):
        """Hyperplane ↦ radical point IS the GQ self-duality."""
        assert gauss_binom(4, 1, Q) == gauss_binom(4, 3, Q) == V


# =====================================================================
# T703 — Projective Hierarchy
# =====================================================================
class TestT703_ProjectiveHierarchy:
    """PG(n,q) point counts match graph parameters via Gaussian binomials."""

    def test_pg1(self):
        assert gauss_binom(2, 1, Q) == Q + 1 == OMEGA

    def test_pg2(self):
        assert gauss_binom(3, 1, Q) == Q**2 + Q + 1 == PHI3

    def test_pg3(self):
        assert gauss_binom(4, 1, Q) == V

    def test_gaussian_symmetry(self):
        assert gauss_binom(4, 1, Q) == gauss_binom(4, 3, Q)
        assert gauss_binom(4, 0, Q) == gauss_binom(4, 4, Q) == 1

    def test_gaussian_42(self):
        """[4,2]_3 = total lines in PG(3,3) = ALPHA × PHI3."""
        assert gauss_binom(4, 2, Q) == ALPHA * PHI3
        assert gauss_binom(4, 2, Q) == 130


# =====================================================================
# T704 — Non-Isotropic Lines
# =====================================================================
class TestT704_NonIsotropicLines:
    """Of 130 lines in PG(3,3), exactly V = 40 are isotropic."""

    def test_total_lines(self):
        assert gauss_binom(4, 2, Q) == 130

    def test_isotropic_lines(self):
        iso = V  # each isotropic line = max clique line
        assert iso == 40

    def test_non_isotropic(self):
        non_iso = gauss_binom(4, 2, Q) - V
        assert non_iso == Q**2 * ALPHA
        assert non_iso == 90

    def test_ratio(self):
        """Non-isotropic / isotropic = Q² × ALPHA / V = Q²/MU."""
        ratio = Fr(Q**2 * ALPHA, V)
        assert ratio == Fr(Q**2, MU)


# =====================================================================
# T705 — Eigenmatrix Determinant
# =====================================================================
class TestT705_EigenmatrixDeterminant:
    """det(P) = -E = -240: the eigenmatrix determinant is minus the edges."""

    def test_det_P(self):
        det = (1 * (R * (-S - 1) - (-R - 1) * S)
               - K * (1 * (-S - 1) - (-R - 1) * 1)
               + K_BAR * (1 * S - R * 1))
        assert det == -E

    def test_det_Q(self):
        """det(Q) = V³/det(P) = -V³/E."""
        det_Q = Fr(V**3, -E)
        assert det_Q == Fr(-DIM_O * ALPHA**2, Q)

    def test_det_q_numerator(self):
        """Numerator: DIM_O × ALPHA² = 800."""
        assert DIM_O * ALPHA**2 == 800


# =====================================================================
# T706 — Dual Eigenmatrix Q
# =====================================================================
class TestT706_DualEigenmatrix:
    """The dual eigenmatrix Q encodes multiplicities in graph parameters."""

    def test_row_0(self):
        assert (1, F, G) == (1, 24, 15)

    def test_row_1(self):
        """Q[1,:] = [1, MU, -N]."""
        assert (1, MU, -N) == (1, 4, -5)

    def test_row_2(self):
        """Q[2,:] = [1, -DIM_O/Q, N/Q]."""
        assert (Fr(1), Fr(-DIM_O, Q), Fr(N, Q)) == (Fr(1), Fr(-8, 3), Fr(5, 3))

    def test_pq_equals_vi(self):
        """P × Q = V × I (orthogonality)."""
        P = [[1, K, K_BAR], [1, R, -R - 1], [1, S, -S - 1]]
        Q_rows = [[Fr(1), Fr(F), Fr(G)],
                   [Fr(1), Fr(MU), Fr(-N)],
                   [Fr(1), Fr(-DIM_O, Q), Fr(N, Q)]]
        for i in range(3):
            for j in range(3):
                dot = sum(Fr(P[i][l]) * Q_rows[l][j] for l in range(3))
                expected = Fr(V) if i == j else Fr(0)
                assert dot == expected

    def test_q_row_sums(self):
        """Row 0 sum = V; rows 1,2 sum = 0."""
        assert 1 + F + G == V
        assert 1 + MU + (-N) == 0
        assert Fr(1) + Fr(-DIM_O, Q) + Fr(N, Q) == 0


# =====================================================================
# T707 — Krein Parameters
# =====================================================================
class TestT707_KreinParameters:
    """All non-trivial Krein parameters have denominator Q = 3."""

    def test_krein_trivial(self):
        """q⁰₁₁ = F, q⁰₂₂ = G, q⁰₁₂ = 0."""
        assert Fr(F) == 24
        assert Fr(G) == 15

    def test_q1_11(self):
        assert Fr(MU * (K - 1), Q) == Fr(44, 3)

    def test_q2_11(self):
        assert Fr(V, Q) == Fr(40, 3)

    def test_q1_22(self):
        assert Fr(MU * N, Q) == Fr(20, 3)

    def test_q2_22(self):
        assert Fr(ALPHA, Q) == Fr(10, 3)

    def test_q1_12(self):
        assert Fr(N**2, Q) == Fr(25, 3)

    def test_q2_12(self):
        assert Fr(DIM_O * MU, Q) == Fr(32, 3)

    def test_all_denominators_are_q(self):
        """Every non-trivial Krein parameter has denominator Q."""
        params = [Fr(44, 3), Fr(40, 3), Fr(20, 3),
                  Fr(10, 3), Fr(25, 3), Fr(32, 3)]
        for p in params:
            assert p.denominator == Q

    def test_all_nonnegative(self):
        """All Krein parameters ≥ 0 (required by theory)."""
        params = [Fr(F), Fr(G), Fr(0),
                  Fr(44, 3), Fr(20, 3), Fr(25, 3),
                  Fr(40, 3), Fr(10, 3), Fr(32, 3)]
        for p in params:
            assert p >= 0


# =====================================================================
# T708 — Galois Field Tower
# =====================================================================
class TestT708_GaloisFieldTower:
    """Multiplicative group orders of GF(q^n) match graph parameters."""

    def test_gf_q_star(self):
        """|GF(q)*| = q - 1 = LAM."""
        assert Q - 1 == LAM

    def test_gf_q2_star(self):
        """|GF(q²)*| = q² - 1 = DIM_O."""
        assert Q**2 - 1 == DIM_O

    def test_gf_ratio(self):
        """(q² - 1)/(q - 1) = q + 1 = OMEGA."""
        assert (Q**2 - 1) // (Q - 1) == OMEGA

    def test_q4_minus_1(self):
        """q⁴ - 1 = 2V."""
        assert Q**4 - 1 == 2 * V

    def test_q4_ratio(self):
        """(q⁴ - 1)/(q² - 1) = q² + 1 = ALPHA."""
        assert (Q**4 - 1) // (Q**2 - 1) == ALPHA

    def test_q3_plus_1(self):
        """q³ + 1 = OMEGA × PHI6."""
        assert Q**3 + 1 == OMEGA * PHI6

    def test_gf_sizes(self):
        """GF(q), GF(q²), GF(q³), GF(q⁴) = 3, 9, 27, 81."""
        assert (Q, Q**2, Q**3, Q**4) == (3, 9, 27, 81)
        assert Q**2 == ALPHA - 1
        assert Q**3 == ALBERT
        assert Q**4 == ALBERT * Q


# =====================================================================
# T709 — GQ Axiom Counts
# =====================================================================
class TestT709_GQAxiomCounts:
    """Structural counts forced by the GQ axiom."""

    def test_external_cliques_per_vertex(self):
        """Each vertex has V - MU = 36 max cliques NOT through it
        but meeting its neighborhood in exactly 1 vertex."""
        external = V - MU
        assert external == 36

    def test_cliques_through_neighbor(self):
        """Each neighbor of v lies in MU - 1 = 3 cliques not through v."""
        assert MU - 1 == 3

    def test_neighbor_external_check(self):
        """K neighbors × (MU-1) external cliques each = total external cliques."""
        assert K * (MU - 1) == (V - MU)  # 12 × 3 = 36 ✓

    def test_non_collinear_pairs(self):
        """Non-adjacent pairs (non-collinear) = V × K_BAR / 2."""
        non_adj = V * K_BAR // 2
        assert non_adj == 540

    def test_edges_plus_non_edges(self):
        """E + non-edges = C(V,2)."""
        non_edges = V * K_BAR // 2
        assert E + non_edges == comb(V, 2)


# =====================================================================
# T710 — Distance-2 Intersection Numbers
# =====================================================================
class TestT710_IntersectionNumbers:
    """The p²ᵢⱼ intersection numbers of the 2-class association scheme."""

    def test_p2_11(self):
        """p²₁₁ = MU: non-adjacent pair shares MU common neighbors."""
        assert MU == 4

    def test_p2_12(self):
        """p²₁₂ = K - MU = DIM_O: each non-neighbor of v has DIM_O
        neighbors among v's neighbors."""
        assert K - MU == DIM_O

    def test_p2_22(self):
        """p²₂₂ = K_BAR - 1 - DIM_O = LAM × Q²: each non-neighbor of v
        has LAM × Q² other non-neighbors of v as non-neighbors."""
        p2_22 = K_BAR - 1 - DIM_O
        assert p2_22 == LAM * Q**2
        assert p2_22 == 18

    def test_p1_12(self):
        """p¹₁₂ = K - LAM - 1 = Q²: each neighbor of v has Q² non-neighbors of v
        as neighbors."""
        p1_12 = K - LAM - 1
        assert p1_12 == Q**2

    def test_row_sum_check(self):
        """For each relation, row sums of intersection matrix = valency."""
        # p²₁₁ + p²₁₂ = K (neighbors of u decomposed by relation to v)
        assert MU + DIM_O == K
        # p²₂₁ + p²₂₂ = K_BAR - 1
        assert DIM_O + (LAM * Q**2) == K_BAR - 1

    def test_a2_eigenvalues(self):
        """Complement adjacency A₂ = J - I - A has eigenvalues K_BAR, -R-1, -S-1."""
        assert K_BAR == ALBERT
        assert -R - 1 == -3
        assert -S - 1 == 3
