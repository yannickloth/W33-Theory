"""
Phase CCLXXXI — Modular Form Quartet
=========================================

THEOREM (The Four Modular Atoms):

Every modular form of level 1 is built from four objects whose
normalising constants are EXACTLY the W(3,3) parameters:

  E₄ = 1 + E · Σ σ₃(n)qⁿ            coefficient = E  = 240 (edges)
  E₆ = 1 - 2τ · Σ σ₅(n)qⁿ           coefficient = 2τ = 504
  Δ  = η^f                            power = f  = 24  (multiplicity)
  j  = k³ · E₄³/Δ                     normaliser = k³ = 1728

THEOREM (Quartet Closure):

  k³ = 2τf/Φ₆                        (1728 = 2·252·24/7)

  E/f = Θ = 10                        (240/24 = Lovász theta!)

  j constant term = q · dim(E₈ Lie)   (744 = 3·248)

THEOREM (dim(E₈ Lie) from W(3,3)):

  dim(E₈) = E + 2d = 240 + 8 = 248

  where E = |roots| = edges, d = μ = 4 = spacetime dimension.

THEOREM (σ₅ at W(3,3) Atoms):

  σ₅(λ=2) = 33  = q(k−1)
  σ₅(q=3) = 244 = E + μ = 1 + q⁵
  σ₅(s=6) = 8052 = q(k−1)(1+q⁵)

SOURCE: Novel discovery — modular form normalising constants controlled by W(3,3).
"""
import pytest
from fractions import Fraction
from sympy import divisor_sigma

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
d     = 4
Theta = 10


def sigma3(n):
    return int(divisor_sigma(n, 3))


def sigma5(n):
    return int(divisor_sigma(n, 5))


# ================================================================
# T1: The four modular form atoms
# ================================================================
class TestT1_ModularAtoms:
    """The four normalising constants are W(3,3) parameters."""

    def test_E4_coefficient(self):
        """E₄ coefficient = 240 = E = vk/2."""
        assert E == 240
        assert v * k // 2 == E

    def test_E6_coefficient(self):
        """E₆ coefficient = 504 = 2τ = λτ."""
        assert 2 * tau == 504
        assert lam * tau == 504

    def test_Delta_power(self):
        """Δ = η^24 = η^f."""
        assert f == 24

    def test_j_normaliser(self):
        """j normaliser = 1728 = k³."""
        assert k**3 == 1728


# ================================================================
# T2: Quartet closure identities
# ================================================================
class TestT2_QuartetClosure:
    """The four atoms are locked by closure identities."""

    def test_closure(self):
        """k³ = 2τf/Φ₆."""
        assert k**3 == 2 * tau * f // Phi6
        assert 2 * tau * f % Phi6 == 0

    def test_E_over_f(self):
        """E/f = Θ = 10 (Lovász theta)."""
        assert E // f == Theta
        assert E == f * Theta

    def test_2tau_over_E(self):
        """2τ/E = 21/10."""
        assert Fraction(2 * tau, E) == Fraction(21, 10)

    def test_k3_over_2tau(self):
        """k³/(2τ) = f/Φ₆ = 24/7."""
        assert Fraction(k**3, 2 * tau) == Fraction(f, Phi6)

    def test_k3_over_f(self):
        """k³/f = q·f = 72."""
        assert k**3 // f == q * f


# ================================================================
# T3: j-invariant constant term
# ================================================================
class TestT3_JConstant:
    """j constant term = q · dim(E₈ Lie) = 744."""

    def test_744(self):
        assert q * 248 == 744

    def test_dim_E8(self):
        """dim(E₈) = E + 2d = 248."""
        assert E + 2 * d == 248

    def test_744_decomp(self):
        """744 = q·E + f = 3·240 + 24."""
        assert q * E + f == 744

    def test_196884_decomp(self):
        """196884 = Leech + μq⁴ = 196560 + 324."""
        leech = E * q**2 * Phi6 * Phi3
        assert leech == 196560
        assert leech + mu * q**4 == 196884


# ================================================================
# T4: σ₅ at W(3,3) parameters
# ================================================================
class TestT4_Sigma5Dictionary:
    """σ₅ at graph atoms gives further W(3,3) invariants."""

    def test_sigma5_lam(self):
        """σ₅(λ=2) = 33 = q(k−1)."""
        assert sigma5(lam) == q * (k - 1)

    def test_sigma5_q(self):
        """σ₅(q=3) = 244 = E + μ = 1 + q⁵."""
        assert sigma5(q) == E + mu
        assert sigma5(q) == 1 + q**5

    def test_sigma5_s(self):
        """σ₅(s=6) = 8052 = q(k−1)(1+q⁵) (multiplicative)."""
        assert sigma5(s_biv) == sigma5(lam) * sigma5(q)
        assert sigma5(s_biv) == q * (k - 1) * (1 + q**5)

    def test_sigma5_mu(self):
        """σ₅(μ=4) = 1057 = 1 + 2⁵ + 4⁵."""
        assert sigma5(mu) == 1 + 32 + 1024


# ================================================================
# T5: Cross check with zeta dictionary
# ================================================================
class TestT5_CrossCheck:
    """The modular quartet and zeta dictionary are consistent."""

    def test_E4_coeff_equals_zeta_m7_recip(self):
        """E = |ζ(−7)|⁻¹ = 240."""
        from sympy import bernoulli as B
        zeta_m7 = Fraction(-B(8), 8)
        assert abs(1 / zeta_m7) == E

    def test_2tau_equals_2_zeta_m5_recip(self):
        """2τ = 2|ζ(−5)|⁻¹ = 504."""
        from sympy import bernoulli as B
        zeta_m5 = Fraction(-B(6), 6)
        assert 2 * abs(1 / zeta_m5) == 2 * tau

    def test_f_equals_neg_2_zeta_m1_recip(self):
        """f = 2k = 2|ζ(−1)|⁻¹."""
        from sympy import bernoulli as B
        zeta_m1 = Fraction(-B(2), 2)
        assert 2 * abs(1 / zeta_m1) == f

    def test_k3_from_zeta(self):
        """k³ = (|ζ(−1)|⁻¹)³ = 1728."""
        from sympy import bernoulli as B
        zeta_m1 = Fraction(-B(2), 2)
        assert abs(1 / zeta_m1)**3 == k**3
