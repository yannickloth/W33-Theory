from __future__ import annotations

from w33_qcd_beta_phi6_bridge import build_qcd_beta_phi6_summary


def test_qcd_beta0_matches_phi6_exactly() -> None:
    summary = build_qcd_beta_phi6_summary()
    data = summary["qcd_beta_dictionary"]
    selector = summary["selector_bridge"]

    assert data["group"] == "SU(3)"
    assert data["active_flavours"] == 6
    assert data["beta0_formula"] == "11 - 2 n_f / 3"
    assert data["beta0_su3"]["exact"] == "7"
    assert data["phi6_formula"] == "q^2 - q + 1"
    assert data["phi6_q3"]["exact"] == "7"
    assert selector["beta0_equals_phi6"] is True
    assert selector["positive_integer_solution_of_phi6_equals_7"] == [3]


def test_phi6_crosses_pmns_higgs_and_topological_channels() -> None:
    summary = build_qcd_beta_phi6_summary()
    data = summary["qcd_beta_dictionary"]
    selector = summary["selector_bridge"]

    assert data["pmns_atmospheric_ratio"]["exact"] == "7/13"
    assert data["higgs_quartic"]["exact"] == "7/55"
    assert data["topological_over_continuum_ratio"]["exact"] == "7"
    assert selector["phi6_controls_pmns_atmospheric_numerator"] is True
    assert selector["phi6_controls_higgs_quartic_numerator"] is True
    assert selector["phi6_controls_topological_ratio"] is True
