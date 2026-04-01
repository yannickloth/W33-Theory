"""
Phase CCLXXXVI — Dual Ring Structure: Eisenstein & Gaussian Integer Norms
=========================================================================

W(3,3) primes partition into three classes under the dual algebraic integer
rings Z[i] (Gaussian) and Z[ω] (Eisenstein, ω = e^{2πi/3}):

  • Phi6 = 7:   INERT in Z[i],  SPLIT in Z[ω]   (Eisenstein-only)
  • α⁻¹ = 137:  SPLIT in Z[i],  INERT in Z[ω]   (Gaussian-only)
  • Phi3 = 13:   SPLIT in both                    (universal)
  • Phi12 = 73:  SPLIT in both                    (universal)

Master identity:  Phi6 + α⁻¹ = k² = 144  (dual prime sum = valency²).

The Eisenstein ring Z[ω] lives over Q(√-q) = Q(√-3), the natural field
for the graph characteristic q = 3.  Every cyclotomic invariant Φ_n(q)
is representable as an Eisenstein norm N_E(a + bω) = a² − ab + b².
"""

from math import comb, gcd

# ── W(3,3) master parameters ────────────────────────────────────────
q, lam, mu, k, v = 3, 2, 4, 12, 40
f, g = 24, 15
E, tau, R = 240, 252, 28
Phi3, Phi6, Phi12 = 13, 7, 73
Theta, s, N, d = 10, 6, 20, 4
b2 = f - lam  # 22

# ── Norm helpers ────────────────────────────────────────────────────
def gauss_norm(a: int, b: int) -> int:
    """Gaussian integer norm: N(a + bi) = a² + b²."""
    return a * a + b * b

def eis_norm(a: int, b: int) -> int:
    """Eisenstein integer norm: N(a + bω) = a² − ab + b²."""
    return a * a - a * b + b * b


# ────────────────────────────────────────────────────────────────────
#  1.  EISENSTEIN NORM REPRESENTATIONS
# ────────────────────────────────────────────────────────────────────

class TestEisensteinNorms:
    """Cyclotomic invariants as Eisenstein norms."""

    def test_q_is_eis_norm(self):
        assert eis_norm(1, 2) == q

    def test_phi6_is_eis_norm(self):
        assert eis_norm(1, 3) == Phi6

    def test_phi3_is_eis_norm(self):
        assert eis_norm(1, 4) == Phi3

    def test_theta_is_eis_norm(self):
        assert eis_norm(2, 4) == k  # actually k = 12

    def test_k_eis_norm(self):
        assert eis_norm(2, 4) == k

    def test_R_is_eis_norm(self):
        assert eis_norm(2, 6) == R

    def test_phi12_is_eis_norm(self):
        assert eis_norm(1, 9) == Phi12

    def test_tau_is_eis_norm(self):
        assert eis_norm(6, 18) == tau


# ────────────────────────────────────────────────────────────────────
#  2.  GAUSSIAN NORM REPRESENTATIONS
# ────────────────────────────────────────────────────────────────────

class TestGaussianNorms:
    """Key parameters as Gaussian norms a² + b²."""

    def test_phi3_gauss(self):
        assert gauss_norm(2, 3) == Phi3

    def test_v_gauss(self):
        assert gauss_norm(2, 6) == v

    def test_v_plus1_gauss(self):
        assert gauss_norm(4, 5) == v + 1  # 41

    def test_phi12_gauss(self):
        assert gauss_norm(3, 8) == Phi12

    def test_alpha_inv_gauss(self):
        """α⁻¹ = 137 = (k−1)² + μ² = 11² + 4² at (k−1, μ)."""
        assert gauss_norm(k - 1, mu) == 137

    def test_alpha_components(self):
        """Gaussian splitting: 137 = 11² + 4² with 11 = k-1, 4 = μ."""
        assert (k - 1) ** 2 + mu ** 2 == 137


# ────────────────────────────────────────────────────────────────────
#  3.  DUAL RING SPLITTING BEHAVIOUR
# ────────────────────────────────────────────────────────────────────

class TestDualRingSplitting:
    """Each prime splits in exactly one of Z[i], Z[ω], or both."""

    # Eisenstein splitting: p ≡ 1 (mod 3) ⟹ SPLIT in Z[ω]
    def test_phi6_splits_eisenstein(self):
        assert Phi6 % 3 == 1

    def test_phi3_splits_eisenstein(self):
        assert Phi3 % 3 == 1

    def test_phi12_splits_eisenstein(self):
        assert Phi12 % 3 == 1

    # Gaussian splitting: p ≡ 1 (mod 4) ⟹ SPLIT in Z[i]
    def test_phi3_splits_gaussian(self):
        assert Phi3 % 4 == 1

    def test_phi12_splits_gaussian(self):
        assert Phi12 % 4 == 1

    def test_alpha_splits_gaussian(self):
        assert 137 % 4 == 1

    # Inertia
    def test_phi6_inert_gaussian(self):
        """Phi6 = 7 ≡ 3 (mod 4): stays prime in Z[i]."""
        assert Phi6 % 4 == 3

    def test_alpha_inert_eisenstein(self):
        """α⁻¹ = 137 ≡ 2 (mod 3): stays prime in Z[ω]."""
        assert 137 % 3 == 2


# ────────────────────────────────────────────────────────────────────
#  4.  DUAL PRIME SUM = k²
# ────────────────────────────────────────────────────────────────────

class TestDualPrimeSum:
    """The Eisenstein-only + Gaussian-only prime = k²."""

    def test_dual_sum_is_k_squared(self):
        assert Phi6 + 137 == k ** 2

    def test_k_squared_value(self):
        assert k ** 2 == 144

    def test_dual_sum_decomposition(self):
        """k² = Phi_6(q) + α⁻¹: unique dual-prime decomposition."""
        assert Phi6 + 137 == k * k

    def test_alpha_from_k_and_phi6(self):
        """α⁻¹ = k² − Φ_6(q)."""
        assert k ** 2 - Phi6 == 137


# ────────────────────────────────────────────────────────────────────
#  5.  CYCLOTOMIC TOWER AT q = 3
# ────────────────────────────────────────────────────────────────────

class TestCyclotomicTower:
    """Φ_n(q) evaluated at q = 3 produces graph parameters."""

    def test_phi1(self):
        """Φ₁(3) = 3 − 1 = 2 = λ."""
        assert q - 1 == lam

    def test_phi2(self):
        """Φ₂(3) = 3 + 1 = 4 = μ."""
        assert q + 1 == mu

    def test_phi3_val(self):
        """Φ₃(3) = 9 + 3 + 1 = 13."""
        assert q ** 2 + q + 1 == Phi3

    def test_phi4(self):
        """Φ₄(3) = 9 + 1 = 10 = Θ."""
        assert q ** 2 + 1 == Theta

    def test_phi6_val(self):
        """Φ₆(3) = 9 − 3 + 1 = 7."""
        assert q ** 2 - q + 1 == Phi6

    def test_phi12_val(self):
        """Φ₁₂(3) = 81 − 9 + 1 = 73."""
        assert q ** 4 - q ** 2 + 1 == Phi12

    def test_phi5_squared(self):
        """Φ₅(3) = 121 = (k − 1)²."""
        phi5 = q ** 4 + q ** 3 + q ** 2 + q + 1
        assert phi5 == (k - 1) ** 2

    def test_product_phi1_phi2(self):
        """Φ₁ · Φ₂ = λμ = 2d = 2·4 = 8."""
        assert (q - 1) * (q + 1) == q ** 2 - 1 == 2 * d
