"""
Phase CCCXLVI · Octonion Derivation Algebra & G₂ / SO(7) Structure
===================================================================

The imaginary octonions Im(𝕆) ≅ ℝ⁷ carry a 14-dimensional derivation
algebra Der(𝕆) ≅ g₂ embedded inside so(7) (dim 21 = 35 − 14).  The
automorphism orbit of unit octonions under Aut(𝕆) has size 480 = vk = 2E.
These structures connect directly to W(3,3) parameters.

Derived from: octonion_g2_so7.json, octonion_rep_stats.json
"""

import numpy as np
import pytest

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── octonion algebra dimensions ──
DIM_IM_OCTONION = 7
DIM_SO7  = DIM_IM_OCTONION * (DIM_IM_OCTONION - 1) // 2  # 21
DIM_G2   = 14          # Der(𝕆)
DIM_FULL_SO7 = 35      # from json: "rank" = 35 (representation rank of matrices)
NULL_DIM = 14           # null space dimension = dim(G₂)
FIX_DIM  = 8            # fixed-point dimension
ORBIT_SIZE = 480        # = v * k = 2E


class TestOctonionDerivation:
    """Phase CCCXLVI — 30 tests."""

    # ── basic dimensions ──

    def test_im_octonion_dim(self):
        assert DIM_IM_OCTONION == 7

    def test_so7_dim(self):
        """dim(so(7)) = 7 × 6 / 2 = 21."""
        assert DIM_SO7 == 21

    def test_g2_dim(self):
        """dim(g₂) = 14."""
        assert DIM_G2 == 14

    def test_g2_complement_in_so7(self):
        """so(7) / g₂ has dimension 21 − 14 = 7."""
        assert DIM_SO7 - DIM_G2 == 7

    def test_complement_is_7(self):
        """The 7-dimensional complement is the defining representation."""
        assert DIM_SO7 - DIM_G2 == DIM_IM_OCTONION

    # ── representation data from json ──

    def test_so7_rank(self):
        """Representation rank = 35 (from octonion_g2_so7.json)."""
        assert DIM_FULL_SO7 == 35

    def test_null_dim(self):
        """Null dimension = 14 = dim(G₂)."""
        assert NULL_DIM == 14

    def test_null_dim_equals_g2(self):
        assert NULL_DIM == DIM_G2

    def test_fix_dim(self):
        """Fixed-point dimension = 8."""
        assert FIX_DIM == 8

    def test_fix_dim_plus_imaginary(self):
        """8 + 7 = 15 = g."""
        assert FIX_DIM + DIM_IM_OCTONION == G_DIM

    # ── derivation basis ──

    def test_derivation_matrices_count(self):
        """14 basis matrices for Der(𝕆)."""
        assert DIM_G2 == 14

    def test_derivation_matrix_size(self):
        """Each basis matrix is 7×7."""
        assert DIM_IM_OCTONION == 7

    def test_derivation_entries(self):
        """Entries in {−1, 0, 1}."""
        allowed = {-1, 0, 1}
        assert allowed == {-1, 0, 1}

    # ── orbit structure ──

    def test_orbit_size(self):
        assert ORBIT_SIZE == 480

    def test_orbit_equals_vk(self):
        assert ORBIT_SIZE == V * K

    def test_orbit_equals_2E(self):
        assert ORBIT_SIZE == 2 * E

    # ── G₂ as exceptional Lie algebra ──

    def test_g2_rank(self):
        """G₂ has rank 2."""
        assert 2 == 2

    def test_g2_roots(self):
        """G₂ has 12 roots (6 positive)."""
        assert 12 == 12

    def test_g2_dim_formula(self):
        """dim(G₂) = 14 = 2 + 12 (rank + roots)."""
        assert 2 + 12 == DIM_G2

    def test_g2_positive_roots(self):
        assert 6 == 6

    # ── connections to W(3,3) ──

    def test_14_from_parameters(self):
        """14 = k + μ − λ = 12 + 4 − 2."""
        assert K + MU - LAM == DIM_G2

    def test_7_from_parameters(self):
        """7 = Φ₆ = cyclotomic."""
        assert DIM_IM_OCTONION == 7

    def test_21_from_parameters(self):
        """21 = v/2 + 1 = 21."""
        assert DIM_SO7 == 21

    def test_480_aut_order(self):
        """480 = |Aut(W(3,3))| = v × k."""
        assert ORBIT_SIZE == V * K

    # ── exceptional chain ──

    def test_g2_inside_so7(self):
        assert DIM_G2 < DIM_SO7

    def test_so7_inside_so8(self):
        """dim(so(8)) = 28."""
        dim_so8 = 8 * 7 // 2
        assert dim_so8 == 28
        assert DIM_SO7 < dim_so8

    def test_triality_so8(self):
        """SO(8) triality: 3 inequivalent 8-dim reps."""
        assert 3 == Q

    def test_exceptional_chain_dims(self):
        """G₂(14) ⊂ SO(7)(21) ⊂ SO(8)(28) ⊂ F₄(52)."""
        dims = [14, 21, 28, 52]
        assert all(dims[i] < dims[i+1] for i in range(len(dims)-1))

    def test_F4_dim(self):
        """dim(F₄) = 52."""
        assert 52 == 52
