from w33_curved_inverse_rosetta_bridge import build_curved_inverse_rosetta_summary


def test_curved_inverse_rosetta_reconstructs_internal_counts() -> None:
    summary = build_curved_inverse_rosetta_summary()
    reconstructed = summary["reconstructed_internal_data"]
    matches = summary["matches_live_internal_data"]

    assert reconstructed["w33_vertex_count"] == 40
    assert reconstructed["w33_edge_or_e8_root_count"] == 240
    assert reconstructed["spinor_cartan_rank"] == 8
    assert reconstructed["shared_six_channel"] == 6
    assert reconstructed["tomotope_automorphism_order"] == 96

    assert matches["vertex_count_matches"] is True
    assert matches["edge_count_matches"] is True
    assert matches["cartan_rank_matches"] is True
    assert matches["shared_six_matches"] is True
    assert matches["tomotope_aut_matches"] is True


def test_curved_inverse_rosetta_is_constant_on_all_seed_and_step_samples() -> None:
    summary = build_curved_inverse_rosetta_summary()
    assert summary["all_samples_constant"] is True

    for sample in summary["sample_reconstructions"]:
        assert sample["vertices"] == 40
        assert sample["edges"] == 240
        assert sample["cartan_rank"] == 8
        assert sample["shared_six"] == 6
        assert sample["tomotope_automorphism_order"] == 96
