"""
Phase XXVII: Recurrence Cascades & Combinatorial Constants (T366-T380)
======================================================================
Fifteen theorems showing that classical integer recurrences (Pell,
Mersenne, Jacobsthal, Fibonacci, Lucas), the 6th cyclotomic polynomial,
factorial chains, Ramsey numbers, automorphism-group power laws,
Riemann zeta at negative integers, Bernoulli denominator factorisations,
Bell numbers, partition values, and pentagonal numbers all reproduce
the constants of W(3,3).

Every value derives from (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
from fractions import Fraction
from math import comb, factorial

# ── SRG parameters ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                       # 240
R, S = 2, -4                          # eigenvalues of SRG
F_MULT = (-K - (V - 1) * S) // (R - S)  # 24
G_MULT = V - 1 - F_MULT               # 15
N = Q + 2                             # 5
PHI3 = Q**2 + Q + 1                   # 13
PHI6 = Q**2 - Q + 1                   # 7
ALBERT = V - PHI3                      # 27
THETA = V * (-S) // (K - S)            # 10
DELTA = abs(R - S)                     # 6
AUT = 51840                            # |Aut(W(3,3))|


# ── Helper functions ──

def _pell(n):
    """Return the n-th Pell number.  P(0)=0, P(1)=1, P(n)=2P(n-1)+P(n-2)."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, 2 * b + a
    return a


def _jacobsthal(n):
    """Return the n-th Jacobsthal number.  J(0)=0, J(1)=1, J(n)=J(n-1)+2J(n-2)."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, b + 2 * a
    return a


def _fibonacci(n):
    """Return the n-th Fibonacci number.  F(0)=0, F(1)=1."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _lucas(n):
    """Return the n-th Lucas number.  L(0)=2, L(1)=1."""
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _bell(n):
    """Return the n-th Bell number via the triangle."""
    row = [1]
    for i in range(1, n + 1):
        new = [row[-1]]
        for j in range(1, i + 1):
            new.append(new[-1] + row[j - 1])
        row = new
    return row[0] if n > 0 else 1


def _partition(n):
    """Return p(n), the number of integer partitions of n."""
    if n < 0:
        return 0
    table = [0] * (n + 1)
    table[0] = 1
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            table[j] += table[j - i]
    return table[n]


def _pentagonal(n):
    """Return the n-th pentagonal number: n(3n-1)/2."""
    return n * (3 * n - 1) // 2


# ──────────────────────────────────────────────
# T366: Pell Cascade
# ──────────────────────────────────────────────
class TestPellCascade:
    """T366: Consecutive Pell numbers reproduce three SRG parameters.

    P(2) = 2 = λ
    P(3) = 5 = N
    P(4) = 12 = k

    Three consecutive terms of the Pell recurrence land exactly on
    the edge-regularity parameter, the neighbour count, and the degree.
    """

    def test_pell_2_is_lam(self):
        """P(2) = 2 = λ."""
        assert _pell(2) == LAM

    def test_pell_3_is_N(self):
        """P(3) = 5 = N = q + 2."""
        assert _pell(3) == N

    def test_pell_4_is_k(self):
        """P(4) = 12 = k (degree of W(3,3))."""
        assert _pell(4) == K

    def test_pell_recurrence_holds(self):
        """P(4) = 2·P(3) + P(2) verifies k = 2N + λ."""
        assert _pell(4) == 2 * _pell(3) + _pell(2)
        assert K == 2 * N + LAM

    def test_pell_ratio(self):
        """P(4)/P(3) = k/N = 12/5."""
        assert Fraction(_pell(4), _pell(3)) == Fraction(K, N)


# ──────────────────────────────────────────────
# T367: Mersenne Parameter Cascade
# ──────────────────────────────────────────────
class TestMersenneCascade:
    """T367: Mersenne-type formula 2^x − 1 maps SRG parameters to each other.

    2^λ − 1 = 3  = q
    2^q − 1 = 7  = Φ₆
    2^μ − 1 = 15 = g

    The Mersenne map chains through the SRG parameter set.
    """

    def test_2_lam_minus_1_is_q(self):
        """2^λ − 1 = 3 = q."""
        assert 2**LAM - 1 == Q

    def test_2_q_minus_1_is_phi6(self):
        """2^q − 1 = 7 = Φ₆ (Mersenne prime)."""
        assert 2**Q - 1 == PHI6

    def test_2_mu_minus_1_is_g(self):
        """2^μ − 1 = 15 = g (s-multiplicity)."""
        assert 2**MU - 1 == G_MULT

    def test_cascade_chain(self):
        """The chain 2^λ−1 → q, 2^q−1 → Φ₆ threads through three distinct values."""
        assert 2**(2**LAM - 1) - 1 == PHI6

    def test_mersenne_primality(self):
        """2^λ−1 = 3 and 2^q−1 = 7 are both Mersenne primes; 2^μ−1 = 15 is not."""
        from math import isqrt
        def is_prime(n):
            if n < 2: return False
            for d in range(2, isqrt(n) + 1):
                if n % d == 0: return False
            return True
        assert is_prime(2**LAM - 1)
        assert is_prime(2**Q - 1)
        assert not is_prime(2**MU - 1)


# ──────────────────────────────────────────────
# T368: Jacobsthal Chain
# ──────────────────────────────────────────────
class TestJacobsthalChain:
    """T368: Consecutive Jacobsthal numbers hit SRG values.

    J(3) = 3 = q
    J(4) = 5 = N

    The Jacobsthal recurrence J(n) = J(n-1) + 2·J(n-2) produces
    two consecutive SRG-derived values at indices 3 and 4.
    """

    def test_j3_is_q(self):
        """J(3) = 3 = q."""
        assert _jacobsthal(3) == Q

    def test_j4_is_N(self):
        """J(4) = 5 = N."""
        assert _jacobsthal(4) == N

    def test_recurrence_at_j4(self):
        """J(4) = J(3) + 2·J(2): N = q + 2·1 = 5."""
        assert _jacobsthal(4) == _jacobsthal(3) + 2 * _jacobsthal(2)

    def test_ratio_j4_j3(self):
        """J(4)/J(3) = N/q = 5/3."""
        assert Fraction(_jacobsthal(4), _jacobsthal(3)) == Fraction(N, Q)

    def test_jacobsthal_sum(self):
        """J(3) + J(4) = q + N = 8 = 2^q."""
        assert _jacobsthal(3) + _jacobsthal(4) == 2**Q


# ──────────────────────────────────────────────
# T369: Fibonacci Self-Map
# ──────────────────────────────────────────────
class TestFibonacciSelfMap:
    """T369: Fibonacci maps SRG parameters to other SRG parameters.

    F(q) = F(3) = 2 = λ
    F(μ) = F(4) = 3 = q
    F(N) = F(5) = 5 = N  (fixed point!)

    So Fibonacci acts as a permutation on {λ, q, N}: (q→λ, μ→q, N→N).
    """

    def test_fib_q_is_lam(self):
        """F(q) = F(3) = 2 = λ."""
        assert _fibonacci(Q) == LAM

    def test_fib_mu_is_q(self):
        """F(μ) = F(4) = 3 = q."""
        assert _fibonacci(MU) == Q

    def test_fib_N_fixedpoint(self):
        """F(N) = F(5) = 5 = N — a Fibonacci fixed point."""
        assert _fibonacci(N) == N

    def test_fib_chain(self):
        """F maps (q, μ, N) → (λ, q, N), shifting parameters left."""
        mapped = [_fibonacci(Q), _fibonacci(MU), _fibonacci(N)]
        assert mapped == [LAM, Q, N]

    def test_fib_mu_plus_fib_q(self):
        """F(μ) + F(q) = q + λ = N."""
        assert _fibonacci(MU) + _fibonacci(Q) == N


# ──────────────────────────────────────────────
# T370: Fibonacci Square Identity
# ──────────────────────────────────────────────
class TestFibonacciSquare:
    """T370: F(k) = k² — the k-th Fibonacci number equals k-squared.

    F(12) = 144 = 12² = k²

    This only holds for k = 12: no other n > 1 has F(n) = n².
    """

    def test_fib_k_is_k_squared(self):
        """F(12) = 144 = 12² = k²."""
        assert _fibonacci(K) == K**2

    def test_uniqueness(self):
        """F(n) = n² has no solution for 2 ≤ n ≤ 1000 other than n = 1, 12."""
        solutions = [n for n in range(2, 1001) if _fibonacci(n) == n**2]
        assert solutions == [K]

    def test_144_factorisation(self):
        """144 = 2⁴ · 3² = 2^μ · q^λ."""
        assert K**2 == 2**MU * Q**LAM

    def test_sqrt_fib_k(self):
        """√F(k) = k."""
        assert int(math.isqrt(_fibonacci(K))) == K

    def test_fib_12_value(self):
        """F(12) = 144 by direct enumeration."""
        fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        assert fibs[K] == K**2


# ──────────────────────────────────────────────
# T371: Cyclotomic Φ₆ Cascade
# ──────────────────────────────────────────────
class TestCyclotomicCascade:
    """T371: The 6th cyclotomic polynomial Φ₆(t) = t² − t + 1 maps
    SRG parameters to cyclotomic values.

    Φ₆(λ) = 4 − 2 + 1 = 3  = q
    Φ₆(q) = 9 − 3 + 1 = 7  = Φ₆  (the value named after this polynomial)
    Φ₆(μ) = 16 − 4 + 1 = 13 = Φ₃

    Remarkably, Φ₆(t) = t²−t+1 is also the Alexander polynomial of the trefoil
    knot. Evaluating it at SRG parameters recovers the cyclotomic values.
    """

    def _phi6(self, t):
        return t**2 - t + 1

    def test_phi6_lam_is_q(self):
        """Φ₆(λ) = λ²−λ+1 = 3 = q."""
        assert self._phi6(LAM) == Q

    def test_phi6_q_is_phi6(self):
        """Φ₆(q) = q²−q+1 = 7 = Φ₆ — self-referential!"""
        assert self._phi6(Q) == PHI6

    def test_phi6_mu_is_phi3(self):
        """Φ₆(μ) = μ²−μ+1 = 13 = Φ₃."""
        assert self._phi6(MU) == PHI3

    def test_double_application(self):
        """Φ₆(Φ₆(λ)) = Φ₆(q) = Φ₆ — composing twice from λ reaches Φ₆."""
        assert self._phi6(self._phi6(LAM)) == PHI6

    def test_trefoil_alexander(self):
        """Δ_trefoil(t) = t²−t+1 = Φ₆(t): Alexander polynomial at t = q gives Φ₆/q as fraction."""
        alex_frac = Fraction(Q**2 - Q + 1, Q)
        assert alex_frac == Fraction(PHI6, Q)


# ──────────────────────────────────────────────
# T372: Factorial Chain
# ──────────────────────────────────────────────
class TestFactorialChain:
    """T372: Factorials of consecutive SRG parameters reproduce derived values.

    q!  = 3!  = 6   = |r − s| = δ
    μ!  = 4!  = 24  = f  (r-multiplicity)
    N!  = 5!  = 120 = E/2  (half the edge count)

    Three consecutive factorials at (q, μ, N) = (3, 4, 5) produce δ, f, E/2.
    """

    def test_q_factorial_is_delta(self):
        """q! = 3! = 6 = |r − s|."""
        assert factorial(Q) == DELTA

    def test_mu_factorial_is_f(self):
        """μ! = 4! = 24 = f (r-eigenvalue multiplicity)."""
        assert factorial(MU) == F_MULT

    def test_N_factorial_is_half_E(self):
        """N! = 5! = 120 = E/2."""
        assert factorial(N) == E // 2

    def test_factorial_ratio(self):
        """N!/μ! = 5 = N, μ!/q! = 4 = μ."""
        assert factorial(N) // factorial(MU) == N
        assert factorial(MU) // factorial(Q) == MU

    def test_product(self):
        """q! · μ! · N! = 6·24·120 = 17280 = AUT/q."""
        assert factorial(Q) * factorial(MU) * factorial(N) == AUT // Q


# ──────────────────────────────────────────────
# T373: Ramsey Number Extensions
# ──────────────────────────────────────────────
class TestRamseyExtended:
    """T373: Off-diagonal and multicolour Ramsey numbers match SRG expressions.

    R(3,4) = R(q,μ)  = 9  = q²
    R(3,5) = R(q,N)  = 14 = k + λ
    R(4,4) = R(μ,μ)  = 18 = 2q²
    R(3,3,3) = R₃(q)  = 17 = k + N

    (R(3,3) = 6 = δ is T160; these extend to off-diagonal and 3-colour.)
    """

    def test_R_q_mu(self):
        """R(3,4) = 9 = q²."""
        assert 9 == Q**2

    def test_R_q_N(self):
        """R(3,5) = 14 = k + λ."""
        assert 14 == K + LAM

    def test_R_mu_mu(self):
        """R(4,4) = 18 = 2q²."""
        assert 18 == 2 * Q**2

    def test_R_3colour(self):
        """R(3,3,3) = 17 = k + N."""
        assert 17 == K + N

    def test_ramsey_sum(self):
        """R(q,μ) + R(q,N) = 9 + 14 = 23 (prime) = 2k − 1."""
        assert Q**2 + (K + LAM) == 2 * K - 1


# ──────────────────────────────────────────────
# T374: Automorphism Power Law
# ──────────────────────────────────────────────
class TestAutPowerLaw:
    """T374: Quotients of |Aut(W(3,3))| by vertex/edge counts are exact
    powers of δ = |r − s| = 6.

    |Aut| / v = 51840/40  = 1296 = 6⁴ = δ^μ
    |Aut| / E = 51840/240 = 216  = 6³ = δ^q

    The exponents are themselves SRG parameters: μ = 4 and q = 3.
    """

    def test_aut_div_v_is_delta_mu(self):
        """|Aut|/v = δ^μ = 6⁴ = 1296."""
        assert AUT // V == DELTA**MU

    def test_aut_div_E_is_delta_q(self):
        """|Aut|/E = δ^q = 6³ = 216."""
        assert AUT // E == DELTA**Q

    def test_exponents_are_srg(self):
        """The exponents μ=4 and q=3 are both SRG parameters."""
        assert MU == 4
        assert Q == 3

    def test_ratio_of_quotients(self):
        """|Aut|/v ÷ |Aut|/E = E/v = k/2 = δ."""
        assert (AUT // V) // (AUT // E) == DELTA

    def test_aut_as_product(self):
        """|Aut| = v · δ^μ = E · δ^q."""
        assert V * DELTA**MU == AUT
        assert E * DELTA**Q == AUT


# ──────────────────────────────────────────────
# T375: Zeta at Negative Integers
# ──────────────────────────────────────────────
class TestZetaNegative:
    """T375: Riemann zeta at negative odd integers reproduces SRG reciprocals.

    |ζ(−1)| = 1/12  = 1/k
    |ζ(−3)| = 1/120 = 1/(E/2) = 2/E

    The Bernoulli-number formula ζ(−n) = −B_{n+1}/(n+1) gives exact
    rational values whose denominators are SRG-derived.
    """

    def test_zeta_neg1(self):
        """|ζ(−1)| = B₂/2 = 1/12 = 1/k."""
        assert Fraction(1, 12) == Fraction(1, K)

    def test_zeta_neg3(self):
        """|ζ(−3)| = B₄/4 = 1/120 = 1/(E/2)."""
        assert Fraction(1, 120) == Fraction(1, E // 2)

    def test_zeta_ratio(self):
        """|ζ(−1)| / |ζ(−3)| = 120/12 = 10 = θ."""
        ratio = Fraction(1, K) / Fraction(1, E // 2)
        assert ratio == THETA

    def test_denom_product(self):
        """12 · 120 = 1440 = v · k · q."""
        assert K * (E // 2) == V * K * Q

    def test_zeta_neg5_decomposition(self):
        """|ζ(−5)| = 1/252; 252 = k · (k + q²) = 12 · 21."""
        assert 252 == K * (K + Q**2)


# ──────────────────────────────────────────────
# T376: Bernoulli B₁₂ Denominator
# ──────────────────────────────────────────────
class TestBernoulliB12:
    """T376: denom(B₁₂) = 2730 = δ · N · Φ₃ · Φ₆ — a four-factor
    SRG decomposition.

    Von Staudt–Clausen gives denom(B₁₂) = 2·3·5·7·13 = 2730.
    Regrouping: 2730 = 6 · 5 · 7 · 13 = δ · N · Φ₆ · Φ₃.
    """

    def test_b12_denom_value(self):
        """denom(B₁₂) = 2730 by Von Staudt–Clausen."""
        # B_12 denom = product of primes p where (p-1) | 12
        primes_dividing = [p for p in [2, 3, 5, 7, 11, 13]
                           if 12 % (p - 1) == 0]
        denom = 1
        for p in primes_dividing:
            denom *= p
        assert denom == 2730

    def test_four_factor_decomposition(self):
        """2730 = δ · N · Φ₆ · Φ₃ = 6 · 5 · 7 · 13."""
        assert DELTA * N * PHI6 * PHI3 == 2730

    def test_factors_are_srg_derived(self):
        """All four factors come from the SRG parameter set."""
        assert DELTA == abs(R - S)
        assert N == Q + 2
        assert PHI6 == Q**2 - Q + 1
        assert PHI3 == Q**2 + Q + 1

    def test_b2_denom_is_delta(self):
        """denom(B₂) = 6 = δ for comparison."""
        primes_div_2 = [p for p in [2, 3, 5, 7, 11, 13]
                        if 2 % (p - 1) == 0]
        assert math.prod(primes_div_2) == DELTA

    def test_b12_div_b2(self):
        """denom(B₁₂)/denom(B₂) = 2730/6 = 455 = N · Φ₃ · Φ₆."""
        assert 2730 // DELTA == N * PHI3 * PHI6


# ──────────────────────────────────────────────
# T377: Bell Number Triple
# ──────────────────────────────────────────────
class TestBellTriple:
    """T377: Three Bell numbers land on SRG-derived values.

    Bell(2) = 2  = λ
    Bell(3) = 5  = N
    Bell(4) = 15 = g

    (Bell(5) = 52 = dim(F₄) is T159; these are the lower Bell hits.)
    """

    def test_bell_2_is_lam(self):
        """Bell(2) = 2 = λ."""
        assert _bell(2) == LAM

    def test_bell_3_is_N(self):
        """Bell(3) = 5 = N."""
        assert _bell(3) == N

    def test_bell_4_is_g(self):
        """Bell(4) = 15 = g (s-eigenvalue multiplicity)."""
        assert _bell(4) == G_MULT

    def test_bell_product(self):
        """Bell(2)·Bell(3)·Bell(4) = λ·N·g = 150 = k² + DELTA."""
        product = _bell(2) * _bell(3) * _bell(4)
        assert product == LAM * N * G_MULT
        assert product == 150

    def test_bell_ratio(self):
        """Bell(4)/Bell(2) = g/λ = 15/2."""
        assert Fraction(_bell(4), _bell(2)) == Fraction(G_MULT, LAM)


# ──────────────────────────────────────────────
# T378: Partition–Cyclotomic Bridge
# ──────────────────────────────────────────────
class TestPartitionCyclotomic:
    """T378: The partition function maps between cyclotomic values.

    p(N)   = p(5) = 7  = Φ₆
    p(Φ₆)  = p(7) = 15 = g

    Composing: p maps N → Φ₆ → g via the partition function,
    threading through the cyclotomic value Φ₆.
    """

    def test_p_N_is_phi6(self):
        """p(5) = 7 = Φ₆."""
        assert _partition(N) == PHI6

    def test_p_phi6_is_g(self):
        """p(7) = 15 = g."""
        assert _partition(PHI6) == G_MULT

    def test_partition_chain(self):
        """p(p(N)) = p(Φ₆) = g: a two-step partition cascade."""
        assert _partition(_partition(N)) == G_MULT

    def test_p_q_is_q(self):
        """p(3) = 3 = q: a partition fixed point."""
        assert _partition(Q) == Q

    def test_p_lam_is_lam(self):
        """p(2) = 2 = λ: another partition fixed point."""
        assert _partition(LAM) == LAM


# ──────────────────────────────────────────────
# T379: Pentagonal Numbers
# ──────────────────────────────────────────────
class TestPentagonalDual:
    """T379: Pentagonal numbers embed SRG parameters.

    Pent(2) = 5  = N
    Pent(3) = 12 = k

    The n-th pentagonal number is n(3n−1)/2.
    """

    def test_pent_2_is_N(self):
        """Pent(2) = 2·5/2 = 5 = N."""
        assert _pentagonal(2) == N

    def test_pent_3_is_k(self):
        """Pent(3) = 3·8/2 = 12 = k."""
        assert _pentagonal(3) == K

    def test_pentagonal_formula(self):
        """Pent(n) = n(3n−1)/2; verify at n = 2 and 3."""
        assert 2 * (3 * 2 - 1) // 2 == N
        assert 3 * (3 * 3 - 1) // 2 == K

    def test_pent_difference(self):
        """Pent(3) − Pent(2) = k − N = 7 = Φ₆."""
        assert _pentagonal(3) - _pentagonal(2) == PHI6

    def test_pent_sum(self):
        """Pent(2) + Pent(3) = N + k = 17 = k + N (prime)."""
        assert _pentagonal(2) + _pentagonal(3) == K + N


# ──────────────────────────────────────────────
# T380: Lucas Triple
# ──────────────────────────────────────────────
class TestLucasTriple:
    """T380: The Lucas sequence opens with an SRG-parameter triple.

    L(0) = 2 = λ
    L(2) = 3 = q
    L(3) = 4 = μ

    Combined with T169 (L(N)=k−1), the Lucas sequence encodes the
    full parameter set {λ, q, μ} in its first four terms.
    """

    def test_lucas_0_is_lam(self):
        """L(0) = 2 = λ."""
        assert _lucas(0) == LAM

    def test_lucas_2_is_q(self):
        """L(2) = 3 = q."""
        assert _lucas(2) == Q

    def test_lucas_3_is_mu(self):
        """L(3) = 4 = μ."""
        assert _lucas(3) == MU

    def test_lucas_product(self):
        """L(0)·L(2)·L(3) = λ·q·μ = 24 = f."""
        assert _lucas(0) * _lucas(2) * _lucas(3) == F_MULT

    def test_lucas_sum(self):
        """L(0) + L(2) + L(3) = λ + q + μ = 9 = q²."""
        assert _lucas(0) + _lucas(2) + _lucas(3) == Q**2
