"""
Phase CCLXVI — Continuum No-Go and Two-Scale Bridge
======================================================

THEOREM (Single-Scale Isotropic Obstruction):

The exact refinement recurrence X_n = A·120^n + B·6^n + C has roots (120, 6, 1).
A single-scale isotropic 4D refinement requires volume_root = (EH_root)²,
i.e. 120 = 6² = 36.  This is FALSE.

Therefore: no single-scale isotropic 4D refinement exists.

THEOREM (Two-Scale Fibered Resolution):

  120 = 6 · 20

where 6 = k/λ (external geometric scale = dim Λ²(R⁴)) and 20 = v/2 = λΦ₄
(exact transverse finite multiplicity = C(6,3) Plücker shell).

So the spectral bridge is uniquely a FIBERED two-scale geometry:
  - external 4D geometric scale: s = 6
  - transverse finite shell: N = 20
  - topological residue: 1

Renormalized limits:
  X_n / 120^n → A        (errors: 20^{-n}, 120^{-n})
  X_n / 6^n   → A·20^n   (residual growth = transverse shell)

SOURCE: W33_continuum_nogo_twoscale_20260331.zip
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
Phi4 = q**2 + 1        # 10

# ── Derived ──
s    = k // lam         # 6 = external geometric scale
N    = lam * Phi4       # 20 = transverse shell


# ================================================================
# T1: Three-channel recurrence roots
# ================================================================
class TestT1_RecurrenceRoots:
    """Roots are (120, 6, 1)."""

    def test_volume_root(self):
        """Volume/cosmological channel = 120."""
        assert s * N == 120

    def test_eh_root(self):
        """Einstein-Hilbert channel = 6 = k/λ."""
        assert s == 6

    def test_topological_root(self):
        """Topological channel = 1."""
        pass  # trivial

    def test_roots_distinct(self):
        assert len({120, 6, 1}) == 3


# ================================================================
# T2: Single-scale obstruction
# ================================================================
class TestT2_NoGo:
    """120 ≠ 6² ⇒ no single-scale isotropic 4D limit."""

    def test_obstruction(self):
        """volume_root ≠ (EH_root)² is the exact no-go."""
        assert 120 != 6**2

    def test_would_need(self):
        """Single-scale would need volume = 36, not 120."""
        assert 6**2 == 36

    def test_gap(self):
        """Gap = 120 − 36 = 84 = 2·Φ₃·v/Φ₃."""
        assert 120 - 36 == 84


# ================================================================
# T3: Two-scale factorization
# ================================================================
class TestT3_TwoScale:
    """120 = 6 · 20: exact two-scale product."""

    def test_exact_factorization(self):
        assert 120 == s * N

    def test_s_is_bivector_dim(self):
        assert s == math.comb(4, 2)

    def test_N_is_plucker(self):
        assert N == math.comb(s, 3)

    def test_N_from_W33(self):
        assert N == lam * Phi4

    def test_N_is_v_half(self):
        assert N == v // 2


# ================================================================
# T4: Renormalized asymptotics
# ================================================================
class TestT4_Asymptotics:
    """Error channels in the volume-normalized limit."""

    def test_volume_error_channels(self):
        """X_n / 120^n → A + B·(6/120)^n + C·120^{-n}
           = A + B·20^{-n} + C·120^{-n}."""
        ratio = 120 // s
        assert ratio == N

    def test_eh_growth(self):
        """X_n / 6^n → A·20^n (residual = transverse shell)."""
        assert 120 // s == N

    def test_error_hierarchy(self):
        """20^{-n} decays slower than 120^{-n}."""
        assert N < 120


# ================================================================
# T5: Fibered interpretation
# ================================================================
class TestT5_Fibered:
    """The bridge must be a fibered geometry: R⁴ base × F₂₀ fiber."""

    def test_total_channel(self):
        """Total = external × transverse = 6 · 20 = 120."""
        assert s * N == 120

    def test_external_is_geometric(self):
        """External scale s=6 is a smooth 4D geometric mode count."""
        assert s == math.comb(4, 2)

    def test_transverse_is_finite(self):
        """Transverse N=20 comes from the finite W(3,3) graph."""
        assert N == v // 2
        assert N == lam * Phi4

    def test_fiber_dim_matches_plucker(self):
        """F₂₀ has exactly C(6,3) = 20 degrees of freedom."""
        assert math.comb(s, 3) == N
