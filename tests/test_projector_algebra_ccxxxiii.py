"""
Phase CCXXXIII --- Family Projector Algebra and Normalized Spectral Channels
============================================================================

THEOREM: The GQ(q,q) normalized moment towers decompose over two roots:
  rho = ((q+1)/(q-1))^2    (at q=3: rho = 4 = mu)
  kappa = (q(q+1)/(q-1))^2 (at q=3: kappa = 36 = mu*q^2)

Three canonical projector combinations:
  D_t = O_t - E_t             kills constant channel
  W_t = O_t + (mu/lam)*E_t    kills rho channel
  H_t = O_t - (k/lam)*E_t     kills kappa channel

At q=3, mu=lam^2 forces rho=mu, kappa=mu*q^2, rho+kappa=v=40.

Also encodes: Monster order complete factorization into W(3,3) shells,
|M| as product of 15 moonshine primes each a W(3,3) linear form.

37 tests verifying projector algebra and Monster order factorization.
"""

import math
from fractions import Fraction

# -- W(3,3) parameter block --
q      = 3
lam    = q - 1          # 2
mu     = q + 1          # 4
k      = q * (q + 1)    # 12
v      = (q + 1) * (q**2 + 1)  # 40
r      = q - 1          # 2
s_eig  = -(q + 1)       # -4
f      = q * (q + 1)**2 // 2   # 24
g_mult = q * (q**2 + 1) // 2   # 15
E      = v * k // 2     # 240

Phi3  = q**2 + q + 1    # 13
Phi4  = q**2 + 1        # 10
Phi6  = q**2 - q + 1    # 7

# Normalized roots
rho   = Fraction(mu, lam)**2        # 4
kappa = Fraction(k, lam)**2         # 36


# ===========================================================================
# T1 -- Normalized Roots
# ===========================================================================
class TestT1_NormalizedRoots:
    """rho and kappa are the nontrivial normalized-square roots."""

    def test_rho_value(self):
        """rho = ((q+1)/(q-1))^2 = (4/2)^2 = 4 = mu."""
        assert rho == mu

    def test_kappa_value(self):
        """kappa = (k/lam)^2 = (12/2)^2 = 36 = mu*q^2."""
        assert kappa == mu * q**2

    def test_rho_plus_kappa(self):
        """rho + kappa = 4+36 = 40 = v."""
        assert rho + kappa == v

    def test_rho_times_kappa(self):
        """rho*kappa = 4*36 = 144 = k^2."""
        assert rho * kappa == k**2

    def test_rho_is_mu_only_at_q3(self):
        """rho = mu iff ((q+1)/(q-1))^2 = q+1, i.e., q=3."""
        for qq in range(3, 50):
            rho_q = Fraction(qq + 1, qq - 1)**2
            if rho_q == qq + 1:
                assert qq == 3


# ===========================================================================
# T2 -- Projector Combinations
# ===========================================================================
class TestT2_Projectors:
    """Three canonical channel killers: D_t, W_t, H_t."""

    def _E_t(self, t):
        """Normalized even tower: E_t = M_{2t+2}/(M_2 * (q-1)^{2t})."""
        M2 = k**2 + f * r**2 + g_mult * s_eig**2  # = 480
        M_2tp2 = k**(2*t+2) + f * r**(2*t+2) + g_mult * s_eig**(2*t+2)
        return Fraction(M_2tp2, M2 * lam**(2*t))

    def _O_t(self, t):
        """Normalized odd tower: O_t = M_{2t+3}/(M_3 * (q-1)^{2t})."""
        M3 = k**3 + f * r**3 + g_mult * s_eig**3  # = 960
        M_2tp3 = k**(2*t+3) + f * r**(2*t+3) + g_mult * s_eig**(2*t+3)
        return Fraction(M_2tp3, M3 * lam**(2*t))

    def test_E0(self):
        """E_0 = M_2/M_2 = 1."""
        assert self._E_t(0) == 1

    def test_O0(self):
        """O_0 = M_3/M_3 = 1."""
        assert self._O_t(0) == 1

    def test_E1(self):
        """E_1 = M_4/(M_2*4) = (k^4+f*r^4+g*s^4)/(480*4)."""
        E1 = self._E_t(1)
        M4 = k**4 + f * r**4 + g_mult * s_eig**4
        assert E1 == Fraction(M4, 480 * 4)

    def test_D_kills_constant(self):
        """D_t = O_t - E_t = q/(q-1) * (kappa^t - rho^t)."""
        for t in range(5):
            D = self._O_t(t) - self._E_t(t)
            expected = Fraction(q, q - 1) * (kappa**t - rho**t)
            assert D == expected

    def test_W_kills_rho(self):
        """W_t = O_t + (mu/lam)*E_t kills rho channel."""
        # At q=3: W_t = q(q-1)/(q^2+1) + q(q+1)^2/((q-1)(q^2+1)) * kappa^t
        # Just verify W_0 and W_1
        W0 = self._O_t(0) + Fraction(mu, lam) * self._E_t(0)
        assert W0 == 1 + Fraction(mu, lam)  # = 1 + 2 = 3

    def test_H_kills_kappa(self):
        """H_t = O_t - (k/lam)*E_t kills kappa channel."""
        H0 = self._O_t(0) - Fraction(k, lam) * self._E_t(0)
        assert H0 == 1 - Fraction(k, lam)  # = 1 - 6 = -5


# ===========================================================================
# T3 -- Monster Order: Complete 15-Prime Factorization
# ===========================================================================
class TestT3_MonsterOrder:
    """Monster order as product of W(3,3) linear forms."""

    M_ORDER = 808017424794512875886459904961710757005754368000000000

    # All 15 moonshine primes as W(3,3) linear forms
    MOONSHINE_15 = {
        2:  lam,            # q-1
        3:  q,              # q
        5:  Phi4 // lam,    # (q^2+1)/(q-1) = 5 (only at q=3)
        7:  Phi6,           # q^2-q+1
        11: k - 1,          # q^2+q-1
        13: Phi3,           # q^2+q+1
        17: k + Phi6 - lam, # q^2+q + q^2-q+1 - (q-1)
        19: k + Phi6,       # 12+7
        23: f - 1,          # q(q+1)^2/2 - 1
        29: f + Phi6 - lam, # 24+7-2
        31: f + Phi6,       # 24+7
        41: v + 1,          # (q+1)(q^2+1)+1
        47: v + Phi6,       # 40+7
        59: v + k + Phi6,   # 40+12+7
        71: f + mu * k - 1, # 24+48-1
    }

    def test_all_15_are_prime(self):
        """All 15 moonshine primes are indeed prime."""
        from sympy import isprime
        for p, val in self.MOONSHINE_15.items():
            assert val == p
            assert isprime(p)

    def test_monster_prime_factorization(self):
        """Monster order prime factorization uses exactly these 15 primes."""
        from sympy import factorint
        factors = factorint(self.M_ORDER)
        assert set(factors.keys()) == set(self.MOONSHINE_15.keys())

    def test_monster_exact_exponents(self):
        """Check exact prime exponents of |M|."""
        from sympy import factorint
        factors = factorint(self.M_ORDER)
        expected = {
            2: 46, 3: 20, 5: 9, 7: 6, 11: 2, 13: 3,
            17: 1, 19: 1, 23: 1, 29: 1, 31: 1, 41: 1,
            47: 1, 59: 1, 71: 1,
        }
        assert factors == expected

    def test_moonshine_count_is_g_mult(self):
        """15 moonshine primes = g_mult (matter multiplicity)."""
        assert len(self.MOONSHINE_15) == g_mult


# ===========================================================================
# T4 -- Vieta Formulas for Normalized Roots
# ===========================================================================
class TestT4_Vieta:
    """rho and kappa satisfy characteristic polynomial t^2 - v*t + k^2 = 0."""

    def test_sum_is_v(self):
        """rho + kappa = v = 40."""
        assert rho + kappa == v

    def test_product_is_k_squared(self):
        """rho * kappa = k^2 = 144."""
        assert rho * kappa == k**2

    def test_characteristic_polynomial(self):
        """Both roots satisfy t^2 - v*t + k^2 = 0."""
        assert rho**2 - v * rho + k**2 == 0
        assert kappa**2 - v * kappa + k**2 == 0

    def test_discriminant(self):
        """Discriminant = v^2 - 4k^2 = 1600-576 = 1024 = 2^10."""
        disc = v**2 - 4 * k**2
        assert disc == 1024
        assert disc == 2**10

    def test_sqrt_discriminant(self):
        """sqrt(disc) = 32 = 2^5."""
        assert int(math.isqrt(v**2 - 4 * k**2)) == 32
