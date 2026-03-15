from __future__ import annotations

import pytest

from w33_electroweak_lagrangian_bridge import build_electroweak_lagrangian_summary


def test_graph_inputs_close_exactly() -> None:
    summary = build_electroweak_lagrangian_summary()
    graph = summary["graph_inputs"]

    assert graph["alpha"]["exact"] == "1111/152247"
    assert graph["weinberg_x"]["exact"] == "3/13"
    assert graph["cos2_theta_w"]["exact"] == "10/13"
    assert graph["higgs_ratio_square"]["exact"] == "14/55"
    assert graph["lambda_h"]["exact"] == "7/55"
    assert graph["vev_formula"] == "q^5 + q = |E| + 2q"
    assert graph["vev_ew_gev"] == 246


def test_dimensionless_lagrangian_dictionary_is_exact() -> None:
    summary = build_electroweak_lagrangian_summary()
    lagrangian = summary["dimensionless_lagrangian_dictionary"]

    assert lagrangian["heaviside_lorentz_charge_formula"] == "e^2 = 4 pi alpha"
    assert lagrangian["weak_coupling_formula"] == "g^2 = e^2 / sin^2(theta_W)"
    assert lagrangian["hypercharge_coupling_formula"] == "g'^2 = e^2 / cos^2(theta_W)"
    assert lagrangian["neutral_coupling_formula"] == "g_Z^2 = g^2 + g'^2"
    assert lagrangian["e_squared_over_4pi_alpha"]["exact"] == "1"
    assert lagrangian["g_squared_over_4pi_alpha"]["exact"] == "13/3"
    assert lagrangian["gprime_squared_over_4pi_alpha"]["exact"] == "13/10"
    assert lagrangian["gz_squared_over_4pi_alpha"]["exact"] == "169/30"
    assert lagrangian["one_over_e_squared_equals_sum"] is True
    assert lagrangian["g_squared_over_gprime_squared"]["exact"] == "10/3"
    assert lagrangian["rho_parameter"]["exact"] == "1"
    assert lagrangian["mw_squared_over_mz_squared"]["exact"] == "10/13"
    assert lagrangian["lambda_h_exact"]["exact"] == "7/55"


def test_natural_unit_couplings_and_tree_level_relations_hold() -> None:
    summary = build_electroweak_lagrangian_summary()
    couplings = summary["natural_unit_couplings"]
    exact = summary["exact_tree_level_relations"]

    assert couplings["e"]["float"] == pytest.approx(0.30282211588162705)
    assert couplings["g"]["float"] == pytest.approx(0.6303745025171762)
    assert couplings["gprime"]["float"] == pytest.approx(0.3452703347047545)
    assert couplings["gZ"]["float"] == pytest.approx(0.718737516379179)
    assert couplings["mw_tree_gev"]["float"] == pytest.approx(77.53606380961267)
    assert couplings["mz_tree_gev"]["float"] == pytest.approx(88.40471451463902)
    assert couplings["mh_tree_gev"]["float"] == pytest.approx(124.1131448609402)
    assert couplings["fermi_constant_tree"]["float"] == pytest.approx(1.168462524268867e-05)

    assert exact["e_equals_g_sin_theta"] is True
    assert exact["e_equals_gprime_cos_theta"] is True
    assert exact["mz_equals_mw_over_cos_theta"] is True
    assert exact["mh_equals_v_sqrt_2lambda"] is True
    assert exact["gf_equals_one_over_sqrt2_v2"] is True
