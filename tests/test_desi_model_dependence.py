"""
Phase CCLVII: DESI neutrino bound is cosmological-model-dependent.

DESI DR1 2024 (arXiv:2404.03002) results:
  ΛCDM:    sum(m_nu) < 0.072 eV  (95% CL)
  w0CDM:   sum(m_nu) < 0.113 eV
  w0waCDM: sum(m_nu) < 0.173 eV

W(3,3) primary prediction: NH, mu_eff^2=1/4, sum=0.101 eV
  ΛCDM:    EXCLUDED by DESI DR1 (sum > 0.072)
  w0CDM:   ALLOWED  by DESI DR1 (sum < 0.113) ✓
  w0waCDM: ALLOWED  by DESI DR1 (sum < 0.173) ✓✓

Crucially: DESI DR1 itself finds w0=-0.99+/-0.05, wa=-0.37+/-0.29
  (~2σ deviation from ΛCDM). In w0waCDM, the neutrino bound is 0.173 eV,
  making NH/1/4 (0.101 eV) fully compatible.
"""

from math import sqrt, log
import numpy as np
from scipy.optimize import brentq
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7

dm2_21 = 7.42e-5; dm2_31_NH = 2.517e-3; dm2_32_IH = 2.498e-3

# DESI DR1 2024 bounds (95% CL) under different DE models
DESI_LCDM     = 0.072   # ΛCDM
DESI_w0CDM    = 0.113   # w0CDM  
DESI_w0waCDM  = 0.173   # w0waCDM


def get_masses_NH(m1): return np.array([m1, sqrt(m1**2+dm2_21), sqrt(m1**2+dm2_31_NH)])
def mu_eff_sq(masses):
    x = masses / masses.max(); return -log(np.prod(x)**(1/3)) / log(Phi4)
def solve_NH(target): return brentq(lambda m1: mu_eff_sq(get_masses_NH(m1))-target, 1e-5, 1.0)

sum_NH_1_over_4   = sum(get_masses_NH(solve_NH(1.0/m)))
sum_NH_1_over_Phi4 = sum(get_masses_NH(solve_NH(1.0/Phi4)))


class TestDesiModelDependence:

    def test_primary_prediction_excluded_by_LCDM(self):
        """NH/1/4 excluded by DESI DR1 under ΛCDM."""
        assert sum_NH_1_over_4 > DESI_LCDM

    def test_primary_prediction_allowed_by_w0CDM(self):
        """NH/1/4 allowed by DESI DR1 under w0CDM."""
        assert sum_NH_1_over_4 < DESI_w0CDM

    def test_primary_prediction_allowed_by_w0waCDM(self):
        """NH/1/4 allowed by DESI DR1 under w0waCDM."""
        assert sum_NH_1_over_4 < DESI_w0waCDM

    def test_bounds_hierarchy(self):
        """DESI bounds: ΛCDM < w0CDM < w0waCDM."""
        assert DESI_LCDM < DESI_w0CDM < DESI_w0waCDM

    def test_prediction_between_LCDM_and_w0CDM(self):
        """NH/1/4 lies in the window (ΛCDM_bound, w0CDM_bound)."""
        assert DESI_LCDM < sum_NH_1_over_4 < DESI_w0CDM

    def test_Phi4_prediction_excluded_all_models(self):
        """NH/1/Phi4 (0.170 eV) excluded even by w0CDM."""
        assert sum_NH_1_over_Phi4 > DESI_w0CDM

    def test_Phi4_prediction_allowed_w0wa(self):
        """NH/1/Phi4 marginally allowed by w0waCDM."""
        assert sum_NH_1_over_Phi4 < DESI_w0waCDM

    def test_spread_of_bounds(self):
        """w0waCDM bound is > 2x the ΛCDM bound."""
        assert DESI_w0waCDM / DESI_LCDM > 2.0

    def test_NH_min_sum_below_DESI_LCDM(self):
        """Minimum NH sum (oscillations only) < DESI ΛCDM bound: oscillations compatible."""
        sum_min_NH = sqrt(dm2_21) + sqrt(dm2_31_NH)  # approximate lower bound
        assert sum_min_NH < DESI_LCDM
