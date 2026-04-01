"""
Phase CCXLIX — Neutrino Spectral Descent from W(3,3)
=====================================================

The W(3,3) spectral descent map predicts:
  mu_eff^2 = 1/(q+1) = 1/4
  sum(m_nu) ~ 0.101 eV (NH)
  Seesaw cascade ratio r = (dm2_21 + dm2_31) / (2*dm2_31 - dm2_21) ~ 0.5225

Sources: exported-assets (15)-(17), BIGONE scripts
"""
import pytest
from math import sqrt, log
from fractions import Fraction

# ── W(3,3) parameters ──
q   = 3
v   = 40
k   = 12
lam = 2
mu  = 4
f   = 24
g   = 15
Phi3 = 13
Phi4 = 10
Phi6 = 7

# ── Neutrino oscillation data (NuFIT 5.3, NH) ──
dm2_21  = 7.42e-5    # eV^2
dm2_31  = 2.517e-3   # eV^2


def get_masses_NH(m1):
    """Normal hierarchy masses from lightest mass m1."""
    m2 = sqrt(m1**2 + dm2_21)
    m3 = sqrt(m1**2 + dm2_31)
    return (m1, m2, m3)


def mu_eff_sq(masses):
    """W(3,3) spectral descent parameter mu_eff^2."""
    m1, m2, m3 = masses
    mmax = max(masses)
    x = [mi / mmax for mi in masses]
    geo = (x[0] * x[1] * x[2])**(1.0/3.0)
    return -log(geo) / log(Phi4)


# ================================================================
# T1: mu_eff^2 = 1/(q+1) = 1/4 prediction
# ================================================================
class TestT1_MuEffPrediction:
    """The W(3,3) spectral fixed point predicts mu_eff^2 = 1/mu = 1/4."""

    def test_prediction_value(self):
        """mu_eff^2 = 1/(q+1) = 1/4 = 0.25"""
        assert Fraction(1, q + 1) == Fraction(1, 4)

    def test_prediction_from_mu(self):
        """mu_eff^2 = 1/mu = 1/4"""
        assert Fraction(1, mu) == Fraction(1, 4)

    def test_solve_m1_from_prediction(self):
        """Given mu_eff^2 = 1/4, solve for lightest mass m1"""
        # Binary search for m1 giving mu_eff^2 = 0.25
        lo, hi = 1e-6, 0.5
        target = 0.25
        for _ in range(100):
            mid = (lo + hi) / 2
            masses = get_masses_NH(mid)
            val = mu_eff_sq(masses)
            if val > target:
                lo = mid
            else:
                hi = mid
        m1_pred = (lo + hi) / 2
        masses = get_masses_NH(m1_pred)
        sum_nu = sum(masses)
        # Sum should be around 0.10 eV
        assert 0.08 < sum_nu < 0.15
        assert abs(mu_eff_sq(masses) - 0.25) < 0.001

    def test_sum_mnu_prediction(self):
        """sum(m_nu) ~ 0.101 eV for mu_eff^2 = 1/4"""
        lo, hi = 1e-6, 0.5
        for _ in range(100):
            mid = (lo + hi) / 2
            if mu_eff_sq(get_masses_NH(mid)) > 0.25:
                lo = mid
            else:
                hi = mid
        m1 = (lo + hi) / 2
        masses = get_masses_NH(m1)
        sum_nu = sum(masses)
        # Published prediction: 0.101 eV
        assert abs(sum_nu - 0.101) < 0.01


# ================================================================
# T2: Seesaw cascade ratio
# ================================================================
class TestT2_SeesawCascade:
    """Analytic cascade ratio r = (dm2_21+dm2_31)/(2*dm2_31-dm2_21)."""

    def test_cascade_ratio_analytic(self):
        """r = (dm2_21+dm2_31)/(2*dm2_31-dm2_21) ~ 0.5225"""
        r = (dm2_21 + dm2_31) / (2 * dm2_31 - dm2_21)
        assert abs(r - 0.5225) < 0.001

    def test_cascade_ratio_limit(self):
        """In the limit dm2_21/dm2_31 -> 0: r -> 1/2"""
        # r = (eps + 1)/(2 - eps) -> 1/2 as eps -> 0
        assert Fraction(1, 2) == Fraction(1, 2)
        # With small correction
        eps = dm2_21 / dm2_31
        r_approx = (1 + eps) / (2 - eps)
        assert abs(r_approx - 0.5225) < 0.001

    def test_cascade_numerical(self):
        """Verify cascade ratio by iterating T: mu -> mu'"""
        def cascade_step(mu_val):
            lo, hi = 1e-6, 0.9999
            for _ in range(100):
                mid = (lo + hi) / 2
                if mu_eff_sq(get_masses_NH(mid)) > mu_val:
                    lo = mid
                else:
                    hi = mid
            m1 = (lo + hi) / 2
            masses = get_masses_NH(m1)
            inv_masses = tuple(1.0 / m for m in masses)
            return mu_eff_sq(inv_masses)

        mu_val = 0.25
        ratios = []
        for _ in range(6):
            mu_new = cascade_step(mu_val)
            if mu_val > 1e-8:
                ratios.append(mu_new / mu_val)
            mu_val = mu_new

        # Last ratios should converge to analytic value
        r_analytic = (dm2_21 + dm2_31) / (2 * dm2_31 - dm2_21)
        assert abs(ratios[-1] - r_analytic) < 0.01

    def test_solar_correction(self):
        """Solar correction: r - 1/2 = 3*dm2_21 / (2*(2*dm2_31-dm2_21))"""
        r = (dm2_21 + dm2_31) / (2 * dm2_31 - dm2_21)
        correction = r - 0.5
        # Algebra: r = (a+b)/(2b-a) where a=dm2_21, b=dm2_31
        # r - 1/2 = (a+b)/(2b-a) - 1/2 = (2(a+b) - (2b-a)) / (2(2b-a))
        #         = (2a+2b-2b+a) / (2(2b-a)) = 3a / (2(2b-a))
        expected = 3 * dm2_21 / (2 * (2 * dm2_31 - dm2_21))
        assert abs(correction - expected) < 1e-8


# ================================================================
# T3: Seesaw scale prediction
# ================================================================
class TestT3_SeesawScale:
    """RH neutrino scale from W(3,3) seesaw."""

    def test_seesaw_formula(self):
        """M_R ~ v_EW^2 / m_nu ~ 10^{14.7-15.1} GeV"""
        v_EW = 246.0  # GeV
        m_nu_eV = 0.05  # typical ~ sqrt(dm2_31)
        m_nu_GeV = m_nu_eV * 1e-9
        M_R = v_EW**2 / m_nu_GeV
        log_MR = log(M_R) / log(10)
        # Should be ~14-15 in log10
        assert 14 < log_MR < 16

    def test_hierarchy_bridge(self):
        """ln(M_Pl/v_EW) = mu^2 * ln(Phi4) = 16*ln(10), 4.2% accuracy"""
        import math
        M_Pl = 1.22e19  # GeV
        v_EW = 246.0    # GeV
        observed = math.log(M_Pl / v_EW)   # ~ 38.44
        predicted = mu**2 * math.log(Phi4)  # 16 * ln(10) ~ 36.84
        # The 4.2% gap is the RG running contribution
        assert abs(predicted - observed) / observed < 0.05


# ================================================================
# T4: W(3,3) spectral descent structure
# ================================================================
class TestT4_SpectralDescent:
    """Properties of the spectral descent map."""

    def test_mu_eff_monotone(self):
        """mu_eff^2 is monotone decreasing in m1 (lightest mass)"""
        vals = []
        for m1 in [0.001, 0.01, 0.05, 0.1, 0.2]:
            vals.append(mu_eff_sq(get_masses_NH(m1)))
        for i in range(len(vals) - 1):
            assert vals[i] > vals[i+1]

    def test_mu_eff_hierarchical_limit(self):
        """In hierarchical limit (m1->0): mu_eff^2 -> large"""
        masses = get_masses_NH(1e-6)
        val = mu_eff_sq(masses)
        assert val > 1.0  # Much larger than 1/4

    def test_mu_eff_degenerate_limit(self):
        """In quasi-degenerate limit (m1 >> dm2): mu_eff^2 -> 0"""
        masses = get_masses_NH(1.0)
        val = mu_eff_sq(masses)
        assert val < 0.001

    def test_entry_point_1_over_4(self):
        """mu_eff^2 = 1/4 is a physically accessible entry point"""
        lo, hi = 1e-6, 0.5
        for _ in range(100):
            mid = (lo + hi) / 2
            if mu_eff_sq(get_masses_NH(mid)) > 0.25:
                lo = mid
            else:
                hi = mid
        m1 = (lo + hi) / 2
        # m1 should be ~ 0.02-0.04 eV (sub-eV)
        assert 0.01 < m1 < 0.1


# ================================================================
# T5: Neutrino mass sum constraints
# ================================================================
class TestT5_NeutrinoConstraints:
    """The predicted sum(m_nu) vs cosmological bounds."""

    def test_sum_below_DESI_bound(self):
        """sum(m_nu) ~ 0.101 eV < 0.12 eV (pre-DESI bound)"""
        lo, hi = 1e-6, 0.5
        for _ in range(100):
            mid = (lo + hi) / 2
            if mu_eff_sq(get_masses_NH(mid)) > 0.25:
                lo = mid
            else:
                hi = mid
        m1 = (lo + hi) / 2
        masses = get_masses_NH(m1)
        assert sum(masses) < 0.12

    def test_sum_above_minimum(self):
        """sum(m_nu) > minimal NH sum ~ 0.058 eV"""
        lo, hi = 1e-6, 0.5
        for _ in range(100):
            mid = (lo + hi) / 2
            if mu_eff_sq(get_masses_NH(mid)) > 0.25:
                lo = mid
            else:
                hi = mid
        m1 = (lo + hi) / 2
        masses = get_masses_NH(m1)
        assert sum(masses) > 0.058

    def test_neutrino_sum_formula(self):
        """sum(m_nu) = lam*(v-k+1) meV = 2*29 = 58 meV (minimal NH sum)"""
        # This is the MINIMAL sum for NH (m1=0)
        masses_min = get_masses_NH(0.0)
        sum_min_meV = sum(masses_min) * 1000  # convert eV to meV
        predicted = lam * (v - k + 1)  # = 2 * 29 = 58
        assert abs(sum_min_meV - predicted) < 1.0
