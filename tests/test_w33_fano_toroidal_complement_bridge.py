from exploration.w33_fano_toroidal_complement_bridge import (
    build_fano_toroidal_complement_summary,
)


def test_fano_toroidal_complement_summary() -> None:
    summary = build_fano_toroidal_complement_summary()
    operator = summary["operator_dictionary"]
    exact = summary["exact_factorizations"]

    assert operator["space_dimension"] == 7
    assert operator["fano_selector_formula"] == "2I + J"
    assert operator["toroidal_laplacian_formula"] == "7I - J"
    assert operator["complement_formula"] == "9I"
    assert operator["q_squared"] == 9
    assert operator["selector_spectrum_exact"] == ["2", "2", "2", "2", "2", "2", "9"]
    assert operator["toroidal_laplacian_spectrum_exact"] == [0, 7, 7, 7, 7, 7, 7]
    assert operator["selector_trace"] == 21
    assert operator["selector_nontrivial_trace"] == 12
    assert operator["toroidal_trace"] == 42
    assert operator["combined_trace"] == 63
    assert operator["combined_nontrivial_trace"] == 54
    assert operator["selector_determinant"] == 576
    assert operator["selector_determinant_square_root"] == 24
    assert operator["selector_minimal_polynomial"] == "x^2 - 11x + 18"

    assert exact["complement_operator_equals_q_squared_identity"] is True
    assert exact["selector_trace_equals_ag21_length"] is True
    assert exact["selector_nontrivial_trace_equals_gauge_dimension"] is True
    assert exact["toroidal_trace_equals_6_times_phi6"] is True
    assert exact["combined_nontrivial_trace_equals_exceptional_projector_rank"] is True
    assert exact["selector_determinant_square_root_equals_hurwitz_unit_shell"] is True
    assert exact["selector_quadratic_matches_heawood_quartic_in_x_squared"] is True
    assert exact["gauge_plus_toroidal_equals_exceptional_rank"] is True
