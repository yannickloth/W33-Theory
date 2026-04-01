"""
Phase CCLXXXIII — GUT Gauge Tower & Weinberg Angle
======================================================

THEOREM (Gauge Dimension Tower):

The full GUT hierarchy of gauge group dimensions is W(3,3):

  dim SU(q)  = q²−1  = 8  = 2d    (strong force)
  dim SU(λ)  = λ²−1  = 3  = q     (weak force)
  dim U(1)   = 1              (hypercharge)
  ─────────────────────────────
  Total SM   = 12     = k     (valency)

  dim SU(5)  = 24     = f     (SU(5) GUT = eigenvalue multiplicity)
  dim SO(10) = 45     = C(Θ,2) (SO(10) GUT = Lovász theta choose 2)
  dim E₆     = 78     = s·Φ₃  (E₆ = bivector × cyclotomic)
  dim E₈     = 248    = E+2d  (E₈ = edges + Cartan rank)

THEOREM (Weinberg Angle from W(3,3)):

  sin²θ_W(GUT)  = q/(2μ) = 3/8 = 0.375    (exact SU(5) value)
  sin²θ_W(low)  ≈ q/Φ₃   = 3/13 ≈ 0.2308  (0.2% from experiment!)

  Running: Δ(sin²θ) = q/(2μ) − q/Φ₃ = g/(2dΦ₃) = 15/104

THEOREM (Three Generations):

  N_gen = q = 3

  States per generation = 2^d = μ² = 16   (SO(10) spinor dim)
  Total fermion states  = q·2^d = 2f = 48

THEOREM (126 of SO(10)):

  The Higgs representation 126 of SO(10) = σ₃(5) = τ/2 = C(q², μ)

  This is the representation giving Majorana masses to ν_R.

SOURCE: Novel synthesis connecting GUT hierarchy to W(3,3).
"""
import pytest
from fractions import Fraction
from math import comb

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
N_curv = 20
d     = 4
Theta = 10


# ================================================================
# T1: SM gauge dimension tower
# ================================================================
class TestT1_GaugeTower:
    """SM gauge group dimensions = W(3,3) parameters."""

    def test_SU3(self):
        """dim SU(3) = q²−1 = 8 = 2d."""
        assert q**2 - 1 == 8
        assert 8 == 2 * d

    def test_SU2(self):
        """dim SU(2) = λ²−1 = 3 = q."""
        assert lam**2 - 1 == q

    def test_U1(self):
        """dim U(1) = 1."""
        assert 1 == 1

    def test_total_SM(self):
        """dim(SU(3)×SU(2)×U(1)) = 8+3+1 = 12 = k."""
        assert (q**2 - 1) + (lam**2 - 1) + 1 == k


# ================================================================
# T2: GUT tower
# ================================================================
class TestT2_GUTTower:
    """GUT gauge dimensions are higher W(3,3) invariants."""

    def test_SU5(self):
        """dim SU(5) = 24 = f."""
        assert 5**2 - 1 == f

    def test_SO10(self):
        """dim SO(10) = 45 = C(Θ,2)."""
        assert comb(Theta, 2) == 45
        assert 10 * 9 // 2 == 45

    def test_E6(self):
        """dim E₆ = 78 = s·Φ₃."""
        assert s_biv * Phi3 == 78

    def test_E8(self):
        """dim E₈ = 248 = E + 2d."""
        assert E + 2 * d == 248


# ================================================================
# T3: Weinberg angle
# ================================================================
class TestT3_WeinbergAngle:
    """sin²θ_W at GUT and low scale from W(3,3)."""

    def test_GUT_scale(self):
        """sin²θ_W(GUT) = q/(2μ) = 3/8."""
        assert Fraction(q, 2 * mu) == Fraction(3, 8)

    def test_low_scale(self):
        """sin²θ_W(low) = q/Φ₃ = 3/13 ≈ 0.2308."""
        val = q / Phi3
        assert abs(val - 0.23122) < 0.001  # within 0.2%

    def test_running(self):
        """Δ(sin²θ) = q/(2μ) − q/Φ₃ = g/(2dΦ₃) = 15/104."""
        delta = Fraction(q, 2 * mu) - Fraction(q, Phi3)
        assert delta == Fraction(g, 2 * d * Phi3)
        assert delta == Fraction(15, 104)

    def test_running_numerator(self):
        """Numerator of running = g = 15 = second eigenvalue multiplicity."""
        delta = Fraction(q, 2 * mu) - Fraction(q, Phi3)
        assert delta.numerator == g


# ================================================================
# T4: Three generations
# ================================================================
class TestT4_ThreeGenerations:
    """N_gen = q = 3."""

    def test_Ngen(self):
        assert q == 3

    def test_spinor_dim(self):
        """SO(10) spinor = 2^d = μ² = 16."""
        assert 2**d == mu**2 == 16

    def test_total_fermions(self):
        """q · 2^d = 48 = 2f."""
        assert q * 2**d == 2 * f

    def test_48_is_mu_k(self):
        """48 = μ·k."""
        assert mu * k == 48


# ================================================================
# T5: 126 representation
# ================================================================
class TestT5_Rep126:
    """The 126 of SO(10) from σ₃ and combinatorics."""

    def test_126_is_tau_half(self):
        """126 = τ/2."""
        assert tau // 2 == 126

    def test_126_is_comb(self):
        """126 = C(q², μ) = C(9,4)."""
        assert comb(q**2, mu) == 126

    def test_126_from_sigma3(self):
        """σ₃(5) = 126."""
        from sympy import divisor_sigma
        assert int(divisor_sigma(5, 3)) == 126


# ================================================================
# T6: Grand tower consistency
# ================================================================
class TestT6_TowerConsistency:
    """The full tower is self-consistent."""

    def test_chain(self):
        """SM(12) ⊂ SU(5)(24) ⊂ SO(10)(45) ⊂ E₆(78) ⊂ E₈(248)."""
        dims = [k, f, 45, s_biv * Phi3, E + 2 * d]
        assert dims == [12, 24, 45, 78, 248]
        # Verify monotone
        assert all(dims[i] < dims[i+1] for i in range(len(dims)-1))

    def test_ratios(self):
        """f/k = 2, 45/f = 15/8, 78/45 = 26/15, 248/78 = 124/39."""
        assert Fraction(f, k) == 2
        assert Fraction(45, f) == Fraction(15, 8)

    def test_E8_accounts_for_all(self):
        """248 = 8(SU3) + 3(SU2) + 1(U1) + 236(coset)."""
        sm = (q**2 - 1) + (lam**2 - 1) + 1
        coset = 248 - sm
        assert coset == 236
        # 236 = 4*59 = mu*59
        assert coset == mu * 59
