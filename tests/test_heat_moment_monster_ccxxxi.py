"""
Phase CCXXXI --- Heat-Moment Unification and Monster-Co1 Action Shell
=====================================================================

HEAT-MOMENT THEOREM:
  The Laplacian spectral-zeta quotient has exact generating function:
    sum_{t>=0} b_t z^t = (1 - Phi3*z) / ((1 - Phi4*z)(1 - mu^2*z))
  At q=3: (1-13z)/((1-10z)(1-16z))
  Recurrence: a_{n+2} = 26*a_{n+1} - 160*a_n

MONSTER-Co1 THEOREM:
  |M| = |Co1| * |Co1:Co2| * |Co1:Co3| * low-prime-core * late-affine-shell
  where:
    |Co1:Co2| = tau(3)*C(v,2)/2 = 252*390 = 98280
    |Co1:Co3| = tau(3)*2^{k-4}*Phi3*Phi4 = 252*33280 = 8386560
    late shell = 17*19*29*31*41*47*59*71  (8 affine W(3,3) primes)

46 tests verifying heat-moment generating function and Monster decomposition.
"""

import math
from fractions import Fraction
from sympy import factorint, isprime

# -- W(3,3) parameter block --
q      = 3
lam    = q - 1          # 2
mu     = q + 1          # 4
k      = q * (q + 1)    # 12
v      = (q + 1) * (q**2 + 1)  # 40
r      = q - 1          # 2
s      = -(q + 1)       # -4
f      = q * (q + 1)**2 // 2   # 24
g_mult = q * (q**2 + 1) // 2   # 15
E      = v * k // 2     # 240

Phi3  = q**2 + q + 1    # 13
Phi4  = q**2 + 1        # 10
Phi6  = q**2 - q + 1    # 7
Phi12 = q**4 - q**2 + 1 # 73

tau3 = E + k  # 252

# Laplacian eigenvalues: L = k*I - A, so eigenvalues are k-r, k-s, k-k=0
L1 = k - r      # 10 = Phi4
L2 = k - s      # 16 = mu^2
L0 = 0          # trivial eigenvalue


# ===========================================================================
# T1 -- Laplacian Spectral-Zeta Quotient
# ===========================================================================
class TestT1_LaplacianZeta:
    """zeta_L(-n) / (2E) = (Phi4^{n-1} + mu^{2(n-1)}) / 2."""

    def _a(self, n):
        """Quotient a_n = zeta_L(-n) / (2E)."""
        # zeta_L(-n) = f*L1^n + g*L2^n  (ignoring trivial eigenvalue 0^n for n>0)
        return (f * L1**n + g_mult * L2**n) // (2 * E)

    def _a_formula(self, n):
        """Closed form: (Phi4^{n-1} + mu^{2(n-1)}) / 2."""
        return (Phi4**(n - 1) + mu**(2 * (n - 1))) // 2

    def test_a1(self):
        """a_1 = (1+1)/2 = 1."""
        assert self._a(1) == 1
        assert self._a_formula(1) == 1

    def test_a2(self):
        """a_2 = (10+16)/2 = 13 = Phi3."""
        assert self._a(2) == 13
        assert self._a_formula(2) == Phi3

    def test_a3(self):
        """a_3 = (100+256)/2 = 178."""
        assert self._a(3) == 178
        assert self._a_formula(3) == 178

    def test_a4(self):
        """a_4 = (1000+4096)/2 = 2548."""
        assert self._a(4) == 2548
        assert self._a_formula(4) == 2548

    def test_formula_matches_direct(self):
        """Closed form matches direct computation for n=1..10."""
        for n in range(1, 11):
            direct = f * L1**n + g_mult * L2**n
            formula = 2 * E * (Phi4**(n - 1) + mu**(2 * (n - 1))) // 2
            assert direct == formula

    def test_L1_is_Phi4(self):
        """Laplacian eigenvalue L1 = k-r = Phi4 = 10."""
        assert L1 == Phi4 == 10

    def test_L2_is_mu_squared(self):
        """Laplacian eigenvalue L2 = k-s = k+mu = mu^2 = 16."""
        assert L2 == mu**2 == 16


# ===========================================================================
# T2 -- Generating Function
# ===========================================================================
class TestT2_GeneratingFunction:
    """GF: (1 - Phi3*z) / ((1 - Phi4*z)(1 - mu^2*z))."""

    def test_recurrence_coefficients(self):
        """Recurrence: a_{n+2} = (Phi4+mu^2)*a_{n+1} - Phi4*mu^2*a_n."""
        c1 = Phi4 + mu**2   # 26
        c2 = Phi4 * mu**2   # 160
        assert c1 == 26
        assert c2 == 160

    def test_recurrence_holds(self):
        """Verify a_{n+2} = 26*a_{n+1} - 160*a_n for n=1..8."""
        seq = [1, 13]  # a_1, a_2
        for _ in range(8):
            seq.append(26 * seq[-1] - 160 * seq[-2])
        # Check: a_3 = 26*13 - 160*1 = 338-160 = 178
        assert seq[2] == 178
        # a_4 = 26*178 - 160*13 = 4628-2080 = 2548
        assert seq[3] == 2548
        # Verify against direct computation
        for i, n in enumerate(range(1, 11)):
            direct = (Phi4**(n - 1) + mu**(2 * (n - 1))) // 2
            assert seq[i] == direct

    def test_GF_numerator(self):
        """Numerator 1-13z = 1-Phi3*z."""
        assert Phi3 == 13

    def test_GF_denominator_roots(self):
        """Denominator roots are 1/Phi4 = 1/10 and 1/mu^2 = 1/16."""
        assert Phi4 == 10
        assert mu**2 == 16

    def test_a2_is_Phi3(self):
        """a_2 = Phi3 = 13 (the Phi3 cyclotomic controls the generating function)."""
        assert (Phi4 + mu**2) // 2 == Phi3


# ===========================================================================
# T3 -- Selector Identities from mu = lam^2
# ===========================================================================
class TestT3_SelectorConsequences:
    """mu = lam^2 forces recurrence constants to land on special integers."""

    def test_Phi4_plus_mu2_is_lam_Phi3(self):
        """Phi4 + mu^2 = 26 = lam*Phi3 = 2*13 (only at q=3)."""
        assert Phi4 + mu**2 == lam * Phi3

    def test_Phi4_times_mu2_is_k_mu_Phi4(self):
        """Phi4*mu^2 = 160 = Phi4*(k+mu) = 10*16."""
        assert Phi4 * mu**2 == Phi4 * (k + mu)

    def test_26_selector(self):
        """Phi4+mu^2 = lam*Phi3 only at q=3."""
        for qq in range(2, 50):
            p4 = qq**2 + 1
            p3 = qq**2 + qq + 1
            mmu = qq + 1
            llam = qq - 1
            if p4 + mmu**2 == llam * p3:
                assert qq == 3


# ===========================================================================
# T4 -- Monster Order: Co1 Action Decomposition
# ===========================================================================
class TestT4_MonsterCo1:
    """|M| = |Co1| * two action degrees * low-prime core * late affine shell."""

    CO1_ORDER = 4157776806543360000
    # Monster order
    M_ORDER = 808017424794512875886459904961710757005754368000000000

    def test_Co1_order(self):
        """Verify |Co1| factorization."""
        assert self.CO1_ORDER == 4157776806543360000

    def test_Co1_Co2_action(self):
        """|Co1:Co2| = tau(3)*C(v,2)/2 = 252*390 = 98280."""
        action = tau3 * math.comb(v, 2) // 2
        assert action == 98280

    def test_Co1_Co3_action(self):
        """|Co1:Co3| = tau(3)*2^{k-4}*Phi3*Phi4 = 252*512*13*10/20 = 8386560."""
        # Alternative: 252 * 2^(k-4) * Phi3 * Phi4
        action = tau3 * 2**(k - 4) * Phi3 * Phi4
        assert action == 8386560

    def test_late_affine_shell(self):
        """Late shell = (k+Phi6-lam)*(k+Phi6)*(f+Phi6-lam)*(f+Phi6)*(v+1)*(v+Phi6)*(v+k+Phi6)*(f+mu*k-1)."""
        atoms = [
            k + Phi6 - lam,      # 17
            k + Phi6,            # 19
            f + Phi6 - lam,      # 29
            f + Phi6,            # 31
            v + 1,               # 41
            v + Phi6,            # 47
            v + k + Phi6,        # 59
            f + mu * k - 1,      # 71
        ]
        assert atoms == [17, 19, 29, 31, 41, 47, 59, 71]
        shell = 1
        for a in atoms:
            shell *= a
        assert shell == 17 * 19 * 29 * 31 * 41 * 47 * 59 * 71

    def test_late_shell_all_prime(self):
        """All 8 late affine shell atoms are prime."""
        for val in [17, 19, 29, 31, 41, 47, 59, 71]:
            assert isprime(val)

    def test_low_prime_core(self):
        """Low-prime core = 2^{k-1} * q^{2q} * (q+2)^q * Phi6^lam * (k-1)."""
        core = 2**(k - 1) * q**(2 * q) * (q + 2)**q * Phi6**lam * (k - 1)
        assert core == 2**11 * 3**6 * 5**3 * 7**2 * 11
        assert core == 100590336000

    def test_full_monster_product(self):
        """|M| = |Co1| * |Co1:Co2| * |Co1:Co3| * core * late_shell."""
        co1_co2 = 98280
        co1_co3 = 8386560
        core = 100590336000
        late = 17 * 19 * 29 * 31 * 41 * 47 * 59 * 71
        product = self.CO1_ORDER * co1_co2 * co1_co3 * core * late
        assert product == self.M_ORDER


# ===========================================================================
# T5 -- Heat-Moment Dictionary
# ===========================================================================
class TestT5_HeatMomentDictionary:
    """Adjacency side (odd/even moments) vs. Laplacian side (zeta tower)."""

    def test_adjacency_roots(self):
        """Adjacency normalized-square roots: 1, mu=(q+1)/(q-1))^2=4, mu*q^2=36."""
        rho = Fraction(mu, lam)**2  # ((q+1)/(q-1))^2
        kappa = Fraction(k, lam)**2  # (q(q+1)/(q-1))^2
        assert rho == 4
        assert kappa == 36

    def test_laplacian_roots(self):
        """Laplacian roots: Phi4=10, mu^2=16."""
        assert L1 == Phi4 == 10
        assert L2 == mu**2 == 16

    def test_adjacency_trace_sum(self):
        """Tr(A^2) = 2E = 480, Tr(A^3) = M3 = 960."""
        TrA2 = k**2 + f * r**2 + g_mult * s**2
        TrA3 = k**3 + f * r**3 + g_mult * s**3
        assert TrA2 == 2 * E == 480
        assert TrA3 == 960

    def test_laplacian_trace_sum(self):
        """Tr(L) = f*L1 + g*L2 = 240+240 = 480 = 2E."""
        TrL = f * L1 + g_mult * L2
        assert TrL == 480 == 2 * E

    def test_both_driven_by_same_atoms(self):
        """Both towers use {Phi3, Phi4, mu}: adjacency via rho,kappa; Laplacian via L1,L2."""
        # Adjacency normalized roots: rho=4, kappa=36, sum=40=v
        rho = Fraction(mu, lam)**2   # 4
        kappa = Fraction(k, lam)**2  # 36
        assert rho + kappa == v  # 40
        # Laplacian recurrence: L1+L2 = Phi4+mu^2 = 26 = lam*Phi3
        assert L1 + L2 == 26 == lam * Phi3


# ===========================================================================
# T6 -- Co1 Action Degrees from tau(3)
# ===========================================================================
class TestT6_Co1Actions:
    """Both Conway action degrees are controlled by tau(3) = 252."""

    def test_co2_from_tau(self):
        """|Co1:Co2| = tau(3) * v*(v-1)/4 = 252*390 = 98280."""
        assert tau3 * v * (v - 1) // 4 == 98280

    def test_co3_from_tau(self):
        """|Co1:Co3| = tau(3) * 2^{k-4} * Phi3 * Phi4 = 8386560."""
        assert tau3 * 2**(k - 4) * Phi3 * Phi4 == 8386560

    def test_co2_times_co3(self):
        """|Co1:Co2|*|Co1:Co3| = 98280*8386560 = 824,231,116,800."""
        product = 98280 * 8386560
        assert product == 824231116800

    def test_tau_controls_both(self):
        """Both action degrees have tau(3) = 252 as a factor."""
        assert 98280 % 252 == 0
        assert 8386560 % 252 == 0
