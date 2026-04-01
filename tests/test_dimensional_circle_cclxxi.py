"""
Phase CCLXXI — Dimensional–Curvature Circle
==============================================

THEOREM (Dimensional Circle):

At d = μ = q+1 = 4 (spacetime dimension):

  k  = 3d = 12        (SRG valency = 3× spacetime dim)
  r_c = 2d = 8         (compact rank)
  R  = C(2d,2) = 28    (μΦ₆ = scalar curvature atom)
  τ  = (d−1)²C(2d,2) = 9·28 = 252  (Ramanujan core)

CONSEQUENCES:
  Leech kissing = C(v,2)·τ = 780·252 = 196,560
  McKay c₁     = Leech + d(d−1)⁴ = 196560 + 324 = 196,884
  Monster dim   = McKay − 1 = 196,883

SELECTORS (each has (q−3) factor):
  k − 3μ = q(q−3)
  r_c − 2μ = (q+1)(q−3)
  2R − r_c(r_c−1) = −q²(q−3)(q+1)
  2R − 2μ(2μ−1) = −(q−3)(q+1)²

SOURCE: W33_dimensional_curvature_closure_20260330.zip
"""
import math
import pytest

# ── W(3,3) parameters ──
q    = 3
d    = q + 1  # 4 = spacetime dimension
v    = 40
k    = 12
lam  = 2
mu   = 4
Phi6 = q**2 - q + 1  # 7

# ── Derived ──
r_c  = k - mu       # 8 = compact rank
R    = mu * Phi6     # 28
tau  = q**2 * R      # 252


# ================================================================
# T1: Dimensional identifications
# ================================================================
class TestT1_DimensionalCircle:
    """d=4, k=3d, r_c=2d, R=C(2d,2)."""

    def test_d_is_4(self):
        assert d == 4

    def test_k_is_3d(self):
        assert k == 3 * d

    def test_compact_rank(self):
        assert r_c == 2 * d

    def test_R_is_binomial(self):
        assert R == math.comb(2 * d, 2)

    def test_R_value(self):
        assert R == 28

    def test_tau_from_R(self):
        assert tau == (d - 1)**2 * math.comb(2 * d, 2)

    def test_tau_value(self):
        assert tau == 252


# ================================================================
# T2: Selectors vanish uniquely at q=3
# ================================================================
class TestT2_Selectors:
    def test_k_3mu(self):
        assert q * (q - 3) == 0

    def test_rc_2mu(self):
        assert (q + 1) * (q - 3) == 0

    def test_binomial_rc(self):
        assert -q**2 * (q - 3) * (q + 1) == 0

    def test_binomial_2mu(self):
        assert -(q - 3) * (q + 1)**2 == 0


# ================================================================
# T3: Leech and McKay from the circle
# ================================================================
class TestT3_LeechMcKay:
    """Leech kissing = C(v,2)·τ, McKay = Leech + d(d−1)⁴."""

    def test_leech_kissing(self):
        leech = math.comb(v, 2) * tau
        assert leech == 196560

    def test_mckay_c1(self):
        leech = math.comb(v, 2) * tau
        mckay = leech + d * (d - 1)**4
        assert mckay == 196884

    def test_d_correction(self):
        """d(d−1)⁴ = 4·81 = 324."""
        assert d * (d - 1)**4 == 324

    def test_monster_dim(self):
        """Faithful Monster rep = McKay − 1 = 196883."""
        leech = math.comb(v, 2) * tau
        mckay = leech + d * (d - 1)**4
        assert mckay - 1 == 196883


# ================================================================
# T4: All from one parameter d
# ================================================================
class TestT4_OneDParam:
    """Everything from d=4."""

    def test_q_from_d(self):
        assert q == d - 1

    def test_lam_from_d(self):
        assert lam == d - 2

    def test_v_from_d(self):
        computed = d * ((d-1)**2 + 1)
        assert computed == v

    def test_leech_formula(self):
        """Leech = C(v,2) · (d−1)² · C(2d,2)."""
        leech = math.comb(v, 2) * (d - 1)**2 * math.comb(2*d, 2)
        assert leech == 196560

    def test_mckay_formula(self):
        """McKay = C(v,2)(d−1)²C(2d,2) + d(d−1)⁴."""
        mckay = (math.comb(v, 2) * (d-1)**2 * math.comb(2*d, 2)
                 + d * (d-1)**4)
        assert mckay == 196884
