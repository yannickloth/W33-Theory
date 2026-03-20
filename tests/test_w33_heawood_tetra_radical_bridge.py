from __future__ import annotations

from exploration.w33_heawood_tetra_radical_bridge import (
    build_heawood_tetra_radical_summary,
)


def test_heawood_middle_shell_is_exact_quadratic_packet() -> None:
    summary = build_heawood_tetra_radical_summary()
    shell = summary["heawood_middle_shell"]
    projectors = summary["heawood_spectral_projectors"]
    exact = summary["exact_factorizations"]

    assert shell["full_laplacian_minimal_polynomial"] == "x (x - 6) (x^2 - 6x + 7)"
    assert shell["constant_line_dimension"] == 1
    assert shell["sign_line_dimension"] == 1
    assert shell["middle_shell_dimension"] == 12
    assert shell["middle_projector_rank"] == 12
    assert shell["middle_quadratic_polynomial"] == "x^2 - 6x + 7"
    assert shell["middle_quadratic_relation_holds"] is True
    assert shell["middle_branch_eigenvalues_exact"] == {
        "minus": "3 - sqrt(2)",
        "plus": "sqrt(2) + 3",
    }
    assert shell["middle_branch_multiplicity_each"] == 6
    assert shell["middle_shell_trace_exact"] == "36"
    assert shell["middle_shell_pseudodeterminant_exact"] == "117649"
    assert projectors["projector_three_formula"] == "((H^2 - 2I)(H + 3I)) / 42"
    assert projectors["projector_sqrt2_formula"] == "((9I - H^2)(H + sqrt(2)I)) / (14 sqrt(2))"
    assert projectors["low_shell_projector_formula"] == "P_3 + P_sqrt(2)"
    assert projectors["projector_three_is_idempotent"] is True
    assert projectors["projector_sqrt2_is_idempotent"] is True
    assert projectors["projector_three_and_sqrt2_are_orthogonal"] is True
    assert projectors["projector_three_rank"] == 1
    assert projectors["projector_sqrt2_rank"] == 6
    assert projectors["low_shell_projector_rank"] == 7

    assert exact["middle_shell_dimension_equals_gauge_dimension"] is True
    assert exact["low_shell_rank_equals_toroidal_seed_order"] is True
    assert exact["middle_branch_multiplicity_equals_shared_six_channel"] is True
    assert exact["middle_quadratic_linear_term_equals_shared_six_channel"] is True
    assert exact["middle_quadratic_constant_term_equals_phi6"] is True
    assert exact["middle_branch_sum_equals_shared_six_channel"] is True
    assert exact["middle_branch_product_equals_phi6"] is True
    assert exact["middle_shell_trace_equals_q_times_gauge_dimension"] is True
    assert exact["middle_shell_pseudodeterminant_equals_phi6_to_shared_six"] is True
    assert exact["toroidal_selector_refines_to_heawood_middle_quadratic"] is True


def test_klein_tetra_packet_realizes_the_two_heawood_branches() -> None:
    summary = build_heawood_tetra_radical_summary()
    tetra = summary["klein_tetra_local_packet"]
    exact = summary["exact_factorizations"]

    assert tetra["packet_is_k4"] is True
    assert tetra["tetra_packet_size"] == 4
    assert tetra["tetra_packet_automorphism_order"] == 24
    assert tetra["weighted_tetra_branch_weights_exact"] == {
        "minus": "3/4 - sqrt(2)/4",
        "plus": "sqrt(2)/4 + 3/4",
    }
    assert tetra["weighted_tetra_minus_spectrum_exact"] == [
        "0",
        "3 - sqrt(2)",
        "3 - sqrt(2)",
        "3 - sqrt(2)",
    ]
    assert tetra["weighted_tetra_plus_spectrum_exact"] == [
        "0",
        "sqrt(2) + 3",
        "sqrt(2) + 3",
        "sqrt(2) + 3",
    ]
    assert tetra["weighted_tetra_minus_matches_exactly"] is True
    assert tetra["weighted_tetra_plus_matches_exactly"] is True
    assert tetra["tetra_nonzero_multiplicity"] == 3

    assert exact["weighted_klein_tetra_minus_realizes_middle_minus_branch"] is True
    assert exact["weighted_klein_tetra_plus_realizes_middle_plus_branch"] is True
    assert exact["tetra_packet_size_equals_mu"] is True
