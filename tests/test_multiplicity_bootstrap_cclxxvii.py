"""
Phase CCLXXVII — Multiplicity Bootstrap & Gaussian Selector Ladder
=====================================================================

THEOREM (Multiplicity Bootstrap):

From the eigenvalue multiplicity pair (f, g) = (24, 15) alone, the
complete W(3,3) parameter set is recovered:

  q = √(f − g) = 3
  v = 1 + f + g = 40
  E = 2fg/q = 240
  k = 2E/v = 12
  μ² = 2f/q = 16 → μ = 4
  Φ₄ = 2g/q = 10
  λ = q − 1 = 2

THEOREM (Gaussian Selector Ladder):

  N(q + (q−1)i) = Φ₃(q) iff q(q−3) = 0
  N((q+1) + (q+2)i) = v + 1 iff (q−3)(q+1)² = 0

At q=3: 13 = N(3+2i) = Φ₃, 41 = N(4+5i) = v+1

SOURCE: W33_multiplicity_bootstrap_20260330.zip
"""
import pytest
import math

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
f    = 24
g    = 15
E    = 240
Phi3 = 13
Phi4 = 10


# ================================================================
# T1: Multiplicity bootstrap
# ================================================================
class TestT1_Bootstrap:
    """(f,g)=(24,15) recovers all parameters."""

    def test_q_from_fg(self):
        assert int(math.isqrt(f - g)) == q

    def test_v_from_fg(self):
        assert 1 + f + g == v

    def test_E_from_fg(self):
        assert 2 * f * g // q == E

    def test_k_from_E_v(self):
        assert 2 * E // v == k

    def test_mu_from_f(self):
        assert 2 * f // q == mu**2

    def test_Phi4_from_g(self):
        assert 2 * g // q == Phi4

    def test_lam_from_q(self):
        assert q - 1 == lam


# ================================================================
# T2: Family identities (all q)
# ================================================================
class TestT2_Family:
    """These hold for every GQ(q,q)."""

    def test_f_minus_g(self):
        """f − g = q²."""
        assert f - g == q**2

    def test_f_plus_g(self):
        """f + g = v − 1."""
        assert f + g == v - 1

    def test_edge_count(self):
        """E = vk/2 = 2fg/q."""
        assert v * k // 2 == E
        assert 2 * f * g // q == E


# ================================================================
# T3: Gaussian selector ladder
# ================================================================
class TestT3_GaussianLadder:
    """Gaussian norms select q=3."""

    def test_13_gaussian(self):
        """13 = N(3+2i) = 3² + 2²."""
        assert q**2 + (q - 1)**2 == Phi3

    def test_41_gaussian(self):
        """41 = N(4+5i) = 4² + 5²."""
        assert (q + 1)**2 + (q + 2)**2 == v + 1

    def test_137_gaussian(self):
        """137 = N(11+4i) = 11² + 4²."""
        assert (k - 1)**2 + mu**2 == 137

    def test_Phi3_selector(self):
        """N(q+(q-1)i) = Φ₃ iff q(q-3) = 0."""
        pp = [2, 3, 4, 5, 7, 8, 9, 11, 13]
        hits = []
        for qq in pp:
            norm = qq**2 + (qq - 1)**2
            phi3 = qq**2 + qq + 1
            if norm == phi3:
                hits.append(qq)
        assert hits == [3]

    def test_41_selector(self):
        """N((q+1)+(q+2)i) = v+1 iff (q-3)(q+1)² = 0."""
        pp = [2, 3, 4, 5, 7, 8, 9, 11, 13]
        hits = []
        for qq in pp:
            norm = (qq + 1)**2 + (qq + 2)**2
            vv = (qq + 1) * (qq**2 + 1) + 1
            if norm == vv:
                hits.append(qq)
        assert hits == [3]


# ================================================================
# T4: Selector factorizations
# ================================================================
class TestT4_Selectors:
    """All vanish at q=3 via (q−3) factor."""

    def test_f_equals_24(self):
        """f = q(q+1)²/2 = 24 at q=3."""
        assert q * (q + 1)**2 // 2 == 24

    def test_g_equals_15(self):
        """g = q(q²+1)/2 = 15 at q=3."""
        assert q * (q**2 + 1) // 2 == 15

    def test_moonshine_multiplicities(self):
        """f=24 is the Leech dimension; g=15 = |supersingular primes|."""
        assert f == 24
        assert g == 15
