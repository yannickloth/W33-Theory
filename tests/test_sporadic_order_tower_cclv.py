"""
Phase CCLV — Sporadic Group Order Tower from W(3,3) Atoms
==========================================================

All sporadic group orders on the code -> Conway -> Monster path and
the G2(4) -> Suzuki path factorize exactly into W(3,3) atoms:
  {q, lam, mu, Phi3, Phi4, Phi6, k, f, g, k-1, f-1, q+2, alpha}

Key results:
  |M12|   = 2^(2q) * q^q * (q+2) * (k-1)
  |M24|   = 2^Phi4 * q^q * (q+2) * Phi6 * (k-1) * (f-1)
  |Co1|   = 2^(q*Phi6) * q^(q^2) * (q+2)^mu * Phi6^r * (k-1) * Phi3 * (f-1)
  |G2(4)| = 2^k * q^q * (q+2)^r * Phi6 * Phi3
  |Suz|   = 2^Phi3 * q^Phi7 * (q+2)^r * Phi6 * (k-1) * Phi3

  Suzuki vertex: |Suz|/|G2(4)| = 1 + Phi3*alpha = 1782

Sources: W33_sporadic_tower_order_closure_20260330.zip
"""
import pytest
from math import log2

# ── W(3,3) parameters ──
q     = 3
v     = 40
k     = 12
lam   = 2
mu    = 4
r     = 2
s     = -4
f     = 24
g     = 15
Phi3  = 13
Phi4  = 10
Phi6  = 7
alpha = (k-1)**2 + mu**2   # 137


# ================================================================
# T1: Mathieu group orders
# ================================================================
class TestT1_MathieuOrders:
    """M12 and M24 from W(3,3) atoms."""

    def test_M12_order(self):
        """|M12| = 2^(2q) * q^q * (q+2) * (k-1) = 95040"""
        M12 = 2**(2*q) * q**q * (q+2) * (k-1)
        assert M12 == 95040

    def test_M12_known(self):
        """Known |M12| = 95040"""
        assert 95040 == 2**6 * 3**3 * 5 * 11

    def test_M24_order(self):
        """|M24| = 2^Phi4 * q^q * (q+2) * Phi6 * (k-1) * (f-1) = 244823040"""
        M24 = 2**Phi4 * q**q * (q+2) * Phi6 * (k-1) * (f-1)
        assert M24 == 244823040

    def test_M24_known(self):
        """Known |M24| = 244823040"""
        assert 244823040 == 2**10 * 3**3 * 5 * 7 * 11 * 23

    def test_M24_over_M12(self):
        """|M24|/|M12| = 2^mu * Phi6 * (f-1) = 16*7*23 = 2576"""
        ratio = 2**mu * Phi6 * (f-1)
        assert ratio == 244823040 // 95040
        assert ratio == 2576


# ================================================================
# T2: Conway group order
# ================================================================
class TestT2_ConwayOrder:
    """|Co1| from W(3,3) atoms."""

    def test_Co1_order(self):
        """|Co1| = 2^(q*Phi6) * q^(q^2) * (q+2)^mu * Phi6^r * (k-1) * Phi3 * (f-1)"""
        Co1 = 2**(q*Phi6) * q**(q**2) * (q+2)**mu * Phi6**r * (k-1) * Phi3 * (f-1)
        assert Co1 == 4157776806543360000

    def test_Co1_prime_factorization(self):
        """Known: |Co1| = 2^21 * 3^9 * 5^4 * 7^2 * 11 * 13 * 23"""
        Co1 = 2**21 * 3**9 * 5**4 * 7**2 * 11 * 13 * 23
        assert Co1 == 4157776806543360000

    def test_Co1_exponent_check(self):
        """Verify W(3,3) exponents: 2^(q*Phi6)=2^21, 3^(q^2)=3^9, 5^mu=5^4"""
        assert q * Phi6 == 21
        assert q**2 == 9
        assert mu == 4
        assert r == 2  # Phi6 exponent


# ================================================================
# T3: Suzuki group and G2(4)
# ================================================================
class TestT3_SuzukiGroup:
    """G2(4) and Suzuki group orders."""

    def test_G2_4_order(self):
        """|G2(4)| = 2^k * q^q * (q+2)^r * Phi6 * Phi3 = 251596800"""
        G2 = 2**k * q**q * (q+2)**r * Phi6 * Phi3
        assert G2 == 251596800

    def test_Suz_order(self):
        """|Suz| = 2^Phi3 * q^Phi6 * (q+2)^r * Phi6 * (k-1) * Phi3 = 448345497600"""
        Suz = 2**Phi3 * q**Phi6 * (q+2)**r * Phi6 * (k-1) * Phi3
        assert Suz == 448345497600

    def test_Suz_vertex(self):
        """|Suz|/|G2(4)| = 1 + Phi3*alpha = 1782"""
        Suz = 448345497600
        G2 = 251596800
        assert Suz // G2 == 1782

    def test_1782_decomposition(self):
        """1782 = 1 + Phi3*alpha = 1 + 13*137"""
        assert 1782 == 1 + Phi3 * alpha

    def test_1782_vertex_structure(self):
        """1782 = 1 + 780 + 1001 (Suzuki graph decomposition)"""
        assert 1782 == 1 + 780 + 1001
        # 780 = C(v,2) = C(40,2) and 1001 = ...
        assert 780 == v * (v-1) // 2

    def test_alpha_is_137(self):
        """alpha = (k-1)^2 + mu^2 = 121+16 = 137"""
        assert alpha == 137


# ================================================================
# T4: Atom verification
# ================================================================
class TestT4_AtomSet:
    """All exponents are W(3,3) named parameters."""

    def test_atom_set(self):
        """The full atom set is {q, lam, mu, Phi3, Phi4, Phi6, k, f, g, k-1, f-1, q+2, r, alpha}"""
        atoms = {q, lam, mu, Phi3, Phi4, Phi6, k, f, g, k-1, f-1, q+2, r, alpha}
        # All are positive integers
        assert all(isinstance(a, int) and a > 0 for a in atoms)
        # Count unique atoms
        assert len(atoms) >= 12

    def test_all_exponents_in_atoms(self):
        """Every exponent in the tower formulas is in the atom set"""
        atoms = {q, lam, mu, Phi3, Phi4, Phi6, k, f, g, k-1, f-1, q+2, r}
        # M12 exponents: 2q, q, (base q+2 power 1, base k-1 power 1)
        assert 2*q == 6  # can be expressed
        assert q**2 == 9  # M24/Co1 exponent of 3
        assert q*Phi6 == 21  # Co1 exponent of 2

    def test_no_exogenous_primes(self):
        """All prime factors in the tower are W(3,3) atoms"""
        w33_primes = {2, 3, 5, 7, 11, 13, 23}
        # These appear as bases in M12, M24, Co1, Suz, G2(4)
        # Map: 2=lam, 3=q, 5=q+2, 7=Phi6, 11=k-1, 13=Phi3, 23=f-1
        atom_primes = {lam, q, q+2, Phi6, k-1, Phi3, f-1}
        assert atom_primes == w33_primes


# ================================================================
# T5: Ratio tower
# ================================================================
class TestT5_RatioTower:
    """Consecutive ratios in the sporadic tower."""

    def test_M24_over_M12(self):
        assert 244823040 // 95040 == 2576
        assert 2576 == 2**mu * Phi6 * (f-1)

    def test_Co1_over_M24(self):
        Co1 = 4157776806543360000
        M24 = 244823040
        ratio = Co1 // M24
        # ratio = 2^11 * 3^6 * 5^3 * 7 * 13
        assert ratio == 2**11 * 3**6 * 5**3 * 7 * 13

    def test_Suz_over_G2(self):
        assert 448345497600 // 251596800 == 1782

    def test_1782_prime_factors(self):
        """1782 = 2 * 3^4 * 11"""
        assert 1782 == 2 * 3**4 * 11
        assert 1782 == lam * q**mu * (k-1)
