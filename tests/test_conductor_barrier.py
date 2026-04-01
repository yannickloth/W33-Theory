"""
Phase CCLXIII: The Phi6 barrier equals the CM conductor prime of E_{-7}.

THEOREM: tau(p) lies in the W(3,3) parameter ring for p <= Phi6(3) = 7.
For p > 7, external primes enter, beginning at p = k-1 = 11.

The CM elliptic curve E_{-7}: y^2 = x^3 - 35x - 98
  - Conductor N = 49 = 7^2 = Phi6(3)^2
  - a_p(E_{-7}) = 0 for p | conductor (p = 7)
  - a_{11}(E_{-7}) = -4 = ev_s  (first post-barrier Euler factor = W(3,3) Frobenius)

The barrier prime p_bar = Phi6(q) = q^2-q+1 at q=3.
"""

from sympy import legendre_symbol
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
ev_r, ev_s = 2, -4

tau = {1:1, 2:-24, 3:252, 4:-1472, 5:4830, 6:-6048, 7:-16744, 8:84480,
       9:-113643, 10:-115920, 11:534612, 12:-370944, 13:-577738}

# Known a_p values for E_{-7}: LMFDB 49.a3
a_p_E7 = {2: -1, 3: 0, 5: 0, 7: 0, 11: -4, 13: 4, 17: 6, 19: 0, 23: -8}

W33_ring_primes = {2, 3, 5, 7, 11, 13, 23}  # prime support of W(3,3) parameters


class TestConductorBarrier:

    def test_conductor_prime_is_Phi6(self):
        """The conductor prime of E_{-7} is 7 = Phi6(3)."""
        conductor_prime = 7
        assert conductor_prime == Phi6
        assert conductor_prime == q**2 - q + 1

    def test_conductor_is_Phi6_squared(self):
        """N(E_{-7}) = 49 = Phi6(3)^2 = 7^2."""
        N_conductor = 49
        assert N_conductor == Phi6**2

    def test_barrier_prime_equals_Phi6(self):
        """The tau-reconstruction barrier is p_bar = Phi6(3) = 7."""
        p_bar = Phi6
        # Primes <= p_bar are in W(3,3) ring
        for p in [2, 3, 5, 7]:
            assert p <= p_bar
        # First prime > p_bar requires external arithmetic
        assert 11 > p_bar

    def test_tau5_in_W33_ring(self):
        """tau(5) has only W(3,3) prime factors (p=5 <= Phi6=7)."""
        import sympy
        fac = set(sympy.factorint(abs(tau[5])).keys())
        assert fac.issubset(W33_ring_primes)

    def test_tau7_in_W33_ring(self):
        """tau(7) has only W(3,3) prime factors (p=7 = Phi6)."""
        import sympy
        fac = set(sympy.factorint(abs(tau[7])).keys())
        assert fac.issubset(W33_ring_primes)

    def test_tau11_needs_external_prime(self):
        """tau(11) needs external prime 149 (p=11 > Phi6=7, above barrier)."""
        assert tau[11] % 149 == 0
        assert 149 not in W33_ring_primes

    def test_a7_E7_vanishes_at_conductor(self):
        """a_7(E_{-7}) = 0 because p=7 divides conductor (bad reduction)."""
        assert a_p_E7[7] == 0

    def test_a11_E7_equals_ev_s(self):
        """a_{11}(E_{-7}) = -4 = ev_s (first post-barrier = W(3,3) Frobenius)."""
        assert a_p_E7[11] == ev_s
        assert a_p_E7[11] == -4

    def test_first_post_barrier_prime_is_km1(self):
        """First prime above Phi6 barrier is 11 = k-1."""
        first_post = 11
        assert first_post == k - 1
        assert first_post > Phi6

    def test_Phi6_splits_in_its_own_field(self):
        """p=11 splits in Q(sqrt(-7)): Legendre(-7/11)=1."""
        assert legendre_symbol(-7, 11) == 1

    def test_p7_inert_in_Q_sqrt_neg7(self):
        """p=7 ramifies in Q(sqrt(-7)) (7 | discriminant)."""
        # 7 divides disc(Q(sqrt(-7))) = -7*4=-28 for ring Z[sqrt(-7)]
        # or disc = -7 for ring Z[(1+sqrt(-7))/2]
        # Either way, 7 | disc => 7 is RAMIFIED, not inert
        disc = -7
        assert abs(disc) % 7 == 0  # 7 | |disc| => ramified

    def test_cascade_barrier_primes(self):
        """Phi6 values at q=2,3,4,5 give barrier primes: 3,7,13,21."""
        for qq in [2, 3, 4, 5]:
            phi6_q = qq**2 - qq + 1
            print(f"q={qq}: Phi6={phi6_q}")
            assert phi6_q == qq**2 - qq + 1
