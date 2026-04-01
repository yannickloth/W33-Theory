"""
Phase CCLXXXVIII — String Theory Dimensions & Compactification
==============================================================

Every critical dimension, compactification radius, central charge, and
spinor structure of string/M-theory is a W(3,3) parameter:

  D_bosonic   = 26 = f + λ       (transverse d.o.f. = f = 24)
  D_super     = 10 = Θ = Φ₄(q)  (transverse d.o.f. = 2d = 8)
  D_M-theory  = 11 = k − 1

Compactification to 4D:
  26 → 4:  22 = b₂(K3) compact dimensions
  10 → 4:   6 = s compact dimensions (Calabi-Yau₃)
  11 → 4:   7 = Φ₆ compact dimensions (G₂ manifold)
  26 → 10: 16 = μ² = 2^d (Heterotic gap → E₈×E₈ root lattice rank)

Virasoro central charges:
  c_bosonic = 26 = f + λ,   c_ghost = −(f + λ)
  c_super   = 15 = g,       c_ghost = −g

The heterotic string's E₈×E₈ gauge group yields:
  dim(E₈) = 248 = E + 2d,  rank(E₈×E₈) = 16 = μ²,
  dim(E₈×E₈) = 496 = λ · dim(E₈) = 3rd perfect number.
"""

from math import comb
from fractions import Fraction

# ── W(3,3) master parameters ────────────────────────────────────────
q, lam, mu, k, v = 3, 2, 4, 12, 40
f, g = 24, 15
E, tau, R = 240, 252, 28
Phi3, Phi6, Phi12 = 13, 7, 73
Theta, s, N, d = 10, 6, 20, 4
b2 = f - lam  # 22


# ────────────────────────────────────────────────────────────────────
#  1.  CRITICAL DIMENSIONS
# ────────────────────────────────────────────────────────────────────

class TestCriticalDimensions:
    """String/M-theory critical dimensions from W(3,3)."""

    def test_bosonic_dim(self):
        """D_bosonic = 26 = f + λ."""
        assert f + lam == 26

    def test_bosonic_alt(self):
        """26 = R − λ = C(2d,2) − λ."""
        assert R - lam == 26
        assert comb(2 * d, 2) - lam == 26

    def test_superstring_dim(self):
        """D_super = 10 = Θ = Φ₄(q)."""
        assert Theta == 10
        assert q ** 2 + 1 == Theta

    def test_m_theory_dim(self):
        """D_M = 11 = k − 1."""
        assert k - 1 == 11

    def test_physical_spacetime(self):
        """D = 4 = d = |s_neg|."""
        assert d == 4


# ────────────────────────────────────────────────────────────────────
#  2.  COMPACTIFICATION DIMENSIONS
# ────────────────────────────────────────────────────────────────────

class TestCompactification:
    """Every compact dimension count is a W(3,3) parameter."""

    def test_bosonic_to_4d(self):
        """26 − 4 = 22 = b₂(K3) = f − λ."""
        assert (f + lam) - d == b2

    def test_super_to_4d(self):
        """10 − 4 = 6 = s  (Calabi-Yau₃)."""
        assert Theta - d == s

    def test_m_to_4d(self):
        """11 − 4 = 7 = Φ₆  (G₂ manifold)."""
        assert (k - 1) - d == Phi6

    def test_bosonic_to_super(self):
        """26 − 10 = 16 = μ² = 2^d  (Heterotic gap)."""
        assert (f + lam) - Theta == mu ** 2

    def test_mu_sq_is_2d(self):
        assert mu ** 2 == 2 ** d


# ────────────────────────────────────────────────────────────────────
#  3.  VIRASORO CENTRAL CHARGES
# ────────────────────────────────────────────────────────────────────

class TestCentralCharges:
    """Central charges for bosonic and super strings."""

    def test_bosonic_matter(self):
        """c_matter = 26 = f + λ."""
        assert f + lam == 26

    def test_bosonic_ghost(self):
        """c_ghost = −26 = −(f + λ)."""
        assert -(f + lam) == -26

    def test_bosonic_anomaly_free(self):
        """c_matter + c_ghost = 0."""
        assert (f + lam) + (-(f + lam)) == 0

    def test_super_matter(self):
        """c_super(NS) = 15 = g."""
        assert g == 15

    def test_super_ghost(self):
        """c_ghost = −15 = −g."""
        assert -g == -15

    def test_super_anomaly_free(self):
        assert g + (-g) == 0

    def test_super_r_sector(self):
        """Ramond sector central charge = Θ = 10."""
        assert Theta == 10


# ────────────────────────────────────────────────────────────────────
#  4.  TRANSVERSE POLARISATIONS
# ────────────────────────────────────────────────────────────────────

class TestTransversePolarisations:
    """Transverse d.o.f. = D − 2 for each theory."""

    def test_bosonic_transverse(self):
        """26 − 2 = 24 = f = rank(Leech lattice)."""
        assert (f + lam) - lam == f

    def test_super_transverse(self):
        """10 − 2 = 8 = 2d."""
        assert Theta - lam == 2 * d

    def test_physical_transverse(self):
        """4 − 2 = 2 = λ."""
        assert d - lam == lam  # in 4D d = 4, but really d-2=2=lam

    def test_transverse_bosonic_is_leech_rank(self):
        """The 24 transverse modes ↔ rank-24 Leech lattice."""
        assert f == 24


# ────────────────────────────────────────────────────────────────────
#  5.  HETEROTIC STRING & E₈
# ────────────────────────────────────────────────────────────────────

class TestHeteroticString:
    """E₈ × E₈ structure from W(3,3)."""

    def test_e8_dim(self):
        """dim(E₈) = E + 2d = 240 + 8 = 248."""
        assert E + 2 * d == 248

    def test_e8_rank(self):
        """rank(E₈) = 2d = 8."""
        assert 2 * d == 8

    def test_e8e8_rank(self):
        """rank(E₈ × E₈) = 2 · 2d = μ² = 16."""
        assert 2 * (2 * d) == mu ** 2

    def test_e8e8_dim(self):
        """dim(E₈ × E₈) = 496 = λ · dim(E₈)."""
        assert lam * (E + 2 * d) == 496

    def test_496_is_perfect(self):
        """496 is the 3rd perfect number: σ(496) = 2 · 496."""
        from sympy import divisor_sigma
        assert int(divisor_sigma(496, 1)) == 2 * 496

    def test_heterotic_gap(self):
        """Left − right = 26 − 10 = μ² = rank(E₈ × E₈)."""
        assert (f + lam) - Theta == mu ** 2
        assert mu ** 2 == 2 * (2 * d)


# ────────────────────────────────────────────────────────────────────
#  6.  SPINOR DIMENSIONS
# ────────────────────────────────────────────────────────────────────

class TestSpinorDimensions:
    """Spinor representations at each critical dimension."""

    def test_weyl_4d(self):
        """4D Weyl spinor: 2^(d/2−1) = 2 = λ."""
        assert 2 ** (d // 2 - 1) == lam

    def test_weyl_10d(self):
        """10D Weyl spinor: 2^(Θ/2−1) = 2⁴ = μ²."""
        assert 2 ** (Theta // 2 - 1) == mu ** 2

    def test_spinor_11d(self):
        """11D spinor: 2^((k−1−1)/2) = 2⁵ = 2μ²."""
        assert 2 ** ((k - 2) // 2) == 2 * mu ** 2

    def test_n1_susy_10d(self):
        """N=1 SUSY in 10D: μ² = 16 supercharges."""
        assert mu ** 2 == 16

    def test_maximal_susy_4d(self):
        """N=8 in 4D = N=1 in 11D: 2μ² = 32 supercharges."""
        assert 2 * mu ** 2 == 32


# ────────────────────────────────────────────────────────────────────
#  7.  LEECH LATTICE SHELLS
# ────────────────────────────────────────────────────────────────────

class TestLeechShells:
    """Kissing numbers of successive Leech shells from W(3,3)."""

    def test_shell1(self):
        """196 560 = E · q² · Φ₆ · Φ₃."""
        assert E * q ** 2 * Phi6 * Phi3 == 196_560

    def test_shell2(self):
        """16 773 120 = 2^k · (2^k − 1)."""
        assert 2 ** k * (2 ** k - 1) == 16_773_120

    def test_shell3(self):
        """398 034 000 = shell₁ · C(Θ,2)²."""
        shell1 = E * q ** 2 * Phi6 * Phi3
        assert shell1 * comb(Theta, 2) ** 2 == 398_034_000

    def test_shell_ratio_21(self):
        """shell₂ / shell₁ = μ^d / q = 256/3."""
        assert Fraction(2 ** k * (2 ** k - 1),
                        E * q ** 2 * Phi6 * Phi3) == Fraction(mu ** d, q)

    def test_shell_ratio_31(self):
        """shell₃ / shell₁ = C(Θ,2)² = dim(SO(10))²."""
        assert Fraction(398_034_000, 196_560) == comb(Theta, 2) ** 2


# ────────────────────────────────────────────────────────────────────
#  8.  MODULAR FORM DIMENSIONS
# ────────────────────────────────────────────────────────────────────

class TestModularFormDimensions:
    """dim M_w and dim S_w on SL(2,ℤ) at graph weights."""

    def _dim_M(self, w: int) -> int:
        """Dimension of M_w(SL₂ℤ) for even w ≥ 2."""
        if w == 2:
            return 0
        if w % 12 == 2:
            return w // 12
        return w // 12 + 1

    def test_dim_M_k_is_lambda(self):
        """dim M_12 = 2 = λ."""
        assert self._dim_M(k) == lam

    def test_dim_S_k_is_one(self):
        """dim S_12 = 1  (Δ is the unique weight-12 cusp form)."""
        assert self._dim_M(k) - 1 == 1

    def test_dim_M_f_is_q(self):
        """dim M_24 = 3 = q."""
        assert self._dim_M(f) == q

    def test_dim_S_f_is_lambda(self):
        """dim S_24 = 2 = λ."""
        assert self._dim_M(f) - 1 == lam

    def test_dim_M_3k_is_mu(self):
        """dim M_36 = 4 = μ."""
        assert self._dim_M(3 * k) == mu

    def test_weight_of_delta(self):
        """Δ = η^f has weight f/2 = k."""
        assert f // 2 == k
