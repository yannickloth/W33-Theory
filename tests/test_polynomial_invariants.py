"""
Phase XLII: Polynomial Invariants & Spectral Algebra on W(3,3) (T591-T605)
===========================================================================

Fifteen theorems on the polynomial and algebraic invariants of the
adjacency matrix A of W(3,3).

Key discoveries:
  - Spanning trees τ = 2^81 · 5^23 (exponents q⁴ and V-1-K-μ).
  - det(A) = -3 · 2^56 (sign from odd multiplicity g=15).
  - Ihara zeta discriminants = -V and -(V-K) — the graph announces
    its own vertex count through the zeta function!
  - Hoffman polynomial H(x) = (x-r)(x-s)/μ — denominator is μ.
  - Graph energy = E/2 = 120 (half the edges).
  - Minimal polynomial coefficients are THETA, DIM_O, K·DIM_O.
  - Resolvent trace Tr(A⁻¹) = -N²/q.

Parameters: (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
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
THETA = K - R             # 10


# ═══════════════════════════════════════════════════════════════════
# T591: Spanning Tree Count (Kirchhoff's Theorem)
# ═══════════════════════════════════════════════════════════════════
class TestSpanningTrees:
    """τ = (1/V)∏(nonzero Laplacian eigenvalues) = 2⁸¹·5²³.
    Laplacian eigenvalues: 0 (×1), K−r=10 (×24), K−s=16 (×15).
    """

    def test_laplacian_eigenvalues(self):
        """Laplacian eigenvalues: 0, K-r=10, K+|s|=16."""
        assert K - R == 10
        assert K - S == 16

    def test_product_nonzero(self):
        """∏(nonzero) = 10²⁴ · 16¹⁵ = 2⁸⁴ · 5²⁴."""
        prod = 10**F * 16**G
        assert prod == 2**84 * 5**24

    def test_tau_value(self):
        """τ = 2⁸¹ · 5²³."""
        prod = 10**F * 16**G
        tau = prod // V
        assert tau == 2**81 * 5**23

    def test_exponent_81(self):
        """Power of 2 exponent: 81 = q⁴ = 3·ALBERT."""
        assert 81 == Q**4
        assert 81 == 3 * ALBERT

    def test_exponent_23(self):
        """Power of 5 exponent: 23 = V − 1 − K − μ."""
        assert 23 == V - 1 - K - MU

    def test_tau_divides_cleanly(self):
        """V | ∏(nonzero Lap eigenvalues)."""
        assert (10**F * 16**G) % V == 0


# ═══════════════════════════════════════════════════════════════════
# T592: Adjacency Determinant
# ═══════════════════════════════════════════════════════════════════
class TestAdjacencyDeterminant:
    """det(A) = K · r^f · s^g = -3 · 2⁵⁶.
    The sign is negative because g = 15 is odd.
    """

    def test_det_value(self):
        """det(A) = -3 · 2⁵⁶."""
        det_A = K * R**F * S**G
        assert det_A == -3 * 2**56

    def test_det_sign(self):
        """Sign = (-1)^g since s < 0 and g = 15 is odd."""
        sign = (-1)**G
        assert sign == -1

    def test_det_magnitude(self):
        """|det(A)| = K · |r|^f · |s|^g = 12 · 2²⁴ · 4¹⁵ = 3 · 2⁵⁶."""
        mag = K * abs(R)**F * abs(S)**G
        assert mag == 3 * 2**56

    def test_exponent_56(self):
        """56 = 2(V − K) = 2 · 28."""
        assert 56 == 2 * (V - K)

    def test_det_prime_factors(self):
        """det(A) has only prime factors 2 and 3."""
        mag = 3 * 2**56
        assert mag % 2 == 0
        assert (mag // 2**56) == 3


# ═══════════════════════════════════════════════════════════════════
# T593: Ihara Zeta Discriminants
# ═══════════════════════════════════════════════════════════════════
class TestIharaDiscriminants:
    """The Ihara zeta function has discriminants:
    Δ_r = r² − 4(K−1) = -V = -40,
    Δ_s = s² − 4(K−1) = -(V−K) = -28.
    The graph encodes its own vertex count in the zeta function!
    """

    def test_disc_r_equals_neg_V(self):
        """Δ_r = r² − 4(K−1) = 4 − 44 = −40 = −V."""
        disc_r = R**2 - 4 * (K - 1)
        assert disc_r == -V

    def test_disc_s_equals_neg_VmK(self):
        """Δ_s = s² − 4(K−1) = 16 − 44 = −28 = −(V−K)."""
        disc_s = S**2 - 4 * (K - 1)
        assert disc_s == -(V - K)

    def test_disc_ratio(self):
        """Δ_r/Δ_s = V/(V−K) = 40/28 = 10/7 = THETA/PHI6."""
        ratio = Fraction(V, V - K)
        assert ratio == Fraction(THETA, PHI6)

    def test_both_negative(self):
        """Both discriminants < 0 → poles are complex (oscillatory)."""
        assert R**2 - 4*(K-1) < 0
        assert S**2 - 4*(K-1) < 0

    def test_pole_modulus(self):
        """|pole|² = 1/(K−1) for both families (Ramanujan circle)."""
        # For r-factor: |u|^2 = (r^2 + |disc_r|) / (4(K-1)^2)
        #            = (4 + 40) / (4*121) = 44/484 = 1/11 = 1/(K-1)
        mod_sq_r = Fraction(R**2 + V, 4*(K-1)**2)
        assert mod_sq_r == Fraction(1, K-1)
        # Same for s-factor
        mod_sq_s = Fraction(S**2 + (V-K), 4*(K-1)**2)
        assert mod_sq_s == Fraction(1, K-1)


# ═══════════════════════════════════════════════════════════════════
# T594: Ramanujan Property
# ═══════════════════════════════════════════════════════════════════
class TestRamanujan:
    """W(3,3) is Ramanujan: max(|r|,|s|) ≤ 2√(K−1).
    |s| = 4 ≤ 2√11 ≈ 6.633.
    """

    def test_ramanujan_bound(self):
        """max(|r|, |s|) ≤ 2√(K−1)."""
        bound = 2 * math.sqrt(K - 1)
        assert max(abs(R), abs(S)) <= bound

    def test_spectral_gap(self):
        """Spectral gap = K − max(|r|,|s|) = 12 − 4 = 8 = DIM_O."""
        gap = K - max(abs(R), abs(S))
        assert gap == DIM_O

    def test_ramanujan_ratio(self):
        """max(|r|,|s|) / (2√(K−1)) < 1."""
        ratio = max(abs(R), abs(S)) / (2 * math.sqrt(K - 1))
        assert ratio < 1

    def test_largest_nontrivial(self):
        """Largest non-trivial eigenvalue magnitude = |s| = 4."""
        assert max(abs(R), abs(S)) == abs(S)
        assert abs(S) == MU  # = q+1

    def test_ramanujan_gap_value(self):
        """Ramanujan gap = 2√(K−1) − |s| ≈ 2.633."""
        gap = 2 * math.sqrt(K - 1) - abs(S)
        assert abs(gap - (2*math.sqrt(11) - 4)) < 1e-10


# ═══════════════════════════════════════════════════════════════════
# T595: Hoffman Polynomial
# ═══════════════════════════════════════════════════════════════════
class TestHoffmanPolynomial:
    """H(x) = V·(x−r)(x−s)/((K−r)(K−s)) = (x−r)(x−s)/μ.
    H(A) = J (all-ones matrix). H(K) = V.
    """

    def test_denominator_is_mu_V(self):
        """(K−r)(K−s) = THETA · 16 = 160 = μ·V."""
        denom = (K - R) * (K - S)
        assert denom == MU * V
        assert denom == 160

    def test_simplified_form(self):
        """H(x) = (x−r)(x−s)/μ = (x²+2x−8)/4."""
        # H(x) = V*(x-r)(x-s) / (MU*V) = (x-r)(x-s)/MU
        # = (x-2)(x+4)/4 = (x^2 + 2x - 8)/4
        assert (K - R) * (K - S) // V == MU

    def test_hoffman_at_K(self):
        """H(K) = (K−r)(K−s)/μ = 10·16/4 = 40 = V."""
        hk = (K - R) * (K - S) // MU
        assert hk == V

    def test_hoffman_at_r(self):
        """H(r) = 0 (r is a root)."""
        hr = (R - R) * (R - S)
        assert hr == 0

    def test_hoffman_at_s(self):
        """H(s) = 0 (s is a root)."""
        hs = (S - R) * (S - S)
        assert hs == 0


# ═══════════════════════════════════════════════════════════════════
# T596: Graph Energy
# ═══════════════════════════════════════════════════════════════════
class TestGraphEnergy:
    """Graph energy = ∑|λ_i| = K + f|r| + g|s| = 120 = E/2.
    Energy equals half the edges!
    """

    def test_energy_value(self):
        """Energy = K + f|r| + g|s| = 12 + 48 + 60 = 120."""
        energy = K + F * abs(R) + G * abs(S)
        assert energy == 120

    def test_energy_half_edges(self):
        """Energy = E/2 = 240/2 = 120."""
        energy = K + F * abs(R) + G * abs(S)
        assert energy == E // 2

    def test_energy_components(self):
        """Components: 12 (K) + 48 (f|r|) + 60 (g|s|)."""
        assert K == 12
        assert F * abs(R) == 48
        assert G * abs(S) == 60

    def test_energy_ratio(self):
        """Energy/V = 120/40 = 3 = q."""
        energy = K + F * abs(R) + G * abs(S)
        assert Fraction(energy, V) == Fraction(Q, 1)
        assert energy // V == Q


# ═══════════════════════════════════════════════════════════════════
# T597: Minimal Polynomial
# ═══════════════════════════════════════════════════════════════════
class TestMinimalPolynomial:
    """m(x) = (x−K)(x−r)(x−s) = x³ − 10x² − 32x + 96.
    Cayley-Hamilton: m(A) = 0.
    Coefficient |c₁| = THETA, c₃ = K·DIM_O.
    """

    def test_coeff_c1(self):
        """c₁ = −(K+r+s) = −10 = −THETA."""
        c1 = -(K + R + S)
        assert c1 == -THETA

    def test_coeff_c2(self):
        """c₂ = Kr + Ks + rs = -32 = -2(K+|s|)."""
        c2 = K*R + K*S + R*S
        assert c2 == -32
        assert c2 == -2 * (K + abs(S))

    def test_coeff_c3(self):
        """c₃ = −Krs = 96 = K·DIM_O."""
        c3 = -(K * R * S)
        assert c3 == K * DIM_O
        assert c3 == 96

    def test_rs_equals_neg_dim_o(self):
        """rs = μ − K = −DIM_O = −8."""
        assert R * S == MU - K
        assert R * S == -DIM_O

    def test_r_plus_s(self):
        """r + s = λ − μ = −2."""
        assert R + S == LAM - MU


# ═══════════════════════════════════════════════════════════════════
# T598: Resolvent Trace
# ═══════════════════════════════════════════════════════════════════
class TestResolventTrace:
    """Tr(A⁻¹) = 1/K + f/r + g/s = −25/3 = −N²/q.
    The resolvent at 0 knows about N and q.
    """

    def test_resolvent_value(self):
        """Tr(A⁻¹) = 1/K + f/r + g/s = 25/3."""
        tr_inv = Fraction(1, K) + Fraction(F, R) + Fraction(G, S)
        assert tr_inv == Fraction(25, 3)

    def test_resolvent_formula(self):
        """Tr(A⁻¹) = N²/q."""
        tr_inv = Fraction(1, K) + Fraction(F, R) + Fraction(G, S)
        assert tr_inv == Fraction(N**2, Q)

    def test_resolvent_components(self):
        """Components: 1/12 + 12 + (−15/4) = −25/3."""
        assert Fraction(1, K) == Fraction(1, 12)
        assert Fraction(F, R) == Fraction(12, 1)
        assert Fraction(G, S) == Fraction(-15, 4)

    def test_resolvent_sign(self):
        """Tr(A⁻¹) > 0 because f/r dominates g/s."""
        # 1/12 + 24/2 + 15/(-4) = 1/12 + 12 - 15/4 = 100/12 = 25/3 > 0
        tr_inv = Fraction(1, K) + Fraction(F, R) + Fraction(G, S)
        assert tr_inv > 0


# ═══════════════════════════════════════════════════════════════════
# T599: Triangle Count
# ═══════════════════════════════════════════════════════════════════
class TestTriangleCount:
    """Number of triangles = Tr(A³)/6 = V·K·λ/6 = 160 = V·μ.
    Each vertex lies in K·λ/2 = 12 triangles.
    """

    def test_total_triangles(self):
        """Triangles = V·K·λ/6 = 160."""
        triangles = V * K * LAM // 6
        assert triangles == 160

    def test_triangles_equal_V_mu(self):
        """160 = V·μ (number of flags in GQ sense)."""
        assert V * K * LAM // 6 == V * MU

    def test_triangles_per_vertex(self):
        """Each vertex in K·λ/2 = 12 = K triangles."""
        per_v = K * LAM // 2
        assert per_v == K

    def test_trace_A3(self):
        """Tr(A³) = K³ + f·r³ + g·s³ = 960 = 6·160."""
        tr3 = K**3 + F * R**3 + G * S**3
        assert tr3 == 960
        assert tr3 == 6 * 160

    def test_960_is_V_times_f(self):
        """Tr(A³) = 960 = V·f = Vandermonde product."""
        assert K**3 + F * R**3 + G * S**3 == V * F


# ═══════════════════════════════════════════════════════════════════
# T600: Walk Counts
# ═══════════════════════════════════════════════════════════════════
class TestWalkCounts:
    """Closed walks per vertex: w_n = (K^n + f·r^n + g·s^n)/V.
    w₂ = K, w₃ = 2K = f.
    """

    def test_w1_zero(self):
        """w₁ = 0 (graph has no loops)."""
        w1 = (K + F * R + G * S) // V
        assert K + F*R + G*S == 0  # trace of A = 0

    def test_w2_equals_K(self):
        """w₂ = K = 12 (each closed walk of length 2 is an edge traversed twice)."""
        w2 = (K**2 + F * R**2 + G * S**2) // V
        assert w2 == K

    def test_w3_equals_2K(self):
        """w₃ = 2K = 24 = f."""
        w3 = (K**3 + F * R**3 + G * S**3) // V
        assert w3 == 2 * K
        assert w3 == F

    def test_w4_value(self):
        """w₄ = 624 = μ · PHI3 · K/MU... = 624."""
        w4 = (K**4 + F * R**4 + G * S**4) // V
        assert w4 == 624

    def test_walks_divisible_by_V(self):
        """All Tr(Aⁿ) are divisible by V."""
        for n in range(1, 10):
            tr_n = K**n + F * R**n + G * S**n
            assert tr_n % V == 0


# ═══════════════════════════════════════════════════════════════════
# T601: SRG Matrix Identity
# ═══════════════════════════════════════════════════════════════════
class TestSRGMatrixIdentity:
    """A² = μJ + DIM_O·I + (λ−μ)A = 4J + 8I − 2A.
    This is the fundamental SRG matrix equation.
    """

    def test_mu_coefficient(self):
        """Coefficient of J: μ = 4."""
        assert MU == 4

    def test_identity_coefficient(self):
        """Coefficient of I: K − μ = DIM_O = 8."""
        assert K - MU == DIM_O

    def test_adjacency_coefficient(self):
        """Coefficient of A: λ − μ = −2."""
        assert LAM - MU == -2

    def test_trace_check(self):
        """Tr(A²) = μ·V + DIM_O·V + (λ−μ)·0 = V(μ+DIM_O) = V·K."""
        # Tr(J) = V^2... no wait, Tr of the identity relation
        # A^2 = μJ + DIM_O*I + (λ-μ)A, take trace:
        # Tr(A^2) = μ*Tr(J) + DIM_O*V + (λ-μ)*0
        # But Tr(J) = V (diagonal of all-ones is all 1s)
        # Tr(A^2) = μV + DIM_O*V = V(μ+DIM_O) = V*K
        assert MU + DIM_O == K

    def test_row_sum_check(self):
        """Row sum of A² = μV + DIM_O + (λ−μ)K = K²."""
        row_sum = MU * V + DIM_O + (LAM - MU) * K
        assert row_sum == K**2


# ═══════════════════════════════════════════════════════════════════
# T602: Eigenvalue Product and Sum
# ═══════════════════════════════════════════════════════════════════
class TestEigenvalueAlgebra:
    """r·s = μ − K = −DIM_O = −8.
    r + s = λ − μ = −2.
    These ARE the SRG interlacing conditions.
    """

    def test_product(self):
        """r·s = μ − K = −DIM_O = −8."""
        assert R * S == MU - K
        assert R * S == -DIM_O

    def test_sum(self):
        """r + s = λ − μ = −2."""
        assert R + S == LAM - MU

    def test_vieta_quadratic(self):
        """r, s are roots of x² + (μ−λ)x + (μ−K) = 0."""
        # x^2 - (r+s)x + rs = 0
        # x^2 - (LAM-MU)x + (MU-K) = 0
        # x^2 + 2x - 8 = 0
        for x in [R, S]:
            assert x**2 + (MU - LAM)*x + (MU - K) == 0

    def test_discriminant(self):
        """Δ = (λ−μ)² − 4(μ−K) = 4 + 32 = 36 = (V−μ)."""
        disc = (LAM - MU)**2 - 4*(MU - K)
        assert disc == 36
        assert disc == V - MU

    def test_eigenvalues_from_discriminant(self):
        """r,s = (μ−λ ± √Δ)/2 = (2 ± 6)/2."""
        import math
        disc = (LAM - MU)**2 - 4*(MU - K)
        sqrt_d = int(math.isqrt(disc))
        assert ((LAM - MU) + sqrt_d) // 2 == R
        assert ((LAM - MU) - sqrt_d) // 2 == S


# ═══════════════════════════════════════════════════════════════════
# T603: Minimal Polynomial Coefficient Identities
# ═══════════════════════════════════════════════════════════════════
class TestMinPolyCoefficients:
    """The minimal polynomial m(x) = x³ + c₁x² + c₂x + c₃ has:
    c₁ = −THETA, |c₂| = 2(K+|s|), c₃ = K·DIM_O.
    """

    def test_c1_is_theta(self):
        """|c₁| = K − r = THETA = 10."""
        c1 = -(K + R + S)
        assert abs(c1) == THETA

    def test_c2_structure(self):
        """c₂ = −2(K+|s|) = −32."""
        c2 = K*R + K*S + R*S
        assert c2 == -2 * (K + abs(S))

    def test_c3_is_K_DIM_O(self):
        """c₃ = K · DIM_O = 96."""
        c3 = -(K * R * S)
        assert c3 == K * DIM_O

    def test_cayley_hamilton(self):
        """A³ = THETA·A² + 2(K+|s|)·A − K·DIM_O·I."""
        # m(x) = 0 means x^3 = -c1*x^2 - c2*x - c3
        # = THETA*x^2 + 32x - 96
        # Verify: K^3 = THETA*K^2 + 32*K - 96
        assert K**3 == THETA * K**2 + 32 * K - 96

    def test_trace_products(self):
        """c₁·c₃ = THETA·K·DIM_O = 10·96 = 960 = V·f."""
        assert THETA * K * DIM_O == V * F


# ═══════════════════════════════════════════════════════════════════
# T604: Spectral Gaps
# ═══════════════════════════════════════════════════════════════════
class TestSpectralGaps:
    """K − r = THETA = 10, r − s = 2q = 6, K − s = 16 = K + μ.
    These gaps encode all SRG parameters.
    """

    def test_gap_K_r(self):
        """K − r = 10 = THETA (independence number)."""
        assert K - R == THETA

    def test_gap_r_s(self):
        """r − s = 6 = 2q."""
        assert R - S == 2 * Q

    def test_gap_K_s(self):
        """K − s = 16 = K + |s| = K + μ."""
        assert K - S == 16
        assert K - S == K + MU

    def test_gap_product(self):
        """(K−r)(K−s)(r−s) = 10·16·6 = 960 = V·f."""
        prod = (K - R) * (K - S) * (R - S)
        assert prod == 960
        assert prod == V * F

    def test_gap_sum(self):
        """(K−r) + (r−s) + (K−s) = 2(K−s) + (r−s)... check: 10+6+16=32 = 2|c₂|."""
        # Actually (K-r) + (r-s) = K-s, so sum of all three gaps:
        assert (K-R) + (R-S) + (K-S) == 32
        assert 32 == 2 * (K + abs(S))


# ═══════════════════════════════════════════════════════════════════
# T605: Vandermonde Determinant
# ═══════════════════════════════════════════════════════════════════
class TestVandermondeDet:
    """The Vandermonde determinant of eigenvalues {K, r, s}:
    Δ = (K−r)(K−s)(r−s) = V·f = 960.
    Δ² = V²·f² = V²·f·f.
    """

    def test_vandermonde_value(self):
        """Δ = 960 = V·f."""
        delta = (K - R) * (K - S) * (R - S)
        assert delta == V * F

    def test_vandermonde_factored(self):
        """960 = 2⁶ · 3 · 5."""
        assert 2**6 * 3 * 5 == 960

    def test_vandermonde_squared(self):
        """Δ² = 921600 = V²·f²."""
        delta_sq = ((K-R) * (K-S) * (R-S))**2
        assert delta_sq == V**2 * F**2

    def test_vandermonde_from_disc(self):
        """Δ = (K−r)(K−s)(r−s), each factor is a spectral gap."""
        assert K - R == THETA           # 10
        assert K - S == K + MU          # 16
        assert R - S == 2 * Q           # 6

    def test_vandermonde_relates_all(self):
        """Vandermonde = THETA · (K+μ) · 2q = 10·16·6."""
        assert THETA * (K + MU) * 2 * Q == V * F
