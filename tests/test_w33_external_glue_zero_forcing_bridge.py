from w33_external_glue_zero_forcing_bridge import (
    build_external_glue_zero_forcing_bridge_summary,
)


def test_external_glue_zero_forcing_bridge_summary() -> None:
    summary = build_external_glue_zero_forcing_bridge_summary()
    theorem = summary["external_glue_zero_forcing_theorem"]

    assert summary["current_external_transport_object"]["source"] == (
        "canonical_mixed_k3_plane_qutrit_lift"
    )
    assert summary["current_external_transport_object"]["qutrit_lift_split"] == [81, 81]
    assert summary["current_external_transport_object"]["total_qutrit_lift_dimension"] == 162
    assert summary["current_external_transport_object"]["split_qutrit_package"] is True
    assert summary["current_external_transport_object"]["ordered_line_types"] == [
        "positive",
        "negative",
    ]
    assert summary["external_glue_slot"]["slot_direction"] == "tail_to_head"
    assert summary["external_glue_slot"]["slot_shape"] == [81, 81]
    assert summary["external_glue_slot"]["current_external_rank"] == 0
    assert summary["external_glue_slot"]["current_external_state"] == "zero_by_splitness"
    assert theorem[
        "current_external_162_sector_is_exactly_the_split_qutrit_lift_of_the_canonical_mixed_k3_plane"
    ] is True
    assert theorem["current_external_transport_shadow_has_zero_extension_class"] is True
    assert theorem["split_vs_nonsplit_obstruction_is_already_exact_at_the_current_bridge_level"] is True
    assert theorem[
        "the_unique_external_tail_to_head_glue_slot_is_structurally_zero_on_the_present_bridge_object"
    ] is True
    assert theorem[
        "any_nonzero_external_glue_operator_would_require_new_external_data_beyond_the_current_bridge_objects"
    ] is True
