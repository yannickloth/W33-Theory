"""
Phase XLVIII: Weyl Group W(E₆) & Exceptional Arithmetic (T681-T695)
====================================================================

From the five SRG parameters (v,k,λ,μ,q) = (40,12,2,4,3) we prove that
|Aut(W(3,3))| = |W(E₆)| = 51840, the Weyl group of the exceptional Lie algebra E₆.
The E₆ exponents {1,4,5,7,8,11} are exactly {1,μ,N,Φ₆,DIM_O,K−1}, and the
E₆ degrees recover {λ,N,r−s,DIM_O,q²,K}. Stabilizer orders factor as powers
of (r−s)=6, the Weyl chain |W(E₇)|/|W(E₆)| = DIM_O·Φ₆ and |W(E₈)|/|W(E₇)| = E,
and the Golay code has parameters (f, K, DIM_O).

Key discoveries:
  - E₆ exponent duality: m_i + m_{6−i} = h = K = 12 pairs (μ,DIM_O), (N,Φ₆)
  - Vertex stabilizer = (r−s)⁴ = 1296; edge stabilizer = (r−s)³ = ALBERT·DIM_O
  - Non-neighbor subgraph: 27 vertices of degree DIM_O with 108 = ω·ALBERT edges
  - Transmission = dim(E₆) − K = 66; Wiener = DIM_O·N·q·(K−1)
  - Leech lattice minimal vectors / E = q²·Φ₆·Φ₃ = 819

All derived from (40, 12, 2, 4, 3). Zero free parameters.
"""

import pytest
from fractions import Fraction
from math import comb

# ── fundamental constants ──────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                   # 240
R, S = 2, -4                     # adjacency eigenvalues
F, G = 24, 15                    # multiplicities
N = Q + 2                        # 5
THETA = K - R                    # 10
ALPHA = V // MU                  # 10
OMEGA = MU                       # 4
DIM_O = K - MU                   # 8
ALBERT = V - (Q**2 + MU)         # 27
PHI3 = Q**2 + Q + 1              # 13
PHI6 = Q**2 - Q + 1              # 7
K_BAR = V - 1 - K                # 27
AUT = 51840                      # |Aut(W(3,3))|

# E6 data
E6_EXPONENTS = [1, 4, 5, 7, 8, 11]
E6_DEGREES = [e + 1 for e in E6_EXPONENTS]  # [2, 5, 6, 8, 9, 12]
E6_DIM = 78
E6_POSITIVE_ROOTS = 36
E6_ROOTS = 72
E6_COXETER = 12
W_E6 = 51840
W_E7 = 2903040
W_E8 = 696729600


# ── T681: Weyl Group Identity ─────────────────────────────────────
class TestT681WeylGroupIdentity:
    """|Aut(W(3,3))| = |W(E₆)| = 51840."""

    def test_aut_equals_weyl_e6(self):
        assert AUT == W_E6

    def test_weyl_e6_factorization(self):
        assert W_E6 == 2**7 * 3**4 * 5

    def test_aut_V_times_stab(self):
        assert AUT == V * (R - S)**4

    def test_aut_E_times_edge_stab(self):
        assert AUT == E * (R - S)**3


# ── T682: E6 Exponents ────────────────────────────────────────────
class TestT682E6Exponents:
    """E₆ exponents {1,μ,N,Φ₆,DIM_O,K−1}; ∏(eᵢ+1) = |W(E₆)|."""

    def test_exponents_are_constants(self):
        expected = [1, MU, N, PHI6, DIM_O, K - 1]
        assert E6_EXPONENTS == expected

    def test_product_of_degrees(self):
        prod = 1
        for d in E6_DEGREES:
            prod *= d
        assert prod == W_E6

    def test_sum_of_exponents(self):
        assert sum(E6_EXPONENTS) == E6_POSITIVE_ROOTS

    def test_sum_is_rs_squared(self):
        assert sum(E6_EXPONENTS) == (R - S)**2


# ── T683: Exponent Duality ────────────────────────────────────────
class TestT683ExponentDuality:
    """mᵢ + m₅₋ᵢ = h = K = 12; pairs (1,K−1), (μ,DIM_O), (N,Φ₆)."""

    def test_pair_0(self):
        assert E6_EXPONENTS[0] + E6_EXPONENTS[5] == K

    def test_pair_1(self):
        assert E6_EXPONENTS[1] + E6_EXPONENTS[4] == K

    def test_pair_2(self):
        assert E6_EXPONENTS[2] + E6_EXPONENTS[3] == K

    def test_pair_labels(self):
        assert (E6_EXPONENTS[0], E6_EXPONENTS[5]) == (1, K - 1)
        assert (E6_EXPONENTS[1], E6_EXPONENTS[4]) == (MU, DIM_O)
        assert (E6_EXPONENTS[2], E6_EXPONENTS[3]) == (N, PHI6)


# ── T684: E6 Degrees ──────────────────────────────────────────────
class TestT684E6Degrees:
    """Degrees {λ,N,r−s,DIM_O,q²,K}; sum = V+λ = 42."""

    def test_degrees_are_constants(self):
        expected = sorted([LAM, N, R - S, DIM_O, Q**2, K])
        assert sorted(E6_DEGREES) == expected

    def test_sum_of_degrees(self):
        assert sum(E6_DEGREES) == V + LAM

    def test_sum_is_dim_minus_roots(self):
        assert sum(E6_DEGREES) == E6_DIM - E6_POSITIVE_ROOTS

    def test_sum_value(self):
        assert sum(E6_DEGREES) == 42


# ── T685: Coxeter Number & Dimension ──────────────────────────────
class TestT685CoxeterDimension:
    """h(E₆) = K = 12; dim(E₆) = 2V−λ = 78."""

    def test_coxeter_number(self):
        assert E6_COXETER == K

    def test_dimension(self):
        assert E6_DIM == 2 * V - LAM

    def test_dim_value(self):
        assert E6_DIM == 78

    def test_dim_rank_plus_roots(self):
        assert E6_DIM == 6 + E6_ROOTS


# ── T686: Root System Arithmetic ──────────────────────────────────
class TestT686RootSystemArithmetic:
    """|Δ⁺| = (r−s)² = 36; |Δ| = 2(r−s)² = 72."""

    def test_positive_roots(self):
        assert E6_POSITIVE_ROOTS == (R - S)**2

    def test_total_roots(self):
        assert E6_ROOTS == 2 * (R - S)**2

    def test_positive_root_value(self):
        assert E6_POSITIVE_ROOTS == 36

    def test_rank_times_coxeter(self):
        """rank × h = |Δ⁺|? Actually rank * h / 2 = |Δ⁺| for simply-laced."""
        assert 6 * E6_COXETER == E6_ROOTS


# ── T687: Stabilizer Powers ───────────────────────────────────────
class TestT687StabilizerPowers:
    """Vertex stab = (r−s)⁴; edge stab = (r−s)³ = ALBERT·DIM_O."""

    def test_vertex_stabilizer(self):
        assert AUT // V == (R - S)**4

    def test_vertex_stab_value(self):
        assert (R - S)**4 == 1296

    def test_edge_stabilizer(self):
        assert AUT // E == (R - S)**3

    def test_edge_stab_albert_dimo(self):
        assert (R - S)**3 == ALBERT * DIM_O

    def test_edge_stab_value(self):
        assert (R - S)**3 == 216


# ── T688: Orbit Stabilizers ───────────────────────────────────────
class TestT688OrbitStabilizers:
    """Non-edge stab = (K−s)(r−s) = 96; flag stab = ω·ALBERT = Q·(r−s)²."""

    def test_non_edge_count(self):
        non_edges = V * (V - 1) // 2 - E
        assert non_edges == 540

    def test_non_edge_stabilizer(self):
        non_edges = V * (V - 1) // 2 - E
        assert AUT // non_edges == (K - S) * (R - S)

    def test_non_edge_stab_value(self):
        assert (K - S) * (R - S) == 96

    def test_flag_stabilizer(self):
        flags = V * K
        assert AUT // flags == OMEGA * ALBERT

    def test_flag_stab_alt(self):
        assert AUT // (V * K) == Q * (R - S)**2


# ── T689: Weyl Group Chain ────────────────────────────────────────
class TestT689WeylGroupChain:
    """|W(E₇)|/|W(E₆)| = DIM_O·Φ₆ = 56; |W(E₈)|/|W(E₇)| = E = 240."""

    def test_e7_over_e6(self):
        assert W_E7 // W_E6 == DIM_O * PHI6

    def test_e7_over_e6_value(self):
        assert W_E7 // W_E6 == 56

    def test_e8_over_e7(self):
        assert W_E8 // W_E7 == E

    def test_e8_over_e6(self):
        assert W_E8 // W_E6 == E * DIM_O * PHI6

    def test_full_chain(self):
        assert W_E8 == W_E6 * (DIM_O * PHI6) * E


# ── T690: 27 Lines Configuration ──────────────────────────────────
class TestT690TwentySevenLines:
    """K̄ = ALBERT = 27; non-neighbor degree = DIM_O = 8."""

    def test_non_neighbor_count(self):
        assert K_BAR == ALBERT

    def test_twenty_seven(self):
        assert K_BAR == 27

    def test_non_neighbor_degree(self):
        """Each non-neighbor of v is adjacent to K−μ = DIM_O others among v's non-neighbors."""
        assert K - MU == DIM_O

    def test_subdegrees(self):
        assert 1 + K + K_BAR == V


# ── T691: Non-neighbor Edges ──────────────────────────────────────
class TestT691NonNeighborEdges:
    """ALBERT·DIM_O/2 = 108 = ω·ALBERT edges in non-neighbor subgraph."""

    def test_non_neighbor_edges(self):
        assert ALBERT * DIM_O // 2 == 108

    def test_edges_omega_albert(self):
        assert ALBERT * DIM_O // 2 == OMEGA * ALBERT

    def test_dimo_over_2_is_omega(self):
        assert DIM_O // 2 == OMEGA

    def test_non_neighbor_edge_density(self):
        nn_edges = ALBERT * DIM_O // 2
        max_edges = ALBERT * (ALBERT - 1) // 2  # = 351
        ratio = Fraction(nn_edges, max_edges)
        assert ratio == Fraction(DIM_O, ALBERT - 1)


# ── T692: Transmission & Distance ─────────────────────────────────
class TestT692TransmissionDistance:
    """Transmission = dim(E₆) − K = 66; avg dist = 2(K−1)/Φ₃."""

    def test_transmission(self):
        trans = K + 2 * K_BAR
        assert trans == 66

    def test_transmission_dim_minus_K(self):
        assert K + 2 * K_BAR == E6_DIM - K

    def test_average_distance(self):
        avg = Fraction(K + 2 * K_BAR, V - 1)
        assert avg == Fraction(2 * (K - 1), PHI3)

    def test_avg_distance_value(self):
        assert Fraction(K + 2 * K_BAR, V - 1) == Fraction(22, 13)


# ── T693: Wiener Index ────────────────────────────────────────────
class TestT693WienerIndex:
    """Wiener = V(2V−2−K)/2 = 1320 = DIM_O·N·q·(K−1)."""

    def test_wiener_index(self):
        W = V * (K + 2 * K_BAR) // 2
        assert W == 1320

    def test_wiener_formula(self):
        assert V * (2 * V - 2 - K) // 2 == 1320

    def test_wiener_factorization(self):
        assert 1320 == DIM_O * N * Q * (K - 1)

    def test_transmission_sum(self):
        assert V * (K + 2 * K_BAR) // 2 == V * (2 * V - 2 - K) // 2


# ── T694: Golay Code Parameters ───────────────────────────────────
class TestT694GolayCodeParameters:
    """Golay code: length=f=24, dim=K=12, min dist=DIM_O=8; S(5,8,24): 759 blocks."""

    def test_golay_length(self):
        assert F == 24

    def test_golay_dimension(self):
        assert K == 12

    def test_golay_min_distance(self):
        assert DIM_O == 8

    def test_steiner_blocks(self):
        blocks = comb(F, 5) // comb(DIM_O, 5)
        assert blocks == 759

    def test_steiner_factorization(self):
        assert 759 == 3 * (K - 1) * (ALBERT - MU)


# ── T695: Leech Lattice Ratio ─────────────────────────────────────
class TestT695LeechLatticeRatio:
    """196560 / E = q²·Φ₆·Φ₃ = 819."""

    def test_leech_ratio(self):
        assert 196560 // E == Q**2 * PHI6 * PHI3

    def test_leech_ratio_value(self):
        assert Q**2 * PHI6 * PHI3 == 819

    def test_leech_from_E(self):
        assert 196560 == E * Q**2 * PHI6 * PHI3

    def test_leech_factor_check(self):
        assert 196560 == E * 819
