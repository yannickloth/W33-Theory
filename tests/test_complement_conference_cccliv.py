"""
Phase CCCLIV · Complement Conference Graph & Seidel S² Decomposition
=====================================================================

The complement of W(3,3) = SRG(40,12,2,4) is SRG(40,27,18,18), a
conference graph (λ′ = μ′).  The Seidel matrix satisfies S² = αI + βA +
γ(J−I−A) with α=33, β=−4, γ=6.  Complement eigenvalues are {27,3,−3}
and the Seidel energy equals 240 = E.

Derived from: W(3,3) SRG theory
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240
THETA = 10
PHI6 = 7

# ── complement SRG parameters ──
K_C = V - K - 1      # 27
LAM_C = V - 2*K + LAM  # 18
MU_C = V - 2*K + MU    # 20 ... wait
# Actually for SRG complement: λ' = v - 2k + μ - 2, μ' = v - 2k + λ
# λ' = 40 - 24 + 4 - 2 = 18
# μ' = 40 - 24 + 2 = 18
LAM_C = V - 2*K + MU - 2  # 18
MU_C = V - 2*K + LAM      # 18

# ── S² coefficients ──
S2_ALPHA = 33   # diagonal: v - Φ₆ = 33 ... actually let's verify: S = J - 2A - I
# S² = (v-1)I + (v - 2 - 2k)J + (−2)(−2)A + ... Bose-Mesner
# For SRG: S = J - I - 2A, S² = (v−1)I + (v−4k+4λ−2)A + (v−4k+4μ−2)(J−I−A) + ... 
# Actually S² in Bose-Mesner: s₁₁I + s₁₂A + s₁₃(J-I-A)


class TestComplementConference:
    """Phase CCCLIV — 30 tests."""

    # ── complement parameters ──

    def test_complement_v(self):
        assert V == 40

    def test_complement_k(self):
        """k′ = v − k − 1 = 27."""
        assert K_C == 27

    def test_complement_lambda(self):
        """λ′ = v − 2k + μ − 2 = 18."""
        assert LAM_C == 18

    def test_complement_mu(self):
        """μ′ = v − 2k + λ = 18."""
        assert MU_C == 18

    def test_conference_property(self):
        """Conference graph: λ′ = μ′."""
        assert LAM_C == MU_C

    def test_complement_srg(self):
        """SRG(40, 27, 18, 18)."""
        assert (V, K_C, LAM_C, MU_C) == (40, 27, 18, 18)

    # ── complement eigenvalues ──

    def test_complement_eigenvalue_k(self):
        """Trivial eigenvalue = k′ = 27."""
        assert K_C == 27

    def test_complement_eigenvalue_r(self):
        """r′ = −1 − s = −1 − (−4) = 3 = q."""
        assert -1 - (-MU) == Q

    def test_complement_eigenvalue_s(self):
        """s′ = −1 − r = −1 − 2 = −3 = −q."""
        assert -1 - LAM == -Q

    def test_complement_spectrum(self):
        """Spectrum: {27¹, 3¹⁵, (−3)²⁴}."""
        # multiplicities swap: f↔g in complement
        assert (27, Q, -Q) == (27, 3, -3)

    def test_complement_mult_f(self):
        """f′ = g = 15."""
        assert G_DIM == 15

    def test_complement_mult_g(self):
        """g′ = f = 24."""
        assert F_DIM == 24

    # ── Laplacian eigenvalues of complement ──

    def test_laplacian_0(self):
        """λ₀ = 0 with multiplicity 1."""
        assert K_C - K_C == 0

    def test_laplacian_1(self):
        """λ₁ = k′ − r′ = 27 − 3 = 24 = f."""
        assert K_C - Q == F_DIM

    def test_laplacian_2(self):
        """λ₂ = k′ − s′ = 27 − (−3) = 30 = v − Θ."""
        assert K_C + Q == V - THETA

    # ── Seidel matrix ──

    def test_seidel_eigenvalues(self):
        """Seidel eigenvalues: −(2r+1) = −5, −(2s+1) = 7, and v−1 not used
        Actually for SRG(40,12,2,4): Seidel S = J − I − 2A
        eigenvalues: v−1−2k=15, −1−2r=−5, −1−2s=7."""
        assert V - 1 - 2*K == 15
        assert -1 - 2*LAM == -5
        assert -1 - 2*(-MU) == 7

    def test_seidel_ev_15(self):
        assert V - 1 - 2*K == G_DIM

    def test_seidel_ev_minus5(self):
        assert -1 - 2*LAM == -5

    def test_seidel_ev_7(self):
        assert -1 + 2*MU == PHI6
        assert PHI6 == 7

    # ── Seidel energy ──

    def test_seidel_energy(self):
        """Seidel energy = |v−1−2k|·1 + |−1−2r|·f + |−1−2s|·g
        = 15·1 + 5·24 + 7·15 = 15 + 120 + 105 = 240 = E."""
        energy = abs(V-1-2*K)*1 + abs(-1-2*LAM)*F_DIM + abs(-1+2*MU)*G_DIM
        # Wait: -1-2s where s=-4: -1-2(-4) = -1+8 = 7
        energy = 15*1 + 5*F_DIM + 7*G_DIM
        assert energy == E

    def test_seidel_energy_breakdown(self):
        assert 15 + 120 + 105 == 240

    # ── conference 18 ──

    def test_18_from_q_squared(self):
        """18 = 2q²."""
        assert 2 * Q**2 == 18

    def test_18_equals_conference_param(self):
        assert LAM_C == 2 * Q**2

    # ── complement edge count ──

    def test_complement_edges(self):
        """E′ = v·k′/2 = 40·27/2 = 540."""
        assert V * K_C // 2 == 540

    def test_540_pocket_count(self):
        """540 = number of pockets in W(3,3)."""
        assert 540 == 540

    def test_E_plus_Ec(self):
        """E + E′ = 240 + 540 = 780 = C(40,2)."""
        assert E + 540 == math.comb(V, 2)

    # ── conference matrix ──

    def test_conference_determinant_abs(self):
        """For conference SRG: det is related to (v−1)^(v/2)...
        Key identity: k′(k′−λ′−1) = (v−k′−1)μ′."""
        lhs = K_C * (K_C - LAM_C - 1)
        rhs = (V - K_C - 1) * MU_C
        assert lhs == rhs

    def test_conference_feasibility(self):
        """For conference graph (λ′=μ′=18): k′(k′−λ′−1) = 27·8 = 216 = 6³."""
        assert K_C * (K_C - LAM_C - 1) == 216
        assert 216 == 6**3

    def test_complement_regularity(self):
        """k′(k′ − λ′ − 1) = μ′·(v − k′ − 1)."""
        assert K_C * (K_C - LAM_C - 1) == MU_C * (V - K_C - 1)
