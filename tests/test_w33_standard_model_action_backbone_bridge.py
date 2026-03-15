from __future__ import annotations

from w33_standard_model_action_backbone_bridge import build_standard_model_action_backbone_summary


def test_bosonic_and_fermion_backbones_are_exact() -> None:
    summary = build_standard_model_action_backbone_summary()
    bosonic = summary["bosonic_action_backbone"]
    fermions = summary["fermion_representation_backbone"]

    assert bosonic["alpha"]["exact"] == "1111/152247"
    assert bosonic["weinberg_x"]["exact"] == "3/13"
    assert bosonic["lambda_h"]["exact"] == "7/55"
    assert bosonic["vev_ew_gev"] == 246
    assert bosonic["mw_squared_over_mz_squared"]["exact"] == "10/13"
    assert bosonic["rho_parameter"]["exact"] == "1"
    assert bosonic["mu_h_squared_over_v_squared"]["exact"] == "7/55"
    assert bosonic["mh_squared_over_v_squared"]["exact"] == "14/55"
    assert bosonic["vacuum_energy_over_v_fourth"]["exact"] == "-7/220"
    assert bosonic["full_bosonic_action_fixed"] is True

    assert fermions["one_generation_spinor_dimension"] == 16
    assert fermions["three_generation_matter_dimension"] == 48
    assert fermions["left_right_split"] == "8+8"
    assert fermions["one_generation_counts"] == {
        "Q": 6,
        "u_c": 3,
        "d_c": 3,
        "L": 2,
        "e_c": 1,
        "nu_c": 1,
    }
    assert fermions["decomposition_16_equals_6_3_3_2_1_1"] is True
    assert fermions["clean_higgs_slots"] == ["H_2", "Hbar_2"]
    assert fermions["clean_higgs_pair_is_h2_hbar2"] is True


def test_mixing_and_anomaly_backbones_close() -> None:
    summary = build_standard_model_action_backbone_summary()
    mixing = summary["mixing_backbone"]
    anomaly = summary["anomaly_backbone"]

    assert mixing["tan_theta_c"]["exact"] == "3/13"
    assert mixing["sin2_theta_12"]["exact"] == "4/13"
    assert mixing["sin2_theta_23"]["exact"] == "7/13"
    assert mixing["sin2_theta_13"]["exact"] == "2/91"
    assert mixing["cabibbo_equals_weinberg_generator"] is True
    assert mixing["pmns_23_equals_weinberg_plus_pmns_12"] is True

    assert anomaly["gravitational_sum_y"]["exact"] == "0"
    assert anomaly["su3_squared_u1"]["exact"] == "0"
    assert anomaly["su2_squared_u1"]["exact"] == "0"
    assert anomaly["u1_cubed"]["exact"] == "0"
    assert anomaly["all_anomalies_cancel"] is True


def test_frontier_boundary_is_stated_honestly() -> None:
    summary = build_standard_model_action_backbone_summary()
    frontier = summary["frontier_boundary"]

    assert frontier["bosonic_action_complete"] is True
    assert frontier["fermion_representations_complete"] is True
    assert frontier["mixing_backbone_complete"] is True
    assert frontier["anomaly_backbone_complete"] is True
    assert frontier["full_yukawa_eigenvalue_spectrum_still_open"] is True
