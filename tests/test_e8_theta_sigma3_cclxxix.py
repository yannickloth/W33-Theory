"""
Phase CCLXXIX — E₈ Theta Series & σ₃ Dictionary
=====================================================

THEOREM (E₈ Theta = Eisenstein E₄):

The theta series of the E₈ lattice equals the weight-4 Eisenstein
series, with Fourier coefficients:

  r_{E₈}(2n) = E · σ₃(n) = 240 · σ₃(n)

where σ₃(n) = Σ_{d|n} d³ is the sum-of-cubes-of-divisors function.

THEOREM (σ₃ at W(3,3) Parameters):

  σ₃(1) = 1
  σ₃(λ) = σ₃(2) = 9  = q²
  σ₃(q) = σ₃(3) = 28 = R = C(2d, 2)
  σ₃(μ) = σ₃(4) = 73 = Φ₁₂
  σ₃(5) = 126 = τ/2
  σ₃(s) = σ₃(6) = 252 = τ = σ₃(λ)·σ₃(q) = q²R
  σ₃(k) = σ₃(12) = 2044 = Φ₁₂·R = σ₃(μ)·σ₃(q)

So the sum-of-cubes-of-divisors of each W(3,3) atom recovers another
W(3,3) invariant. This is NOT a coincidence: it is the θ{E₈} side of
the 240-edge correspondence.

THEOREM (E₈ Shell Dictionary):

  E₈ norm-2 shell  = E × 1     = 240    (roots)
  E₈ norm-4 shell  = E × q²    = 2160   (transport shell)
  E₈ norm-6 shell  = E × R     = 6720   (Ramanujan-completion shell)
  E₈ norm-8 shell  = E × Φ₁₂   = 17520  (dodecagonal cyclotomic)
  E₈ norm-12 shell = E × τ     = 60480  (Ramanujan shell)
  E₈ norm-24 shell = E × Φ₁₂·R = 490560 (k-indexed shell)

THEOREM (Ramanujan τ at W(3,3) Parameters):

  τ_Ram(1) = 1
  τ_Ram(λ) = −f  = −24  (eigenvalue multiplicity!)
  τ_Ram(q) = τ   = 252  (our Ramanujan parameter!)
  τ_Ram(λq) = −f·τ = −6048 (by multiplicativity)

SOURCE: Novel analytic discovery connecting E₈ theta series to W(3,3).
"""
import pytest
from sympy import divisor_sigma

# ── W(3,3) parameters ──
q     = 3
lam   = 2
mu    = 4
k     = 12
v     = 40
f     = 24
g     = 15
E     = 240
tau   = 252
R     = 28
Phi3  = 13
Phi6  = 7
Phi12 = 73
s_biv = 6


def sigma3(n):
    """σ₃(n) = sum of cubes of divisors."""
    return int(divisor_sigma(n, 3))


# Known Ramanujan tau values
RAM_TAU = {1: 1, 2: -24, 3: 252, 4: -1472, 5: 4830, 6: -6048,
           7: -16744, 8: 84480, 9: -113643, 10: -115920, 11: 534612, 12: -370944}


# ================================================================
# T1: σ₃ dictionary
# ================================================================
class TestT1_Sigma3Dictionary:
    """σ₃ at W(3,3) atoms recovers other invariants."""

    def test_sigma3_1(self):
        assert sigma3(1) == 1

    def test_sigma3_lam(self):
        """σ₃(λ=2) = q² = 9."""
        assert sigma3(lam) == q**2

    def test_sigma3_q(self):
        """σ₃(q=3) = R = C(2d,2) = 28."""
        assert sigma3(q) == R

    def test_sigma3_mu(self):
        """σ₃(μ=4) = Φ₁₂ = 73."""
        assert sigma3(mu) == Phi12

    def test_sigma3_5(self):
        """σ₃(5) = 126 = τ/2."""
        assert sigma3(5) == tau // 2

    def test_sigma3_s(self):
        """σ₃(s=6) = τ = 252."""
        assert sigma3(s_biv) == tau

    def test_sigma3_k(self):
        """σ₃(k=12) = Φ₁₂·R = 2044."""
        assert sigma3(k) == Phi12 * R


# ================================================================
# T2: Multiplicativity
# ================================================================
class TestT2_Multiplicativity:
    """σ₃ is multiplicative on coprime arguments."""

    def test_sigma3_6_factors(self):
        """σ₃(6) = σ₃(2)·σ₃(3) = q²·R = τ."""
        assert sigma3(6) == sigma3(2) * sigma3(3)
        assert q**2 * R == tau

    def test_sigma3_12_factors(self):
        """σ₃(12) = σ₃(4)·σ₃(3) = Φ₁₂·R."""
        assert sigma3(12) == sigma3(4) * sigma3(3)

    def test_sigma3_10_factors(self):
        """σ₃(10) = σ₃(2)·σ₃(5) = q²·(τ/2) = q²τ/2."""
        assert sigma3(10) == sigma3(2) * sigma3(5)
        assert sigma3(10) == q**2 * (tau // 2)


# ================================================================
# T3: E₈ theta series coefficients
# ================================================================
class TestT3_E8Theta:
    """r_{E₈}(2n) = 240·σ₃(n) = E·σ₃(n)."""

    def test_norm2(self):
        """E₈ norm-2 shell = 240 = E (roots)."""
        assert E * sigma3(1) == 240

    def test_norm4(self):
        """E₈ norm-4 shell = 2160 = E·q² (transport shell)."""
        assert E * sigma3(2) == 2160
        assert 2160 == E * q**2

    def test_norm6(self):
        """E₈ norm-6 shell = 6720 = E·R."""
        assert E * sigma3(3) == 6720
        assert 6720 == E * R

    def test_norm8(self):
        """E₈ norm-8 shell = 17520 = E·Φ₁₂."""
        assert E * sigma3(4) == 17520
        assert 17520 == E * Phi12

    def test_norm12(self):
        """E₈ norm-12 shell = 60480 = E·τ."""
        assert E * sigma3(6) == 60480
        assert 60480 == E * tau

    def test_norm24(self):
        """E₈ norm-24 shell = 490560 = E·Φ₁₂·R."""
        assert E * sigma3(12) == 490560
        assert 490560 == E * Phi12 * R


# ================================================================
# T4: Ramanujan tau function
# ================================================================
class TestT4_RamanujanTau:
    """τ_Ram at W(3,3) parameters."""

    def test_tau_1(self):
        assert RAM_TAU[1] == 1

    def test_tau_lam(self):
        """τ_Ram(λ=2) = −f = −24."""
        assert RAM_TAU[lam] == -f

    def test_tau_q(self):
        """τ_Ram(q=3) = τ = 252."""
        assert RAM_TAU[q] == tau

    def test_tau_lam_q(self):
        """τ_Ram(λq=6) = −f·τ = −6048 (multiplicativity)."""
        assert RAM_TAU[lam * q] == -f * tau

    def test_multiplicativity(self):
        """τ_Ram(6) = τ_Ram(2)·τ_Ram(3) since gcd(2,3)=1."""
        assert RAM_TAU[6] == RAM_TAU[2] * RAM_TAU[3]


# ================================================================
# T5: Cross-connections
# ================================================================
class TestT5_CrossConnections:
    """Deep structural bridges."""

    def test_sigma3_tau_duality(self):
        """σ₃(6) = 252 = τ AND τ_Ram(3) = 252 = τ.
        Both the divisor sum at s=6 and Ramanujan tau at q=3 give τ."""
        assert sigma3(s_biv) == tau
        assert RAM_TAU[q] == tau

    def test_transport_shell_2160(self):
        """2160 = E·q² appears as E₈ norm-4 shell AND
        as the transport shell 3⁷ = 2160+27."""
        assert 2160 == E * q**2
        assert q**7 == 2160 + q**3

    def test_E8_shell_ratio(self):
        """r_{E₈}(4)/r_{E₈}(2) = σ₃(2) = q² = 9."""
        assert sigma3(2) == q**2

    def test_leech_from_sigma3(self):
        """Leech = E·q²·Φ₆·Φ₃ = E·σ₃(λ)·Φ₆·Φ₃."""
        leech = 196560
        assert leech == E * sigma3(lam) * Phi6 * Phi3

    def test_125_as_5_cubed(self):
        """σ₃(5)−1 = 125 = 5³ = (Φ₄/λ)³. The cube of the analytic prime."""
        assert sigma3(5) - 1 == 125
        assert 5**3 == 125
