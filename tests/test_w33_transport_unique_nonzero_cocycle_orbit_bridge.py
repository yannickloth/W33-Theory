from w33_transport_unique_nonzero_cocycle_orbit_bridge import (
    build_transport_unique_nonzero_cocycle_orbit_bridge_summary,
)


def test_transport_unique_nonzero_cocycle_orbit_bridge_summary() -> None:
    summary = build_transport_unique_nonzero_cocycle_orbit_bridge_summary()
    theorem = summary["transport_unique_nonzero_cocycle_orbit_theorem"]

    assert summary["ternary_fiber_shift_orbit"]["base_shift"] == [[0, 1], [0, 0]]
    assert summary["ternary_fiber_shift_orbit"]["other_nonzero_scalar_multiple"] == [
        [0, 2],
        [0, 0],
    ]
    assert summary["ternary_fiber_shift_orbit"]["conjugating_basis_change"] == [
        [1, 0],
        [0, 2],
    ]
    assert summary["ternary_fiber_shift_orbit"]["conjugated_shift"] == [
        [0, 2],
        [0, 0],
    ]
    assert summary["ternary_fiber_shift_orbit"]["nonzero_scalar_orbit_size"] == 2
    assert theorem["the_internal_transport_cocycle_is_nontrivial"] is True
    assert theorem[
        "the_only_nonzero_scalar_multiples_of_the_fiber_shift_over_f3_are_n_and_2n"
    ] is True
    assert theorem[
        "the_two_nonzero_scalar_multiples_are_gauge_equivalent_by_adapted_diagonal_basis_change"
    ] is True
    assert theorem[
        "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
    ] is True
    assert theorem[
        "the_remaining_external_wall_is_existence_of_that_unique_nonzero_orbit_not_selection_among_several_nonzero_types"
    ] is True
