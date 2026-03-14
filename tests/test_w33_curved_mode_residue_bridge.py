from exploration.w33_curved_mode_residue_bridge import build_curved_mode_residue_bridge_summary


def test_generating_function_has_expected_pole_channels() -> None:
    summary = build_curved_mode_residue_bridge_summary()
    generating = summary["generating_function"]
    assert generating["formula"] == "A/(1 - 120 z) + B/(1 - 6 z) + C/(1 - z)"
    assert generating["normalized_residue_definition"] == "R_alpha(G) = -alpha * Res_{z = 1/alpha} G(z)"


def test_residue_bridge_recovers_same_eh_and_continuum_values() -> None:
    summary = build_curved_mode_residue_bridge_summary()
    cp2, k3 = summary["seed_residue_data"]

    assert cp2["eh_from_residue_over_six_mode"]["exact"] == "12480"
    assert k3["eh_from_residue_over_six_mode"]["exact"] == "12480"
    assert cp2["continuum_eh_after_rank39_normalization"]["exact"] == "320"
    assert k3["continuum_eh_after_rank39_normalization"]["exact"] == "320"


def test_finite_profile_records_same_eh_coefficient() -> None:
    summary = build_curved_mode_residue_bridge_summary()
    finite = summary["finite_profile"]
    assert finite["a0"]["exact"] == "480"
    assert finite["a2"]["exact"] == "2240"
    assert finite["einstein_hilbert_coefficient"]["exact"] == "12480"
