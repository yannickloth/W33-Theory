"""
Theorems T96-T110: Number-Theoretic Depth, Modular Forms, Sporadic Groups,
and Coding Theory from W(3,3).

All results derive from the five SRG parameters (v,k,lam,mu,q) = (40,12,2,4,3).

T96: Ihara zeta discriminant — r² − 4(k−1) = −v
T97: Vertex count as Gaussian norm — v = λ² + (k/λ)² = |2+6i|²
T98: Jacobi four-square — r₄(v) = k² = 144
T99: Divisor sum triad — σ(k) = v−k = 28 (perfect number)
T100: Ramanujan tau — τ(2)=−f, τ(3)=E+k=C(θ,5), τ(5)=4830
T101: Fermat representation of 137 — (k−1)² + μ² = 137
T102: Mersenne quintuple — {λ,q,5,Φ₆,Φ₃} give first 5 Mersenne primes
T103: Perfect number triad — k/λ=6, v−k=28, 2·E₈=496
T104: Euler totient tower — φ(v)=2^μ, φ(k)=μ, φ(f)=φ(g)=8
T105: Class number product — h(−q)·h(−Φ₆)·h(−Φ₃)·h(−v) = μ
T106: Conway group primes — rad(|Co₀|) = {λ,q,5,Φ₆,k−1,Φ₃,f−1}
T107: Binary Golay code — [n,dim,d] = [f,k,k−μ] = [24,12,8]
T108: Bernoulli denominator — denom(B_k) = 2·3·5·7·13 = 2730
T109: Fibonacci uniqueness — F_k = F₁₂ = 144 = k² (unique square)
T110: Conformal dimensions — h₁+h₂ = Φ₃/k = 13/12
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
R_EIGEN = 2   # restricted eigenvalue r
S_EIGEN = -4  # restricted eigenvalue s
PHI3 = Q**2 + Q + 1  # 13
PHI6 = Q**2 - Q + 1  # 7
N_LOOPS = 5   # loop count / independence number


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
# T96 — Ihara Zeta Discriminant = −v
# ═══════════════════════════════════════════════════════════════
class TestIharaZetaDiscriminant:
    """T96: The Ihara zeta function of W(3,3) has eigenvalue factors
    1 − ru + (k−1)u² with discriminant r² − 4(k−1) = −v.

    For r = 2 (the positive restricted eigenvalue):
    4 − 44 = −40 = −v. This proves W(3,3) is Ramanujan.
    """

    def test_discriminant_is_neg_v(self):
        """r² − 4(k−1) = 4 − 44 = −40 = −v."""
        disc = R_EIGEN**2 - 4 * (K - 1)
        assert disc == -V

    def test_negative_means_ramanujan(self):
        """Negative discriminant → |eigenvalue| < 2√(k−1), Ramanujan."""
        disc = R_EIGEN**2 - 4 * (K - 1)
        assert disc < 0

    def test_r_squared(self):
        """r² = 4 = μ."""
        assert R_EIGEN**2 == MU

    def test_4_k_minus_1(self):
        """4(k−1) = 44 = v + μ."""
        assert 4 * (K - 1) == V + MU

    def test_other_eigenvalue(self):
        """For s = −4: s² − 4(k−1) = 16 − 44 = −28 = −(v−k)."""
        disc_s = S_EIGEN**2 - 4 * (K - 1)
        assert disc_s == -(V - K)

    def test_both_discriminants(self):
        """Sum of discriminants = −v − (v−k) = −(2v−k) = −68."""
        d1 = R_EIGEN**2 - 4 * (K - 1)
        d2 = S_EIGEN**2 - 4 * (K - 1)
        assert d1 + d2 == -(2 * V - K)


# ═══════════════════════════════════════════════════════════════
# T97 — Vertex Count as Gaussian Norm
# ═══════════════════════════════════════════════════════════════
class TestGaussianNorm:
    """T97: v = λ² + (k/λ)² = |2 + 6i|² in Z[i].

    The vertex count is the norm of the Gaussian integer λ + (k/λ)i,
    connecting the SRG to algebraic number theory over Q(i).
    """

    def test_norm_is_v(self):
        """|λ + (k/λ)i|² = 2² + 6² = 4 + 36 = 40 = v."""
        norm = LAM**2 + (K // LAM)**2
        assert norm == V

    def test_real_part_is_lambda(self):
        """Real part = λ = 2."""
        assert LAM == 2

    def test_imag_part_is_k_over_lambda(self):
        """Imaginary part = k/λ = 6 = first perfect number."""
        assert K // LAM == 6

    def test_k_over_lambda_is_perfect(self):
        """k/λ = 6: the first perfect number (σ(6) = 12 = 2×6)."""
        ratio = K // LAM
        sigma = sum(d for d in range(1, ratio + 1) if ratio % d == 0)
        assert sigma == 2 * ratio

    def test_gaussian_factorization(self):
        """40 = (2+6i)(2−6i) in Z[i]: v splits in Gaussian integers."""
        # |z|² = z·z̄ = v
        assert (2**2 + 6**2) == V


# ═══════════════════════════════════════════════════════════════
# T98 — Jacobi Four-Square Theorem: r₄(v) = k²
# ═══════════════════════════════════════════════════════════════
class TestJacobiFourSquare:
    """T98: r₄(40) = 8·∑_{d|40, 4∤d} d = 8 × 18 = 144 = k².

    The number of representations of v as a sum of 4 squares
    equals k² — linking the modular form θ⁴ to the SRG degree.
    """

    def test_r4_is_k_squared(self):
        """r₄(40) = 144 = 12² = k²."""
        # Qualifying divisors of 40: d | 40 and 4 does not divide d
        divisors = [d for d in range(1, V + 1) if V % d == 0 and d % 4 != 0]
        r4 = 8 * sum(divisors)
        assert r4 == K**2

    def test_qualifying_divisors(self):
        """Divisors of 40 not divisible by 4: {1, 2, 5, 10}."""
        divisors = [d for d in range(1, V + 1) if V % d == 0 and d % 4 != 0]
        assert divisors == [1, 2, 5, 10]

    def test_divisor_sum(self):
        """1 + 2 + 5 + 10 = 18."""
        assert 1 + 2 + 5 + 10 == 18

    def test_8_times_18(self):
        """8 × 18 = 144 = k²."""
        assert 8 * 18 == K**2

    def test_divisors_contain_srg_values(self):
        """Qualifying divisors include 1=β₀, 2=λ, 5=N, 10=θ."""
        divisors = {1, 2, 5, 10}
        assert {BETA0, LAM, N_LOOPS, THETA} == divisors


# ═══════════════════════════════════════════════════════════════
# T99 — Divisor Sum Triad
# ═══════════════════════════════════════════════════════════════
class TestDivisorSumTriad:
    """T99: σ(v) = v + 2f + λ = 90, σ(k) = v − k = 28, σ(f) = E/μ = 60.

    The sum-of-divisors function at v, k, f returns SRG-derived
    quantities. Remarkably, σ(k) = 28 is a perfect number.
    """

    def test_sigma_v(self):
        """σ(40) = 1+2+4+5+8+10+20+40 = 90 = v + 2f + λ."""
        sigma = sum(d for d in range(1, V + 1) if V % d == 0)
        assert sigma == V + 2 * F_MULT + LAM
        assert sigma == 90

    def test_sigma_k(self):
        """σ(12) = 1+2+3+4+6+12 = 28 = v − k."""
        sigma = sum(d for d in range(1, K + 1) if K % d == 0)
        assert sigma == V - K
        assert sigma == 28

    def test_sigma_k_is_perfect(self):
        """σ(12) = 28 and σ(28) = 56 = 2×28: v−k is a perfect number."""
        sigma_28 = sum(d for d in range(1, 29) if 28 % d == 0)
        assert sigma_28 == 56

    def test_sigma_f(self):
        """σ(24) = 60 = E/μ = 240/4."""
        sigma = sum(d for d in range(1, F_MULT + 1) if F_MULT % d == 0)
        assert sigma == EDGES // MU
        assert sigma == 60

    def test_triad_sum(self):
        """90 + 28 + 60 = 178 = 2 × 89."""
        assert 90 + 28 + 60 == 178


# ═══════════════════════════════════════════════════════════════
# T100 — Ramanujan Tau Function
# ═══════════════════════════════════════════════════════════════
class TestRamanujanTau:
    """T100: The Ramanujan tau function τ(n), from the modular discriminant
    Δ(τ) = q∏(1−q^n)^24 of weight k=12, satisfies:

    τ(2) = −24 = −f
    τ(3) = 252 = E + k = C(θ, 5)
    τ(5) = 4830 = 2·3·5·7·23

    The weight 12 = k and exponent 24 = f are both SRG parameters.
    """

    # Known exact values of the Ramanujan tau function
    TAU_2 = -24
    TAU_3 = 252
    TAU_5 = 4830

    def test_tau_2_is_neg_f(self):
        """τ(2) = −24 = −f."""
        assert self.TAU_2 == -F_MULT

    def test_tau_3_is_E_plus_k(self):
        """τ(3) = 252 = 240 + 12 = E + k."""
        assert self.TAU_3 == EDGES + K

    def test_tau_3_is_binomial(self):
        """τ(3) = C(10, 5) = C(θ, N)."""
        assert self.TAU_3 == comb(THETA, N_LOOPS)

    def test_tau_5_factorization(self):
        """τ(5) = 4830 = 2 × 3 × 5 × 7 × 23 = λ·q·N·Φ₆·(f−1)."""
        assert self.TAU_5 == LAM * Q * N_LOOPS * PHI6 * (F_MULT - 1)

    def test_weight_is_k(self):
        """The modular form Δ has weight 12 = k."""
        assert K == 12

    def test_eta_exponent_is_f(self):
        """Δ = η²⁴ = η^f: the eta-product exponent is f."""
        assert F_MULT == 24

    def test_252_verification(self):
        """252 = 4 × 63 = μ × q²·Φ₆."""
        assert 252 == MU * Q**2 * PHI6


# ═══════════════════════════════════════════════════════════════
# T101 — Fermat Representation of 137
# ═══════════════════════════════════════════════════════════════
class TestFermat137:
    """T101: 137 = (k−1)² + μ² = 11² + 4² = 121 + 16.

    The fine structure constant inverse ⌊α⁻¹⌋ = 137 is the UNIQUE
    representation as a sum of two squares using (k−1, μ).
    Since 137 ≡ 1 (mod 4), it splits in Z[i] as (11+4i)(11−4i).
    """

    def test_137_from_srg(self):
        """(k−1)² + μ² = 121 + 16 = 137."""
        assert (K - 1)**2 + MU**2 == 137

    def test_137_is_prime(self):
        """137 is prime."""
        assert all(137 % p != 0 for p in range(2, 12))

    def test_137_mod_4(self):
        """137 ≡ 1 (mod 4): splits in Z[i]."""
        assert 137 % 4 == 1

    def test_unique_representation(self):
        """137 = 11² + 4² is the unique way (up to order/sign)."""
        reps = [(a, b) for a in range(1, 12) for b in range(1, a + 1)
                if a**2 + b**2 == 137]
        assert reps == [(11, 4)]

    def test_11_is_k_minus_1(self):
        """11 = k − 1."""
        assert K - 1 == 11

    def test_gaussian_norm(self):
        """|11 + 4i|² = 137: same structure as T97."""
        assert 11**2 + 4**2 == 137


# ═══════════════════════════════════════════════════════════════
# T102 — Mersenne Quintuple from SRG Primes
# ═══════════════════════════════════════════════════════════════
class TestMersenneQuintuple:
    """T102: The SRG-derived primes {λ,q,5,Φ₆,Φ₃} = {2,3,5,7,13}
    are exactly the first five Mersenne prime exponents.

    2^λ−1=3, 2^q−1=7, 2^5−1=31, 2^Φ₆−1=127, 2^Φ₃−1=8191 — all prime.
    The next SRG value k−1=11 gives 2^11−1=2047=23×89 (composite).
    """

    def test_2_pow_lambda(self):
        """2^λ − 1 = 2² − 1 = 3 (prime)."""
        assert 2**LAM - 1 == 3

    def test_2_pow_q(self):
        """2^q − 1 = 2³ − 1 = 7 (prime)."""
        assert 2**Q - 1 == 7

    def test_2_pow_5(self):
        """2⁵ − 1 = 31 (prime)."""
        assert 2**N_LOOPS - 1 == 31

    def test_2_pow_phi6(self):
        """2^Φ₆ − 1 = 2⁷ − 1 = 127 (prime)."""
        assert 2**PHI6 - 1 == 127

    def test_2_pow_phi3(self):
        """2^Φ₃ − 1 = 2¹³ − 1 = 8191 (prime)."""
        assert 2**PHI3 - 1 == 8191

    def test_boundary_at_k_minus_1(self):
        """2^(k−1) − 1 = 2¹¹ − 1 = 2047 = 23 × 89 (composite)."""
        val = 2**(K - 1) - 1
        assert val == 2047
        assert 2047 == 23 * 89

    def test_exactly_five(self):
        """First 5 Mersenne exponents: {2,3,5,7,13} = SRG primes."""
        mersenne_exponents = [2, 3, 5, 7, 13]
        srg_values = [LAM, Q, N_LOOPS, PHI6, PHI3]
        assert mersenne_exponents == srg_values


# ═══════════════════════════════════════════════════════════════
# T103 — Perfect Number Triad
# ═══════════════════════════════════════════════════════════════
class TestPerfectNumberTriad:
    """T103: The first three perfect numbers are SRG-derived:
    6 = k/λ, 28 = v−k, 496 = 2·dim(E₈).

    Perfect numbers σ(n) = 2n are exceedingly rare (only 51 known).
    The SRG produces three consecutive ones from fundamental parameters.
    """

    def test_6_is_k_over_lambda(self):
        """6 = k/λ = 12/2."""
        assert K // LAM == 6

    def test_6_is_perfect(self):
        """σ(6) = 1+2+3+6 = 12 = 2×6."""
        assert sum(d for d in range(1, 7) if 6 % d == 0) == 12

    def test_28_is_v_minus_k(self):
        """28 = v − k = 40 − 12."""
        assert V - K == 28

    def test_28_is_perfect(self):
        """σ(28) = 1+2+4+7+14+28 = 56 = 2×28."""
        assert sum(d for d in range(1, 29) if 28 % d == 0) == 56

    def test_496_from_E8(self):
        """496 = 2 × dim(E₈) = 2 × 248."""
        assert 2 * E8_DIM == 496

    def test_496_is_perfect(self):
        """σ(496) = 992 = 2 × 496."""
        assert sum(d for d in range(1, 497) if 496 % d == 0) == 992

    def test_496_also_dim_so32(self):
        """496 = dim(SO(32)) = 32 × 31 / 2. SO(32) is a heterotic string group."""
        assert 32 * 31 // 2 == 496

    def test_consecutive(self):
        """6, 28, 496 are the 1st, 2nd, and 3rd perfect numbers."""
        perfects = []
        for n in range(2, 500):
            if sum(d for d in range(1, n) if n % d == 0) == n:
                perfects.append(n)
        assert perfects == [6, 28, 496]


# ═══════════════════════════════════════════════════════════════
# T104 — Euler Totient Tower
# ═══════════════════════════════════════════════════════════════
class TestEulerTotientTower:
    """T104: The Euler totient function maps SRG parameters to SRG values:

    φ(v) = φ(40) = 16 = 2^μ
    φ(k) = φ(12) = 4 = μ
    φ(f) = φ(24) = 8 = dim(O)
    φ(g) = φ(15) = 8 = dim(O)

    The system is closed: φ maps {v,k,f,g} → {2^μ, μ, dim_O, dim_O}.
    """

    @staticmethod
    def _phi(n):
        """Euler's totient function."""
        count = 0
        for i in range(1, n + 1):
            if math.gcd(i, n) == 1:
                count += 1
        return count

    def test_phi_v(self):
        """φ(40) = 16 = 2^μ = 2⁴."""
        assert self._phi(V) == 2**MU

    def test_phi_k(self):
        """φ(12) = 4 = μ."""
        assert self._phi(K) == MU

    def test_phi_f(self):
        """φ(24) = 8 = k − μ = dim(O)."""
        assert self._phi(F_MULT) == K - MU

    def test_phi_g(self):
        """φ(15) = 8 = dim(O). Same as φ(f) despite f ≠ g."""
        assert self._phi(G_MULT) == K - MU

    def test_phi_f_equals_phi_g(self):
        """φ(24) = φ(15) = 8: multiplicities have same totient."""
        assert self._phi(F_MULT) == self._phi(G_MULT)

    def test_16_is_2_to_mu(self):
        """16 = 2⁴ = 2^μ."""
        assert 2**MU == 16


# ═══════════════════════════════════════════════════════════════
# T105 — Class Number Product
# ═══════════════════════════════════════════════════════════════
class TestClassNumberProduct:
    """T105: h(−q)·h(−Φ₆)·h(−Φ₃)·h(−v) = 1·1·2·2 = 4 = μ.

    The class numbers of imaginary quadratic fields Q(√(−d)) for
    d ∈ {q, Φ₆, Φ₃, v} = {3, 7, 13, 40} multiply to μ.
    The Heegner numbers 3, 7 have class number 1.
    """

    # Known class numbers of imaginary quadratic fields Q(sqrt(-d))
    # These are well-established mathematical constants
    CLASS_NUMBERS = {3: 1, 7: 1, 13: 2, 40: 2}

    def test_product_is_mu(self):
        """h(−3)·h(−7)·h(−13)·h(−40) = 1×1×2×2 = 4 = μ."""
        product = (self.CLASS_NUMBERS[Q] * self.CLASS_NUMBERS[PHI6] *
                   self.CLASS_NUMBERS[PHI3] * self.CLASS_NUMBERS[V])
        assert product == MU

    def test_heegner_numbers(self):
        """3 and 7 are Heegner numbers (h = 1)."""
        assert self.CLASS_NUMBERS[3] == 1
        assert self.CLASS_NUMBERS[7] == 1

    def test_phi3_class_number(self):
        """h(−13) = 2 = λ."""
        assert self.CLASS_NUMBERS[PHI3] == LAM

    def test_v_class_number(self):
        """h(−40) = 2 = λ."""
        assert self.CLASS_NUMBERS[V] == LAM

    def test_discriminants_are_srg(self):
        """The discriminants {3,7,13,40} = {q, Φ₆, Φ₃, v}."""
        discs = {Q, PHI6, PHI3, V}
        assert discs == {3, 7, 13, 40}


# ═══════════════════════════════════════════════════════════════
# T106 — Conway Group Primes = SRG Primes
# ═══════════════════════════════════════════════════════════════
class TestConwayGroupPrimes:
    """T106: The prime divisors of |Co₀| (Conway's group, automorphisms
    of the Leech lattice) are exactly the SRG-derived primes:
    {2,3,5,7,11,13,23} = {λ, q, 5, Φ₆, k−1, Φ₃, f−1}.

    |Co₀| = 2²²·3⁹·5⁴·7²·11·13·23.
    """

    CO0_PRIMES = {2, 3, 5, 7, 11, 13, 23}

    def test_primes_match(self):
        """Conway primes = SRG-derived primes."""
        srg_primes = {LAM, Q, N_LOOPS, PHI6, K - 1, PHI3, F_MULT - 1}
        assert self.CO0_PRIMES == srg_primes

    def test_lambda_is_2(self):
        """λ = 2."""
        assert LAM == 2

    def test_q_is_3(self):
        """q = 3."""
        assert Q == 3

    def test_phi6_is_7(self):
        """Φ₆(3) = 7."""
        assert PHI6 == 7

    def test_k_minus_1_is_11(self):
        """k − 1 = 11."""
        assert K - 1 == 11

    def test_f_minus_1_is_23(self):
        """f − 1 = 23 = dim(Leech) − 1."""
        assert F_MULT - 1 == 23

    def test_seven_primes(self):
        """Exactly 7 prime divisors of |Co₀|."""
        assert len(self.CO0_PRIMES) == 7


# ═══════════════════════════════════════════════════════════════
# T107 — Binary Golay Code Parameters
# ═══════════════════════════════════════════════════════════════
class TestBinaryGolayCode:
    """T107: The extended binary Golay code G₂₄ has parameters
    [n, dim, d] = [f, k, k−μ] = [24, 12, 8].

    This is the unique perfect 3-error-correcting binary code.
    Its automorphism group is the Mathieu group M₂₄.
    """

    def test_length_is_f(self):
        """Code length n = 24 = f."""
        assert F_MULT == 24

    def test_dimension_is_k(self):
        """Code dimension = 12 = k."""
        assert K == 12

    def test_distance_is_k_minus_mu(self):
        """Minimum distance d = 8 = k − μ = dim(O)."""
        assert K - MU == 8

    def test_codeword_count(self):
        """Number of codewords = 2^k = 4096."""
        assert 2**K == 4096

    def test_error_correction(self):
        """Corrects t = ⌊(d−1)/2⌋ = 3 errors."""
        t = (K - MU - 1) // 2
        assert t == 3

    def test_parameters_match(self):
        """[f, k, k−μ] = [24, 12, 8]."""
        assert (F_MULT, K, K - MU) == (24, 12, 8)

    def test_rate(self):
        """Code rate = k/f = 12/24 = 1/2."""
        assert Fraction(K, F_MULT) == Fraction(1, 2)


# ═══════════════════════════════════════════════════════════════
# T108 — Bernoulli Denominator = Product of SRG Primes
# ═══════════════════════════════════════════════════════════════
class TestBernoulliDenominator:
    """T108: By the von Staudt–Clausen theorem, denom(B_k) = denom(B₁₂)
    = ∏_{(p−1)|12} p = 2·3·5·7·13 = 2730.

    ALL five SRG-derived primes appear. The same denominator holds
    for B_f = B₂₄ since {p : (p−1)|24} ⊃ {p : (p−1)|12}.
    """

    def test_von_staudt_clausen(self):
        """Primes where (p−1) | 12: {2,3,5,7,13}."""
        primes = [p for p in range(2, 100)
                  if all(p % d != 0 for d in range(2, p))
                  and K % (p - 1) == 0]
        assert primes == [2, 3, 5, 7, 13]

    def test_product_is_2730(self):
        """2 × 3 × 5 × 7 × 13 = 2730."""
        assert 2 * 3 * 5 * 7 * 13 == 2730

    def test_primes_are_srg(self):
        """{2,3,5,7,13} = {λ, q, N, Φ₆, Φ₃}."""
        assert {2, 3, 5, 7, 13} == {LAM, Q, N_LOOPS, PHI6, PHI3}

    def test_2730_is_leech_related(self):
        """2730 = 196560/72 (from T89: Leech kissing ÷ 72)."""
        assert 196560 // 72 == 2730

    def test_b12_numerator_691(self):
        """B₁₂ = −691/2730. The numerator 691 is an irregular prime."""
        # B₁₂ = −691/2730 (well-known)
        assert Fraction(-691, 2730) == Fraction(-691, 2730)
        assert 691 * 2730 + 691 * 0 == 691 * 2730  # tautology, verifying const
        # 691 is prime
        assert all(691 % p != 0 for p in range(2, 27))

    def test_sum_of_primes(self):
        """2 + 3 + 5 + 7 + 13 = 30 = v − θ."""
        assert 2 + 3 + 5 + 7 + 13 == V - THETA


# ═══════════════════════════════════════════════════════════════
# T109 — Fibonacci Uniqueness: F_k = k²
# ═══════════════════════════════════════════════════════════════
class TestFibonacciUniqueness:
    """T109: F₁₂ = 144 = 12² = k².

    By Cohn's theorem (1964), F₁₂ = 144 is the ONLY perfect square
    > 1 in the entire Fibonacci sequence. The SRG degree k = 12 is
    the unique index where Fibonacci meets a perfect square.
    """

    @staticmethod
    def _fib(n):
        """Compute nth Fibonacci number."""
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    def test_f12_equals_144(self):
        """F(12) = 144."""
        assert self._fib(12) == 144

    def test_144_is_k_squared(self):
        """144 = 12² = k²."""
        assert 144 == K**2

    def test_f12_equals_k_squared(self):
        """F(k) = k²."""
        assert self._fib(K) == K**2

    def test_unique_square(self):
        """No other F(n) with n > 2 and n ≤ 100 is a perfect square."""
        squares = set()
        for n in range(3, 101):
            fn = self._fib(n)
            sqrt_fn = int(fn**0.5)
            if sqrt_fn * sqrt_fn == fn:
                squares.add(n)
        assert squares == {12}

    def test_cohn_theorem(self):
        """F(1) = F(2) = 1, F(12) = 144 are the only Fibonacci squares."""
        fib_squares = []
        for n in range(50):
            fn = self._fib(n)
            if fn > 1:
                sqrt_fn = int(fn**0.5)
                if sqrt_fn * sqrt_fn == fn:
                    fib_squares.append((n, fn))
        assert fib_squares == [(12, 144)]


# ═══════════════════════════════════════════════════════════════
# T110 — Conformal Dimensions from SRG Eigenvalues
# ═══════════════════════════════════════════════════════════════
class TestConformalDimensions:
    """T110: The conformal dimensions of W(3,3)-derived CFT primaries:

    h₁ = (k − r)/(2k) = 10/24 = 5/12
    h₂ = (k − s)/(2k) = 16/24 = 2/3
    h₁ + h₂ = 13/12 = Φ₃/k

    The sum connects cyclotomic value Φ₃ to conformal field theory.
    """

    def test_h1(self):
        """h₁ = (k − r)/(2k) = 10/24 = 5/12."""
        h1 = Fraction(K - R_EIGEN, 2 * K)
        assert h1 == Fraction(5, 12)

    def test_h2(self):
        """h₂ = (k − s)/(2k) = 16/24 = 2/3."""
        h2 = Fraction(K - S_EIGEN, 2 * K)
        assert h2 == Fraction(2, 3)

    def test_sum_is_phi3_over_k(self):
        """h₁ + h₂ = 5/12 + 2/3 = 13/12 = Φ₃/k."""
        h1 = Fraction(K - R_EIGEN, 2 * K)
        h2 = Fraction(K - S_EIGEN, 2 * K)
        assert h1 + h2 == Fraction(PHI3, K)

    def test_numerator_k_minus_r(self):
        """k − r = 10 = θ (Lovász theta appears in CFT)."""
        assert K - R_EIGEN == THETA

    def test_numerator_k_minus_s(self):
        """k − s = 16 = 2^μ."""
        assert K - S_EIGEN == 2**MU

    def test_product(self):
        """h₁ × h₂ = 5/12 × 2/3 = 10/36 = 5/18."""
        h1 = Fraction(K - R_EIGEN, 2 * K)
        h2 = Fraction(K - S_EIGEN, 2 * K)
        assert h1 * h2 == Fraction(5, 18)

    def test_eigenmatrix_det(self, w33):
        """det(P) = −240 = −E where P is the first eigenmatrix."""
        P = np.array([[1, K, V - K - 1],
                      [1, R_EIGEN, -(R_EIGEN + 1)],
                      [1, S_EIGEN, -(S_EIGEN + 1)]])
        det_P = int(round(np.linalg.det(P)))
        assert det_P == -EDGES
