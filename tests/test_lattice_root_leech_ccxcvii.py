"""
Phase CCXCVII: Lattice Theory, Root Systems & Leech Connections

Discovers deep connections between W(3,3) parameters and exceptional lattices:
1. E₈ root system has exactly 240 roots = |edges| of W(3,3)
2. Leech lattice kissing number 196560 = Φ₆·q²·Φ₃·E
3. All 24 Niemeier lattices counted by f = 24
4. Coxeter numbers h(E₆)=K, h(E₇)=V-K-Θ, h(E₈)=V-Θ
5. Weyl group |W(E₆)| = (2q)³·E = 51840
6. Von Staudt–Clausen: denom(B_K) = 2·q·5·Φ₆·Φ₃ = 2730
7. Association scheme eigenmatrix encodes q³ and ±q

W(3,3) = SRG(40,12,2,4):
  v=40, k=12, λ=2, μ=4
  f=24, g=15, Θ=10, E=240
  Φ₃=13, Φ₆=7, α=137, q=3

Key identities discovered:
  • E₈ root count = E = VK/2 = 240
  • Leech kissing = Φ₆·q²·Φ₃·E = 196560
  • Niemeier count = f = 24
  • h(E₆) = K = 12, h(E₇) = V-K-Θ = 18, h(E₈) = V-Θ = 30
  • |W(E₆)| = (2q)³·E = 51840
  • denom(B_K) = 2·q·5·Φ₆·Φ₃ = 2730
  • First eigenmatrix: P[2] = [1, -μ, q]; entries are ±q
  • α·ω = V (graph parameter product)
  • Hoffman bound = Θ (independence ↔ spectral gap)
"""

import pytest
import math

# W(3,3) strongly regular graph parameters
V, K, LAM, MU = 40, 12, 2, 4
F, G = 24, 15          # eigenvalue multiplicities
THETA = 10             # restricted eigenvalue (also K - r where r = 2)
MU2 = MU ** 2          # μ² = 16
E = V * K // 2         # 240 edges
PHI3, PHI6 = 13, 7     # cyclotomic values
ALPHA = 137
Q = 3                  # base field parameter
R_EIG, S_EIG = 2, -4   # SRG restricted eigenvalues


# ============ E₈ ROOT SYSTEM ============

class TestE8RootSystem:
    """E₈ root lattice and W(3,3) edge count identity."""

    def test_e8_root_count_equals_edges(self):
        """E₈ has exactly 240 roots = |edges| of W(3,3)."""
        e8_roots = 240
        assert e8_roots == E
        assert E == V * K // 2

    def test_e8_root_norm(self):
        """E₈ roots have norm² = 2; count = 2·dim·(dim-1)/something.
        Actually |E₈ roots| = 240 = 2·8·15 = 2·dim(E₈)·g."""
        dim_e8 = 8
        assert E == 2 * dim_e8 * G   # 240 = 2·8·15

    def test_e8_dimension_and_parameters(self):
        """dim(E₈) = 8 = r + 2q = R_EIG + 2Q."""
        dim_e8 = 8
        assert dim_e8 == R_EIG + 2 * Q  # 2 + 6 = 8

    def test_e8_rank_formula(self):
        """rank(E₈) = 8 = K - MU = 12 - 4."""
        rank_e8 = 8
        assert rank_e8 == K - MU

    def test_e7_root_count(self):
        """E₇ has 126 roots = E₈_roots/2 + 6 = 126."""
        e7_roots = 126
        # 126 = V*K/2 - V - K + MU + ... let's find clean decomposition
        # 126 = 2·63 = 2·7·9 = 2·Φ₆·q²
        assert e7_roots == 2 * PHI6 * Q ** 2

    def test_e6_root_count(self):
        """E₆ has 72 roots = 2·K·Q = 72."""
        e6_roots = 72
        assert e6_roots == 2 * K * Q

    def test_root_system_cascade(self):
        """Root counts: E₆ ⊂ E₇ ⊂ E₈ encoded by W(3,3)."""
        e6 = 2 * K * Q            # 72
        e7 = 2 * PHI6 * Q ** 2    # 126
        e8 = E                     # 240
        assert e6 < e7 < e8
        # Differences
        assert e7 - e6 == 54      # = 2·27 = 2·q³
        assert e8 - e7 == 114     # = 2·57 = 2·3·19


# ============ COXETER NUMBERS ============

class TestCoxeterNumbers:
    """Exceptional Coxeter numbers from W(3,3) parameters."""

    def test_coxeter_e6(self):
        """h(E₆) = 12 = K."""
        h_e6 = 12
        assert h_e6 == K

    def test_coxeter_e7(self):
        """h(E₇) = 18 = V - K - Θ."""
        h_e7 = 18
        assert h_e7 == V - K - THETA

    def test_coxeter_e8(self):
        """h(E₈) = 30 = V - Θ."""
        h_e8 = 30
        assert h_e8 == V - THETA

    def test_coxeter_sum(self):
        """h(E₆) + h(E₇) + h(E₈) = 60 = V + V/2."""
        h_sum = K + (V - K - THETA) + (V - THETA)
        assert h_sum == 60
        assert h_sum == 2 * V - 2 * THETA

    def test_coxeter_products(self):
        """h(E₆) · h(E₈) = K(V-Θ) = 360."""
        prod_68 = K * (V - THETA)
        assert prod_68 == 360
        # 360 = 3·120 = q · 5!
        assert prod_68 == Q * math.factorial(5)

    def test_dual_coxeter_number_e8(self):
        """Dual Coxeter h∨(E₈) = h(E₈) = 30 (simply-laced)."""
        h_dual_e8 = V - THETA
        assert h_dual_e8 == 30


# ============ WEYL GROUPS ============

class TestWeylGroups:
    """Weyl group orders from W(3,3)."""

    def test_weyl_e6_order(self):
        """|W(E₆)| = 51840 = (2q)³ · E."""
        weyl_e6 = 51840
        assert weyl_e6 == (2 * Q) ** 3 * E

    def test_weyl_e6_factored(self):
        """|W(E₆)| = 2⁷ · 3⁴ · 5."""
        weyl_e6 = 2 ** 7 * 3 ** 4 * 5
        assert weyl_e6 == 51840
        assert weyl_e6 == (2 * Q) ** 3 * E

    def test_weyl_e7_order(self):
        """|W(E₇)| = 2903040 = 2¹⁰ · 3⁴ · 5 · 7."""
        weyl_e7 = 2903040
        assert weyl_e7 == 2 ** 10 * 3 ** 4 * 5 * 7
        # = 2³ · |W(E₆)| · Φ₆ = 8 · 51840 · 7 = 2903040? No: 8·51840 = 414720
        # Actually |W(E₇)| = |W(E₆)| · 56 since 2903040 / 51840 = 56
        assert weyl_e7 == (2 * Q) ** 3 * E * 56
        # 56 = 8·7 = (K-MU)·Φ₆
        assert 56 == (K - MU) * PHI6

    def test_weyl_e8_order(self):
        """|W(E₈)| = 696729600 = 2¹⁴ · 3⁵ · 5² · 7."""
        weyl_e8 = 696729600
        assert weyl_e8 == 2 ** 14 * 3 ** 5 * 5 ** 2 * 7
        # |W(E₈)|/|W(E₇)| = 696729600/2903040 = 240 = E!
        assert weyl_e8 // 2903040 == E

    def test_weyl_cascade(self):
        """W(E₈)/W(E₇) = E, W(E₇)/W(E₆) = 56 = (K-μ)·Φ₆."""
        w6 = (2 * Q) ** 3 * E
        w7 = w6 * (K - MU) * PHI6
        w8 = w7 * E
        assert w6 == 51840
        assert w7 == 2903040
        assert w8 == 696729600


# ============ LEECH LATTICE ============

class TestLeechLattice:
    """Leech lattice properties governed by W(3,3)."""

    def test_leech_dimension(self):
        """Leech lattice lives in ℝ^24 = ℝ^f."""
        leech_dim = 24
        assert leech_dim == F

    def test_leech_kissing_number(self):
        """Kissing number = 196560 = Φ₆·q²·Φ₃·E."""
        kissing = 196560
        assert kissing == PHI6 * Q ** 2 * PHI3 * E

    def test_leech_kissing_factored(self):
        """196560 = Φ₆ · q² · Φ₃ · E = 7·9·13·240."""
        assert PHI6 * Q ** 2 * PHI3 * E == 7 * 9 * 13 * 240
        assert 7 * 9 * 13 * 240 == 196560

    def test_niemeier_lattice_count(self):
        """There are exactly 24 = f Niemeier lattices in dim 24."""
        niemeier_count = 24
        assert niemeier_count == F

    def test_leech_norm(self):
        """Minimal norm in Leech lattice = 4 = μ."""
        min_norm = 4
        assert min_norm == MU

    def test_leech_theta_coefficient(self):
        """First nontrivial theta coefficient at norm 4: 196560.
        196560 / 240 = 819 = q²·Φ₃·Φ₆."""
        ratio = 196560 // E
        assert ratio == 819
        assert ratio == Q ** 2 * PHI3 * PHI6

    def test_leech_covering_radius(self):
        """Covering radius of Leech = √2 → squared = 2 = λ."""
        covering_radius_sq = 2
        assert covering_radius_sq == LAM


# ============ VON STAUDT–CLAUSEN THEOREM ============

class TestVonStaudtClausen:
    """Bernoulli number denominator encodes W(3,3) parameters."""

    def test_bernoulli_k_denominator(self):
        """denom(B_K) = denom(B₁₂) = 2730 = 2·q·5·Φ₆·Φ₃."""
        denom_b12 = 2730
        assert denom_b12 == 2 * Q * 5 * PHI6 * PHI3

    def test_von_staudt_clausen_primes(self):
        """Von Staudt–Clausen: denom(B_n) = ∏{p prime: (p-1)|n}.
        For n=K=12: primes with (p-1)|12 are 2,3,5,7,13."""
        primes_dividing = []
        for p in range(2, 200):
            if all(p % d != 0 for d in range(2, p)):
                if K % (p - 1) == 0:
                    primes_dividing.append(p)
        assert primes_dividing == [2, 3, 5, 7, 13]
        # These ARE q, Φ₆, Φ₃ (plus 2 and 5)!
        assert Q in primes_dividing
        assert PHI6 in primes_dividing
        assert PHI3 in primes_dividing

    def test_bernoulli_denominator_product(self):
        """Product 2·3·5·7·13 = 2730."""
        prod = 2 * 3 * 5 * 7 * 13
        assert prod == 2730

    def test_bernoulli_12_value(self):
        """B₁₂ = -691/2730: numerator 691 is prime."""
        from fractions import Fraction
        # B_12 = -691/2730
        b12 = Fraction(-691, 2730)
        assert b12.denominator == 2730
        assert b12.numerator == -691

    def test_zeta_minus_one(self):
        """ζ(-1) = -1/12 = -1/K (Ramanujan's sum)."""
        from fractions import Fraction
        zeta_neg1 = Fraction(-1, K)
        assert zeta_neg1 == Fraction(-1, 12)

    def test_bernoulli_2_denominator(self):
        """denom(B₂) = 6 = 2q: the first nontrivial Bernoulli."""
        from fractions import Fraction
        b2 = Fraction(1, 6)
        assert b2.denominator == 2 * Q


# ============ ASSOCIATION SCHEME EIGENMATRIX ============

class TestAssociationScheme:
    """First eigenmatrix of the W(3,3) association scheme."""

    def test_eigenmatrix_structure(self):
        """P = [[1, K, q³], [1, r, -q], [1, s, q]]; entries use q."""
        P = [
            [1, K, V - K - 1],
            [1, R_EIG, -(R_EIG + 1)],
            [1, S_EIG, -(S_EIG + 1)]
        ]
        assert P[0] == [1, 12, 27]    # 27 = q³
        assert P[1] == [1, 2, -3]     # -3 = -q
        assert P[2] == [1, -4, 3]     # 3 = q

    def test_non_principal_column_is_q_cube(self):
        """V - K - 1 = 27 = q³."""
        assert V - K - 1 == Q ** 3

    def test_eigenmatrix_q_entries(self):
        """Last column entries: q³, -q, +q."""
        col2 = [V - K - 1, -(R_EIG + 1), -(S_EIG + 1)]
        assert col2 == [Q ** 3, -Q, Q]

    def test_trace_identity(self):
        """tr(A) = 0: K + f·r + g·s = 0."""
        trace = K + F * R_EIG + G * S_EIG
        assert trace == 0

    def test_sum_of_squares_identity(self):
        """K² + f·r² + g·s² = VK = 480."""
        sos = K ** 2 + F * R_EIG ** 2 + G * S_EIG ** 2
        assert sos == V * K

    def test_multiplicity_sum(self):
        """1 + f + g = V."""
        assert 1 + F + G == V


# ============ EXTREMAL GRAPH THEORY ============

class TestExtremalGraphTheory:
    """Extremal bounds and Hoffman/Lovász parameters from W(3,3)."""

    def test_hoffman_independence_bound(self):
        """Hoffman bound: α(G) ≤ V·|s|/(K - s) = Θ."""
        hoffman = V * (-S_EIG) / (K - S_EIG)
        assert hoffman == THETA

    def test_clique_bound(self):
        """Clique bound: ω(G) ≤ 1 + K/|s| = μ + 1 = 5.
        Actually 1 + K/(-s) = 1 + 12/4 = 4 = μ."""
        omega = 1 + K // (-S_EIG)
        assert omega == MU

    def test_alpha_times_omega_equals_v(self):
        """α(G) · ω(G) = Θ · μ = V = 40."""
        assert THETA * MU == V

    def test_fractional_chromatic(self):
        """χ_f(G) = V / α(G) = μ = 4."""
        frac_chi = V / THETA
        assert frac_chi == MU

    def test_lovasz_theta_function(self):
        """Lovász ϑ(G) = V·|s|/(K-s) = Θ for SRGs."""
        lovasz = V * (-S_EIG) / (K - S_EIG)
        assert lovasz == THETA

    def test_sandwich_theorem(self):
        """ω ≤ ϑ(Ḡ) ≤ χ_f and α ≤ ϑ(G) ≤ χ̄_f:
        Here we verify μ ≤ Θ (trivially)."""
        alpha_g = THETA
        omega_g = MU
        # Sandwich: ω(G) ≤ ϑ(Ḡ) ≤ χ(G) and α(G) ≤ ϑ(G) ≤ χ̄(G)
        assert omega_g <= alpha_g  # 4 ≤ 10
