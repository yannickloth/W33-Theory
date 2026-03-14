from exploration.w33_weinberg_reconstruction_bridge import build_weinberg_reconstruction_summary


def test_master_variable_is_weinberg_angle() -> None:
    summary = build_weinberg_reconstruction_summary()
    master = summary["master_variable"]
    assert master["symbol"] == "x"
    assert master["meaning"] == "sin^2(theta_W)"
    assert master["exact"]["exact"] == "3/13"


def test_all_reconstruction_channels_recover_same_x() -> None:
    summary = build_weinberg_reconstruction_summary()
    channels = summary["independent_reconstructions"]
    assert channels["from_cabibbo"]["exact"]["exact"] == "3/13"
    assert channels["from_pmns_12"]["exact"]["exact"] == "3/13"
    assert channels["from_pmns_23"]["exact"]["exact"] == "3/13"
    assert channels["from_omega_lambda"]["exact"]["exact"] == "3/13"
    assert channels["from_higgs_ratio"]["exact"]["exact"] == "3/13"
    assert channels["from_a2_over_a0"]["exact"]["exact"] == "3/13"
    assert channels["from_a4_over_a0"]["exact"]["exact"] == "3/13"
    assert channels["from_discrete_6_mode_over_a0"]["exact"]["exact"] == "3/13"
    assert channels["from_discrete_to_continuum_ratio"]["exact"]["exact"] == "3/13"
    assert all(channel["matches_master_variable"] for channel in channels.values())
