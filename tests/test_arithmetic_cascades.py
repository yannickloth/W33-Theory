"""
Phase XXXI — Arithmetic Cascades & Classical Sequences (T426–T440)
═══════════════════════════════════════════════════════════════════
Cyclotomic self-reference, consecutive prime sums, Farey lengths,
base-q repunits, totient summatory, Dedekind numbers, radical function,
p-adic valuations, σ₂ chain, Stern diatomic, Delannoy/Narayana,
polygon diagonals, ballot/Catalan/Motzkin, Bernoulli/harmonic, CF period.

All from (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
from fractions import Fraction

# ── SRG(40,12,2,4) master constants ─────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2          # 240
R, S = 2, -4
F, G_MULT = 24, 15
THETA = 10
PHI3, PHI6 = 13, 7
DIM_O = 8
N = 5
ALBERT = 27
DELTA = abs(R - S)      # 6

# ── helpers ─────────────────────────────────────────────────

def _euler_phi(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def _sigma(n, k=1):
    return sum(d**k for d in range(1, n + 1) if n % d == 0)


def _radical(n):
    """Product of distinct prime factors of n."""
    rad = 1
    temp = n
    for p in range(2, temp + 1):
        if temp % p == 0:
            rad *= p
            while temp % p == 0:
                temp //= p
        if temp == 1:
            break
    return rad


def _legendre_val(n_fac, p):
    """p-adic valuation of n! via Legendre's formula."""
    val = 0
    pk = p
    while pk <= n_fac:
        val += n_fac // pk
        pk *= p
    return val


def _stern(n):
    """Stern's diatomic sequence st(n)."""
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n % 2 == 0:
        return _stern(n // 2)
    return _stern((n - 1) // 2) + _stern((n + 1) // 2)


def _delannoy(m, n):
    return sum(math.comb(m, kk) * math.comb(n, kk) * (2**kk)
               for kk in range(min(m, n) + 1))


def _narayana(n, k):
    return math.comb(n, k) * math.comb(n, k - 1) // n


def _ballot(n, k):
    """Ballot number B(n,k) = (n-k)/(n+k) * C(n+k, k)."""
    if n + k == 0:
        return 0
    return (n - k) * math.comb(n + k, k) // (n + k)


def _cf_period_len(n):
    """Length of the periodic part of continued fraction of sqrt(n)."""
    a0 = int(math.sqrt(n))
    if a0 * a0 == n:
        return 0
    period = 0
    m, d, a = 0, 1, a0
    while True:
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        period += 1
        if a == 2 * a0:
            break
    return period


def _digital_root(n, base=10):
    while n >= base:
        s = 0
        while n > 0:
            s += n % base
            n //= base
        n = s
    return n


def _motzkin(n):
    """Motzkin number M(n)."""
    M = [1, 1]
    for i in range(2, n + 1):
        M.append(((2 * i + 1) * M[-1] + 3 * (i - 1) * M[-2]) // (i + 2))
    return M[n]


def _bernoulli(n):
    """Compute Bernoulli number B_n as a Fraction."""
    B = [Fraction(0)] * (n + 1)
    B[0] = Fraction(1)
    for m in range(1, n + 1):
        B[m] = Fraction(0)
        for kk in range(m):
            B[m] -= Fraction(math.comb(m + 1, kk)) * B[kk]
        B[m] /= (m + 1)
    return B[n]


# ══════════════════════════════════════════════
# T426: Cyclotomic Self-Reference
# ══════════════════════════════════════════════
class TestCyclotomicSelfReference:
    """The naming convention becomes identity: the 3rd cyclotomic
    polynomial evaluated at q = 3 gives Φ₃ = 13, and the 6th
    cyclotomic at q gives Φ₆ = 7.  Notation mirrors mathematics.

    Φ₃(q) = q² + q + 1 = 9 + 3 + 1 = 13 = Φ₃
    Φ₆(q) = q² − q + 1 = 9 − 3 + 1 = 7  = Φ₆
    Φ₃(q) · Φ₆(q) = Φ₃ · Φ₆ = 91 = 7 × 13
    Φ₆(μ) = 13 = Φ₃  (cross-reference)
    Φ₁₂(λ) = 13 = Φ₃"""

    def test_phi3_at_q(self):
        """Φ₃(q) = q² + q + 1 = 13 = Φ₃."""
        assert Q**2 + Q + 1 == PHI3

    def test_phi6_at_q(self):
        """Φ₆(q) = q² − q + 1 = 7 = Φ₆."""
        assert Q**2 - Q + 1 == PHI6

    def test_product(self):
        """Φ₃(q)·Φ₆(q) = 13·7 = 91 = q⁴ + q² + 1."""
        assert PHI3 * PHI6 == Q**4 + Q**2 + 1

    def test_phi6_at_mu(self):
        """Φ₆(μ) = μ² − μ + 1 = 16 − 4 + 1 = 13 = Φ₃."""
        assert MU**2 - MU + 1 == PHI3

    def test_phi12_at_lam(self):
        """Φ₁₂(λ) = λ⁴ − λ² + 1 = 16 − 4 + 1 = 13 = Φ₃."""
        assert LAM**4 - LAM**2 + 1 == PHI3


# ══════════════════════════════════════════════
# T427: Consecutive Prime Sum Cascade
# ══════════════════════════════════════════════
class TestConsecutivePrimeSum:
    """Sums of consecutive primes hit SRG values at multiple windows.
    The crowning identity: 8 consecutive primes starting at 17
    sum to E = 240 = the edge count.

    2 + 3 = 5 = N
    2 + 3 + 5 = 10 = θ
    3 + 5 = 8 = dim(O)
    3 + 5 + 7 = 15 = g
    5 + 7 = 12 = k
    11 + 13 = 24 = f
    17+19+23+29+31+37+41+43 = 240 = E"""

    _primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]

    def test_first_two_primes(self):
        """2 + 3 = 5 = N."""
        assert sum(self._primes[0:2]) == N

    def test_first_three_primes(self):
        """2 + 3 + 5 = 10 = θ."""
        assert sum(self._primes[0:3]) == THETA

    def test_primes_3_5_7(self):
        """3 + 5 + 7 = 15 = g."""
        assert sum(self._primes[1:4]) == G_MULT

    def test_primes_5_7(self):
        """5 + 7 = 12 = k."""
        assert sum(self._primes[2:4]) == K

    def test_eight_primes_to_E(self):
        """17 + 19 + 23 + 29 + 31 + 37 + 41 + 43 = 240 = E."""
        assert sum(self._primes[6:14]) == E


# ══════════════════════════════════════════════
# T428: Farey Sequence Lengths
# ══════════════════════════════════════════════
class TestFareyLengths:
    """|F_n| = 1 + Σ_{k=1}^{n} φ(k) gives the length of the Farey
    sequence of order n.  Five Farey lengths land on SRG values:
    |F₁| = 2 = λ,  |F₂| = 3 = q,  |F₃| = 5 = N,
    |F₄| = 7 = Φ₆,  |F₆| = 13 = Φ₃."""

    def _farey_len(self, n):
        return 1 + sum(_euler_phi(k) for k in range(1, n + 1))

    def test_f1(self):
        """|F₁| = 2 = λ."""
        assert self._farey_len(1) == LAM

    def test_f2(self):
        """|F₂| = 3 = q."""
        assert self._farey_len(2) == Q

    def test_f3(self):
        """|F₃| = 5 = N."""
        assert self._farey_len(3) == N

    def test_f4(self):
        """|F₄| = 7 = Φ₆."""
        assert self._farey_len(4) == PHI6

    def test_f6(self):
        """|F₆| = 13 = Φ₃."""
        assert self._farey_len(6) == PHI3


# ══════════════════════════════════════════════
# T429: Base-q Repunits
# ══════════════════════════════════════════════
class TestBaseQRepunits:
    """Repunit R_n(q) = (q^n − 1)/(q − 1) in base q = 3:
    R₂(3) = 4 = μ,  R₃(3) = 13 = Φ₃,  R₄(3) = 40 = v.
    The graph order v is the 4-digit repunit in the field's base!"""

    def test_r2(self):
        """R₂(3) = (9−1)/2 = 4 = μ."""
        assert (Q**2 - 1) // (Q - 1) == MU

    def test_r3(self):
        """R₃(3) = (27−1)/2 = 13 = Φ₃."""
        assert (Q**3 - 1) // (Q - 1) == PHI3

    def test_r4(self):
        """R₄(3) = (81−1)/2 = 40 = v."""
        assert (Q**4 - 1) // (Q - 1) == V

    def test_repunit_formula(self):
        """R_n(q) = Σ q^i for i=0..n-1; check all three."""
        for n, expected in [(2, MU), (3, PHI3), (4, V)]:
            assert sum(Q**i for i in range(n)) == expected

    def test_r3_is_phi3(self):
        """R₃(q) = q² + q + 1 = Φ₃(q), linking repunits to cyclotomics."""
        assert (Q**3 - 1) // (Q - 1) == Q**2 + Q + 1 == PHI3


# ══════════════════════════════════════════════
# T430: Totient Summatory Cascade
# ══════════════════════════════════════════════
class TestTotientSummatoryCascade:
    """Φ(n) = Σ_{k=1}^{n} φ(k) maps 5 consecutive SRG parameters
    to other SRG parameters:
    Φ(λ) = λ (fixed point!), Φ(q) = μ, Φ(μ) = δ, Φ(N) = θ, Φ(δ) = k.
    The summatory totient cascades through the parameter space."""

    def _summatory_totient(self, n):
        return sum(_euler_phi(k) for k in range(1, n + 1))

    def test_phi_at_lam_fixed(self):
        """Φ(2) = φ(1) + φ(2) = 1 + 1 = 2 = λ — a fixed point!"""
        assert self._summatory_totient(LAM) == LAM

    def test_phi_at_q(self):
        """Φ(3) = 1 + 1 + 2 = 4 = μ."""
        assert self._summatory_totient(Q) == MU

    def test_phi_at_mu(self):
        """Φ(4) = 1 + 1 + 2 + 2 = 6 = δ."""
        assert self._summatory_totient(MU) == DELTA

    def test_phi_at_N(self):
        """Φ(5) = 1 + 1 + 2 + 2 + 4 = 10 = θ."""
        assert self._summatory_totient(N) == THETA

    def test_phi_at_delta(self):
        """Φ(6) = 1 + 1 + 2 + 2 + 4 + 2 = 12 = k."""
        assert self._summatory_totient(DELTA) == K


# ══════════════════════════════════════════════
# T431: Dedekind Number Triad
# ══════════════════════════════════════════════
class TestDedekindNumbers:
    """Dedekind numbers D(n) count antichains in the power set of [n].
    D(0) = 2 = λ,  D(1) = 3 = q,  D(2) = 6 = δ.
    Three consecutive Dedekind numbers are SRG values!
    Also D(3)/D(0) = 20/2 = 10 = θ."""

    _D = [2, 3, 6, 20, 168]  # D(0) through D(4)

    def test_d0(self):
        """D(0) = 2 = λ."""
        assert self._D[0] == LAM

    def test_d1(self):
        """D(1) = 3 = q."""
        assert self._D[1] == Q

    def test_d2(self):
        """D(2) = 6 = δ."""
        assert self._D[2] == DELTA

    def test_d3_over_d0(self):
        """D(3)/D(0) = 20/2 = 10 = θ."""
        assert self._D[3] // self._D[0] == THETA

    def test_three_consecutive(self):
        """First three Dedekind numbers all in the SRG parameter set."""
        srg = {V, K, LAM, MU, Q, E, R, S, F, G_MULT, THETA,
               PHI3, PHI6, DIM_O, N, ALBERT, DELTA}
        assert all(self._D[i] in srg for i in range(3))


# ══════════════════════════════════════════════
# T432: Radical Function Cascade
# ══════════════════════════════════════════════
class TestRadicalFunction:
    """rad(n) = product of distinct prime factors of n.
    rad(k) = rad(12) = 6 = δ,  rad(f) = rad(24) = 6 = δ,
    rad(v) = rad(40) = 10 = θ, rad(albert) = rad(27) = 3 = q.
    The radical strips SRG composites down to SRG primes/products."""

    def test_rad_k(self):
        """rad(12) = 2·3 = 6 = δ."""
        assert _radical(K) == DELTA

    def test_rad_f(self):
        """rad(24) = 2·3 = 6 = δ."""
        assert _radical(F) == DELTA

    def test_rad_v(self):
        """rad(40) = 2·5 = 10 = θ."""
        assert _radical(V) == THETA

    def test_rad_albert(self):
        """rad(27) = 3 = q."""
        assert _radical(ALBERT) == Q

    def test_rad_mu(self):
        """rad(4) = 2 = λ."""
        assert _radical(MU) == LAM


# ══════════════════════════════════════════════
# T433: p-adic Valuation of Factorials
# ══════════════════════════════════════════════
class TestPadicValuationFactorial:
    """Legendre's formula v_p(n!) = Σ ⌊n/p^k⌋ maps SRG factorials
    to other SRG values:
    v₃(albert!) = v₃(27!) = 13 = Φ₃      (exponent of 3 in 27!)
    v₂(k!) = v₂(12!) = 10 = θ
    v₂(θ!) = v₂(10!) = 8 = dim(O)
    v₃(k!) = v₃(12!) = 5 = N
    v₂(dimO!) = v₂(8!) = 7 = Φ₆"""

    def test_v3_albert_factorial(self):
        """v₃(27!) = 13 = Φ₃."""
        assert _legendre_val(ALBERT, 3) == PHI3

    def test_v2_k_factorial(self):
        """v₂(12!) = 10 = θ."""
        assert _legendre_val(K, 2) == THETA

    def test_v2_theta_factorial(self):
        """v₂(10!) = 8 = dim(O)."""
        assert _legendre_val(THETA, 2) == DIM_O

    def test_v3_k_factorial(self):
        """v₃(12!) = 5 = N."""
        assert _legendre_val(K, 3) == N

    def test_v2_dimO_factorial(self):
        """v₂(8!) = 7 = Φ₆."""
        assert _legendre_val(DIM_O, 2) == PHI6


# ══════════════════════════════════════════════
# T434: σ₂ Chain (Sum of Squares of Divisors)
# ══════════════════════════════════════════════
class TestSigma2Chain:
    """σ₂(n) = Σ d² for d|n: the sum of SQUARES of divisors.
    σ₂(λ) = 1+4 = 5 = N,  σ₂(q) = 1+9 = 10 = θ.
    Meanwhile σ(σ(n)) extends the known σ₁ chain:
    σ(σ(μ)) = σ(7) = 8 = dim(O),  σ(σ(dimO)) = σ(15) = 24 = f."""

    def test_sigma2_lam(self):
        """σ₂(2) = 1² + 2² = 5 = N."""
        assert _sigma(LAM, 2) == N

    def test_sigma2_q(self):
        """σ₂(3) = 1² + 3² = 10 = θ."""
        assert _sigma(Q, 2) == THETA

    def test_sigma_sigma_mu(self):
        """σ(σ(4)) = σ(7) = 8 = dim(O)."""
        assert _sigma(_sigma(MU)) == DIM_O

    def test_sigma_sigma_dimO(self):
        """σ(σ(8)) = σ(15) = 24 = f."""
        assert _sigma(_sigma(DIM_O)) == F

    def test_sigma_sigma_phi6(self):
        """σ(σ(7)) = σ(8) = 15 = g."""
        assert _sigma(_sigma(PHI6)) == G_MULT


# ══════════════════════════════════════════════
# T435: Stern's Diatomic Sequence
# ══════════════════════════════════════════════
class TestSternDiatomic:
    """Stern's diatomic st(n): st(2n)=st(n), st(2n+1)=st(n)+st(n+1).
    Maps SRG values to SRG values:
    st(Φ₃) = st(13) = 5 = N,  st(albert) = st(27) = 8 = dim(O),
    st(g) = st(15) = 4 = μ,   st(N) = st(5) = 3 = q."""

    def test_st_phi3(self):
        """st(13) = 5 = N."""
        assert _stern(PHI3) == N

    def test_st_albert(self):
        """st(27) = 8 = dim(O)."""
        assert _stern(ALBERT) == DIM_O

    def test_st_g(self):
        """st(15) = 4 = μ."""
        assert _stern(G_MULT) == MU

    def test_st_N(self):
        """st(5) = 3 = q."""
        assert _stern(N) == Q

    def test_st_theta(self):
        """st(10) = 3 = q."""
        assert _stern(THETA) == Q


# ══════════════════════════════════════════════
# T436: Delannoy & Narayana Numbers
# ══════════════════════════════════════════════
class TestDelannoyNarayana:
    """Delannoy numbers D(m,n) count lattice paths with steps
    (1,0), (0,1), (1,1).  Narayana numbers N(n,k) refine Catalan.
    D(2,2) = 13 = Φ₃,  D(1,2) = 5 = N,  D(1,3) = 7 = Φ₆.
    Narayana(6,2) = 15 = g,  Narayana(5,2) = 10 = θ."""

    def test_delannoy_2_2(self):
        """D(2,2) = 13 = Φ₃."""
        assert _delannoy(2, 2) == PHI3

    def test_delannoy_1_2(self):
        """D(1,2) = 5 = N."""
        assert _delannoy(1, 2) == N

    def test_delannoy_1_3(self):
        """D(1,3) = 7 = Φ₆."""
        assert _delannoy(1, 3) == PHI6

    def test_narayana_6_2(self):
        """N(6,2) = 15 = g."""
        assert _narayana(6, 2) == G_MULT

    def test_narayana_5_2(self):
        """N(5,2) = 10 = θ."""
        assert _narayana(5, 2) == THETA


# ══════════════════════════════════════════════
# T437: Polygon Diagonals & Polytopes
# ══════════════════════════════════════════════
class TestPolygonDiagonals:
    """The number of diagonals of an n-gon = n(n−3)/2.
    diag(5) = 5 = N (pentagon's diagonals = N!),
    diag(9) = 27 = albert (nonagon has Albert-many diagonals!).
    The 5-cell has V = N = 5 vertices, E = θ = 10 edges."""

    def test_pentagon_diag(self):
        """diag(5-gon) = 5(5−3)/2 = 5 = N."""
        assert N * (N - 3) // 2 == N

    def test_nonagon_diag(self):
        """diag(9-gon) = 9·6/2 = 27 = albert."""
        assert 9 * 6 // 2 == ALBERT

    def test_5cell_vertices(self):
        """5-cell (4D simplex) has 5 = N vertices."""
        assert math.comb(N, 1) == N

    def test_5cell_edges(self):
        """5-cell has C(5,2) = 10 = θ edges."""
        assert math.comb(N, 2) == THETA

    def test_tesseract_faces(self):
        """The tesseract (4D cube) has 24 = f square faces."""
        tesseract_faces = 24
        assert tesseract_faces == F


# ══════════════════════════════════════════════
# T438: Ballot–Catalan–Motzkin Triangle
# ══════════════════════════════════════════════
class TestBallotCatalanMotzkin:
    """Three classical counting sequences hit SRG values:
    Ballot(8,2) = 27 = albert, Catalan(3) = 5 = N,
    Motzkin(3) = 4 = μ, Motzkin(2) = 2 = λ.
    Ballot(4,2) = 5 = N."""

    def test_ballot_8_2(self):
        """Ballot(8,2) = (8−2)/(8+2) · C(10,2) = 6/10 · 45 = 27 = albert."""
        assert _ballot(8, 2) == ALBERT

    def test_catalan_3(self):
        """C₃ = C(6,3)/4 = 5 = N."""
        assert math.comb(6, 3) // 4 == N

    def test_motzkin_3(self):
        """Motz(3) = 4 = μ."""
        assert _motzkin(3) == MU

    def test_motzkin_2(self):
        """Motz(2) = 2 = λ."""
        assert _motzkin(2) == LAM

    def test_ballot_4_2(self):
        """Ballot(4,2) = (4−2)/(4+2) · C(6,2) = 2/6 · 15 = 5 = N."""
        assert _ballot(4, 2) == N


# ══════════════════════════════════════════════
# T439: Bernoulli Numerators & Harmonic Denominators
# ══════════════════════════════════════════════
class TestBernoulliHarmonic:
    """|B₁₀ numerator| = 5 = N,  |B₁₄ numerator| = 7 = Φ₆.
    Harmonic number H(q) has denominator 6 = δ,
    H(μ) has denominator 12 = k."""

    def test_b10_numerator(self):
        """|num(B₁₀)| = 5 = N.  (B₁₀ = 5/66)"""
        b10 = _bernoulli(10)
        assert abs(b10.numerator) == N

    def test_b14_numerator(self):
        """|num(B₁₄)| = 7 = Φ₆.  (B₁₄ = 7/6)"""
        b14 = _bernoulli(14)
        assert abs(b14.numerator) == PHI6

    def test_b14_denominator(self):
        """den(B₁₄) = 6 = δ."""
        b14 = _bernoulli(14)
        assert b14.denominator == DELTA

    def test_harmonic_q_den(self):
        """H(3) = 1 + 1/2 + 1/3 = 11/6; denominator = 6 = δ."""
        h = sum(Fraction(1, i) for i in range(1, Q + 1))
        assert h.denominator == DELTA

    def test_harmonic_mu_den(self):
        """H(4) = 25/12; denominator = 12 = k."""
        h = sum(Fraction(1, i) for i in range(1, MU + 1))
        assert h.denominator == K


# ══════════════════════════════════════════════
# T440: CF Period Length & Digital Root
# ══════════════════════════════════════════════
class TestCFPeriodDigitalRoot:
    """CF period of √Φ₃ = √13 has length 5 = N.
    CF period of √Φ₆ = √7 has length 4 = μ.
    Digital root DR₁₀(Φ₃) = 4 = μ, DR₁₀(g) = 6 = δ."""

    def test_cf_sqrt_phi3(self):
        """CF period of √13 has length 5 = N."""
        assert _cf_period_len(PHI3) == N

    def test_cf_sqrt_phi6(self):
        """CF period of √7 has length 4 = μ."""
        assert _cf_period_len(PHI6) == MU

    def test_dr_phi3(self):
        """DR₁₀(13) = 1+3 = 4 = μ."""
        assert _digital_root(PHI3) == MU

    def test_dr_g(self):
        """DR₁₀(15) = 1+5 = 6 = δ."""
        assert _digital_root(G_MULT) == DELTA

    def test_dr_E(self):
        """DR₁₀(240) = 2+4+0 = 6 = δ."""
        assert _digital_root(E) == DELTA
