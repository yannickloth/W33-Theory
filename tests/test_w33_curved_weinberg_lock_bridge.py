from __future__ import annotations

from w33_curved_weinberg_lock_bridge import build_curved_weinberg_lock_bridge_summary


def test_curved_samples_reconstruct_same_master_variable() -> None:
    summary = build_curved_weinberg_lock_bridge_summary()

    assert summary["master_variable"]["exact"]["exact"] == "3/13"
    assert summary["curved_reconstruction_formula"] == "x = 9 * c_EH,cont / c_6"
    assert all(sample["reconstructed_x"]["exact"] == "3/13" for sample in summary["curved_samples"])
    assert all(sample["matches_master_variable"] is True for sample in summary["curved_samples"])


def test_exceptional_residue_dictionary_recovers_same_x() -> None:
    summary = build_curved_weinberg_lock_bridge_summary()
    exceptional = summary["exceptional_reconstruction"]

    assert exceptional["formula"] == "x = 9 * (40*8) / (40*6*52)"
    assert exceptional["reconstructed_x"]["exact"] == "3/13"
    assert exceptional["matches_master_variable"] is True


def test_promoted_observables_match_public_generator_values() -> None:
    summary = build_curved_weinberg_lock_bridge_summary()
    obs = summary["promoted_observables_from_curved_x"]

    assert obs["tan_theta_c"]["exact"]["exact"] == "3/13"
    assert obs["sin2_theta_12"]["exact"]["exact"] == "4/13"
    assert obs["sin2_theta_23"]["exact"]["exact"] == "7/13"
    assert obs["sin2_theta_13"]["exact"]["exact"] == "2/91"
    assert obs["omega_lambda"]["exact"]["exact"] == "9/13"
    assert obs["higgs_ratio_square"]["exact"]["exact"] == "14/55"
    assert obs["a2_over_a0"]["exact"]["exact"] == "14/3"
    assert obs["a4_over_a0"]["exact"]["exact"] == "110/3"
    assert obs["discrete_to_continuum_ratio"]["exact"]["exact"] == "39"
    assert all(entry["matches_public_generator_value"] is True for entry in obs.values())
