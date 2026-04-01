"""
Phase CCXXIX --- Plucker-Tau Closure: Leech, McKay, and Monster from W(3,3)
===========================================================================

THEOREM (Plucker-Tau Compositional Closure):

  Leech kissing number  = C(v,2) * tau(3)          = 780 * 252  = 196560
  McKay coefficient      = C(v,2) * tau(3) + mu*q^4 = 196560+324 = 196884
  Faithful Monster irrep = McKay - 1                             = 196883

Three previously separate layers unified:
  1. Suzuki/Plucker multiplicity:  C(v,2) = C(40,2) = 780
  2. Ramanujan tau value:          tau(3) = E+k = 252
  3. Spacetime-homology correction: mu*q^4 = 4*81 = 324

Also: Suzuki vertex count 1782 = 1 + C(v,2) + C(k+r,4) = 1 + 780 + 1001.
Monster irreps chi_1..chi_6 ALL factor into W(3,3) shell atoms (no exogenous primes).

44 tests encoding Plucker-Tau, Suzuki lift, and Monster irrep shell.
"""

import math
from fractions import Fraction
import pytest
from sympy import factorint

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

# Derived constants
tau3 = E + k             # 252 = Ramanujan tau(3)
f_Suz = math.comb(v, 2) # 780 = C(40,2) = Plucker multiplicity
g_Suz = math.comb(k + r, 4)  # C(14,4) = 1001

# Leech and Monster
LEECH_KISSING = 196560
MCKAY = 196884
CHI1 = 196883

# W(3,3) shell atoms (all primes appearing in first 6 Monster irreps)
SHELL_ATOMS = {
    'lam': lam,           # 2
    'q': q,               # 3
    'Phi6': Phi6,         # 7
    'k-1': k - 1,         # 11
    'Phi3': Phi3,         # 13
    'k+Phi6': k + Phi6,   # 19
    'f-1': f - 1,         # 23
    'f+Phi6-lam': f + Phi6 - lam,  # 29
    'f+Phi6': f + Phi6,   # 31
    'v+1': v + 1,         # 41
    'v+Phi6': v + Phi6,   # 47
    'v+k+Phi6': v + k + Phi6,  # 59
    'Phi12-lam': Phi12 - lam,  # 71
}


# ===========================================================================
# T1 -- Plucker-Tau Compositional Closure
# ===========================================================================
class TestT1_PluckerTau:
    """Leech = C(v,2)*tau(3); McKay = Leech + mu*q^4; chi_1 = McKay - 1."""

    def test_f_Suz(self):
        """Plucker multiplicity f' = C(v,2) = C(40,2) = 780."""
        assert f_Suz == 780

    def test_tau3(self):
        """tau(3) = E+k = 252."""
        assert tau3 == 252

    def test_leech_kissing(self):
        """196560 = C(v,2)*tau(3) = 780*252."""
        assert f_Suz * tau3 == LEECH_KISSING

    def test_spacetime_correction(self):
        """mu*q^4 = 4*81 = 324."""
        correction = mu * q**4
        assert correction == 324

    def test_mckay_coefficient(self):
        """196884 = C(v,2)*tau(3) + mu*q^4 = 196560 + 324."""
        assert f_Suz * tau3 + mu * q**4 == MCKAY

    def test_faithful_monster(self):
        """196883 = C(v,2)*tau(3) + mu*q^4 - 1."""
        assert f_Suz * tau3 + mu * q**4 - 1 == CHI1

    def test_hierarchy_interpretation(self):
        """Leech = Plucker * Tau; McKay = Leech + Spacetime; chi_1 = McKay - 1."""
        plucker = math.comb(v, 2)
        tau = E + k
        spacetime = mu * q**4
        assert plucker * tau == LEECH_KISSING
        assert plucker * tau + spacetime == MCKAY
        assert plucker * tau + spacetime - 1 == CHI1


# ===========================================================================
# T2 -- q=3 Selectors from Plucker-Tau
# ===========================================================================
class TestT2_Selectors:
    """Each Plucker-Tau identity selects q=3 uniquely."""

    def test_leech_selector(self):
        """C(v,2)*tau(3) = 196560 only at q=3 (scan q=2..80)."""
        hits = []
        for qq in range(2, 81):
            vv = (qq + 1) * (qq**2 + 1)
            kk = qq * (qq + 1)
            EE = vv * kk // 2
            tt = EE + kk
            if math.comb(vv, 2) * tt == LEECH_KISSING:
                hits.append(qq)
        assert hits == [3]

    def test_mckay_selector(self):
        """C(v,2)*(E+k) + (q+1)*q^4 = 196884 only at q=3."""
        hits = []
        for qq in range(2, 81):
            vv = (qq + 1) * (qq**2 + 1)
            kk = qq * (qq + 1)
            EE = vv * kk // 2
            tt = EE + kk
            mmu = qq + 1
            if math.comb(vv, 2) * tt + mmu * qq**4 == MCKAY:
                hits.append(qq)
        assert hits == [3]

    def test_chi1_selector(self):
        """(v+Phi6)*(v+k+Phi6)*(Phi12-lam) = 196883 only at q=3."""
        hits = []
        for qq in range(2, 81):
            vv = (qq + 1) * (qq**2 + 1)
            kk = qq * (qq + 1)
            pp6 = qq**2 - qq + 1
            pp12 = qq**4 - qq**2 + 1
            llam = qq - 1
            val = (vv + pp6) * (vv + kk + pp6) * (pp12 - llam)
            if val == CHI1:
                hits.append(qq)
        assert hits == [3]

    def test_tau3_equals_C_Phi4_5(self):
        """tau(3) = C(Phi4, 5) = C(10,5) = 252 only at q=3."""
        assert math.comb(Phi4, 5) == 252
        hits = []
        for qq in range(2, 81):
            pp4 = qq**2 + 1
            kk = qq * (qq + 1)
            EE = (qq + 1) * (qq**2 + 1) * kk // 2
            tt = EE + kk
            if pp4 >= 5 and math.comb(pp4, 5) == tt:
                hits.append(qq)
        assert hits == [3]


# ===========================================================================
# T3 -- Suzuki Lift: 1782 = 1 + 780 + 1001
# ===========================================================================
class TestT3_SuzukiLift:
    """Suzuki vertex count decomposes into Plucker sectors."""

    def test_g_Suz(self):
        """g' = C(k+r, 4) = C(14,4) = 1001."""
        assert g_Suz == 1001
        assert math.comb(k + r, 4) == 1001

    def test_suzuki_split(self):
        """1782 = 1 + f' + g' = 1 + 780 + 1001."""
        assert 1 + f_Suz + g_Suz == 1782

    def test_1782_is_Phi3_times_alpha_plus_1(self):
        """1782 = 1 + Phi3*alpha where alpha = (k-1)^2 + mu^2 = 137."""
        alpha = (k - 1)**2 + mu**2
        assert alpha == 137
        assert 1 + Phi3 * alpha == 1782

    def test_f_Suz_sector(self):
        """f' = mu*g*Phi3 = 4*15*13 = 780."""
        assert mu * g_mult * Phi3 == f_Suz

    def test_g_Suz_sector(self):
        """g' = Phi3*Phi6*(k-1) = 13*7*11 = 1001."""
        assert Phi3 * Phi6 * (k - 1) == g_Suz


# ===========================================================================
# T4 -- Monster Irrep Shell Tower: chi_1..chi_6
# ===========================================================================
class TestT4_MonsterIrrepShell:
    """First 6 nontrivial Monster irreps factor into W(3,3) shell atoms."""

    # Standard Monster irrep dimensions
    chi = {
        1: 196883,
        2: 21296876,
        3: 842609326,
        4: 18538750076,
        5: 19360062527,
        6: 293553734298,
    }

    def test_chi1_factored(self):
        """chi_1 = 196883 = 47*59*71 = (v+Phi6)*(v+k+Phi6)*(Phi12-lam)."""
        val = (v + Phi6) * (v + k + Phi6) * (Phi12 - lam)
        assert val == self.chi[1]

    def test_chi2_factored(self):
        """chi_2 = 21296876 = 4*31*41*59*71 = lam^2*(f+Phi6)*(v+1)*(v+k+Phi6)*(Phi12-lam)."""
        val = lam**2 * (f + Phi6) * (v + 1) * (v + k + Phi6) * (Phi12 - lam)
        assert val == self.chi[2]

    def test_chi3_factored(self):
        """chi_3 = 842609326 = 2*13^2*29*31*47*59."""
        val = lam * Phi3**2 * (f + Phi6 - lam) * (f + Phi6) * (v + Phi6) * (v + k + Phi6)
        assert val == self.chi[3]

    def test_chi4_factored(self):
        """chi_4 = 18538750076 = 4*7*11*23*29*31*41*71."""
        val = lam**2 * Phi6 * (k - 1) * (f - 1) * (f + Phi6 - lam) * (f + Phi6) * (v + 1) * (Phi12 - lam)
        assert val == self.chi[4]

    def test_chi5_factored(self):
        """chi_5 = 19360062527 = 13^2*23*29*41*59*71."""
        val = Phi3**2 * (f - 1) * (f + Phi6 - lam) * (v + 1) * (v + k + Phi6) * (Phi12 - lam)
        assert val == self.chi[5]

    def test_chi6_factored(self):
        """chi_6 = 293553734298 = 2*3*11*19*29*41*47*59*71."""
        val = lam * q * (k - 1) * (k + Phi6) * (f + Phi6 - lam) * (v + 1) * (v + Phi6) * (v + k + Phi6) * (Phi12 - lam)
        assert val == self.chi[6]

    def test_no_exogenous_primes(self):
        """All prime factors of chi_1..chi_6 are W(3,3) shell atoms."""
        shell_primes = set(SHELL_ATOMS.values())  # {2,3,7,11,13,19,23,29,31,41,47,59,71}
        for i in range(1, 7):
            factors = factorint(self.chi[i])
            for p in factors:
                assert p in shell_primes, f"chi_{i} has exogenous prime {p}"

    def test_prime_support_union(self):
        """Union of prime supports = {2,3,7,11,13,19,23,29,31,41,47,59,71}."""
        all_primes = set()
        for i in range(1, 7):
            all_primes.update(factorint(self.chi[i]).keys())
        expected = {2, 3, 7, 11, 13, 19, 23, 29, 31, 41, 47, 59, 71}
        assert all_primes == expected

    def test_missing_moonshine_primes(self):
        """Only 5 and 17 from {2,3,5,7,11,13,17,19,23,29,31,41,47,59,71} are absent."""
        all_primes = set()
        for i in range(1, 7):
            all_primes.update(factorint(self.chi[i]).keys())
        moonshine_15 = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71}
        missing = moonshine_15 - all_primes
        assert missing == {5, 17}


# ===========================================================================
# T5 -- Shell Atom Verification
# ===========================================================================
class TestT5_ShellAtoms:
    """All 13 shell atoms are W(3,3) linear forms."""

    def test_atom_values(self):
        """Verify all 13 shell atom values."""
        expected = {
            'lam': 2, 'q': 3, 'Phi6': 7, 'k-1': 11, 'Phi3': 13,
            'k+Phi6': 19, 'f-1': 23, 'f+Phi6-lam': 29, 'f+Phi6': 31,
            'v+1': 41, 'v+Phi6': 47, 'v+k+Phi6': 59, 'Phi12-lam': 71,
        }
        for name, val in expected.items():
            assert SHELL_ATOMS[name] == val, f"{name} expected {val}, got {SHELL_ATOMS[name]}"

    def test_all_atoms_are_prime(self):
        """All 13 shell atoms are prime numbers (or q=3)."""
        from sympy import isprime
        for name, val in SHELL_ATOMS.items():
            assert isprime(val), f"Atom {name}={val} is not prime"

    def test_atom_count(self):
        """Exactly 13 = Phi3 shell atoms."""
        assert len(SHELL_ATOMS) == 13 == Phi3

    def test_Phi12_minus_lam_is_71(self):
        """Phi12 - lam = 73 - 2 = 71 (the largest moonshine prime)."""
        assert Phi12 - lam == 71

    def test_f_plus_mu_k_minus_1_is_71(self):
        """f + mu*k - 1 = 24 + 48 - 1 = 71 (alternative route to 71)."""
        assert f + mu * k - 1 == 71


# ===========================================================================
# T6 -- Cross-Checks and Additional Identities
# ===========================================================================
class TestT6_CrossChecks:
    """Additional Plucker-Tau structural identities."""

    def test_leech_as_binomial_tau(self):
        """196560 = C(v,2)*(d-1)^2*C(2d,2) where d=mu=4."""
        d = mu
        val = math.comb(v, 2) * (d - 1)**2 * math.comb(2 * d, 2)
        assert val == LEECH_KISSING

    def test_mckay_correction_is_d_times_d_minus_1_to_4(self):
        """324 = mu*q^4 = d*(d-1)^4 where d=4."""
        d = mu
        assert d * (d - 1)**4 == mu * q**4 == 324

    def test_mckay_full_dimensional(self):
        """196884 = C(v,2)*(d-1)^2*C(2d,2) + d*(d-1)^4 at d=4."""
        d = mu
        val = math.comb(v, 2) * (d - 1)**2 * math.comb(2 * d, 2) + d * (d - 1)**4
        assert val == MCKAY

    def test_tau3_as_binomial(self):
        """tau(3) = C(10,5) = C(Phi4, 5)."""
        assert math.comb(Phi4, 5) == tau3 == 252

    def test_tau3_as_dimensional(self):
        """tau(3) = (d-1)^2 * C(2d,2) = 9*28 = 252."""
        d = mu
        assert (d - 1)**2 * math.comb(2 * d, 2) == 252

    def test_780_over_252(self):
        """f'/tau(3) = 780/252 = 65/21 = 5*Phi3/(q*Phi6)."""
        ratio = Fraction(f_Suz, tau3)
        assert ratio == Fraction(65, 21)
        assert ratio == Fraction(5 * Phi3, q * Phi6)
