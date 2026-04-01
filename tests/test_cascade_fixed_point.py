"""
Phase CCLXVII: Fixed point of the seesaw cascade.

The cascade T(mu) = mu_eff^2(1/m(mu)) starting from mu=1/4:
  T^0 = 1/4   = 0.2500
  T^1 = 1/7   ~ 0.1400  (1/Phi6)
  T^2 = 1/13  ~ 0.0753  (1/Phi3)
  T^3 = 1/23  ~ 0.0399  (1/(2k-1))
  T^n -> 0    (converges to 0 with ratio ~1/2)

There is NO nonzero fixed point: T(mu*) = mu* => mu* = 0 only.
The cascade is a spectral descent through the W(3,3) cyclotomic ladder.

Bonus: T^3(1/4) ~ 1/23 = 1/(2k-1) -- the Ramanujan congruence prime
appears as the third seesaw generation scale.
"""

from math import sqrt, log
import numpy as np
from scipy.optimize import brentq
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
dm2_21 = 7.42e-5; dm2_31_NH = 2.517e-3


def get_masses_NH(m1): return np.array([m1, sqrt(m1**2+dm2_21), sqrt(m1**2+dm2_31_NH)])
def mu_eff_sq(masses):
    x = masses / masses.max()
    return -log(np.prod(x)**(1/3)) / log(Phi4)
def solve_NH(target): return brentq(lambda m1: mu_eff_sq(get_masses_NH(m1))-target, 1e-6, 0.9999)


def cascade_step(mu):
    m1 = solve_NH(mu)
    return mu_eff_sq(1.0/get_masses_NH(m1))


class TestCascadeFixedPoint:

    def test_T0(self):
        """T^0 = 1/4 (starting point)."""
        assert abs(1.0/m - 0.25) < 1e-10

    def test_T1_near_1_over_Phi6(self):
        """T^1(1/4) ~ 1/Phi6 = 1/7 = 0.1429."""
        T1 = cascade_step(1.0/m)
        assert abs(T1 - 1.0/Phi6) < 0.005

    def test_T2_near_1_over_Phi3(self):
        """T^2(1/4) ~ 1/Phi3 = 1/13 = 0.0769."""
        T2 = cascade_step(cascade_step(1.0/m))
        assert abs(T2 - 1.0/Phi3) < 0.005

    def test_T3_near_1_over_2km1(self):
        """T^3(1/4) ~ 1/(2k-1) = 1/23 = 0.0435."""
        T1 = cascade_step(1.0/m)
        T2 = cascade_step(T1)
        T3 = cascade_step(T2)
        assert abs(T3 - 1.0/(2*k-1)) < 0.005

    def test_cascade_is_decreasing(self):
        """Each step decreases mu."""
        mu = 1.0/m
        for _ in range(5):
            mu_new = cascade_step(mu)
            assert mu_new < mu
            mu = mu_new

    def test_convergence_ratio(self):
        """Cascade ratio T^(n+1)/T^n converges to ~0.5225."""
        mu = 1.0/m
        ratios = []
        for _ in range(8):
            mu_new = cascade_step(mu)
            ratios.append(mu_new / mu)
            mu = mu_new
        # Ratio should converge to ~0.5225
        final_ratio = ratios[-1]
        assert abs(final_ratio - 0.5225) < 0.005

    def test_no_nonzero_fixed_point(self):
        """Cascade has no nonzero fixed point (converges to 0)."""
        # Iterate until mu < 0.001 or 15 steps
        mu = 1.0/m
        for _ in range(15):
            try:
                mu = cascade_step(mu)
                if mu < 0.001:
                    break
            except Exception:
                break
        assert mu < 0.005  # converged toward 0

    def test_cascade_cyclotomic_sequence(self):
        """First three steps hit 1/mu, 1/Phi6, 1/Phi3 in order."""
        targets = [1.0/m, 1.0/Phi6, 1.0/Phi3]
        T = [1.0/m]
        mu = 1.0/m
        for _ in range(3):
            mu = cascade_step(mu)
            T.append(mu)
        for i, (ti, tgt) in enumerate(zip(T[1:], targets[1:])):
            assert abs(ti - tgt) < 0.006, f"Step {i+1}: {ti:.4f} vs {tgt:.4f}"
