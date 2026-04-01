"""
Phase CCLXXIV — Dual Cyclotomic Ladder and Fermat Bridge
==========================================================

THEOREM (Dual Cyclotomic Identity):

For the GQ(q,q) family with μ = q+1:
  Φ₁(μ) = q       Φ₂(μ) = q+2       Φ₆(μ) = Φ₃(q)

At q=3, μ=4:
  Φ₂(4) = 5,  Φ₄(4) = 17,  Φ₆(4) = 13 = Φ₃(3)

So the two "analytic" primes {5, 17} and the bridge prime 13 are generated
by the μ-channel cyclotomic evaluations.

THEOREM (H-Projector Fermat Ladder):

The H-projector H_t = −(1 + 4^(t+1)) enumerates exact values:
  −H₀ = 5 = Φ₂(4)       (first Fermat prime)
  −H₁ = 17 = Φ₄(4)      (second Fermat prime)
  −H₂ = 65 = 5·13
  −H₃ = 257 = Φ₈(4)     (third Fermat prime)

Along t = 2^m − 1, this is the Fermat ladder: 4^(2^m) + 1 = Φ_{2^(m+1)}(4).

SOURCE: W33_dual_cyclotomic_ladder_20260330.zip
"""
import pytest
from sympy import cyclotomic_poly, Symbol

# ── W(3,3) parameters ──
q    = 3
mu   = q + 1   # 4
lam  = q - 1   # 2
Phi3 = q**2 + q + 1  # 13


# ================================================================
# T1: Family cyclotomic identities
# ================================================================
class TestT1_FamilyIdentities:
    """Φ₁(μ)=q, Φ₂(μ)=q+2, Φ₆(μ)=Φ₃(q)."""

    def test_Phi1_mu(self):
        """Φ₁(μ) = μ−1 = q."""
        assert mu - 1 == q

    def test_Phi2_mu(self):
        """Φ₂(μ) = μ+1 = q+2."""
        assert mu + 1 == q + 2 == 5

    def test_Phi6_mu_equals_Phi3_q(self):
        """Φ₆(μ) = μ²−μ+1 = 13 = Φ₃(q)."""
        assert mu**2 - mu + 1 == Phi3

    def test_self_reference(self):
        """The bridge prime 13 is Φ₆(4) = Φ₃(3)."""
        assert mu**2 - mu + 1 == q**2 + q + 1 == 13


# ================================================================
# T2: Analytic primes from μ-channel
# ================================================================
class TestT2_AnalyticPrimes:
    """5 and 17 come from cyclotomic evaluations at μ=4."""

    def test_5_is_Phi2_4(self):
        assert mu + 1 == 5

    def test_17_is_Phi4_4(self):
        assert mu**2 + 1 == 17

    def test_13_is_Phi6_4(self):
        assert mu**2 - mu + 1 == 13


# ================================================================
# T3: H-projector sequence
# ================================================================
class TestT3_HProjector:
    """H_t = −(1 + 4^(t+1))."""

    def _H(self, t):
        return -(1 + 4**(t + 1))

    def test_H0(self):
        assert -self._H(0) == 5

    def test_H1(self):
        assert -self._H(1) == 17

    def test_H2(self):
        assert -self._H(2) == 65
        assert 65 == 5 * 13

    def test_H3(self):
        assert -self._H(3) == 257

    def test_H4(self):
        assert -self._H(4) == 1025
        assert 1025 == 5**2 * 41

    def test_H5(self):
        assert -self._H(5) == 4097
        assert 4097 == 17 * 241


# ================================================================
# T4: Fermat ladder
# ================================================================
class TestT4_FermatLadder:
    """Along t = 2^m − 1, get Fermat numbers F_m = 4^(2^m) + 1."""

    def test_F0(self):
        """t=0: 4^1 + 1 = 5 (Fermat prime F₀)."""
        assert 4**(2**0) + 1 == 5

    def test_F1(self):
        """t=1: 4^2 + 1 = 17 (Fermat prime F₁)."""
        assert 4**(2**1) + 1 == 17

    def test_F2(self):
        """t=3: 4^4 + 1 = 257 (Fermat prime F₂)."""
        assert 4**(2**2) + 1 == 257

    def test_F3(self):
        """t=7: 4^8 + 1 = 65537 (Fermat prime F₃)."""
        assert 4**(2**3) + 1 == 65537


# ================================================================
# T5: Selectors vanish at q=3
# ================================================================
class TestT5_Selectors:
    def test_Phi2_selector(self):
        """Φ₂(μ) − 5 = q − 3."""
        assert (mu + 1) - 5 == q - 3 == 0

    def test_Phi4_selector(self):
        """Φ₄(μ) − 17 = (q−3)(q+5)."""
        assert (mu**2 + 1) - 17 == (q - 3) * (q + 5)

    def test_Phi6_selector(self):
        """Φ₆(μ) − 13 = (q−3)(q+4)."""
        assert (mu**2 - mu + 1) - 13 == (q - 3) * (q + 4)
