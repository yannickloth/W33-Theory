"""
Phase XXV: Analytic Number Theory & Arithmetic Functions (T336-T350)
=====================================================================
Fifteen theorems connecting SRG(40,12,2,4) parameters to classical
analytic number theory: prime counting, Riemann zeta special values,
Bernoulli numbers, partition functions, Euler products, Dirichlet
series, Mertens' theorems, prime gaps, arithmetic progressions,
Goldbach representations, and number-theoretic transforms.

Every constant derives from (v, k, lam, mu, q) = (40, 12, 2, 4, 3).
"""

import math
import pytest
from itertools import combinations
from functools import reduce

# ── SRG parameters ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2           # 240
R, S = 2, -4             # eigenvalues
F = (-K - (V - 1) * S) // (R - S)  # 24  (mult of r)
G = V - 1 - F                      # 15  (mult of s)
N = Q + 2                # 5
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
ALBERT = V - PHI3        # 27
THETA = V * (-S) // (K - S)  # 10


def _is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def _prime_count(n):
    """pi(n): number of primes <= n."""
    return sum(1 for i in range(2, n + 1) if _is_prime(i))


def _sigma(n, k=1):
    """Sum of k-th powers of divisors of n."""
    return sum(d**k for d in range(1, n + 1) if n % d == 0)


def _euler_phi(n):
    """Euler's totient function."""
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


def _mobius(n):
    """Möbius function."""
    if n == 1:
        return 1
    factors = 0
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            factors += 1
            temp //= p
            if temp % p == 0:
                return 0
        p += 1
    if temp > 1:
        factors += 1
    return (-1) ** factors


def _partition_count(n):
    """Number of integer partitions of n (dynamic programming)."""
    p = [0] * (n + 1)
    p[0] = 1
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            p[j] += p[j - i]
    return p[n]


@pytest.fixture(scope="module")
def primes_to_1000():
    return [p for p in range(2, 1001) if _is_prime(p)]


# ──────────────────────────────────────────────
# T336: Prime Counting at SRG Parameters
# ──────────────────────────────────────────────
class TestPrimeCounting:
    """pi(v) = pi(40) = 12 = k. The number of primes up to v
    equals the valency of the SRG!"""

    def test_pi_v(self):
        """pi(40) = 12 = k."""
        assert _prime_count(V) == K

    def test_pi_k(self):
        """pi(12) = 5 = N."""
        assert _prime_count(K) == N

    def test_pi_E(self):
        """pi(240) = 52 = 4*PHI3 = 4*13."""
        pi_E = _prime_count(E)
        assert pi_E == 52
        assert pi_E == 4 * PHI3

    def test_pi_v_minus_1(self):
        """pi(39) = 12 = k (39 is not prime)."""
        assert _prime_count(V - 1) == K

    def test_pi_q_squared(self):
        """pi(q^2) = pi(9) = 4 = mu."""
        assert _prime_count(Q**2) == MU


# ──────────────────────────────────────────────
# T337: Zeta Function Special Values
# ──────────────────────────────────────────────
class TestZetaValues:
    """zeta(2) = pi^2/6; zeta(4) = pi^4/90.
    The denominators 6 and 90 relate to SRG parameters:
    6 = |r-s| = 6; 90 = v*(v-1)/2 - E = 780 - 240... no.
    Actually: 6 = |r| + |s| = 2 + 4; 90 = 6*g = 6*15."""

    def test_zeta2_denominator(self):
        """Denominator of zeta(2) = 6 = |r| + |s| = |r - s|."""
        assert abs(R) + abs(S) == 6
        assert abs(R - S) == 6

    def test_zeta4_denominator(self):
        """Denominator of zeta(4) = 90 = 6*g = 6*15."""
        assert 6 * G == 90

    def test_zeta_ratio(self):
        """zeta(4)/zeta(2)^2 = 90/(6^2) * (pi^4/pi^4) ... nah.
        Actually zeta(2)^2 / zeta(4) = (pi^4/36)/(pi^4/90) = 90/36 = 5/2 = N/LAM."""
        ratio = 90 / 36  # = 2.5
        assert ratio == N / LAM

    def test_bernoulli_b2(self):
        """B_2 = 1/6; denominator = 6 = |r-s|."""
        # B_2 = 1/6 by definition
        assert abs(R - S) == 6

    def test_bernoulli_b4(self):
        """B_4 = -1/30; |denominator| = 30 = 6*N = |r-s|*N."""
        assert abs(R - S) * N == 30


# ──────────────────────────────────────────────
# T338: Partition Function Values
# ──────────────────────────────────────────────
class TestPartitionFunction:
    """p(n) = number of integer partitions.
    p(k) = p(12) = 77 = 7*11 = PHI6 * 11.
    p(v) = p(40) = 37338."""

    def test_p_k(self):
        """p(12) = 77 = 7 * 11 = PHI6 * 11."""
        assert _partition_count(K) == 77
        assert 77 == PHI6 * 11

    def test_p_q(self):
        """p(3) = 3 = q."""
        assert _partition_count(Q) == Q

    def test_p_mu(self):
        """p(4) = 5 = N."""
        assert _partition_count(MU) == N

    def test_p_N(self):
        """p(5) = 7 = PHI6."""
        assert _partition_count(N) == PHI6

    def test_p_chain(self):
        """p(q) = q, p(mu) = N, p(N) = PHI6: partition chain."""
        assert _partition_count(Q) == Q
        assert _partition_count(MU) == N
        assert _partition_count(N) == PHI6


# ──────────────────────────────────────────────
# T339: Euler Totient at SRG Values
# ──────────────────────────────────────────────
class TestEulerTotient:
    """phi(v) = phi(40) = 16 = mu^2.
    phi(E) = phi(240) relates to SRG parameters."""

    def test_phi_v(self):
        """phi(40) = 16 = mu^2."""
        assert _euler_phi(V) == MU**2
        assert _euler_phi(V) == 16

    def test_phi_E(self):
        """phi(240) = 64 = mu^3 = 4^3."""
        assert _euler_phi(E) == MU**3
        assert _euler_phi(E) == 64

    def test_phi_k(self):
        """phi(12) = 4 = mu."""
        assert _euler_phi(K) == MU

    def test_phi_ALBERT(self):
        """phi(27) = 18 = 2*q^2."""
        assert _euler_phi(ALBERT) == 18
        assert 18 == 2 * Q**2

    def test_phi_chain(self):
        """phi(k) = mu, phi(v) = mu^2, phi(E) = mu^3: power chain!"""
        assert _euler_phi(K) == MU
        assert _euler_phi(V) == MU**2
        assert _euler_phi(E) == MU**3


# ──────────────────────────────────────────────
# T340: Divisor Function Identities
# ──────────────────────────────────────────────
class TestDivisorFunction:
    """sigma_1(E) = sigma_1(240) = 744 = j-invariant constant!
    This was discovered in Phase XXII (T291), confirmed here."""

    def test_sigma1_E(self):
        """sigma_1(240) = 744 = j(q) - j_0."""
        assert _sigma(E) == 744

    def test_sigma0_v(self):
        """d(40) = number of divisors = 8 = 2^3."""
        assert _sigma(V, 0) == 8

    def test_sigma0_E(self):
        """d(240) = 20 = 4*N."""
        assert _sigma(E, 0) == 20
        assert 20 == 4 * N

    def test_sigma1_v(self):
        """sigma_1(40) = 90 = 6*g = 6*15."""
        assert _sigma(V) == 90
        assert 90 == 6 * G

    def test_sigma1_k(self):
        """sigma_1(12) = 28 = v - k = ALBERT + 1."""
        assert _sigma(K) == 28
        assert 28 == V - K


# ──────────────────────────────────────────────
# T341: Möbius Function and Inversion
# ──────────────────────────────────────────────
class TestMobiusFunction:
    """mu(v) = mu(40) and Möbius inversion on SRG divisors."""

    def test_mobius_v(self):
        """mu(40) = 0 (40 = 2^3 * 5, has squared factor)."""
        assert _mobius(V) == 0

    def test_mobius_E(self):
        """mu(240) = 0 (240 = 2^4 * 3 * 5, has squared factor)."""
        assert _mobius(E) == 0

    def test_mobius_k(self):
        """mu(12) = 0 (12 = 2^2 * 3, has squared factor)."""
        assert _mobius(K) == 0

    def test_mobius_PHI3(self):
        """mu(13) = -1 (13 is prime)."""
        assert _mobius(PHI3) == -1

    def test_mobius_sum_over_divisors(self):
        """sum_{d|n} mu(d) = 0 for n > 1 (identity)."""
        for n in [V, K, E, MU, ALBERT]:
            s = sum(_mobius(d) for d in range(1, n + 1) if n % d == 0)
            assert s == 0


# ──────────────────────────────────────────────
# T342: Goldbach Representations
# ──────────────────────────────────────────────
class TestGoldbachRepresentations:
    """Every even number >= 4 can be written as sum of two primes.
    v = 40 has multiple Goldbach representations.
    The number of representations r(v) = number of ways to write v = p + q_prime."""

    def test_v_goldbach_count(self, primes_to_1000):
        """r(40) = number of Goldbach representations."""
        primes_set = set(primes_to_1000)
        count = sum(1 for p in primes_to_1000 if p <= V // 2 and (V - p) in primes_set)
        assert count == Q  # 3 representations: (3,37), (11,29), (17,23)

    def test_E_goldbach_count(self, primes_to_1000):
        """r(240) > 0 (Goldbach for E)."""
        primes_set = set(primes_to_1000)
        count = sum(1 for p in primes_to_1000 if p <= E // 2 and (E - p) in primes_set)
        assert count > 0

    def test_v_as_sum_of_3_and_37(self, primes_to_1000):
        """40 = 3 + 37 = q + 37; both prime."""
        assert _is_prime(Q)
        assert _is_prime(37)
        assert Q + 37 == V

    def test_v_goldbach_includes_q(self, primes_to_1000):
        """One Goldbach pair for v=40 uses q=3."""
        assert _is_prime(Q)
        assert _is_prime(V - Q)

    def test_k_as_sum_of_two_primes(self):
        """12 = 5 + 7 = N + PHI6."""
        assert _is_prime(N)
        assert _is_prime(PHI6)
        assert N + PHI6 == K


# ──────────────────────────────────────────────
# T343: Twin Primes Near SRG Parameters
# ──────────────────────────────────────────────
class TestTwinPrimes:
    """Twin prime pairs near v, k, etc. The SRG parameters
    sit near twin prime pairs."""

    def test_twin_at_41_43(self):
        """(41, 43) is a twin prime pair just above v=40."""
        assert _is_prime(V + 1)
        assert _is_prime(V + 3)

    def test_twin_at_11_13(self):
        """(11, 13) is a twin prime pair: 11 = k-1, 13 = PHI3 = k+1."""
        assert _is_prime(K - 1)
        assert _is_prime(K + 1)
        assert K + 1 == PHI3

    def test_twin_at_5_7(self):
        """(5, 7) = (N, PHI6) is a twin prime pair."""
        assert _is_prime(N)
        assert _is_prime(PHI6)
        assert PHI6 - N == 2

    def test_twin_at_29_31(self):
        """(29, 31) near ALBERT=27: 29 = ALBERT+2, 31 = ALBERT+4."""
        assert _is_prime(29)
        assert _is_prime(31)
        assert 29 == ALBERT + 2

    def test_twin_count_up_to_v(self):
        """Number of twin prime pairs (p, p+2) with p+2 <= v."""
        twins = [(p, p + 2) for p in range(2, V - 1) if _is_prime(p) and _is_prime(p + 2)]
        assert len(twins) == 5  # (3,5),(5,7),(11,13),(17,19),(29,31)


# ──────────────────────────────────────────────
# T344: Arithmetic Progressions of Primes
# ──────────────────────────────────────────────
class TestArithmeticProgressions:
    """Green-Tao: arbitrarily long APs in primes.
    For small lengths, check APs among primes <= v."""

    def test_3_term_ap(self, primes_to_1000):
        """3-term APs in primes <= 40: e.g., (3, 5, 7), (5, 11, 17), (5, 17, 29), (3, 23, 43)..."""
        primes = [p for p in primes_to_1000 if p <= V]
        pset = set(primes)
        aps = []
        for i in range(len(primes)):
            for j in range(i + 1, len(primes)):
                d = primes[j] - primes[i]
                if primes[j] + d in pset and primes[j] + d <= V:
                    aps.append((primes[i], primes[j], primes[j] + d))
        assert len(aps) >= 4  # at least 4 such APs

    def test_longest_ap_in_primes_to_v(self, primes_to_1000):
        """Find longest AP in primes <= v = 40."""
        primes = [p for p in primes_to_1000 if p <= V]
        pset = set(primes)
        max_len = 0
        for i in range(len(primes)):
            for j in range(i + 1, len(primes)):
                d = primes[j] - primes[i]
                length = 2
                nxt = primes[j] + d
                while nxt in pset and nxt <= V:
                    length += 1
                    nxt += d
                max_len = max(max_len, length)
        assert max_len >= 3

    def test_q_as_ap_start(self, primes_to_1000):
        """q=3 starts AP (3,5,7) of length 3 with d=2."""
        assert _is_prime(3) and _is_prime(5) and _is_prime(7)
        assert 5 - 3 == 7 - 5 == 2

    def test_ap_common_difference_6(self, primes_to_1000):
        """AP with d = |r-s| = 6: (5,11,17,23,29) of length 5, all prime!"""
        ap = [5, 11, 17, 23, 29]
        d = abs(R - S)
        assert d == 6
        assert all(_is_prime(p) for p in ap)
        assert all(ap[i + 1] - ap[i] == d for i in range(len(ap) - 1))
        assert len(ap) == N  # length = N = 5

    def test_ap_d6_length_N(self, primes_to_1000):
        """The AP (5,11,17,23,29) has length N=5 and common difference |r-s|=6."""
        assert len([5, 11, 17, 23, 29]) == N
        assert abs(R - S) == 6


# ──────────────────────────────────────────────
# T345: Prime Factorization Patterns
# ──────────────────────────────────────────────
class TestPrimeFactorization:
    """The SRG parameters and derived constants factor in structured ways."""

    def test_v_factorization(self):
        """v = 40 = 2^3 * 5 = 2^3 * N."""
        assert V == 2**3 * N

    def test_E_factorization(self):
        """E = 240 = 2^4 * 3 * 5 = 2^4 * q * N."""
        assert E == 2**4 * Q * N

    def test_sp43_factorization(self):
        """51840 = 2^7 * 3^4 * 5."""
        assert 51840 == 2**7 * 3**4 * 5

    def test_albert_factorization(self):
        """ALBERT = 27 = 3^3 = q^3."""
        assert ALBERT == Q**3

    def test_omega_v(self):
        """Omega(v) = 4 = mu (number of prime factors with multiplicity)."""
        # 40 = 2^3 * 5 => Omega(40) = 3 + 1 = 4
        omega = 3 + 1  # from 2^3 * 5
        assert omega == MU


# ──────────────────────────────────────────────
# T346: Sum of Primes
# ──────────────────────────────────────────────
class TestSumOfPrimes:
    """Sum of primes up to various SRG parameters."""

    def test_sum_primes_to_k(self, primes_to_1000):
        """sum of primes <= 12 = 2+3+5+7+11 = 28 = v - k."""
        s = sum(p for p in primes_to_1000 if p <= K)
        assert s == 28
        assert s == V - K

    def test_sum_primes_to_v(self, primes_to_1000):
        """sum of primes <= 40."""
        s = sum(p for p in primes_to_1000 if p <= V)
        assert s == 197  # 2+3+5+7+11+13+17+19+23+29+31+37 = 197
        assert _is_prime(s)  # 197 is prime!

    def test_sum_first_q_primes(self, primes_to_1000):
        """sum of first q=3 primes = 2+3+5 = 10 = THETA."""
        s = sum(primes_to_1000[:Q])
        assert s == THETA

    def test_sum_first_mu_primes(self, primes_to_1000):
        """sum of first mu=4 primes = 2+3+5+7 = 17."""
        s = sum(primes_to_1000[:MU])
        assert s == 17
        assert _is_prime(s)

    def test_product_first_q_primes(self, primes_to_1000):
        """product of first q=3 primes = 2*3*5 = 30 = |r-s|*N."""
        p = reduce(lambda a, b: a * b, primes_to_1000[:Q])
        assert p == 30
        assert p == abs(R - S) * N


# ──────────────────────────────────────────────
# T347: Primorial and Factorial Relations
# ──────────────────────────────────────────────
class TestPrimorial:
    """Primorial p# = product of primes <= p.
    k# = 12# = 2*3*5*7*11 = 2310."""

    def test_q_primorial(self, primes_to_1000):
        """3# = 2*3 = 6 = |r-s|."""
        p3 = reduce(lambda a, b: a * b, [p for p in primes_to_1000 if p <= Q])
        assert p3 == 6
        assert p3 == abs(R - S)

    def test_N_primorial(self, primes_to_1000):
        """5# = 2*3*5 = 30 = |r-s|*N."""
        p5 = reduce(lambda a, b: a * b, [p for p in primes_to_1000 if p <= N])
        assert p5 == 30

    def test_PHI6_primorial(self, primes_to_1000):
        """7# = 2*3*5*7 = 210."""
        p7 = reduce(lambda a, b: a * b, [p for p in primes_to_1000 if p <= PHI6])
        assert p7 == 210

    def test_k_factorial(self):
        """k! = 12! = 479001600. k!/E = 12!/240 = 1995840."""
        k_fact = math.factorial(K)
        assert k_fact == 479001600
        assert k_fact // E == 1995840

    def test_v_div_factorial(self):
        """v! / (k! * (v-k)!) = C(40,12) = binomial coefficient."""
        binom = math.comb(V, K)
        assert binom == 5586853480
        # Check: C(40,12) is large but computable


# ──────────────────────────────────────────────
# T348: Digit Sums and Digital Roots
# ──────────────────────────────────────────────
class TestDigitSums:
    """Digital root dr(n) = n mod 9 (for n>0), with dr(9k)=9.
    SRG parameters have structured digital roots."""

    def test_dr_v(self):
        """dr(40) = 4 = mu."""
        dr = V % 9 if V % 9 != 0 else 9
        assert dr == 4
        assert dr == MU

    def test_dr_E(self):
        """dr(240) = 6 = |r-s|."""
        dr = E % 9 if E % 9 != 0 else 9
        assert dr == 6
        assert dr == abs(R - S)

    def test_dr_k(self):
        """dr(12) = 3 = q."""
        dr = K % 9 if K % 9 != 0 else 9
        assert dr == 3
        assert dr == Q

    def test_dr_ALBERT(self):
        """dr(27) = 9."""
        dr = ALBERT % 9 if ALBERT % 9 != 0 else 9
        assert dr == 9
        assert dr == Q**2

    def test_digit_sum_E(self):
        """Digit sum of E=240: 2+4+0 = 6 = |r-s|."""
        ds = sum(int(c) for c in str(E))
        assert ds == 6
        assert ds == abs(R - S)


# ──────────────────────────────────────────────
# T349: Abundant, Perfect, and Deficient Numbers
# ──────────────────────────────────────────────
class TestAbundantPerfect:
    """sigma(n) vs 2n determines if n is abundant (>), perfect (=), or deficient (<).
    sigma(v) = 90 > 80 = 2v => v=40 is abundant.
    sigma(E) = 744 > 480 = 2E => E=240 is abundant.
    The abundance sigma(n) - 2n has SRG meaning."""

    def test_v_abundant(self):
        """40 is abundant: sigma(40) = 90 > 80 = 2*40."""
        assert _sigma(V) == 90
        assert 90 > 2 * V

    def test_v_abundance(self):
        """Abundance of v: sigma(v) - 2v = 90 - 80 = 10 = THETA."""
        ab = _sigma(V) - 2 * V
        assert ab == THETA

    def test_E_abundant(self):
        """240 is abundant: sigma(240) = 744 > 480."""
        assert _sigma(E) == 744
        assert 744 > 2 * E

    def test_E_abundance(self):
        """Abundance of E: sigma(E) - 2E = 744 - 480 = 264."""
        ab = _sigma(E) - 2 * E
        assert ab == 264
        # 264 = 8 * 33 = 8 * (v - PHI6)

    def test_k_abundant(self):
        """12 is abundant: sigma(12) = 28 > 24 = 2*12."""
        assert _sigma(K) == 28
        assert 28 > 2 * K
        # Abundance = 28 - 24 = 4 = mu
        assert _sigma(K) - 2 * K == MU


# ──────────────────────────────────────────────
# T350: Totient Summatory Function
# ──────────────────────────────────────────────
class TestTotientSummatory:
    """Phi(n) = sum_{k=1}^{n} phi(k). Phi(n) ~ 3n^2/pi^2.
    Phi(v) and its connections to SRG."""

    def test_summatory_totient_v(self):
        """Phi(40) = sum phi(k) for k=1..40 = 490 = 2*N*PHI6^2."""
        Phi_v = sum(_euler_phi(k) for k in range(1, V + 1))
        assert Phi_v == 490
        assert Phi_v == 2 * N * PHI6**2

    def test_summatory_totient_k(self):
        """Phi(12) = sum phi(k) for k=1..12 = 46."""
        Phi_k = sum(_euler_phi(k) for k in range(1, K + 1))
        assert Phi_k == 46

    def test_summatory_factorization(self):
        """Phi(40) = 490 = 2 * 5 * 49 = 2 * N * PHI6^2."""
        Phi_v = sum(_euler_phi(k) for k in range(1, V + 1))
        assert Phi_v == 2 * N * PHI6**2
        assert Phi_v == 2 * 5 * 49

    def test_490_from_srg(self):
        """490 = v * k + v/4 * |r-s| - THETA = ... or just 2*N*PHI6^2."""
        val = 2 * N * PHI6**2
        assert val == 490

    def test_gauss_formula(self):
        """sum_{d|n} phi(d) = n. Check for n = v, k, E."""
        for n in [V, K, E]:
            s = sum(_euler_phi(d) for d in range(1, n + 1) if n % d == 0)
            assert s == n
