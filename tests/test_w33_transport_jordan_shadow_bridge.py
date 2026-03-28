from w33_transport_jordan_shadow_bridge import (
    build_transport_jordan_shadow_bridge_summary,
)


def test_transport_jordan_shadow_bridge_summary() -> None:
    summary = build_transport_jordan_shadow_bridge_summary()
    theorem = summary["transport_jordan_shadow_theorem"]

    assert summary["internal_transport_jordan_packet"]["dimension"] == 162
    assert summary["internal_transport_jordan_packet"]["nilpotent_rank"] == 81
    assert summary["internal_transport_jordan_packet"]["nilpotent_nullity"] == 81
    assert summary["internal_transport_jordan_packet"]["square_zero"] is True
    assert summary["internal_transport_jordan_packet"]["jordan_block_size_2_count"] == 81
    assert summary["internal_transport_jordan_packet"]["jordan_block_size_1_count"] == 0
    assert summary["internal_transport_jordan_packet"]["exact_jordan_partition"] == "2^81"
    assert summary["internal_transport_jordan_packet"]["associated_graded_dimensions"] == [
        81,
        81,
    ]
    assert summary["external_polarized_jordan_shadow"]["ordered_filtration_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["external_polarized_jordan_shadow"]["ordered_filtered_shadow_line_types"] == [
        "positive",
        "negative",
    ]
    assert theorem["internal_transport_glue_has_exact_jordan_type_two_power_81"] is True
    assert theorem["internal_transport_associated_graded_is_exactly_81_head_plus_81_tail"] is True
    assert theorem[
        "external_bridge_fixes_the_polarized_associated_graded_of_the_transport_jordan_packet"
    ] is True
    assert theorem[
        "current_bridge_does_not_yet_realize_the_internal_nontrivial_size_two_jordan_blocks"
    ] is True
    assert theorem[
        "current_bridge_reaches_the_polarized_jordan_shadow_but_not_the_internal_jordan_identity"
    ] is True
