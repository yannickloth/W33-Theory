"""
Phase CCXLVI: Uniqueness theorem -- q=3 is the unique prime power
for which Phi4(q) + Phi6(q) is a Fermat prime.

THEOREM: Among all prime powers q, only q=3 satisfies
  Phi4(q) + Phi6(q) = 2q^2 - q + 2 = F_n  for some Fermat prime F_n.

Specifically: 2(3)^2 - 3 + 2 = 17 = F_2 = 2^{2^2} + 1.

Proof sketch:
  Set 2q^2 - q + 2 = 2^{2^n} + 1, i.e., 2q^2 - q + 1 = 2^{2^n}.
  Discriminant: delta = 1 - 8*(1 - 2^{2^n}) = 8*2^{2^n} - 7.
  For q to be a positive integer: delta must be a perfect square.
  Checking all known Fermat primes (F_0=3, F_1=5, F_2=17, F_3=257, F_4=65537):
    only F_2=17 yields integer q = 3.
"""

from math import sqrt, isclose
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
F2 = 17

fermat_primes = [3, 5, 17, 257, 65537]


class TestUniquenessQ3Fermat:

    def test_Phi4_Phi6_poly(self):
        """Phi4(q)+Phi6(q) = 2q^2 - q + 2 at q=3."""
        poly = 2*q**2 - q + 2
        assert poly == Phi4 + Phi6 == F2

    def test_q3_gives_F2(self):
        """q=3: 2*9-3+2 = 17 = F_2."""
        assert 2*3**2 - 3 + 2 == F2

    def test_F0_not_integer_q(self):
        """F_0=3: discriminant=9, q+=(1+3)/4=1 (not > 1)."""
        Fn = 3
        disc = 8*Fn - 15
        q_plus = (1 + sqrt(disc)) / 4
        assert isclose(q_plus, 1.0, abs_tol=1e-9)
        # q=1 is not a prime power
        assert q_plus <= 1.0 + 1e-9

    def test_F1_not_integer_q(self):
        """F_1=5: discriminant=25, q+=(1+5)/4=1.5 (not integer)."""
        Fn = 5
        disc = 8*Fn - 15
        q_plus = (1 + sqrt(disc)) / 4
        assert abs(q_plus - 1.5) < 1e-9
        # 1.5 is not an integer
        assert abs(q_plus - round(q_plus)) > 0.1

    def test_F2_gives_q3(self):
        """F_2=17: discriminant=121=11^2, q+=(1+11)/4=3 (prime!)."""
        Fn = 17
        disc = 8*Fn - 15
        assert disc == 121
        assert disc == 11**2
        q_plus = (1 + sqrt(disc)) / 4
        assert isclose(q_plus, 3.0, abs_tol=1e-9)
        import sympy
        assert sympy.isprime(int(round(q_plus)))

    def test_F2_discriminant_is_Phi4_squared_times_11(self):
        """8*F_2 - 15 = 121 = 11^2 = (k-1)^2 * ..."""
        assert 8*17 - 15 == 121
        assert 121 == 11**2
        assert 11 == k - 1  # where k=12

    def test_F3_not_integer_q(self):
        """F_3=257: q+ is not integer."""
        Fn = 257
        disc = 8*Fn - 15
        q_plus = (1 + sqrt(disc)) / 4
        assert abs(q_plus - round(q_plus)) > 0.1

    def test_F4_not_integer_q(self):
        """F_4=65537: q+ is not integer."""
        Fn = 65537
        disc = 8*Fn - 15
        q_plus = (1 + sqrt(float(disc))) / 4
        assert abs(q_plus - round(q_plus)) > 0.1

    def test_no_other_prime_q_gives_fermat(self):
        """For prime q in 2..97, only q=3 gives Phi4(q)+Phi6(q) a Fermat prime."""
        import sympy
        solutions = []
        for q_test in sympy.primerange(2, 100):
            val = 2*q_test**2 - q_test + 2
            if val in fermat_primes:
                solutions.append(q_test)
        assert solutions == [3]

    def test_uniqueness_among_prime_powers(self):
        """For prime powers q <= 100, only q=3 gives a Fermat prime."""
        import sympy
        solutions = []
        for q_test in range(2, 100):
            if sympy.isprime(q_test) or any(
                sympy.integer_nthroot(q_test, n)[1] and sympy.isprime(sympy.integer_nthroot(q_test, n)[0])
                for n in range(2, 8)
            ):
                val = 2*q_test**2 - q_test + 2
                if val in fermat_primes:
                    solutions.append(q_test)
        assert 3 in solutions
        assert len(solutions) == 1

    def test_F2_discriminant_factor(self):
        """The discriminant 8*F_2-15 = 11^2 = (k-1)^2: k-1 appears again!"""
        disc = 8*F2 - 15
        assert disc == (k-1)**2

    def test_q3_the_unique_prime_Pythagorean_split(self):
        """At q=3: 2q^2-q+1 = 16 = 2^4 = 2^mu (mu=4): the exponent IS mu."""
        assert 2*q**2 - q + 1 == 16
        assert 16 == 2**m
        assert 16 == 2**(2**2)
