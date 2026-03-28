from __future__ import annotations

from w33_transport_nilpotent_glue_obstruction_bridge import (
    build_transport_nilpotent_glue_obstruction_bridge_summary,
)


def test_transport_nilpotent_glue_obstruction_bridge_summary() -> None:
    summary = build_transport_nilpotent_glue_obstruction_bridge_summary()
    theorem = summary["transport_nilpotent_glue_obstruction_theorem"]

    assert summary["internal_transport_nilpotent_glue"]["dimension"] == 162
    assert summary["internal_transport_nilpotent_glue"]["rank"] == 81
    assert summary["internal_transport_nilpotent_glue"]["nullity"] == 81
    assert summary["internal_transport_nilpotent_glue"]["square_zero"] is True
    assert summary["internal_transport_nilpotent_glue"]["image_equals_kernel"] is True
    assert summary["external_split_filtered_shadow"]["ordered_filtration_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["external_split_filtered_shadow"]["ordered_line_types"] == [
        "positive",
        "negative",
    ]
    assert summary["external_split_filtered_shadow"]["is_split"] is True
    assert theorem["internal_transport_162_has_nontrivial_rank_81_square_zero_glue_operator"] is True
    assert theorem["external_transport_shadow_matches_the_ordered_81_in_162_out_81_filtration"] is True
    assert theorem["external_transport_shadow_is_split_and_has_zero_extension_class"] is True
    assert theorem["internal_and_external_transport_packets_match_at_filtered_dimension_level_but_not_at_glue_operator_level"] is True
    assert theorem["current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"] is True
