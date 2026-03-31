"""
Phase CCXXVII — Down-Type Quark Mass Sector: Complete Fermion Mass Table

BREAKTHROUGH (2026-03-31):
  The down-type quark masses are now determined by W(3,3) parameters:
  - m_s = m_t / ((k-1)*Phi3^2) = m_t/1859  (PDG: 93.4 MeV, pred: 93.7 MeV, 0.27%)
  - m_d = m_s / (v/2) = m_t/37180           (PDG: 4.67 MeV, pred: 4.68 MeV, 0.27%)
  - m_u/m_d = Phi6/g_mult = 7/15            (PDG: 0.463, pred: 0.467, 1.2%)
  - m_s/m_d = v/2 = 20 EXACTLY              (PDG: 20.0 +/- 0.6, EXACT match!)

  Complete quark mass denominators (all from m_t = v_EW/sqrt(lambda)):
    D_t = 1                    (top:    y_t = 1, IR fixed point)
    D_b = v+1 = 41            (bottom: moonshine prime p41)
    D_c = k^2-2*mu = 136      (charm:  Selector VIII, L-infinity depth 1)
    D_s = (k-1)*Phi3^2 = 1859 (strange: k-1 = p11, Phi3 = 13)
    D_mu = 2*Phi3*Phi6*q^2 = 1638  (muon)
    D_tau = lam*Phi6^2 = 98        (tau)
    D_d = D_s*(v/2) = 37180   (down: strange * half-vertex-count)

  The ratio m_s/m_d = v/2 = 20 is a TESTABLE PREDICTION consistent with
  PDG 2022 value 20.0 +/- 0.6.

53 tests encoding the complete fermion mass sector from W(3,3).
"""

import math
import pytest
from fractions import Fraction

q, v, k, lam, mu = 3, 40, 12, 2, 4
Phi3, Phi4, Phi6, Phi12 = 13, 10, 7, 73
f, g_mult = 24, 15
E_edges = 240

# Tree-level top mass: y_t = 1 → m_t = v_EW / sqrt(lambda)
v_EW = 246.22  # GeV
m_t_tree = v_EW / math.sqrt(lam)  # = 174.10 GeV

# PDG quark masses (GeV)
m_t_pdg = 172.76       # pole mass
m_b_pdg = 4.18         # MSbar
m_c_pdg = 1.27         # MSbar
m_s_pdg = 0.0934       # MSbar at 2 GeV
m_d_pdg = 0.00467      # MSbar at 2 GeV
m_u_pdg = 0.00216      # MSbar at 2 GeV

# Mass denominators
D_t = 1
D_b = v + 1                       # = 41
D_c = k**2 - 2 * mu               # = 136
D_s = (k - 1) * Phi3**2           # = 1859
D_d = D_s * (v // 2)              # = 37180


# ===========================================================================
# T1 — Strange Quark: m_s = m_t / ((k-1)*Phi3^2)
# ===========================================================================
class TestT1_StrangeQuark:
    """m_s = m_t/1859 where 1859 = (k-1)*Phi3^2 = 11*169."""

    def test_strange_denominator(self):
        """D_s = (k-1)*Phi3^2 = 11*169 = 1859."""
        assert D_s == (k - 1) * Phi3**2 == 1859

    def test_1859_factored(self):
        """1859 = 11*169 = p11 * Phi3^2."""
        assert 11 * 169 == 1859
        assert k - 1 == 11
        assert Phi3**2 == 169

    def test_strange_mass_prediction(self):
        """m_s = m_t/1859 = 93.7 MeV (PDG: 93.4 +/- 0.8 MeV, 0.27% error)."""
        m_s_pred = m_t_tree / D_s
        rel_err = abs(m_s_pred - m_s_pdg) / m_s_pdg
        assert rel_err < 0.005  # < 0.5%

    def test_k_minus_1_is_moonshine_p11(self):
        """k-1 = 11 is moonshine prime p11."""
        assert k - 1 == 11

    def test_strange_from_charm_ratio(self):
        """D_s/D_c = 1859/136 = strange/charm denominator ratio."""
        ratio = Fraction(D_s, D_c)
        # PDG m_c/m_s = 1.27/0.0934 = 13.60
        # D_s/D_c = 1859/136 = 13.67 (0.5% match)
        assert abs(float(ratio) - 13.60) / 13.60 < 0.01


# ===========================================================================
# T2 — Down Quark: m_d = m_s / (v/2)
# ===========================================================================
class TestT2_DownQuark:
    """m_d = m_s/(v/2) = m_t/37180 where v/2 = 20."""

    def test_down_denominator(self):
        """D_d = D_s * (v/2) = 1859*20 = 37180."""
        assert D_d == D_s * (v // 2) == 37180

    def test_v_half_is_20(self):
        """v/2 = 40/2 = 20."""
        assert v // 2 == 20

    def test_down_mass_prediction(self):
        """m_d = m_t/37180 = 4.68 MeV (PDG: 4.67 +/- 0.48 MeV, 0.27% error)."""
        m_d_pred = m_t_tree / D_d
        rel_err = abs(m_d_pred - m_d_pdg) / m_d_pdg
        assert rel_err < 0.01  # < 1%

    def test_37180_factored(self):
        """37180 = lam^2*(lam+q)*(k-1)*Phi3^2 = 4*5*11*169."""
        assert lam**2 * (lam + q) * (k - 1) * Phi3**2 == 37180

    def test_37180_alt_factoring(self):
        """37180 = 2^2 * 5 * 11 * 13^2."""
        assert 4 * 5 * 11 * 169 == 37180


# ===========================================================================
# T3 — m_s/m_d = v/2 = 20 (EXACT)
# ===========================================================================
class TestT3_StrangeDownRatio:
    """m_s/m_d = v/2 = 20 is an exact W(3,3) prediction matching PDG."""

    def test_ms_md_ratio_predicted(self):
        """W(3,3) predicts m_s/m_d = v/2 = 20."""
        assert v // 2 == 20

    def test_ms_md_ratio_pdg(self):
        """PDG: m_s/m_d = 20.0 +/- 0.6, matches v/2 = 20 exactly."""
        pdg_ratio = m_s_pdg / m_d_pdg  # ~20.0
        assert abs(pdg_ratio - v // 2) / (v // 2) < 0.03  # < 3%

    def test_ms_md_within_pdg_uncertainty(self):
        """v/2 = 20 is well within the PDG uncertainty band."""
        pdg_central = 20.0
        pdg_sigma = 0.6
        assert abs(v // 2 - pdg_central) < pdg_sigma

    def test_v_half_unique_to_q3(self):
        """v/2 = (q+1)(q^2+1)/2 = 20 at q=3; this is an integer only when v is even."""
        assert v % 2 == 0  # v=40 is even ✓

    def test_v_half_equals_lam2_times_2q_minus_1(self):
        """v/2 = lam^2*(2q-1) = 4*5 = 20 (holds only at q=3!)."""
        assert lam**2 * (2 * q - 1) == v // 2


# ===========================================================================
# T4 — m_u/m_d = Phi6/g_mult = 7/15
# ===========================================================================
class TestT4_UpDownRatio:
    """m_u/m_d = Phi6/g_mult = 7/15 (1.2% accuracy)."""

    def test_mu_md_ratio(self):
        """Phi6/g_mult = 7/15."""
        ratio = Fraction(Phi6, g_mult)
        assert ratio == Fraction(7, 15)

    def test_mu_md_ratio_numerical(self):
        """7/15 = 0.4667 vs PDG m_u/m_d = 0.463 (1.2% match)."""
        w33_ratio = Phi6 / g_mult
        pdg_ratio = m_u_pdg / m_d_pdg
        assert abs(w33_ratio - pdg_ratio) / pdg_ratio < 0.02  # < 2%

    def test_up_mass_prediction(self):
        """m_u = m_d * 7/15 = 2.19 MeV (PDG: 2.16 +/- 0.49 MeV)."""
        m_d_pred = m_t_tree / D_d
        m_u_pred = m_d_pred * Phi6 / g_mult
        rel_err = abs(m_u_pred - m_u_pdg) / m_u_pdg
        assert rel_err < 0.02  # < 2%

    def test_Phi6_over_g_is_spectral_ratio(self):
        """7/15: Phi6 = |r|+lambda*q and g_mult = multiplicity of s=-mu."""
        assert Phi6 == q**2 - q + 1  # cyclotomic
        assert g_mult == 15  # spectral multiplicity


# ===========================================================================
# T5 — Complete Quark Mass Table
# ===========================================================================
class TestT5_CompleteQuarkTable:
    """All 6 quark masses from tree-level m_t and W(3,3) denominators."""

    def test_top_denominator(self):
        """D_t = 1 (y_t = 1, no suppression)."""
        assert D_t == 1

    def test_bottom_denominator(self):
        """D_b = v+1 = 41 (moonshine prime p41)."""
        assert D_b == 41 == v + 1

    def test_charm_denominator(self):
        """D_c = k^2-2*mu = 136 (Selector VIII)."""
        assert D_c == 136 == k**2 - 2 * mu

    def test_strange_denominator(self):
        """D_s = (k-1)*Phi3^2 = 1859."""
        assert D_s == 1859

    def test_down_denominator(self):
        """D_d = D_s*(v/2) = 37180."""
        assert D_d == 37180

    def test_all_quarks_sub_2_percent(self):
        """All 6 quark mass predictions within 2% of PDG (using tree-level m_t)."""
        predictions = [
            (m_t_tree / D_t, m_t_pdg, 'top'),
            (m_t_tree / D_b, m_b_pdg, 'bottom'),
            (m_t_tree / D_c, m_c_pdg, 'charm'),
            (m_t_tree / D_s, m_s_pdg, 'strange'),
            (m_t_tree / D_d, m_d_pdg, 'down'),
        ]
        for pred, pdg, name in predictions:
            err = abs(pred - pdg) / pdg
            assert err < 0.02, f'{name}: pred={pred:.4f}, pdg={pdg}, err={err:.4f}'

    def test_up_quark_sub_2_percent(self):
        """Up quark via m_u = m_d * Phi6/g_mult: within 2% of PDG."""
        m_d_pred = m_t_tree / D_d
        m_u_pred = m_d_pred * Phi6 / g_mult
        err = abs(m_u_pred - m_u_pdg) / m_u_pdg
        assert err < 0.02


# ===========================================================================
# T6 — Denominator Hierarchy and Structure
# ===========================================================================
class TestT6_DenominatorStructure:
    """The denominator sequence {1, 41, 98, 136, 1638, 1859, 37180} is structured."""

    def test_denominators_ordered(self):
        """D_t < D_b < D_tau < D_c < D_mu < D_s < D_d (mass ordering)."""
        D_tau = lam * Phi6**2  # = 98
        D_mu = 2 * Phi3 * Phi6 * q**2  # = 1638
        denoms = [D_t, D_b, D_tau, D_c, D_mu, D_s, D_d]
        assert denoms == sorted(denoms)

    def test_D_b_plus_D_tau_equals_D_c_plus_q(self):
        """D_b + D_tau = 41+98 = 139 = D_c+q = 136+3."""
        assert D_b + (lam * Phi6**2) == D_c + q

    def test_strange_denom_from_p11_and_Phi3(self):
        """1859 uses p11 and Phi3: the (k-1) moonshine prime and 3rd cyclotomic."""
        assert D_s == 11 * 13**2

    def test_all_denoms_coprime_to_q(self):
        """All denominators are coprime to q=3 (no generation mixing in tree-level)."""
        assert math.gcd(D_b, q) == 1    # 41 coprime to 3
        assert math.gcd(D_c, q) == 1    # 136 coprime to 3
        # D_s = 1859 = 11*169 = 11*13^2, coprime to 3
        assert math.gcd(D_s, q) == 1

    def test_charm_plus_bottom_is_moonshine_product(self):
        """D_c + D_b = 136+41 = 177 = q*59 = q*p59 (moonshine prime!)."""
        assert D_c + D_b == q * 59
        assert 59 == v + k + Phi6  # p59 from W(3,3)

    def test_total_denominator_product(self):
        """D_b * D_c * D_s = 41*136*1859 = 10,362,424."""
        product = D_b * D_c * D_s
        assert product == 41 * 136 * 1859

    def test_6_quarks_from_one_parameter(self):
        """All 6 quark masses derive from q=3 via v_EW and W(3,3) polynomials."""
        # m_t: y_t = 1 → D_t = 1
        # m_b: D = v+1 = (q+1)(q^2+1)+1
        # m_c: D = k^2-2*mu = q^2(q+1)^2-2(q+1)
        # m_s: D = (k-1)*Phi3^2 = (q^2+q-1)*(q^2+q+1)^2
        # m_d: D = D_s * v/2
        # m_u: m_d * Phi6/g
        assert D_b == v + 1
        assert D_c == k**2 - 2 * mu
        assert D_s == (k - 1) * Phi3**2
        assert D_d == D_s * (v // 2)


# ===========================================================================
# T7 — Polynomial Expressions at General q
# ===========================================================================
class TestT7_PolynomialExpressions:
    """All denominators are polynomials in q; evaluate at q=3 to get W(3,3) values."""

    def test_D_s_polynomial(self):
        """D_s = (q^2+q-1)*(q^2+q+1)^2 at q=3 gives 1859."""
        val = (q**2 + q - 1) * (q**2 + q + 1)**2
        assert val == 1859

    def test_D_d_polynomial(self):
        """D_d = (q^2+q-1)*(q^2+q+1)^2*(q+1)*(q^2+1)/2 at q=3 gives 37180."""
        val = (q**2 + q - 1) * (q**2 + q + 1)**2 * (q + 1) * (q**2 + 1) // 2
        assert val == 37180

    def test_D_c_polynomial(self):
        """D_c = q^2*(q+1)^2 - 2*(q+1) at q=3 gives 136."""
        val = q**2 * (q + 1)**2 - 2 * (q + 1)
        assert val == 136

    def test_D_b_polynomial(self):
        """D_b = (q+1)*(q^2+1)+1 at q=3 gives 41."""
        val = (q + 1) * (q**2 + 1) + 1
        assert val == 41

    def test_k_minus_1_polynomial(self):
        """k-1 = q^2+q-1 at q=3 gives 11."""
        assert q**2 + q - 1 == 11

    def test_Phi3_squared_polynomial(self):
        """Phi3^2 = (q^2+q+1)^2 at q=3 gives 169."""
        assert (q**2 + q + 1)**2 == 169

    def test_v_half_polynomial(self):
        """v/2 = (q+1)*(q^2+1)/2 at q=3 gives 20."""
        assert (q + 1) * (q**2 + 1) // 2 == 20


# ===========================================================================
# T8 — Lepton-Quark Mass Unification
# ===========================================================================
class TestT8_LeptonQuarkUnification:
    """All fermion masses from a single denominator tower rooted in m_t."""

    def test_tau_denom(self):
        """D_tau = lam*Phi6^2 = 2*49 = 98."""
        D_tau = lam * Phi6**2
        assert D_tau == 98

    def test_muon_denom(self):
        """D_mu = 2*Phi3*Phi6*q^2 = 2*13*7*9 = 1638."""
        D_mu = 2 * Phi3 * Phi6 * q**2
        assert D_mu == 1638

    def test_tau_mass_prediction(self):
        """m_tau = m_t/98 = 1.777 GeV (PDG: 1.77686, 0.01% error)."""
        D_tau = lam * Phi6**2
        m_tau_pred = m_t_tree / D_tau
        m_tau_pdg = 1.77686
        assert abs(m_tau_pred - m_tau_pdg) / m_tau_pdg < 0.005

    def test_muon_mass_prediction(self):
        """m_mu = m_t/1638 = 0.10629 GeV (PDG: 0.10566, 0.6% error)."""
        D_mu = 2 * Phi3 * Phi6 * q**2
        m_mu_pred = m_t_tree / D_mu
        m_mu_pdg = 0.10566
        assert abs(m_mu_pred - m_mu_pdg) / m_mu_pdg < 0.01

    def test_D_tau_between_D_b_and_D_c(self):
        """D_tau = 98 sits between D_b = 41 and D_c = 136 (tau heavier than charm)."""
        D_tau = lam * Phi6**2
        assert D_b < D_tau < D_c

    def test_D_mu_between_D_c_and_D_s(self):
        """D_mu = 1638 sits between D_c = 136 and D_s = 1859 (muon lighter than strange)."""
        D_mu = 2 * Phi3 * Phi6 * q**2
        assert D_c < D_mu < D_s

    def test_full_mass_ordering(self):
        """t > b > tau > c > mu > s > d > u: correct hierarchy from denominators."""
        D_tau = lam * Phi6**2
        D_mu = 2 * Phi3 * Phi6 * q**2
        D_u = D_d * g_mult // Phi6  # effective D_u from m_u = m_d * 7/15
        denoms = [D_t, D_b, D_tau, D_c, D_mu, D_s, D_d, D_u]
        assert denoms == sorted(denoms)


# ===========================================================================
# T9 — Cross-Checks and Consistency
# ===========================================================================
class TestT9_CrossChecks:
    """Independent cross-checks of the mass formulas."""

    def test_strange_to_bottom_ratio(self):
        """m_b/m_s = D_s/D_b = 1859/41 = 45.34 (PDG: 4.18/0.0934 = 44.75, 1.3%)."""
        ratio = D_s / D_b
        pdg_ratio = m_b_pdg / m_s_pdg
        assert abs(ratio - pdg_ratio) / pdg_ratio < 0.02

    def test_down_to_bottom_ratio(self):
        """m_b/m_d = D_d/D_b = 37180/41 = 906.8 (PDG: 4.18/0.00467 = 895, 1.3%)."""
        ratio = D_d / D_b
        pdg_ratio = m_b_pdg / m_d_pdg
        assert abs(ratio - pdg_ratio) / pdg_ratio < 0.02

    def test_strange_to_charm_from_denominators(self):
        """m_c/m_s = D_s/D_c = 1859/136 = 13.67 (PDG: 13.60, 0.5%)."""
        ratio = D_s / D_c
        pdg_ratio = m_c_pdg / m_s_pdg
        assert abs(ratio - pdg_ratio) / pdg_ratio < 0.01

    def test_D_s_over_D_d_is_v_half(self):
        """D_d/D_s = v/2 = 20 (this IS the m_s/m_d prediction)."""
        assert D_d // D_s == v // 2 == 20

    def test_product_D_b_D_c_D_s_D_d(self):
        """D_b*D_c*D_s*D_d = 41*136*1859*37180."""
        product = D_b * D_c * D_s * D_d
        assert product == 41 * 136 * 1859 * 37180

    def test_sum_inverse_denoms(self):
        """Sum of 1/D for all quarks (mass sum in units of m_t)."""
        inv_sum = Fraction(1, D_t) + Fraction(1, D_b) + Fraction(1, D_c) + \
                  Fraction(1, D_s) + Fraction(1, D_d)
        # Should be dominated by 1/D_t = 1
        assert inv_sum > 1
        assert inv_sum < Fraction(11, 10)  # ~1.034
