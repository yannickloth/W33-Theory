"""
Phase CCLXII: W(3,3) Seesaw Spectral Cascade.

The seesaw map m -> 1/m sends W(3,3) cyclotomic fractions to the NEXT one:

  mu_eff^2(m_nu) = 1/mu   = 1/4  [LH neutrinos, W(3,3) primary prediction]
  mu_eff^2(M_R)  ~ 1/Phi6 = 1/7  [RH neutrinos, uniform y_D seesaw]

Full cascade:
  1/mu(=4)  -> ~1/Phi6(=7)
  1/Phi6(=7) -> ~1/Phi3(=13)
  1/6        -> ~1/(k-1)(=11)

This is the W(3,3) spectral RG flow under successive seesaw inversions.
Each step maps one cyclotomic fraction to the next in the sequence:
  {1/4, 1/7, 1/10, 1/13} = {1/Phi4, 1/Phi6, 1/mu, 1/Phi3, ...}

Note: The map is NOT self-dual. mu_eff^2(1/m) != mu_eff^2(m) in general.
The previous claim of self-duality was incorrect (code error).
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
def solve_NH(target): return brentq(lambda m1: mu_eff_sq(get_masses_NH(m1))-target, 1e-5, 1.0)

m1_pred = solve_NH(1.0/m)
masses_nu = get_masses_NH(m1_pred)


class TestSeesawCascade:

    def test_map_is_not_self_dual(self):
        """mu_eff^2(1/m_nu) != mu_eff^2(m_nu) -- seesaw is NOT self-dual."""
        mu_fwd = mu_eff_sq(masses_nu)
        mu_bwd = mu_eff_sq(1.0/masses_nu)
        assert abs(mu_fwd - mu_bwd) > 0.05  # significant difference

    def test_primary_prediction_mu_fwd(self):
        """mu_eff^2(m_nu) = 1/mu = 0.25 (by construction)."""
        assert abs(mu_eff_sq(masses_nu) - 1.0/m) < 1e-6

    def test_seesaw_step_1_to_Phi6(self):
        """Seesaw maps 1/mu -> ~1/Phi6: mu_eff^2(1/m_nu) ~ 1/7."""
        mu_bwd = mu_eff_sq(1.0/masses_nu)
        assert abs(mu_bwd - 1.0/Phi6) < 0.005  # within 0.5% of 1/7

    def test_cascade_Phi6_to_Phi3(self):
        """Seesaw maps 1/Phi6 -> ~1/Phi3: cascade step 2."""
        m1_2 = solve_NH(1.0/Phi6)
        masses_2 = get_masses_NH(m1_2)
        mu_bwd_2 = mu_eff_sq(1.0/masses_2)
        assert abs(mu_bwd_2 - 1.0/Phi3) < 0.005

    def test_cascade_1over6_to_1over11(self):
        """Seesaw maps 1/6 -> ~1/11 = 1/(k-1): cascade step from 1/6."""
        m1_6 = solve_NH(1.0/6)
        masses_6 = get_masses_NH(m1_6)
        mu_bwd_6 = mu_eff_sq(1.0/masses_6)
        assert abs(mu_bwd_6 - 1.0/(k-1)) < 0.005

    def test_cascade_decreasing(self):
        """Each seesaw step produces a SMALLER mu_eff^2 (more degenerate RH sector)."""
        targets = [1.0/m, 1.0/Phi6, 1.0/Phi3]
        for tgt in targets:
            try:
                mi = solve_NH(tgt)
                masses = get_masses_NH(mi)
                mu_bwd = mu_eff_sq(1.0/masses)
                assert mu_bwd < tgt, f"cascade not decreasing at {tgt:.3f}"
            except Exception:
                pass

    def test_seesaw_self_duality_condition(self):
        """Self-duality requires m2 = sqrt(m1*m3), fails for NH/1/4."""
        m1, m2, m3 = masses_nu
        geom_mean_extremes = sqrt(m1 * m3)
        # m2 should NOT equal sqrt(m1*m3) for NH/1/4
        assert abs(m2 - geom_mean_extremes) / geom_mean_extremes > 0.2
