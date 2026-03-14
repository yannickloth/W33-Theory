from exploration.w33_srg_rosetta_lock_bridge import build_srg_rosetta_lock_summary


def test_srg_data_recovers_q_phi3_phi6() -> None:
    summary = build_srg_rosetta_lock_summary()
    data = summary["srg_data"]
    assert data["k"] == 12
    assert data["lambda"] == 2
    assert data["mu"] == 4
    assert data["q_from_lambda_plus_one"] == 3
    assert data["phi3_from_k_plus_one"] == 13
    assert data["phi6_from_k_minus_lambda_minus_mu_plus_one"] == 7


def test_promoted_observables_match_direct_srg_formulas() -> None:
    summary = build_srg_rosetta_lock_summary()
    obs = summary["promoted_observables"]
    assert obs["sin2_theta_w_ew"]["exact"]["exact"] == "3/13"
    assert obs["tan_theta_c"]["exact"]["exact"] == "3/13"
    assert obs["sin2_theta_12"]["exact"]["exact"] == "4/13"
    assert obs["sin2_theta_23"]["exact"]["exact"] == "7/13"
    assert obs["sin2_theta_13"]["exact"]["exact"] == "2/91"
    assert obs["omega_lambda"]["exact"]["exact"] == "9/13"
    assert obs["higgs_ratio_square"]["exact"]["exact"] == "14/55"
    assert obs["a2_over_a0"]["exact"]["exact"] == "14/3"
    assert obs["a4_over_a0"]["exact"]["exact"] == "110/3"
    assert obs["discrete_6_mode_over_a0"]["exact"]["exact"] == "26"
    assert obs["discrete_to_continuum_ratio"]["exact"]["exact"] == "39"
    assert all(entry["matches_formula"] for entry in obs.values())
