"""
Phase CCLXX: The seesaw cascade is NOT a clean Phi6 tower walk.

Empirical result:
  T^0 = 1/4                          = 1/mu            [exact]
  T^1 = 0.1400  ~ 1/7                = 1/Phi6(3)       [near-exact]
  T^2 = 0.0753  ~ 1/13               = 1/Phi3(3)       [near-exact]
  T^3 = 0.0399  ~ 1/23               = 1/(2k-1)        [closer than 1/Phi6(5)=1/21]
  T^n -> 0 with ratio r = 0.52244...

So the cascade hits W(3,3) named values for the FIRST TWO steps only:
  1/mu -> 1/Phi6 -> 1/Phi3 -> asymptotic descent

It is NOT a walk along the integer Phi6(q) tower. The apparent match at T^2
arises because Phi3(3) = 13 = Phi6(4).
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
def cascade_step(mu): return mu_eff_sq(1.0/get_masses_NH(solve_NH(mu)))
def Phi6_q(qq): return qq**2 - qq + 1


class TestPhi6Tower:

    def test_T1_near_Phi6_3(self):
        """T^1(1/4) ~ 1/Phi6(3) = 1/7."""
        T1 = cascade_step(1.0/m)
        assert abs(T1 - 1.0/Phi6_q(3)) < 0.005

    def test_T2_near_Phi6_4(self):
        """T^2(1/4) ~ 1/Phi6(4) = 1/13 = 1/Phi3(3)."""
        T2 = cascade_step(cascade_step(1.0/m))
        assert abs(T2 - 1.0/Phi6_q(4)) < 0.005
        assert Phi6_q(4) == Phi3  # = 13

    def test_T3_closer_to_23_than_Phi6_5(self):
        """T^3 is closer to 1/23 than to 1/Phi6(5)=1/21."""
        T3 = cascade_step(cascade_step(cascade_step(1.0/m)))
        diff_23 = abs(T3 - 1.0/(2*k-1))
        diff_21 = abs(T3 - 1.0/Phi6_q(5))
        assert diff_23 < diff_21

    def test_not_clean_Phi6_tower_walk(self):
        """Cascade is NOT exactly 1/Phi6(n+const)."""
        values = [1.0/m]
        mu = 1.0/m
        for _ in range(5):
            mu = cascade_step(mu)
            values.append(mu)
        # If exact Phi6 tower walk, T^3 would be near 1/21, but it's not
        assert abs(values[3] - 1.0/21) > 0.005

    def test_first_two_steps_hit_named_values(self):
        """1/mu -> 1/Phi6 -> 1/Phi3 are the first two named W(3,3) hits."""
        T0 = 1.0/m
        T1 = cascade_step(T0)
        T2 = cascade_step(T1)
        assert abs(T0 - 1.0/m) < 1e-10
        assert abs(T1 - 1.0/Phi6) < 0.005
        assert abs(T2 - 1.0/Phi3) < 0.005

    def test_asymptotic_descent_after_T2(self):
        """After T2, the cascade follows asymptotic ratio r~0.5224."""
        mu = 1.0/m
        for _ in range(6):
            mu_next = cascade_step(mu)
            ratio = mu_next / mu
            mu = mu_next
        assert abs(ratio - 0.5224) < 0.01
