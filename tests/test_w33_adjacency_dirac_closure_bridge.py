from __future__ import annotations

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary


def test_bridge_recovers_vertex_laplacian_channels() -> None:
    summary = build_adjacency_dirac_closure_summary()
    adjacency = summary["adjacency_side"]
    assert adjacency["adjacency_spectrum"] == {12: 1, 2: 24, -4: 15}
    assert adjacency["vertex_laplacian_formula"] == "L0 = 12 I - A"
    assert adjacency["vertex_laplacian_matches_formula_exactly"] is True
    assert adjacency["vertex_laplacian_spectrum"] == {0: 1, 10: 24, 16: 15}


def test_bridge_recovers_hodge_lift_and_high_degree_scalar_channels() -> None:
    summary = build_adjacency_dirac_closure_summary()
    hodge = summary["hodge_lift_theorem"]
    high = summary["high_degree_regularities"]
    assert hodge["edge_harmonic_dimension"] == 81
    assert hodge["exact_one_form_dimension"] == 39
    assert hodge["coexact_one_form_dimension"] == 120
    assert hodge["exact_one_form_spectrum_is_vertex_nonzero_spectrum"] is True
    assert hodge["exact_one_form_spectrum"] == {10: 24, 16: 15}
    assert hodge["edge_hodge_spectrum"] == {0: 81, 4: 120, 10: 24, 16: 15}
    assert high["triangle_count"] == 160
    assert high["tetrahedron_count"] == 40
    assert high["triangle_laplacian_is_scalar_4"] is True
    assert high["tetrahedron_laplacian_is_scalar_4"] is True
    assert high["triangle_laplacian_spectrum"] == {4: 160}
    assert high["tetrahedron_laplacian_spectrum"] == {4: 40}


def test_bridge_recovers_full_df2_spectrum_and_spectral_action_moments() -> None:
    summary = build_adjacency_dirac_closure_summary()
    finite = summary["finite_dirac_closure"]
    assert finite["chain_dimensions"] == {"c0": 40, "c1": 240, "c2": 160, "c3": 40, "total": 480}
    assert finite["boundary_ranks"] == {"rank_d1": 39, "rank_d2": 120, "rank_d3": 40}
    assert finite["betti_numbers"] == {"b0": 1, "b1": 81, "b2": 0, "b3": 0}
    assert finite["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
    assert finite["trace_d_squared"] == 2240
    assert finite["trace_d_fourth"] == 17600
    assert finite["seeley_dewitt_moments"] == {"a0_f": 480, "a2_f": 2240, "a4_f": 17600}
    assert finite["spectral_action_ratios"] == {
        "mu_squared": "14/3",
        "lambda": "110/3",
        "higgs_ratio_square": "14/55",
    }
    assert finite["full_finite_spectrum_forced_from_adjacency_plus_clique_regularities"] is True
