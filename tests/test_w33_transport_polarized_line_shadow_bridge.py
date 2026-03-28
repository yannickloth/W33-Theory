from __future__ import annotations

from w33_transport_polarized_line_shadow_bridge import (
    build_transport_polarized_line_shadow_bridge_summary,
)


def test_transport_polarized_line_shadow_bridge_summary() -> None:
    summary = build_transport_polarized_line_shadow_bridge_summary()
    theorem = summary["transport_polarized_line_shadow_theorem"]

    assert summary["internal_transport_polarization"]["ordered_filtration_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["internal_transport_polarization"]["head_type"] == "invariant"
    assert summary["internal_transport_polarization"]["tail_type"] == "sign"
    assert summary["internal_transport_polarization"]["nilpotent_glue_direction"] == (
        "tail_to_head"
    )
    assert summary["external_polarized_split_shadow"]["ordered_filtration_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["external_polarized_split_shadow"]["ordered_filtered_shadow_line_types"] == [
        "positive",
        "negative",
    ]
    assert theorem["internal_transport_has_canonical_head_middle_tail_structure"] is True
    assert theorem["external_bridge_has_canonical_head_biased_and_tail_biased_u1_lines"] is True
    assert theorem["dominant_u1_line_is_head_biased_and_recessive_u1_line_is_tail_biased"] is True
    assert theorem["current_bridge_reaches_a_canonical_head_tail_polarized_split_shadow"] is True
    assert theorem["current_bridge_does_not_yet_realize_the_internal_tail_to_head_nilpotent_glue"] is True
    assert theorem["polarized_shadow_is_stronger_than_filtered_dimension_match_but_weaker_than_extension_identity"] is True
