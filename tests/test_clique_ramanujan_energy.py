"""
Phase XLVII: Clique Geometry, Ramanujan Property & Spectral Energy (T666-T680)
==============================================================================

From the five SRG parameters (v,k,λ,μ,q) = (40,12,2,4,3) we derive the complete
clique geometry of W(3,3) = Sp(4,3), prove the Ramanujan property via Ihara zeta
discriminants, establish algebraic connectivity and expansion identities, and
uncover spectral energy invariants linking the graph to number theory.

Key discoveries:
  - W(3,3) has exactly V=40 max cliques of size ω=μ=4, perfectly partitioning E=240 edges
  - The clique-vertex incidence matrix B satisfies B^T B = μI + A with rank N²=25
  - All Ihara poles lie on |u|=1/√(K-1) → W(3,3) is Ramanujan
  - Ihara discriminant for r-poles is -V=-40 (the vertex count itself!)
  - Graph energy = E/2 = V·q = K·α = 120 (four equivalent forms)
  - det(A) = -q·2^{DIM_O·Φ₆} with exponent 56 = 8×7
  - Heat trace second derivative Z''(0) = 2E·Φ₃ = 6240

All derived from (40, 12, 2, 4, 3). Zero free parameters.
"""

import pytest
import math
from fractions import Fraction

# ── fundamental constants ──────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                   # 240
R, S = 2, -4                     # adjacency eigenvalues
F, G = 24, 15                    # multiplicities
N = Q + 2                        # 5
THETA = K - R                    # 10
ALPHA = V // MU                  # 10
OMEGA = MU                       # 4  (clique number)
DIM_O = K - MU                   # 8
ALBERT = V - (Q**2 + MU)         # 27
PHI3 = Q**2 + Q + 1              # 13
PHI6 = Q**2 - Q + 1              # 7
K_BAR = V - 1 - K                # 27


# ── T666: Clique Geometry ──────────────────────────────────────────
class TestT666CliqueGeometry:
    """Max clique structure of Sp(4,3): size ω = μ = q+1 and count = V."""

    def test_clique_number_is_mu(self):
        assert OMEGA == MU == 4

    def test_clique_size_from_q(self):
        assert OMEGA == Q + 1

    def test_vertex_count_formula(self):
        assert V == (Q**4 - 1) // (Q - 1)

    def test_number_of_max_cliques(self):
        n_cliques = (Q + 1) * (Q**2 + 1)
        assert n_cliques == V

    def test_max_cliques_factor(self):
        assert V == OMEGA * ALPHA


# ── T667: Edge-Clique Partition ────────────────────────────────────
class TestT667EdgeCliquePartition:
    """Every edge lies in exactly one max clique; V cliques × C(ω,2) = E."""

    def test_edges_per_clique(self):
        assert OMEGA * (OMEGA - 1) // 2 == 6

    def test_total_clique_edges_is_E(self):
        n_cliques = V
        edges_per = OMEGA * (OMEGA - 1) // 2
        assert n_cliques * edges_per == E

    def test_edge_partition_ratio(self):
        assert E // V == OMEGA * (OMEGA - 1) // 2


# ── T668: Vertex-Clique Incidence ──────────────────────────────────
class TestT668VertexCliqueIncidence:
    """Each vertex in K/(ω−1) = μ max cliques; K = μ(ω−1); λ = ω−2."""

    def test_cliques_per_vertex(self):
        assert K // (OMEGA - 1) == MU

    def test_K_from_clique_structure(self):
        assert K == MU * (OMEGA - 1)

    def test_lambda_from_omega(self):
        assert LAM == OMEGA - 2

    def test_double_counting(self):
        cliques_per_v = K // (OMEGA - 1)
        assert V * cliques_per_v // OMEGA == V

    def test_neighborhood_partition(self):
        groups = MU
        size = OMEGA - 1
        assert groups * size == K


# ── T669: Incidence Matrix Spectrum ────────────────────────────────
class TestT669IncidenceMatrixSpectrum:
    """B^T B = μI + A has eigenvalues {μ+K, μ+r, μ+s=0}; rank = V−g = N²."""

    def test_btb_eigenvalue_trivial(self):
        assert MU + K == 16

    def test_btb_eigenvalue_r(self):
        assert MU + R == 6

    def test_btb_eigenvalue_s_is_zero(self):
        assert MU + S == 0

    def test_rank_btb(self):
        rank = V - G
        assert rank == 25
        assert rank == N**2

    def test_nullity(self):
        assert G == 15

    def test_btb_trace(self):
        """trace(B^T B) = V·μ since each vertex appears in μ cliques."""
        trace = (MU + K) + F * (MU + R) + G * (MU + S)
        assert trace == V * MU


# ── T670: Fractional Chromatic Duality ─────────────────────────────
class TestT670FractionalChromaticDuality:
    """χ_f(G) = ω = μ; χ_f(Ḡ) = α; product = V."""

    def test_chi_f(self):
        chi_f = V // ALPHA
        assert chi_f == OMEGA

    def test_chi_f_is_mu(self):
        assert V // ALPHA == MU

    def test_chi_f_bar(self):
        chi_f_bar = V // OMEGA
        assert chi_f_bar == ALPHA

    def test_product_is_V(self):
        assert (V // ALPHA) * (V // OMEGA) == V

    def test_clique_cover_number(self):
        assert V // OMEGA == ALPHA


# ── T671: Ramanujan Property ──────────────────────────────────────
class TestT671RamanujanProperty:
    """r², s² ≤ 4(K−1) = 44; all Ihara poles on |u| = 1/√(K−1)."""

    def test_r_squared_bound(self):
        assert R**2 <= 4 * (K - 1)

    def test_s_squared_bound(self):
        assert S**2 <= 4 * (K - 1)

    def test_ramanujan_bound_value(self):
        assert 4 * (K - 1) == 44

    def test_ihara_pole_modulus_r(self):
        mod_sq = Fraction(R**2 + abs(R**2 - 4*(K-1)), 4*(K-1)**2)
        assert mod_sq == Fraction(1, K - 1)

    def test_ihara_pole_modulus_s(self):
        mod_sq = Fraction(S**2 + abs(S**2 - 4*(K-1)), 4*(K-1)**2)
        assert mod_sq == Fraction(1, K - 1)

    def test_ramanujan_radius(self):
        # 1/sqrt(K-1) = 1/sqrt(11)
        assert K - 1 == 11


# ── T672: Ihara Zeta Discriminants ─────────────────────────────────
class TestT672IharaZetaDiscriminants:
    """disc_r = −V; disc_s = −ω·Φ₆; exponent = E−V = V·N."""

    def test_discriminant_r(self):
        disc = R**2 - 4 * (K - 1)
        assert disc == -V

    def test_discriminant_s(self):
        disc = S**2 - 4 * (K - 1)
        assert abs(disc) == OMEGA * PHI6

    def test_disc_s_value(self):
        assert abs(S**2 - 4*(K-1)) == 28

    def test_ihara_exponent(self):
        assert E - V == 200

    def test_ihara_exponent_VN(self):
        assert E - V == V * N

    def test_ihara_exponent_DIM_O_N2(self):
        assert E - V == DIM_O * N**2


# ── T673: Algebraic Connectivity ──────────────────────────────────
class TestT673AlgebraicConnectivity:
    """K − r = Θ = α = 10; Cheeger lower bound = N."""

    def test_algebraic_connectivity(self):
        assert K - R == THETA

    def test_alg_conn_is_alpha(self):
        assert K - R == ALPHA

    def test_cheeger_lower(self):
        cheeger_lb = Fraction(K - R, 2)
        assert cheeger_lb == N

    def test_laplacian_eigenvalue_sum(self):
        assert F * (K - R) + G * (K - S) == 2 * E

    def test_balanced_trace(self):
        """f(K−r) = g(K−s) = E: perfectly balanced Laplacian."""
        assert F * (K - R) == E
        assert G * (K - S) == E


# ── T674: Expansion Ratio ─────────────────────────────────────────
class TestT674ExpansionRatio:
    """K/max(|r|,|s|) = q; spectral gap = DIM_O."""

    def test_expansion_ratio_Q(self):
        assert K // max(abs(R), abs(S)) == Q

    def test_spectral_gap(self):
        gap = K - max(abs(R), abs(S))
        assert gap == DIM_O

    def test_spectral_gap_value(self):
        assert K - max(abs(R), abs(S)) == 8


# ── T675: Normalized Laplacian ─────────────────────────────────────
class TestT675NormalizedLaplacian:
    """Eigenvalues 5/6, 4/3; sum = Φ₃/6; product = α/q²."""

    def test_nlap_r(self):
        assert 1 - Fraction(R, K) == Fraction(5, 6)

    def test_nlap_s(self):
        assert 1 - Fraction(S, K) == Fraction(4, 3)

    def test_nlap_sum(self):
        total = (1 - Fraction(R, K)) + (1 - Fraction(S, K))
        assert total == Fraction(PHI3, 6)

    def test_nlap_product(self):
        prod = (1 - Fraction(R, K)) * (1 - Fraction(S, K))
        assert prod == Fraction(ALPHA, Q**2)

    def test_nlap_product_value(self):
        assert Fraction(ALPHA, Q**2) == Fraction(10, 9)


# ── T676: Graph Energy ────────────────────────────────────────────
class TestT676GraphEnergy:
    """Energy = K + f|r| + g|s| = E/2 = V·q = K·α = 120."""

    def test_graph_energy(self):
        energy = K + F * abs(R) + G * abs(S)
        assert energy == 120

    def test_energy_half_E(self):
        assert K + F * abs(R) + G * abs(S) == E // 2

    def test_energy_Vq(self):
        assert K + F * abs(R) + G * abs(S) == V * Q

    def test_energy_K_alpha(self):
        assert K + F * abs(R) + G * abs(S) == K * ALPHA

    def test_four_forms_equal(self):
        assert E // 2 == V * Q == K * ALPHA == 120


# ── T677: Heat Kernel Anatomy ─────────────────────────────────────
class TestT677HeatKernelAnatomy:
    """Z(0)=V, Z'(0)=−2E, Z''(0)=2E·Φ₃; balanced trace f(K−r)=g(K−s)=E."""

    def test_heat_kernel_at_zero(self):
        assert 1 + F + G == V

    def test_heat_kernel_first_derivative(self):
        deriv = F * (K - R) + G * (K - S)
        assert deriv == 2 * E

    def test_heat_kernel_second_derivative(self):
        deriv2 = F * (K - R)**2 + G * (K - S)**2
        assert deriv2 == 2 * E * PHI3

    def test_second_derivative_value(self):
        assert F * (K - R)**2 + G * (K - S)**2 == 6240

    def test_balanced_laplacian_f_branch(self):
        assert F * (K - R) == E

    def test_balanced_laplacian_g_branch(self):
        assert G * (K - S) == E


# ── T678: Spectral Determinant ─────────────────────────────────────
class TestT678SpectralDeterminant:
    """det(A) = −q·2^{DIM_O·Φ₆}; 2-exponent 56 = 8×7."""

    def test_det_A(self):
        det = K * R**F * S**G
        assert det == -Q * 2**56

    def test_exponent_56(self):
        # 2^2 from K=12, 2^24 from r^f, 2^30 from |s|^g, sign from (-4)^15
        exp = 2 + F + 2 * G
        assert exp == 56

    def test_exponent_is_DIM_O_PHI6(self):
        assert 2 + F + 2 * G == DIM_O * PHI6

    def test_det_sign(self):
        """det(A) is negative since g=15 is odd and s<0."""
        assert K * R**F * S**G < 0


# ── T679: Characteristic Polynomial Evaluations ────────────────────
class TestT679CharPolyEvaluations:
    """p(1) = −(K−1)·N^g; 1−s = N; q−s = Φ₆; p(q) = −q²·Φ₆^g."""

    def test_1_minus_s_is_N(self):
        assert 1 - S == N

    def test_1_minus_r(self):
        assert 1 - R == -1

    def test_q_minus_s_is_PHI6(self):
        assert Q - S == PHI6

    def test_q_minus_K(self):
        assert Q - K == -Q**2

    def test_p_at_1(self):
        p1 = (1 - K) * (1 - R)**F * (1 - S)**G
        assert p1 == -(K - 1) * N**G

    def test_p_at_q(self):
        pq = (Q - K) * (Q - R)**F * (Q - S)**G
        assert pq == -Q**2 * PHI6**G


# ── T680: Complement Triangle Count ───────────────────────────────
class TestT680ComplementTriangleCount:
    """C₃(Ḡ) = V·K̄·λ̄/6 = 3240; mixed triangles = 6480."""

    def test_complement_params(self):
        LAM_BAR = V - 2 - 2 * K + MU
        MU_BAR = V - 2 * K + LAM
        assert LAM_BAR == 18
        assert MU_BAR == 18

    def test_C3_complement(self):
        LAM_BAR = V - 2 - 2 * K + MU
        C3_bar = V * K_BAR * LAM_BAR // 6
        assert C3_bar == 3240

    def test_C3_original(self):
        C3 = V * K * LAM // 6
        assert C3 == 160

    def test_mixed_triangles(self):
        C3_total = V * (V - 1) * (V - 2) // 6
        C3 = V * K * LAM // 6
        LAM_BAR = V - 2 - 2 * K + MU
        C3_bar = V * K_BAR * LAM_BAR // 6
        mixed = C3_total - C3 - C3_bar
        assert mixed == 6480

    def test_total_triples(self):
        assert V * (V - 1) * (V - 2) // 6 == 9880

    def test_C3_bar_ratio(self):
        """C₃(Ḡ)/C₃(G) = K̄·λ̄/(K·λ) = 27·18/(12·2) = 81/4 = q⁴/ω."""
        C3 = V * K * LAM // 6
        LAM_BAR = V - 2 - 2 * K + MU
        C3_bar = V * K_BAR * LAM_BAR // 6
        ratio = Fraction(C3_bar, C3)
        assert ratio == Fraction(Q**4, OMEGA)
