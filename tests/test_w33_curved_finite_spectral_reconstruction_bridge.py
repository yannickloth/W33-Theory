from __future__ import annotations

from w33_curved_finite_spectral_reconstruction_bridge import (
    build_curved_finite_spectral_reconstruction_summary,
)


def test_reconstructed_graph_and_hodge_data_are_exact() -> None:
    summary = build_curved_finite_spectral_reconstruction_summary()

    graph = summary["reconstructed_graph_geometry"]
    hodge = summary["reconstructed_hodge_data"]
    assert graph["q"] == 3
    assert graph["line_size"] == 4
    assert graph["line_count"] == 40
    assert graph["edge_count"] == 240
    assert graph["triangle_count"] == 160
    assert graph["tetrahedron_count"] == 40
    assert graph["edge_count_matches_srg_formula_vk_over_2"] is True
    assert hodge["betti_numbers"] == {"b0": 1, "b1": 81, "b2": 0, "b3": 0}
    assert hodge["boundary_ranks"] == {"rank_d1": 39, "rank_d2": 120, "rank_d3": 40}
    assert hodge["exact_one_form_dimension"] == 39
    assert hodge["coexact_one_form_dimension"] == 120
    assert hodge["coexact_and_high_degree_scalar_channel"] == 4


def test_reconstructed_vertex_channels_and_df2_spectrum_are_exact() -> None:
    summary = build_curved_finite_spectral_reconstruction_summary()

    channels = summary["reconstructed_vertex_channels"]
    finite = summary["reconstructed_finite_dirac_package"]
    assert channels["adjacency_nontrivial_multiplicities"] == {"2": 24, "-4": 15}
    assert channels["vertex_laplacian_spectrum"] == {0: 1, 10: 24, 16: 15}
    assert channels["exact_one_form_nonzero_spectrum"] == {10: 24, 16: 15}
    assert finite["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}


def test_reconstructed_moments_and_ratios_match_live_internal_package() -> None:
    summary = build_curved_finite_spectral_reconstruction_summary()

    finite = summary["reconstructed_finite_dirac_package"]
    matches = summary["matches_live_internal_package"]
    assert finite["seeley_dewitt_moments"] == {"a0_f": 480, "a2_f": 2240, "a4_f": 17600}
    assert finite["spectral_action_ratios"]["mu_squared"]["exact"] == "14/3"
    assert finite["spectral_action_ratios"]["lambda"]["exact"] == "110/3"
    assert finite["spectral_action_ratios"]["higgs_ratio_square"]["exact"] == "14/55"
    assert matches["triangle_count_matches"] is True
    assert matches["tetrahedron_count_matches"] is True
    assert matches["betti_numbers_match"] is True
    assert matches["boundary_ranks_match"] is True
    assert matches["vertex_channels_match"] is True
    assert matches["exact_one_form_channels_match"] is True
    assert matches["df2_spectrum_match"] is True
    assert matches["moments_match"] is True


def test_all_curved_samples_reconstruct_same_finite_package() -> None:
    summary = build_curved_finite_spectral_reconstruction_summary()

    assert summary["all_samples_constant"] is True
    assert len(summary["sample_reconstructions"]) == 6
    for sample in summary["sample_reconstructions"]:
        assert sample["chain_dimensions"] == {"c0": 40, "c1": 240, "c2": 160, "c3": 40, "total": 480}
        assert sample["betti_numbers"] == {"b0": 1, "b1": 81, "b2": 0, "b3": 0}
        assert sample["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
