from __future__ import annotations

import pytest

from w33_bosonic_action_completion_bridge import build_bosonic_action_completion_summary


def test_canonical_action_and_graph_inputs_are_fixed() -> None:
    summary = build_bosonic_action_completion_summary()
    action = summary["canonical_bosonic_action"]
    graph = summary["graph_fixed_inputs"]

    assert action["lagrangian_formula"] == (
        "L_bos = -1/4 W^a_{mu nu} W^{a mu nu} - 1/4 B_{mu nu} B^{mu nu} "
        "+ |D_mu H|^2 - V(H)"
    )
    assert action["covariant_derivative_formula"] == "D_mu = partial_mu - i g tau^a W^a_mu / 2 - i g' B_mu / 2"
    assert action["potential_formula"] == "V(H) = -mu_H^2 (H^dagger H) + lambda_H (H^dagger H)^2"

    assert graph["alpha"]["exact"] == "1111/152247"
    assert graph["weinberg_x"]["exact"] == "3/13"
    assert graph["cos2_theta_w"]["exact"] == "10/13"
    assert graph["lambda_h"]["exact"] == "7/55"
    assert graph["vev_ew_gev"] == 246


def test_gauge_and_higgs_dictionaries_close_exactly() -> None:
    summary = build_bosonic_action_completion_summary()
    gauge = summary["gauge_ratio_dictionary"]
    higgs = summary["higgs_dictionary"]

    assert gauge["g_squared_over_4pi_alpha"]["exact"] == "13/3"
    assert gauge["gprime_squared_over_4pi_alpha"]["exact"] == "13/10"
    assert gauge["gz_squared_over_4pi_alpha"]["exact"] == "169/30"
    assert gauge["g_over_e"]["float"] == pytest.approx(2.0816659994661326)
    assert gauge["gprime_over_e"]["float"] == pytest.approx(1.140175425099138)
    assert gauge["gz_over_e"]["float"] == pytest.approx(2.37346441585572)
    assert gauge["g_squared_over_gprime_squared"]["exact"] == "10/3"
    assert gauge["one_over_e_squared_equals_sum"] is True
    assert gauge["mw_squared_over_mz_squared"]["exact"] == "10/13"
    assert gauge["rho_parameter"]["exact"] == "1"

    assert higgs["mu_h_squared_over_v_squared"]["exact"] == "7/55"
    assert higgs["lambda_h"]["exact"] == "7/55"
    assert higgs["mh_squared_over_v_squared"]["exact"] == "14/55"
    assert higgs["vacuum_energy_over_v_fourth"]["exact"] == "-7/220"
    assert higgs["mu_equals_lambda_v_squared"] is True
    assert higgs["mh_squared_equals_2lambda_v_squared"] is True
    assert higgs["vacuum_energy_equals_minus_lambda_v_fourth_over_4"] is True


def test_completion_claim_is_parameter_complete() -> None:
    summary = build_bosonic_action_completion_summary()
    completion = summary["completion_claim"]

    assert completion["canonical_gauge_kinetics_fixed"] is True
    assert completion["covariant_derivative_fixed_by_alpha_and_x"] is True
    assert completion["higgs_potential_fixed_by_x_and_v"] is True
    assert completion["no_free_bosonic_parameter_beyond_graph_fixed_alpha_x_v"] is True
    assert completion["graph_fixes_full_tree_level_bosonic_electroweak_action"] is True
