"""
Phase CCLXXIII — Hexad Shell and Bernoulli Threshold
=======================================================

THEOREM (Hexad Shell):

The initial Monster/Bernoulli prime shell from W(3,3) is exactly 6 primes:

  {λ, q, Φ₄/λ, Φ₆, k−1, Φ₃} = {2, 3, 5, 7, 11, 13}

THEOREM (Bernoulli Threshold):

k = q(q+1) = 12 is the first even Bernoulli index whose denominator
has ≥5 distinct prime factors AND is stable under weight-doubling:
  den(B₁₂) = den(B₂₄) = 2730 = 2·3·5·7·13

THEOREM (Irreducible Selector):
  den(B₂) = λq = 6   ⟹   (q−1)q = 6   ⟹   q = 3 uniquely

SOURCE: W33_hexad_closure_20260330.zip
"""
import math
import pytest
from fractions import Fraction

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
Phi3 = 13
Phi4 = 10
Phi6 = 7

# ── Bernoulli numbers (exact rational) ──
# Using von Staudt-Clausen for denominators
def bernoulli_denominator(n):
    """den(B_n) = product of primes p where (p-1)|n."""
    if n == 0:
        return 1
    if n == 1:
        return 2
    if n % 2 != 0:
        return 1  # B_n = 0 for odd n > 1
    d = 1
    for p in range(2, n + 2):
        if all(p % i != 0 for i in range(2, int(p**0.5) + 1)) or p == 2:
            if p <= 1:
                continue
            is_prime = p == 2 or all(p % i != 0 for i in range(2, int(p**0.5) + 1))
            if is_prime and n % (p - 1) == 0:
                d *= p
    return d


# ================================================================
# T1: Hexad prime shell
# ================================================================
class TestT1_HexadShell:
    """Initial prime shell = {2, 3, 5, 7, 11, 13}."""

    def test_hexad_from_atoms(self):
        hexad = {lam, q, Phi4 // lam, Phi6, k - 1, Phi3}
        assert hexad == {2, 3, 5, 7, 11, 13}

    def test_hexad_count(self):
        hexad = {lam, q, Phi4 // lam, Phi6, k - 1, Phi3}
        assert len(hexad) == 6

    def test_all_prime(self):
        for p in [2, 3, 5, 7, 11, 13]:
            assert all(p % d != 0 for d in range(2, p))

    def test_atoms(self):
        assert lam == 2
        assert q == 3
        assert Phi4 // lam == 5
        assert Phi6 == 7
        assert k - 1 == 11
        assert Phi3 == 13


# ================================================================
# T2: Bernoulli selector
# ================================================================
class TestT2_BernoulliSelector:
    """den(B₂) = λq = 6 selects q=3 uniquely."""

    def test_B2_denominator(self):
        """den(B₂) = 6 = product of primes p with (p-1)|2."""
        # p=2: (2-1)=1|2 ✓, p=3: (3-1)=2|2 ✓ → den = 6
        assert bernoulli_denominator(2) == 6

    def test_B2_is_lam_q(self):
        assert lam * q == 6

    def test_selector_polynomial(self):
        """(q-1)q = 6 → q²-q-6 = (q-3)(q+2) = 0."""
        assert (q - 3) * (q + 2) == 0


# ================================================================
# T3: Bernoulli threshold
# ================================================================
class TestT3_BernoulliThreshold:
    """k=12 is the first stable 5-prime Bernoulli weight."""

    def test_den_B12(self):
        assert bernoulli_denominator(12) == 2730

    def test_den_B12_factored(self):
        assert 2730 == 2 * 3 * 5 * 7 * 13

    def test_stable_under_doubling(self):
        """den(B₂₄) = den(B₁₂) = 2730."""
        assert bernoulli_denominator(24) == bernoulli_denominator(12)

    def test_first_five_prime(self):
        """No even n < 12 has 5+ distinct prime factors in den(B_n)."""
        for n in range(2, 12, 2):
            d = bernoulli_denominator(n)
            factors = set()
            temp = d
            for p in range(2, temp + 1):
                while temp % p == 0:
                    factors.add(p)
                    temp //= p
            assert len(factors) < 5

    def test_k_equals_12(self):
        assert k == 12


# ================================================================
# T4: Perfect-square spectral condition
# ================================================================
class TestT4_PerfectSquare:
    """1+2k = 25 = 5² is a perfect square only at q=3."""

    def test_1_plus_2k(self):
        assert 1 + 2 * k == 25

    def test_is_perfect_square(self):
        assert int(math.isqrt(1 + 2 * k))**2 == 1 + 2 * k

    def test_uniqueness_prime_powers(self):
        """Among prime powers q=2..19, 1+2q(q+1) is a perfect square only at q=3."""
        prime_powers = [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19]
        hits = []
        for qq in prime_powers:
            val = 1 + 2 * qq * (qq + 1)
            if int(math.isqrt(val))**2 == val:
                hits.append(qq)
        assert hits == [3]
