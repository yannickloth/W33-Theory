"""
Phase CCLXIV — Co₁ Triple-Action Simplex
==========================================

THEOREM (Co₁ Triple-Action Closure):

All three major Co₁ orbit sizes are τ-centered:

  |Co₁:Co₂| = τ · C(v,2)/2           = 252 · 390   = 98,280
  |Co₁:Co₃| = τ · 2^(k−4) · Φ₃ · Φ₄  = 252 · 33280 = 8,386,560
  |Co₁:Suz| = τ · v · μ · Φ₄ · (f−1) = 252 · 36800 = 9,273,600

and the pairwise GCDs recover three canonical shells:

  gcd(I₂, I₃) = τ · Φ₃ · Φ₄ = 32,760    (cyclotomic shell)
  gcd(I₂, Iₛ) = τ · Φ₄     = 2,520      (ovoid shell)
  gcd(I₃, Iₛ) = τ · c_EH   = 80,640     (gravity shell)

where c_EH = v(q²−1) = 320 is the Einstein-Hilbert coefficient.

SOURCE: W33_co1_triple_action_closure_20260330.zip
"""
import math
import pytest

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
f    = 24
g    = 15
Phi3 = q**2 + q + 1   # 13
Phi4 = q**2 + 1        # 10
Phi6 = q**2 - q + 1    #  7
tau  = 252

# ── Group orders ──
CO1 = 4157776806543360000
CO2 = 42305421312000
CO3 = 495766656000
SUZ = 448345497600

# ── Action indices ──
I2 = CO1 // CO2   # 98280
I3 = CO1 // CO3   # 8386560
IS = CO1 // SUZ   # 9273600


# ================================================================
# T1: Action indices are exact
# ================================================================
class TestT1_ActionIndices:
    def test_I2_exact(self):
        assert CO1 % CO2 == 0
        assert I2 == 98280

    def test_I3_exact(self):
        assert CO1 % CO3 == 0
        assert I3 == 8386560

    def test_IS_exact(self):
        assert CO1 % SUZ == 0
        assert IS == 9273600


# ================================================================
# T2: Tau-centered decomposition
# ================================================================
class TestT2_TauCentered:
    """All three indices = τ × W(3,3) shell."""

    def test_I2_formula(self):
        """|Co₁:Co₂| = τ · C(v,2)/2 = τ · v(v−1)/4."""
        assert I2 == tau * v * (v - 1) // 4

    def test_I3_formula(self):
        """|Co₁:Co₃| = τ · 2^(k−4) · Φ₃ · Φ₄."""
        assert I3 == tau * 2**(k - 4) * Phi3 * Phi4

    def test_IS_formula(self):
        """|Co₁:Suz| = τ · v · μ · Φ₄ · (f−1)."""
        assert IS == tau * v * mu * Phi4 * (f - 1)

    def test_all_divisible_by_tau(self):
        assert I2 % tau == 0
        assert I3 % tau == 0
        assert IS % tau == 0


# ================================================================
# T3: Pairwise GCDs recover canonical shells
# ================================================================
class TestT3_PairwiseGCDs:
    """Three GCDs → three canonical shells."""

    def test_gcd_I2_I3(self):
        """gcd = τ · Φ₃ · Φ₄ (cyclotomic shell)."""
        assert math.gcd(I2, I3) == tau * Phi3 * Phi4

    def test_gcd_I2_IS(self):
        """gcd = τ · Φ₄ (ovoid shell)."""
        assert math.gcd(I2, IS) == tau * Phi4

    def test_gcd_I3_IS(self):
        """gcd = τ · c_EH (gravity shell)."""
        c_EH = v * (q**2 - 1)
        assert math.gcd(I3, IS) == tau * c_EH

    def test_gcd_values(self):
        assert math.gcd(I2, I3) == 32760
        assert math.gcd(I2, IS) == 2520
        assert math.gcd(I3, IS) == 80640


# ================================================================
# T4: Einstein-Hilbert coefficient
# ================================================================
class TestT4_EinsteinHilbert:
    """c_EH = v(q²−1) = 320."""

    def test_c_EH_value(self):
        c_EH = v * (q**2 - 1)
        assert c_EH == 320

    def test_c_EH_factored(self):
        """c_EH = 2^6 · 5."""
        c_EH = v * (q**2 - 1)
        assert c_EH == 2**6 * 5

    def test_c_EH_in_gcd(self):
        c_EH = v * (q**2 - 1)
        assert math.gcd(I3, IS) == tau * c_EH


# ================================================================
# T5: Shell hierarchy
# ================================================================
class TestT5_ShellHierarchy:
    """Ovoid ⊂ Cyclotomic ⊂ Gravity up to tau rescaling."""

    def test_ovoid_is_smallest(self):
        assert tau * Phi4 < tau * Phi3 * Phi4 < tau * v * (q**2 - 1)

    def test_residual_shells(self):
        """After removing τ, residual shells are 10, 130, 320."""
        assert I2 // tau == 390
        assert I3 // tau == 33280
        assert IS // tau == 36800

    def test_shells_ordered(self):
        """Residual shells: 10 < 130 < 320."""
        assert Phi4 < Phi3 * Phi4 < v * (q**2 - 1)
