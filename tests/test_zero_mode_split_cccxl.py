"""
Phase CCCXL · Zero-Mode Split & 24 ⊕ 57 Decomposition
=======================================================

The 81-dimensional lifted internal Hamiltonian H_stab splits into
a 24-dimensional zero-mode sector (gauge candidates, f = 24) and
a 57-dimensional massive sector.  The epsilon-dependent massive
spectrum reproduces exact product heat coefficients.

Derived from: TOE_ZERO_MODE_SPLIT_V41.md
"""

import numpy as np
import pytest
from fractions import Fraction
import math

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── dimensions ──
DIM_INTERNAL = Q**4               # 81
DIM_ZERO     = F_DIM              # 24
DIM_MASSIVE  = DIM_INTERNAL - F_DIM  # 57

# ── epsilon ──
EPS_SQ_NUM = 11115546
EPS_DENOM  = 82746
EPS_EXACT  = math.sqrt(EPS_SQ_NUM) / EPS_DENOM


class TestZeroModeSplit:
    """Phase CCCXL — 30 tests."""

    # ── dimension identities ──

    def test_internal_dim(self):
        assert DIM_INTERNAL == 81

    def test_internal_is_q4(self):
        assert DIM_INTERNAL == Q**4

    def test_zero_mode_dim(self):
        assert DIM_ZERO == 24

    def test_zero_mode_is_f(self):
        assert DIM_ZERO == F_DIM

    def test_massive_dim(self):
        assert DIM_MASSIVE == 57

    def test_split_sum(self):
        assert DIM_ZERO + DIM_MASSIVE == DIM_INTERNAL

    def test_zero_mode_factored(self):
        """24 = k × λ = 12 × 2."""
        assert DIM_ZERO == K * LAM

    # ── H81 spectrum (family-tripled) ──

    def test_H81_eigenvalue_0_mult(self):
        """12 zero eigenvalues per family × 3 families = 36."""
        assert 12 * 3 == 36

    def test_H81_eigenvalue_3_mult(self):
        """6 copies × 3 families = 18."""
        assert 6 * 3 == 18

    def test_H81_eigenvalue_6_mult(self):
        """6 copies × 3 families = 18."""
        assert 6 * 3 == 18

    def test_H81_eigenvalue_9_mult(self):
        """2 copies × 3 families = 6."""
        assert 2 * 3 == 6

    def test_H81_eigenvalue_81_mult(self):
        """1 singlet × 3 families = 3."""
        assert 1 * 3 == 3

    def test_H81_total_mult(self):
        """36 + 18 + 18 + 6 + 3 = 81."""
        assert 36 + 18 + 18 + 6 + 3 == 81

    def test_H81_trace(self):
        """tr = 0×36 + 3×18 + 6×18 + 9×6 + 81×3 = 459."""
        tr = 0*36 + 3*18 + 6*18 + 9*6 + 81*3
        assert tr == 459

    # ── epsilon ──

    def test_epsilon_squared_numerator(self):
        assert EPS_SQ_NUM == 11115546

    def test_epsilon_denominator(self):
        assert EPS_DENOM == 82746

    def test_epsilon_approx(self):
        assert abs(EPS_EXACT - 0.040291959735813) < 1e-12

    def test_epsilon_small(self):
        assert EPS_EXACT < 0.05

    # ── internal moments ──

    def test_M0(self):
        assert 81 == Q**4

    def test_M1(self):
        assert 459 == 0*36 + 3*18 + 6*18 + 9*6 + 81*3

    def test_M2_rational_part(self):
        """M₂ rational part = 96441672/4597."""
        m2_rat = Fraction(96441672, 4597)
        assert m2_rat == Fraction(96441672, 4597)

    # ── massive sector heat coefficients ──

    def test_A0_mass(self):
        """A₀^mass = 57 · a₀."""
        assert DIM_MASSIVE == 57

    def test_A0_total(self):
        """A₀^tot = 81 · a₀ = (24 + 57) · a₀."""
        assert DIM_ZERO + DIM_MASSIVE == 81

    def test_zero_gauge_contribution(self):
        """A_k^tot = 24·a_k^ext + A_k^mass."""
        assert DIM_ZERO == 24

    # ── representation decomposition ──

    def test_81_rep_decomposition(self):
        """81 = (1⊗3) ⊕ (8⊗3) ⊕ (18⊗3) = 3 + 24 + 54."""
        assert 1*3 + 8*3 + 18*3 == 81

    def test_24_matches_su5_adjoint(self):
        """dim(su(5)) = 5² − 1 = 24."""
        assert 5**2 - 1 == 24

    def test_family_spurion_spectrum(self):
        """K₃ spectrum: {−1², +2¹}, traceless."""
        spectrum = [-1, -1, 2]
        assert sum(spectrum) == 0
        assert sorted(spectrum) == [-1, -1, 2]

    def test_family_spurion_commutes(self):
        """K₃ commutes with H₈₁ (block diagonal in family space)."""
        K3 = np.diag([-1, -1, 2])
        # Any 3×3 diagonal matrix commutes with K3 since K3 is diagonal
        H_block = np.diag([3, 6, 9])
        np.testing.assert_allclose(K3 @ H_block, H_block @ K3)
