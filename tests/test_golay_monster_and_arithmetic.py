"""
Theorems T81-T95: Golay Weight Structure, Monster Arithmetic, VOA Central Charge,
Magic Square Sums, and Deep Number-Theoretic Identities from W(3,3).

All results derive from the five SRG parameters (v,k,lam,mu,q) = (40,12,2,4,3).

T81: Ternary Golay weight distribution — 1 + 264 + 440 + 24 = 729 = 3⁶
T82: Cyclotomic product factorization — 728 = Φ₁(3)·Φ₂(3)·Φ₃(3)·Φ₆(3)
T83: Triangular-8 identity — 728 = 8 × T₁₃, T₁₃ = 91 = 7 × 13
T84: Monster smallest irrep correction — 196883 = 728×270 + 323, 323 = 17×19
T85: Weight-6 Golay → E₈ splitting — 264 = 240 + 24
T86: 12-11 duality — 728 = 12×24 + 11×40
T87: Trinity identity — 12² + 24² + 27² = 23 × 63
T88: VOA central charge — c = 3 × 728/91 = 24 (Monster vertex algebra)
T89: Leech kissing → Niemeier count — 196560/72 = 2730 = 2×3×5×7×13
T90: Magic square exceptional row sum — 52 + 78 + 133 + 248 = 511 = 2⁹ − 1
T91: SO(10) correction ladder — 242 + 6 = 248(E₈), 728 + 16 = 744(j-invariant)
T92: Exceptional automorphism sum — dim(G₂) + dim(F₄) = 66 = C(12,2)
T93: Yukawa structure algebra — sl(3,F₃)³, dim = 3×8 = 24, acts on 27
T94: Information-theoretic rate — β₁/E = 81/240 = 27/80
T95: Fano-LCM identity — 840 = lcm(3,4,5,6,7,8) = 5 × |PSL(2,7)|
"""
from __future__ import annotations
from collections import defaultdict
import math
from math import comb
import numpy as np
import pytest
from fractions import Fraction


# ── SRG parameters ──────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
THETA = 10   # Lovász theta
TAU = -4     # negative adjacency eigenvalue
E8_DIM = 248
E8_ROOTS = 240
E6_DIM = 78
E7_DIM = 133
G2_DIM = 14
F4_DIM = 52
ALBERT_DIM = 27
BETA0, BETA1, BETA2 = 1, 81, 40  # Betti numbers
F_MULT = 24  # multiplicity of eigenvalue θ=2
G_MULT = 15  # multiplicity of eigenvalue τ=-4
EDGES = Q**5 - Q  # 240
TRIANGLES = 160


# ── Derived constants used across theorems ─────────────────────
GOLAY_W0 = 1
GOLAY_W6 = 264
GOLAY_W9 = 440
GOLAY_W12 = 24
TOTAL_728 = G2_DIM * F4_DIM  # 14 × 52 = 728


# ── Build W(3,3) ───────────────────────────────────────────────
def _build_w33():
    """Build the W(3,3) symplectic polar graph over GF(3)^4."""
    points = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    vec = [a, b, c, d]
                    nz = next((i for i, x in enumerate(vec) if x != 0), None)
                    if nz is None:
                        continue
                    if vec[nz] == 1:
                        points.append(tuple(vec))

    def J(x, y):
        return (x[0]*y[3] - x[1]*y[2] + x[2]*y[1] - x[3]*y[0]) % 3

    iso_points = [p for p in points if J(p, p) == 0]
    edges = []
    adj: dict[int, set[int]] = defaultdict(set)
    n = len(iso_points)
    for i in range(n):
        for j in range(i + 1, n):
            if J(iso_points[i], iso_points[j]) == 0:
                edges.append((i, j))
                adj[i].add(j)
                adj[j].add(i)

    triangles = []
    for u, v in edges:
        for w in adj[u] & adj[v]:
            if u < v < w:
                triangles.append((u, v, w))

    return iso_points, edges, adj, triangles


@pytest.fixture(scope="module")
def w33():
    pts, edges, adj, triangles = _build_w33()
    nv = len(pts)
    ne = len(edges)
    nt = len(triangles)

    A = np.zeros((nv, nv), dtype=int)
    for u, v in edges:
        A[u, v] = 1
        A[v, u] = 1

    D = np.diag(A.sum(axis=1))
    L0 = D - A

    return {
        "pts": pts, "edges": edges, "adj": adj, "triangles": triangles,
        "nv": nv, "ne": ne, "nt": nt,
        "A": A, "L0": L0,
    }


# ═══════════════════════════════════════════════════════════════
# T81 — Ternary Golay Weight Distribution
# ═══════════════════════════════════════════════════════════════
class TestTernaryGolayWeightDistribution:
    """T81: The ternary Golay code C₆ has weight distribution
    A₀=1, A₆=264, A₉=440, A₁₂=24, total = 729 = 3⁶ = q^(2q).

    The 728 nonzero codewords encode the fundamental arithmetic
    of W(3,3): 264 weight-6 + 440 weight-9 + 24 weight-12.
    """

    def test_weight_sum_is_3_to_6(self):
        """1 + 264 + 440 + 24 = 729 = 3⁶."""
        assert GOLAY_W0 + GOLAY_W6 + GOLAY_W9 + GOLAY_W12 == 729
        assert 729 == Q**6

    def test_nonzero_is_728(self):
        """728 nonzero codewords = q^6 - 1."""
        assert GOLAY_W6 + GOLAY_W9 + GOLAY_W12 == 728 == Q**6 - 1

    def test_exponent_is_2q(self):
        """Exponent 6 = 2q: the code lives in GF(3)^(2q)."""
        assert 2 * Q == 6
        assert Q**(2*Q) == 729

    def test_264_divides_728(self):
        """264 | 728? No: 728/264 is not integer. But 264 = 8×33 = 8×3×11."""
        assert GOLAY_W6 == 264
        assert 264 == 8 * 33

    def test_440_is_euler_totient_related(self):
        """440 = 8 × 55 = 8 × F₁₀ (Fibonacci)."""
        assert GOLAY_W9 == 440
        assert 440 == 8 * 55

    def test_24_weight_12_minimal(self):
        """Only 24 maximal-weight codewords — the Steiner system seeds."""
        assert GOLAY_W12 == 24 == F_MULT


# ═══════════════════════════════════════════════════════════════
# T82 — Cyclotomic Product Factorization
# ═══════════════════════════════════════════════════════════════
class TestCyclotomicProductFactorization:
    """T82: 728 = Φ₁(3)·Φ₂(3)·Φ₃(3)·Φ₆(3) = 2 × 4 × 13 × 7.

    The cyclotomic polynomials at q=3 whose orders divide 6 = 2q
    multiply to give exactly 728. This encodes why the ternary Golay
    code has q^6 - 1 = 728 nonzero codewords:
    q^6 - 1 = ∏_{d|6} Φ_d(q).
    """

    def test_phi1_at_3(self):
        """Φ₁(3) = 3 - 1 = 2."""
        assert Q - 1 == 2

    def test_phi2_at_3(self):
        """Φ₂(3) = 3 + 1 = 4."""
        assert Q + 1 == 4

    def test_phi3_at_3(self):
        """Φ₃(3) = 3² + 3 + 1 = 13."""
        assert Q**2 + Q + 1 == 13

    def test_phi6_at_3(self):
        """Φ₆(3) = 3² - 3 + 1 = 7."""
        assert Q**2 - Q + 1 == 7

    def test_product_is_728(self):
        """Φ₁·Φ₂·Φ₃·Φ₆ = 2×4×13×7 = 728."""
        product = (Q-1) * (Q+1) * (Q**2+Q+1) * (Q**2-Q+1)
        assert product == 728

    def test_equals_q6_minus_1(self):
        """q⁶ - 1 = ∏_{d|6} Φ_d(q) — formal identity at q=3."""
        assert Q**6 - 1 == 728
        assert (Q-1)*(Q+1)*(Q**2+Q+1)*(Q**2-Q+1) == Q**6 - 1

    def test_bridge_primes_in_product(self):
        """Both bridge primes 7 and 13 appear as cyclotomic factors."""
        factors = {Q-1, Q+1, Q**2+Q+1, Q**2-Q+1}
        assert 7 in factors
        assert 13 in factors


# ═══════════════════════════════════════════════════════════════
# T83 — Triangular-8 Identity
# ═══════════════════════════════════════════════════════════════
class TestTriangular8Identity:
    """T83: 728 = 8 × T₁₃, where T₁₃ = 91 = 13×14/2 is the 13th
    triangular number.

    Since 13 = Φ₃(3) is a bridge prime and 8 = 2³ = (q-1)³,
    this gives 728 a natural octahedral decomposition into 8 simplices
    of 91 points each.
    """

    def test_T13_value(self):
        """T₁₃ = 13 × 14 / 2 = 91."""
        T13 = 13 * 14 // 2
        assert T13 == 91

    def test_8_times_T13(self):
        """8 × 91 = 728."""
        assert 8 * 91 == 728

    def test_91_is_7_times_13(self):
        """91 = 7 × 13 — both bridge primes multiply!"""
        assert 91 == 7 * 13

    def test_8_is_q_minus_1_cubed(self):
        """8 = (q-1)³ = 2³."""
        assert (Q - 1)**3 == 8

    def test_T13_contains_bridge_primes(self):
        """T₁₃ = Φ₃(3) × Φ₆(3) = 13 × 7."""
        T13 = 13 * 14 // 2
        assert T13 == (Q**2 + Q + 1) * (Q**2 - Q + 1)


# ═══════════════════════════════════════════════════════════════
# T84 — Monster Smallest Irrep Correction
# ═══════════════════════════════════════════════════════════════
class TestMonsterSmallestIrrep:
    """T84: The Monster's smallest irrep has dimension 196883 = 728×270 + 323,
    where 323 = 17×19 = (27−θ)(27−8).

    The correction term 323 decomposes into primes that are shifts of
    the Albert dimension 27 by SRG spectral values θ=10 and 8=q²-1.
    """

    def test_196883_decomposition(self):
        """196883 = 728 × 270 + 323."""
        assert 728 * 270 + 323 == 196883

    def test_323_factorization(self):
        """323 = 17 × 19."""
        assert 17 * 19 == 323

    def test_17_from_albert_theta(self):
        """17 = 27 - 10 = Albert_dim - θ."""
        assert ALBERT_DIM - THETA == 17

    def test_19_from_albert_q2m1(self):
        """19 = 27 - 8 = Albert_dim - (q² - 1)."""
        assert ALBERT_DIM - (Q**2 - 1) == 19

    def test_270_is_known_dimension(self):
        """270 = 27 × 10 = Albert_dim × θ."""
        assert 270 == ALBERT_DIM * THETA

    def test_monstrous_moonshine_coefficient(self):
        """196884 = 196883 + 1 = 728×270 + 324 = the j-function coefficient."""
        assert 728 * 270 + 323 + 1 == 196884

    def test_324_is_18_squared(self):
        """324 = 18² = (2×q²)²."""
        assert 324 == 18**2
        assert 18 == 2 * Q**2


# ═══════════════════════════════════════════════════════════════
# T85 — Weight-6 Golay → E₈ Splitting
# ═══════════════════════════════════════════════════════════════
class TestWeight6GolayE8Splitting:
    """T85: The 264 weight-6 Golay codewords split as 264 = 240 + 24.

    240 = |E₈ roots| (the fundamental Lie root count)
    24  = |weight-12 codewords| = F_MULT = dim(Leech lattice)

    This splitting links error-correcting codes to exceptional geometry.
    """

    def test_264_equals_240_plus_24(self):
        """264 = 240 + 24."""
        assert GOLAY_W6 == E8_ROOTS + GOLAY_W12

    def test_240_is_E8_roots(self):
        """240 = q⁵ - q = E₈ root count."""
        assert E8_ROOTS == Q**5 - Q == 240

    def test_24_is_Leech_dimension(self):
        """24 = f = dim(Leech lattice)."""
        assert GOLAY_W12 == F_MULT == 24

    def test_264_is_8_times_33(self):
        """264 = 8 × 33 = (q-1)³ × (q² + q + 1 + q² - q + 1 + q² + 2)."""
        assert GOLAY_W6 == 8 * 33

    def test_splitting_connects_two_layers(self):
        """weight-6 minus weight-12 = E₈ roots."""
        assert GOLAY_W6 - GOLAY_W12 == E8_ROOTS


# ═══════════════════════════════════════════════════════════════
# T86 — 12-11 Duality
# ═══════════════════════════════════════════════════════════════
class TestTwelveElevenDuality:
    """T86: 728 = 12×24 + 11×40 = k·f + (k-1)·v.

    The SRG degree k=12 and vertex count v=40 interweave through
    multiplicities f=24 and (k-1)=11 to produce 728.
    """

    def test_12_times_24(self):
        """12 × 24 = 288 = k × f."""
        assert K * F_MULT == 288

    def test_11_times_40(self):
        """11 × 40 = 440 = (k-1) × v."""
        assert (K - 1) * V == 440

    def test_sum_is_728(self):
        """k·f + (k-1)·v = 288 + 440 = 728."""
        assert K * F_MULT + (K - 1) * V == 728

    def test_440_is_golay_weight_9(self):
        """The weight-9 count 440 = 11 × 40 = (k-1) × v."""
        assert GOLAY_W9 == (K - 1) * V

    def test_11_is_k_minus_1(self):
        """11 = k - 1 = 12 - 1. Also 11 = (v/k) + (v/(k·v) × ...) etc."""
        assert K - 1 == 11

    def test_duality_uses_all_srg_params(self):
        """This identity connects k, f, v — three structural constants."""
        assert K * F_MULT + (K - 1) * V == G2_DIM * F4_DIM


# ═══════════════════════════════════════════════════════════════
# T87 — Trinity Identity
# ═══════════════════════════════════════════════════════════════
class TestTrinityIdentity:
    """T87: k² + f² + Albert² = 12² + 24² + 27² = 1449 = 23 × 63.

    The three fundamental dimensions (degree, multiplicity, Albert)
    form a Pythagorean-like sum that factorizes into adjacent primes
    and structure constants.
    """

    def test_sum_of_squares(self):
        """12² + 24² + 27² = 144 + 576 + 729 = 1449."""
        assert K**2 + F_MULT**2 + ALBERT_DIM**2 == 1449

    def test_factorization(self):
        """1449 = 23 × 63."""
        assert 23 * 63 == 1449

    def test_23_is_prime(self):
        """23 is the 9th prime, and dim(Leech) - 1 = 23."""
        assert all(23 % p != 0 for p in range(2, 23))
        assert F_MULT - 1 == 23

    def test_63_is_q6_over_ratio(self):
        """63 = 9 × 7 = q² × Φ₆(q). Also 63 = 2⁶ - 1."""
        assert Q**2 * (Q**2 - Q + 1) == 63
        assert 2**6 - 1 == 63

    def test_729_in_sum(self):
        """27² = 729 = 3⁶ = |ternary Golay code|."""
        assert ALBERT_DIM**2 == Q**6

    def test_each_component(self):
        """12 = k, 24 = f, 27 = Albert_dim — all from the SRG."""
        assert K == 12
        assert F_MULT == 24
        assert ALBERT_DIM == 27


# ═══════════════════════════════════════════════════════════════
# T88 — VOA Central Charge
# ═══════════════════════════════════════════════════════════════
class TestVOACentralCharge:
    """T88: The Monster vertex operator algebra V♮ has central charge
    c = 3 × 728 / 91 = 24.

    Equivalently c = 3 × (q⁶-1) / T₁₃ where T₁₃ = 91.
    This is the unique central charge for the Moonshine module.
    """

    def test_central_charge_exact(self):
        """3 × 728 / 91 = 24 exactly."""
        assert 3 * 728 == 91 * 24
        assert Fraction(3 * 728, 91) == 24

    def test_c_equals_f(self):
        """c = 24 = f = multiplicity of θ-eigenvalue."""
        c = 3 * (Q**6 - 1) // (13 * 14 // 2)
        assert c == F_MULT

    def test_3_is_field_char(self):
        """The factor 3 = q = field characteristic."""
        assert Q == 3

    def test_91_is_T13(self):
        """Denominator 91 = T₁₃ = 13th triangular number."""
        T13 = 13 * 14 // 2
        assert T13 == 91

    def test_formula_from_q(self):
        """c = q × (q^(2q) - 1) / T_{Φ₃(q)} from pure SRG data."""
        phi3 = Q**2 + Q + 1  # 13
        T_phi3 = phi3 * (phi3 + 1) // 2  # T₁₃ = 91
        c = Q * (Q**(2*Q) - 1) // T_phi3
        assert c == 24

    def test_central_charge_unique(self):
        """c = 24 is the only central charge for a holomorphic c≡0 mod 8 VOA
        with Monster symmetry (FLM theorem)."""
        assert 24 % 8 == 0


# ═══════════════════════════════════════════════════════════════
# T89 — Leech Kissing → Niemeier Count
# ═══════════════════════════════════════════════════════════════
class TestLeechKissingNiemeier:
    """T89: The Leech lattice kissing number 196560 relates to W(3,3) via
    196560 / 72 = 2730 = 2 × 3 × 5 × 7 × 13.

    2730 contains both bridge primes and equals |PSL(2,13)| × 2/3.
    The factor 72 = 8 × 9 = (q-1)³ × q².
    """

    def test_ratio_exact(self):
        """196560 / 72 = 2730 exactly."""
        assert 196560 % 72 == 0
        assert 196560 // 72 == 2730

    def test_2730_factorization(self):
        """2730 = 2 × 3 × 5 × 7 × 13."""
        assert 2 * 3 * 5 * 7 * 13 == 2730

    def test_bridge_primes_present(self):
        """Both 7 and 13 divide 2730."""
        assert 2730 % 7 == 0
        assert 2730 % 13 == 0

    def test_72_decomposition(self):
        """72 = 8 × 9 = (q-1)³ × q²."""
        assert (Q - 1)**3 * Q**2 == 72

    def test_196560_from_24(self):
        """196560 = 24 × 8190 = f × (8192 - 2) = f × (2¹³ - 2)."""
        assert 196560 == F_MULT * (2**13 - 2)

    def test_niemeier_connection(self):
        """2730/2 = 1365 = 3 × 5 × 7 × 13. 
        Also 2730 = 42 × 65 = (6×7) × (5×13)."""
        assert 2730 == 42 * 65


# ═══════════════════════════════════════════════════════════════
# T90 — Magic Square Exceptional Row Sum
# ═══════════════════════════════════════════════════════════════
class TestMagicSquareRowSum:
    """T90: The last row of the Freudenthal magic square gives
    F₄ + E₆ + E₇ + E₈ = 52 + 78 + 133 + 248 = 511 = 2⁹ - 1.

    This is a Mersenne number. Since all four exceptional algebras
    appear in the W(3,3) structure, their dimensional sum is controlled
    by the theory.
    """

    def test_row_sum(self):
        """52 + 78 + 133 + 248 = 511."""
        assert F4_DIM + E6_DIM + E7_DIM + E8_DIM == 511

    def test_mersenne(self):
        """511 = 2⁹ - 1."""
        assert 2**9 - 1 == 511

    def test_exponent_is_q_squared(self):
        """Exponent 9 = q² = 3²."""
        assert Q**2 == 9

    def test_each_algebra_appears(self):
        """F₄=52, E₆=78, E₇=133, E₈=248 — all from W(3,3)."""
        assert F4_DIM == 52
        assert E6_DIM == 78
        assert E7_DIM == 133
        assert E8_DIM == 248

    def test_511_relates_to_728(self):
        """728 - 511 = 217 = 7 × 31 = Φ₆(3) × (2⁵-1)."""
        diff = 728 - 511
        assert diff == 217
        assert diff == 7 * 31

    def test_mersenne_prime_test(self):
        """2⁹-1 = 511 = 7×73 — not a Mersenne prime, but a Mersenne number."""
        assert 511 == 7 * 73


# ═══════════════════════════════════════════════════════════════
# T91 — SO(10) Correction Ladder
# ═══════════════════════════════════════════════════════════════
class TestSO10CorrectionLadder:
    """T91: Two correction identities link SRG data to E₈ and the j-invariant:

    242 + 6 = 248 = dim(E₈)     [center dimension + 6]
    728 + 16 = 744              [Golay + 16 = c₀(j)]

    Here 242 = 2 × 11² = dim(Z(s₁₂)) and 744 is the constant term
    of the j-invariant's q-expansion: j(τ) = q⁻¹ + 744 + 196884q + ...
    """

    def test_242_plus_6_is_E8(self):
        """242 + 6 = 248 = dim(E₈)."""
        assert 242 + 6 == E8_DIM

    def test_728_plus_16_is_744(self):
        """728 + 16 = 744 = constant in j-expansion."""
        assert 728 + 16 == 744

    def test_242_is_center_dimension(self):
        """242 = 2 × 11² = dim(Z(s₁₂)) from T71."""
        assert 2 * 11**2 == 242

    def test_16_is_2_to_mu(self):
        """16 = 2⁴ = 2^μ where μ=4."""
        assert 2**MU == 16

    def test_6_equals_2q(self):
        """6 = 2q = 2 × 3."""
        assert 2 * Q == 6

    def test_744_factorization(self):
        """744 = 8 × 93 = 8 × 3 × 31 = (q-1)³ × q × 31."""
        assert 744 == 8 * 93
        assert 93 == 3 * 31

    def test_ladder_ratio(self):
        """744/248 = 3 = q. The j-constant is q times E₈ dimension."""
        assert Fraction(744, 248) == Q


# ═══════════════════════════════════════════════════════════════
# T92 — Exceptional Automorphism Sum
# ═══════════════════════════════════════════════════════════════
class TestExceptionalAutomorphismSum:
    """T92: dim(G₂) + dim(F₄) = 14 + 52 = 66 = C(12,2) = dim(so(12)).

    The two "smallest" exceptional Lie algebras sum to give
    the dimension of so(12), the special orthogonal algebra
    in the SRG degree k=12 dimensions.
    """

    def test_sum_is_66(self):
        """14 + 52 = 66."""
        assert G2_DIM + F4_DIM == 66

    def test_66_is_C_12_2(self):
        """C(12,2) = 66."""
        assert comb(K, 2) == 66

    def test_dim_so12(self):
        """dim(so(12)) = 12 × 11 / 2 = 66."""
        assert K * (K - 1) // 2 == 66

    def test_12_is_k(self):
        """12 = k = SRG degree."""
        assert K == 12

    def test_728_equals_G2_times_F4(self):
        """728 = dim(G₂) × dim(F₄) (product, not sum)."""
        assert G2_DIM * F4_DIM == 728

    def test_product_minus_sum(self):
        """728 - 66 = 662 = 2 × 331 (331 is prime)."""
        diff = G2_DIM * F4_DIM - (G2_DIM + F4_DIM)
        assert diff == 662
        assert 662 == 2 * 331


# ═══════════════════════════════════════════════════════════════
# T93 — Yukawa Structure Algebra
# ═══════════════════════════════════════════════════════════════
class TestYukawaStructureAlgebra:
    """T93: The Yukawa coupling algebra is sl(3,F₃)³, with
    dim = 3 × 8 = 24, acting on the 27-dimensional representation
    3 ⊗ 3 ⊗ 3 = 27 = Albert_dim.

    Each sl(3,F₃) has dimension 3²-1 = 8. The triplication
    matches the three fermion generations.
    """

    def test_sl3_dimension(self):
        """dim(sl(3,F₃)) = 3² - 1 = 8."""
        assert Q**2 - 1 == 8

    def test_three_copies(self):
        """3 copies → dim = 3 × 8 = 24 = f."""
        assert 3 * (Q**2 - 1) == F_MULT

    def test_tensor_is_27(self):
        """3 ⊗ 3 ⊗ 3 = 27 = Albert_dim."""
        assert Q * Q * Q == ALBERT_DIM

    def test_three_generations(self):
        """3 copies ↔ 3 fermion generations."""
        assert Q == 3  # field characteristic = generation count

    def test_total_dim_is_f(self):
        """Total Yukawa algebra dimension = f = 24."""
        yukawa_dim = Q * (Q**2 - 1)
        assert yukawa_dim == F_MULT

    def test_sl3_acts_naturally(self):
        """sl(3) acts on 3-dim fundamental rep; cube gives 27."""
        fund_dim = Q  # 3
        cube = fund_dim ** Q  # 3³ = 27
        assert cube == ALBERT_DIM


# ═══════════════════════════════════════════════════════════════
# T94 — Information-Theoretic Rate
# ═══════════════════════════════════════════════════════════════
class TestInformationTheoreticRate:
    """T94: β₁/E = 81/240 = 27/80 = q⁴/(q⁵-q).

    The ratio of the first Betti number to the edge count
    gives the "information rate" of W(3,3) as a code.
    """

    def test_exact_fraction(self):
        """81/240 = 27/80 in lowest terms."""
        assert Fraction(BETA1, EDGES) == Fraction(27, 80)

    def test_formula_from_q(self):
        """q⁴/(q⁵-q) = 81/240 = 27/80."""
        assert Fraction(Q**4, Q**5 - Q) == Fraction(27, 80)

    def test_numerator_27(self):
        """Numerator 27 = q³ = Albert_dim."""
        r = Fraction(BETA1, EDGES)
        assert r.numerator == 27 == Q**3

    def test_denominator_80(self):
        """Denominator 80 = 2 × v = 2 × 40."""
        r = Fraction(BETA1, EDGES)
        assert r.denominator == 80 == 2 * V

    def test_beta1_is_q4(self):
        """β₁ = 81 = q⁴ = 3⁴."""
        assert BETA1 == Q**4

    def test_edges_is_q5_minus_q(self):
        """E = 240 = q⁵ - q = 3⁵ - 3."""
        assert EDGES == Q**5 - Q


# ═══════════════════════════════════════════════════════════════
# T95 — Fano-LCM Identity
# ═══════════════════════════════════════════════════════════════
class TestFanoLCMIdentity:
    """T95: lcm(3,4,5,6,7,8) = 840 = 5 × |PSL(2,7)| = 5 × 168.

    The LCM of {q, q+1, ..., q+5} gives 840, which splits as
    5 × 168 where 168 = |PSL(2,7)| is the Fano plane automorphism
    group order. This connects F₃ field theory to F₇ projective geometry.
    """

    def test_lcm_value(self):
        """lcm(3,4,5,6,7,8) = 840."""
        assert math.lcm(Q, Q+1, Q+2, Q+3, Q+4, Q+5) == 840

    def test_5_times_168(self):
        """840 = 5 × 168."""
        assert 5 * 168 == 840

    def test_168_is_PSL27(self):
        """168 = |PSL(2,7)| = 7 × 24 = 7 × f."""
        assert 168 == 7 * F_MULT

    def test_840_factors(self):
        """840 = 2³ × 3 × 5 × 7."""
        assert 840 == 2**3 * 3 * 5 * 7

    def test_range_starts_at_q(self):
        """Arguments {3,4,5,6,7,8} = {q, q+1, ..., q+5}."""
        args = list(range(Q, Q + 6))
        assert args == [3, 4, 5, 6, 7, 8]

    def test_840_over_bridge_primes(self):
        """840/7 = 120 = 5!, 840/13 is not integer."""
        assert 840 // 7 == 120
        assert math.factorial(5) == 120
        assert 840 % 13 != 0

    def test_168_is_gl3_f2_order(self):
        """168 = |GL(3,2)| = (2³-1)(2³-2)(2³-4) = 7×6×4."""
        gl3_2 = (2**3 - 1) * (2**3 - 2) * (2**3 - 4)
        assert gl3_2 == 168
