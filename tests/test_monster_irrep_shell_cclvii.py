"""
Phase CCLVII — Monster Irrep Shell Tower from 13 W(3,3) Atoms
================================================================

The first 6 nontrivial Monster irrep dimensions chi_1..chi_6 all
factorize into exactly 13 W(3,3) shell atoms. No exogenous primes.

Shell atoms: {2,3,7,11,13,19,23,29,31,41,47,59,71}
= {lam, q, Phi6, k-1, Phi3, k+Phi6, f-1, f+Phi6-lam, f+Phi6, v+1, v+Phi6, v+k+Phi6, Phi12-lam}

chi_1 = 196883  = (v+Phi6)(v+k+Phi6)(Phi12-lam)
chi_2 = 21296876 = lam^2*(f+Phi6)*(v+1)*(v+k+Phi6)*(Phi12-lam)
chi_3 = 842609326 = lam*Phi3^2*(f+Phi6-lam)*(f+Phi6)*(v+Phi6)*(v+k+Phi6)
chi_4 = 18538750076 = lam^2*Phi6*(k-1)*(f-1)*(f+Phi6-lam)*(f+Phi6)*(v+1)*(Phi12-lam)
chi_5 = 19360062527 = Phi3^2*(f-1)*(f+Phi6-lam)*(v+1)*(v+k+Phi6)*(Phi12-lam)
chi_6 = 293553734298 = lam*q*(k-1)*(k+Phi6)*(f+Phi6-lam)*(v+1)*(v+Phi6)*(v+k+Phi6)*(Phi12-lam)

Sources: W33_irrep_shell_tower_20260330.zip
"""
import pytest

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
f    = 24
g    = 15
Phi3 = 13
Phi4 = 10
Phi6 = 7
Phi12 = q**4 - q**2 + 1  # 73

# ── 13 shell atoms ──
ATOMS = {
    'lam':         lam,          # 2
    'q':           q,            # 3
    'Phi6':        Phi6,         # 7
    'k-1':         k - 1,        # 11
    'Phi3':        Phi3,         # 13
    'k+Phi6':      k + Phi6,     # 19
    'f-1':         f - 1,        # 23
    'f+Phi6-lam':  f + Phi6 - lam,  # 29
    'f+Phi6':      f + Phi6,     # 31
    'v+1':         v + 1,        # 41
    'v+Phi6':      v + Phi6,     # 47
    'v+k+Phi6':    v + k + Phi6, # 59
    'Phi12-lam':   Phi12 - lam,  # 71
}

# ── Monster irrep dimensions (first 6 nontrivial) ──
chi = {
    1: 196883,
    2: 21296876,
    3: 842609326,
    4: 18538750076,
    5: 19360062527,
    6: 293553734298,
}


# ================================================================
# T1: Shell atom verification
# ================================================================
class TestT1_ShellAtoms:
    """All 13 shell atoms are W(3,3) parameter expressions."""

    def test_atom_count(self):
        assert len(ATOMS) == 13

    def test_atom_values(self):
        expected = {2, 3, 7, 11, 13, 19, 23, 29, 31, 41, 47, 59, 71}
        assert set(ATOMS.values()) == expected

    def test_all_atoms_prime(self):
        """All 13 atoms are prime numbers"""
        for name, val in ATOMS.items():
            assert val > 1
            assert all(val % d != 0 for d in range(2, int(val**0.5) + 1)), f"{name}={val} not prime"


# ================================================================
# T2: chi_1 = 196883
# ================================================================
class TestT2_Chi1:
    """chi_1 = 196883 = 47*59*71."""

    def test_value(self):
        assert chi[1] == 196883

    def test_shell_formula(self):
        """chi_1 = (v+Phi6)*(v+k+Phi6)*(Phi12-lam)"""
        val = (v + Phi6) * (v + k + Phi6) * (Phi12 - lam)
        assert val == chi[1]

    def test_prime_factors(self):
        """196883 = 47*59*71"""
        assert 47 * 59 * 71 == chi[1]


# ================================================================
# T3: chi_2 = 21296876
# ================================================================
class TestT3_Chi2:
    """chi_2 = 21296876 = 4*31*41*59*71."""

    def test_value(self):
        assert chi[2] == 21296876

    def test_shell_formula(self):
        """chi_2 = lam^2*(f+Phi6)*(v+1)*(v+k+Phi6)*(Phi12-lam)"""
        val = lam**2 * (f + Phi6) * (v + 1) * (v + k + Phi6) * (Phi12 - lam)
        assert val == chi[2]

    def test_prime_factors(self):
        assert 4 * 31 * 41 * 59 * 71 == chi[2]


# ================================================================
# T4: chi_3 = 842609326
# ================================================================
class TestT4_Chi3:
    """chi_3 = 842609326 = 2*169*29*31*47*59."""

    def test_value(self):
        assert chi[3] == 842609326

    def test_shell_formula(self):
        """chi_3 = lam*Phi3^2*(f+Phi6-lam)*(f+Phi6)*(v+Phi6)*(v+k+Phi6)"""
        val = lam * Phi3**2 * (f + Phi6 - lam) * (f + Phi6) * (v + Phi6) * (v + k + Phi6)
        assert val == chi[3]


# ================================================================
# T5: chi_4 = 18538750076
# ================================================================
class TestT5_Chi4:
    """chi_4 = 18538750076."""

    def test_value(self):
        assert chi[4] == 18538750076

    def test_shell_formula(self):
        """chi_4 = lam^2*Phi6*(k-1)*(f-1)*(f+Phi6-lam)*(f+Phi6)*(v+1)*(Phi12-lam)"""
        val = lam**2 * Phi6 * (k-1) * (f-1) * (f+Phi6-lam) * (f+Phi6) * (v+1) * (Phi12-lam)
        assert val == chi[4]


# ================================================================
# T6: chi_5 = 19360062527
# ================================================================
class TestT6_Chi5:
    """chi_5 = 19360062527."""

    def test_value(self):
        assert chi[5] == 19360062527

    def test_shell_formula(self):
        """chi_5 = Phi3^2*(f-1)*(f+Phi6-lam)*(v+1)*(v+k+Phi6)*(Phi12-lam)"""
        val = Phi3**2 * (f-1) * (f+Phi6-lam) * (v+1) * (v+k+Phi6) * (Phi12-lam)
        assert val == chi[5]


# ================================================================
# T7: chi_6 = 293553734298
# ================================================================
class TestT7_Chi6:
    """chi_6 = 293553734298."""

    def test_value(self):
        assert chi[6] == 293553734298

    def test_shell_formula(self):
        """chi_6 = lam*q*(k-1)*(k+Phi6)*(f+Phi6-lam)*(v+1)*(v+Phi6)*(v+k+Phi6)*(Phi12-lam)"""
        val = lam * q * (k-1) * (k+Phi6) * (f+Phi6-lam) * (v+1) * (v+Phi6) * (v+k+Phi6) * (Phi12-lam)
        assert val == chi[6]


# ================================================================
# T8: No exogenous primes
# ================================================================
class TestT8_NoExogenousPrimes:
    """All prime factors of chi_1..chi_6 are shell atoms."""

    def _prime_factors(self, n):
        factors = set()
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.add(d)
                n //= d
            d += 1
        if n > 1:
            factors.add(n)
        return factors

    def test_chi1_primes_in_atoms(self):
        assert self._prime_factors(chi[1]).issubset(set(ATOMS.values()))

    def test_chi2_primes_in_atoms(self):
        assert self._prime_factors(chi[2]).issubset(set(ATOMS.values()))

    def test_chi3_primes_in_atoms(self):
        assert self._prime_factors(chi[3]).issubset(set(ATOMS.values()))

    def test_chi4_primes_in_atoms(self):
        assert self._prime_factors(chi[4]).issubset(set(ATOMS.values()))

    def test_chi5_primes_in_atoms(self):
        assert self._prime_factors(chi[5]).issubset(set(ATOMS.values()))

    def test_chi6_primes_in_atoms(self):
        assert self._prime_factors(chi[6]).issubset(set(ATOMS.values()))

    def test_union_of_all_primes(self):
        """Union of all prime factors = the 13 shell atoms"""
        all_primes = set()
        for i in range(1, 7):
            all_primes |= self._prime_factors(chi[i])
        assert all_primes == set(ATOMS.values())


# ================================================================
# T9: Shell atom origin expressions
# ================================================================
class TestT9_AtomOrigins:
    """Every atom has a clear W(3,3) parameter origin."""

    def test_2_is_lam(self):
        assert lam == 2

    def test_3_is_q(self):
        assert q == 3

    def test_7_is_Phi6(self):
        assert Phi6 == 7

    def test_11_is_k_minus_1(self):
        assert k - 1 == 11

    def test_13_is_Phi3(self):
        assert Phi3 == 13

    def test_19_is_k_plus_Phi6(self):
        assert k + Phi6 == 19

    def test_23_is_f_minus_1(self):
        assert f - 1 == 23

    def test_29_is_f_plus_Phi6_minus_lam(self):
        assert f + Phi6 - lam == 29

    def test_31_is_f_plus_Phi6(self):
        assert f + Phi6 == 31

    def test_41_is_v_plus_1(self):
        assert v + 1 == 41

    def test_47_is_v_plus_Phi6(self):
        assert v + Phi6 == 47

    def test_59_is_v_plus_k_plus_Phi6(self):
        assert v + k + Phi6 == 59

    def test_71_is_Phi12_minus_lam(self):
        assert Phi12 - lam == 71
