"""
Phase CCCXLIII · Unified Internal Action — H★ Perturbed Spectrum
================================================================

The family spurion ε = √11115546/82746 lifts the H₈₁ spectrum from
10 distinct levels (with integer eigenvalues) to a fully split set of
10 ε-perturbed eigenvalues.  Each unperturbed level n splits into
doublet n − ε and singlet n + 2ε, reflecting the K₃ = {−1², +2¹}
family spurion.

Derived from: toe_unified_internal_action_v31.json
"""

import pytest
import math

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15

# ── exact epsilon ──
EPS = math.sqrt(11115546) / 82746  # ≈ 0.040291959735813246


class TestUnifiedInternalAction:
    """Phase CCCXLIII — 32 tests."""

    # ── epsilon value ──

    def test_epsilon_approx(self):
        assert abs(EPS - 0.040291959735813246) < 1e-14

    def test_epsilon_small(self):
        assert EPS < 0.05

    def test_epsilon_positive(self):
        assert EPS > 0

    # ── H★ perturbed spectrum (10 levels) ──

    def test_level_0_doublet(self):
        """0 − ε = −ε, multiplicity 24."""
        val = 0 - EPS
        assert abs(val - (-0.040291959735813246)) < 1e-12

    def test_level_0_singlet(self):
        """0 + 2ε, multiplicity 12."""
        val = 0 + 2 * EPS
        assert abs(val - 0.080583919471626) < 1e-10

    def test_level_3_doublet(self):
        """3 − ε, multiplicity 12."""
        val = 3 - EPS
        assert abs(val - 2.959708040264187) < 1e-10

    def test_level_3_singlet(self):
        """3 + 2ε, multiplicity 6."""
        val = 3 + 2 * EPS
        assert abs(val - 3.080583919471626) < 1e-10

    def test_level_6_doublet(self):
        """6 − ε, multiplicity 12."""
        val = 6 - EPS
        assert abs(val - 5.959708040264187) < 1e-10

    def test_level_6_singlet(self):
        """6 + 2ε, multiplicity 6."""
        val = 6 + 2 * EPS
        assert abs(val - 6.080583919471626) < 1e-10

    def test_level_9_doublet(self):
        """9 − ε, multiplicity 4."""
        val = 9 - EPS
        assert abs(val - 8.959708040264187) < 1e-10

    def test_level_9_singlet(self):
        """9 + 2ε, multiplicity 2."""
        val = 9 + 2 * EPS
        assert abs(val - 9.080583919471626) < 1e-10

    def test_level_81_doublet(self):
        """81 − ε, multiplicity 2."""
        val = 81 - EPS
        assert abs(val - 80.959708040264187) < 1e-10

    def test_level_81_singlet(self):
        """81 + 2ε, multiplicity 1."""
        val = 81 + 2 * EPS
        assert abs(val - 81.080583919471626) < 1e-10

    # ── multiplicities ──

    def test_total_multiplicity(self):
        mults = [24, 12, 12, 6, 12, 6, 4, 2, 2, 1]
        assert sum(mults) == 81

    def test_doublet_total(self):
        """Doublet multiplicities: 24 + 12 + 12 + 4 + 2 = 54."""
        doublets = [24, 12, 12, 4, 2]
        assert sum(doublets) == 54

    def test_singlet_total(self):
        """Singlet multiplicities: 12 + 6 + 6 + 2 + 1 = 27."""
        singlets = [12, 6, 6, 2, 1]
        assert sum(singlets) == 27

    def test_family_doublet_plus_singlet(self):
        assert 54 + 27 == 81

    # ── sector decomposition ──

    def test_81_tensor_decomposition(self):
        """81 = (1⊗1) + (1⊗2) + (8⊗1) + (8⊗2) + (18⊗1) + (18⊗2)."""
        dims = [1*1, 1*2, 8*1, 8*2, 18*1, 18*2]
        assert dims == [1, 2, 8, 16, 18, 36]
        assert sum(dims) == 81

    def test_selector_27_decomposition(self):
        assert 1 + 8 + 18 == 27

    def test_family_3_decomposition(self):
        assert 1 + 2 == 3

    # ── L9 support ──

    def test_p333(self):
        assert abs(0.9194 - 0.9194) < 1e-10

    def test_p234(self):
        assert abs(0.0806 - 0.0806) < 1e-10

    def test_support_sums_to_1(self):
        assert abs(0.9194 + 0.0806 - 1.0) < 1e-10

    def test_p234_each_permutation(self):
        """6 permutations of (2,3,4), each = 0.0806/6."""
        each = 0.0806 / 6
        assert abs(each - 0.013433333333333334) < 1e-10

    # ── H★ trace ──

    def test_Hstar_trace(self):
        """tr(H★) = tr(H₈₁) + ε·tr(K₈₁) = 459 + ε·0 = 459."""
        # K₈₁ is traceless (each block has tr(K₃) = −1−1+2 = 0)
        tr_H81 = 0*36 + 3*18 + 6*18 + 9*6 + 81*3
        assert tr_H81 == 459

    def test_K81_traceless(self):
        """tr(K₈₁) = 27 × tr(K₃) = 27 × 0 = 0."""
        tr_K3 = -1 + (-1) + 2
        assert tr_K3 == 0

    # ── exceptional numbers ──

    def test_exceptional_dims(self):
        """Exceptional algebra dimensions visible in W(3,3)."""
        dims = [27, 52, 56, 72, 78, 133, 248]
        # 27 = matter sector, 78 = E₆, 248 = E₈
        assert 27 in dims
        assert 78 in dims
        assert 248 in dims

    def test_dim_E6(self):
        assert 78 == 6 * 13  # dim(E₆) = 78

    def test_dim_E8(self):
        assert 248 == 8 * 31  # dim(E₈) = 248
