from w33_transport_single_glue_slot_bridge import (
    build_transport_single_glue_slot_bridge_summary,
)


def test_transport_single_glue_slot_bridge_summary() -> None:
    summary = build_transport_single_glue_slot_bridge_summary()
    theorem = summary["transport_single_glue_slot_theorem"]

    assert summary["internal_transport_operator_slot"]["head_dimension"] == 81
    assert summary["internal_transport_operator_slot"]["middle_dimension"] == 162
    assert summary["internal_transport_operator_slot"]["tail_dimension"] == 81
    assert summary["internal_transport_operator_slot"]["slot_direction"] == "tail_to_head"
    assert summary["internal_transport_operator_slot"]["slot_shape"] == [81, 81]
    assert summary["internal_transport_operator_slot"]["required_internal_rank"] == 81
    assert summary["external_current_slot_state"]["current_external_slot_rank"] == 0
    assert summary["external_current_slot_state"]["current_external_slot_state"] == (
        "zero_by_splitness"
    )
    assert theorem["current_bridge_fixes_the_semisimplified_shadow_of_the_transport_packet"] is True
    assert theorem["current_bridge_fixes_the_ordered_filtered_shadow_of_the_transport_packet"] is True
    assert theorem["current_bridge_fixes_the_polarized_jordan_shadow_of_the_transport_packet"] is True
    assert theorem["exact_transport_identity_would_require_a_tail_to_head_rank_81_square_zero_glue_operator"] is True
    assert theorem["the_current_external_bridge_forces_that_single_glue_slot_to_be_zero"] is True
    assert theorem["the_only_missing_exact_transport_datum_is_one_tail_to_head_81_by_81_operator_slot"] is True
