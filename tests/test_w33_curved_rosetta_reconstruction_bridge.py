from __future__ import annotations

from w33_curved_rosetta_reconstruction_bridge import build_curved_rosetta_reconstruction_summary


def test_reconstructed_cyclotomic_and_graph_data_are_exact() -> None:
    summary = build_curved_rosetta_reconstruction_summary()

    assert summary["curved_inputs"]["master_variable"]["exact"] == "3/13"
    assert summary["curved_inputs"]["discrete_to_continuum_ratio"]["exact"] == "39"
    assert summary["curved_inputs"]["phi6_from_topological_over_continuum"]["exact"] == "7"
    assert summary["curved_inputs"]["vertex_count_from_topological_over_e7_fund"] == 40
    assert summary["curved_inputs"]["edge_count_from_discrete_over_f4"] == 240
    assert summary["curved_inputs"]["k_from_two_edges_over_vertices"]["exact"] == "12"
    assert summary["reconstructed_cyclotomic_data"]["q"] == 3
    assert summary["reconstructed_cyclotomic_data"]["phi3"]["exact"] == "13"
    assert summary["reconstructed_cyclotomic_data"]["phi6"]["exact"] == "7"


def test_reconstructed_srg_and_spectral_data_match_live_rosetta() -> None:
    summary = build_curved_rosetta_reconstruction_summary()

    assert summary["reconstructed_srg_data"] == {"v": 40, "k": 12, "lambda": 2, "mu": 4}
    assert summary["reconstructed_spectral_data"] == {"k": 12, "r": 2, "s": -4}
    assert summary["matches_live_rosetta_data"]["srg_k_matches"] is True
    assert summary["matches_live_rosetta_data"]["srg_lambda_matches"] is True
    assert summary["matches_live_rosetta_data"]["srg_mu_matches"] is True
    assert summary["matches_live_rosetta_data"]["spectral_k_matches"] is True
    assert summary["matches_live_rosetta_data"]["spectral_r_matches"] is True
    assert summary["matches_live_rosetta_data"]["spectral_s_matches"] is True


def test_promoted_observables_match_public_values() -> None:
    summary = build_curved_rosetta_reconstruction_summary()
    obs = summary["promoted_observables_from_reconstructed_graph_data"]

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
    assert summary["matches_live_rosetta_data"]["all_promoted_observables_match"] is True


def test_all_curved_samples_reconstruct_same_graph_data() -> None:
    summary = build_curved_rosetta_reconstruction_summary()

    assert summary["all_samples_constant"] is True
    assert len(summary["sample_reconstructions"]) == 6
    for sample in summary["sample_reconstructions"]:
        assert sample["q"] == 3
        assert sample["phi3"] == "13"
        assert sample["phi6"] == "7"
        assert sample["v"] == 40
        assert sample["k"] == 12
        assert sample["lambda"] == 2
        assert sample["mu"] == 4
        assert sample["r"] == 2
        assert sample["s"] == -4
