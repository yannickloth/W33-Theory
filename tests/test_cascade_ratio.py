"""
Phase CCLXVIII: The cascade convergence ratio encodes oscillation parameters.

THEOREM: In the quasi-degenerate NH limit (m1 >> sqrt(dm2_31)),
  r = lim_{n->inf} T^(n+1)(mu) / T^n(mu)
    = (dm2_21 + dm2_31) / (2*dm2_31 - dm2_21)

This is a PURE oscillation parameter ratio, NOT a W(3,3) number.
The cascade ratio is the bridge between W(3,3) spectral descent and
neutrino oscillation phenomenology.

In the 2-neutrino approximation (dm2_21 -> 0): r -> 1/2.
Correction (EXACT): r - 1/2 = 3*dm2_21 / (2*(2*dm2_31 - dm2_21)).
  NOTE: NOT (3/2)*dm2_21 / (...); the correct prefactor is 3, not 3/2.
  Derivation: r - 1/2 = (A+B)/(2B-A) - 1/2 = 3A/[2(2B-A)] where A=dm2_21, B=dm2_31.
"""

from math import sqrt, log
import numpy as np
from scipy.optimize import brentq
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
dm2_21 = 7.42e-5
dm2_31_NH = 2.517e-3

r_analytic = (dm2_21 + dm2_31_NH) / (2*dm2_31_NH - dm2_21)


def get_masses_NH(m1): return np.array([m1, sqrt(m1**2+dm2_21), sqrt(m1**2+dm2_31_NH)])
def mu_eff_sq(masses):
    x = masses / masses.max()
    return -log(np.prod(x)**(1/3)) / log(Phi4)
def solve_NH(target): return brentq(lambda m1: mu_eff_sq(get_masses_NH(m1))-target, 1e-6, 0.9999)
def cascade_step(mu): return mu_eff_sq(1.0/get_masses_NH(solve_NH(mu)))


class TestCascadeRatio:

    def test_analytic_ratio_formula(self):
        assert abs(r_analytic - 0.5224) < 0.001

    def test_numerical_limit_matches_analytic(self):
        mu = 1.0/m
        for _ in range(8): mu = cascade_step(mu)
        ratios = []
        for _ in range(3):
            mu_new = cascade_step(mu); ratios.append(mu_new/mu); mu = mu_new
        assert abs(ratios[-1] - r_analytic) < 5e-4

    def test_2nu_limit_half(self):
        r_2nu = dm2_31_NH / (2*dm2_31_NH)
        assert abs(r_2nu - 0.5) < 1e-10

    def test_solar_correction(self):
        """r - 1/2 = 3*dm2_21 / (2*(2*dm2_31 - dm2_21))  [EXACT]."""
        A, B = dm2_21, dm2_31_NH
        correction = 3*A / (2*(2*B - A))
        assert abs(r_analytic - 0.5 - correction) < 1e-12

    def test_ratio_encodes_oscillations(self):
        A = (dm2_31_NH/3-dm2_21/6)/log(Phi4); B=(dm2_21+dm2_31_NH)/6/log(Phi4)
        r1=B/A; A2=(dm2_31_NH/3-dm2_21/6)/log(13); B2=(dm2_21+dm2_31_NH)/6/log(13)
        r2=B2/A2; assert abs(r1-r2)<1e-10; assert abs(r1-r_analytic)<1e-10
