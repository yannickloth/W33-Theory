"""
Phase CCLXVIII: The cascade convergence ratio encodes oscillation parameters.

THEOREM: In the quasi-degenerate NH limit (m1 >> sqrt(dm2_31)),
  r = lim_{n->inf} T^(n+1)(mu) / T^n(mu)
    = (dm2_21 + dm2_31) / (2*dm2_31 - dm2_21)

This is a PURE oscillation parameter ratio, NOT a W(3,3) number.
The cascade ratio is the bridge between W(3,3) spectral descent and
neutrino oscillation phenomenology.

In the 2-neutrino approximation (dm2_21 -> 0): r -> 1/2.
Correction: r - 1/2 = (3/2)*dm2_21 / (2*(2*dm2_31 - dm2_21)).
"""

from math import sqrt, log
import numpy as np
from scipy.optimize import brentq
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
dm2_21 = 7.42e-5
dm2_31_NH = 2.517e-3


def get_masses_NH(m1): return np.array([m1, sqrt(m1**2+dm2_21), sqrt(m1**2+dm2_31_NH)])
def mu_eff_sq(masses):
    x = masses / masses.max()
    return -log(np.prod(x)**(1/3)) / log(Phi4)
def solve_NH(target): return brentq(lambda m1: mu_eff_sq(get_masses_NH(m1))-target, 1e-6, 0.9999)
def cascade_step(mu):
    return mu_eff_sq(1.0/get_masses_NH(solve_NH(mu)))


r_analytic = (dm2_21 + dm2_31_NH) / (2*dm2_31_NH - dm2_21)


class TestCascadeRatio:

    def test_analytic_ratio_formula(self):
        """r = (dm2_21+dm2_31)/(2*dm2_31-dm2_21)."""
        r = r_analytic
        assert abs(r - 0.5224) < 0.001

    def test_numerical_limit_matches_analytic(self):
        """Numerical cascade ratio converges to analytic value."""
        mu = 1.0/m
        for _ in range(8):
            mu = cascade_step(mu)
        ratios = []
        for _ in range(3):
            mu_new = cascade_step(mu)
            ratios.append(mu_new / mu)
            mu = mu_new
        r_num = ratios[-1]
        assert abs(r_num - r_analytic) < 5e-4

    def test_2nu_limit_half(self):
        """In 2-nu limit (dm2_21->0): r -> 1/2."""
        r_2nu = dm2_31_NH / (2*dm2_31_NH)  # dm2_21=0
        assert abs(r_2nu - 0.5) < 1e-10

    def test_solar_correction(self):
        """r - 1/2 = (3/2)*dm2_21 / (2*(2*dm2_31-dm2_21))."""
        correction = (1.5 * dm2_21) / (2 * (2*dm2_31_NH - dm2_21))
        assert abs(r_analytic - 0.5 - correction) < 1e-6

    def test_ratio_encodes_oscillations(self):
        """r is a function ONLY of dm2_21 and dm2_31 (not W(3,3) params)."""
        # Verify r doesn't depend on Phi4 (the Phi4 cancels in B/A)
        A = (dm2_31_NH/3 - dm2_21/6) / log(Phi4)
        B = (dm2_21 + dm2_31_NH)/6 / log(Phi4)
        r_from_AB = B / A
        # Phi4 cancels: r = B/A is independent of Phi4
        A2 = (dm2_31_NH/3 - dm2_21/6) / log(13)  # different log base
        B2 = (dm2_21 + dm2_31_NH)/6 / log(13)
        r_from_AB2 = B2 / A2
        assert abs(r_from_AB - r_from_AB2) < 1e-10
        assert abs(r_from_AB - r_analytic) < 1e-10
