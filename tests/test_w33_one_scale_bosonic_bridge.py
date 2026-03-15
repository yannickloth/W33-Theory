from __future__ import annotations

import pytest

from w33_one_scale_bosonic_bridge import build_one_scale_bosonic_summary


def test_graph_fixed_inputs_and_higgs_potential_closure() -> None:
    summary = build_one_scale_bosonic_summary()
    graph = summary["graph_fixed_inputs"]
    higgs = summary["higgs_potential_dictionary"]

    assert graph["vev_ew_gev"] == 246
    assert graph["weinberg_x"]["exact"] == "3/13"
    assert graph["cos2_theta_w"]["exact"] == "10/13"
    assert graph["lambda_h"]["exact"] == "7/55"
    assert graph["higgs_ratio_square"]["exact"] == "14/55"

    assert higgs["potential_formula"] == "V(H) = -mu_H^2 (H^dagger H) + lambda_H (H^dagger H)^2"
    assert higgs["mu_h_squared_over_v_squared"]["exact"] == "7/55"
    assert higgs["mh_squared_over_v_squared"]["exact"] == "14/55"
    assert higgs["vacuum_energy_over_v_fourth"]["exact"] == "-7/220"
    assert higgs["mu_equals_lambda_v_squared"] is True
    assert higgs["mh_squared_equals_2lambda_v_squared"] is True
    assert higgs["vacuum_energy_equals_minus_lambda_v_fourth_over_4"] is True


def test_normalized_tree_mass_dictionary_closes() -> None:
    summary = build_one_scale_bosonic_summary()
    masses = summary["normalized_tree_mass_dictionary"]

    assert masses["mw_squared_over_mz_squared"]["exact"] == "10/13"
    assert masses["z_minus_w_split_over_z"]["exact"] == "3/13"
    assert masses["rho_parameter"]["exact"] == "1"
    assert masses["mw_over_v"]["float"] == pytest.approx(0.3151872512585881)
    assert masses["mz_over_v"]["float"] == pytest.approx(0.3593687581895895)
    assert masses["mh_over_v"]["float"] == pytest.approx(0.504524979109513)
    assert masses["mw_over_mz_equals_sqrt_cos2"] is True
    assert masses["mh_over_v_equals_sqrt_higgs_ratio"] is True


def test_one_scale_closure_uses_only_promoted_graph_scale() -> None:
    summary = build_one_scale_bosonic_summary()
    closure = summary["one_scale_closure"]

    assert closure["all_dimensionless_bosonic_data_fixed"] is True
    assert closure["only_overall_scale_is_v"] is True
    assert closure["vev_is_graph_fixed_as_q5_plus_q"] is True
    assert closure["vev_is_graph_fixed_as_edges_plus_2q"] is True
    assert closure["zero_extra_parameter_bosonic_closure_if_promoted_vev_accepted"] is True
