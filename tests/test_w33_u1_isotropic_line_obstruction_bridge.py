from __future__ import annotations

from w33_u1_isotropic_line_obstruction_bridge import (
    build_u1_isotropic_line_obstruction_bridge_summary,
)


def test_u1_isotropic_line_obstruction_bridge_summary() -> None:
    summary = build_u1_isotropic_line_obstruction_bridge_summary()
    theorem = summary["u1_isotropic_line_obstruction_theorem"]

    assert summary["u1_seed_form"] == [[0, 1], [1, 0]]
    assert summary["u1_swapped_seed_form"] == [[0, 1], [1, 0]]
    assert summary["internal_common_line_generator"] == [1, 1, 0]
    assert theorem["line_one_is_primitive"] is True
    assert theorem["line_two_is_primitive"] is True
    assert theorem["line_one_is_isotropic"] is True
    assert theorem["line_two_is_isotropic"] is True
    assert theorem["line_pair_has_unit_hyperbolic_pairing"] is True
    assert theorem["swapping_the_two_isotropic_lines_preserves_the_u1_seed_form"] is True
    assert theorem["swapping_the_two_isotropic_lines_preserves_the_first_refinement_form"] is True
    assert theorem["swapping_the_two_isotropic_lines_preserves_the_reduced_global_prefactor"] is True
    assert theorem["current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other"] is True
    assert theorem["exact_identification_of_the_internal_common_line_with_a_canonical_u1_line_is_not_yet_supported"] is True
