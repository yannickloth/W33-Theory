from __future__ import annotations

from w33_uor_gluing_bridge import build_w33_uor_gluing_summary


EXPECTED = [["AB", "I", "A"], ["AB", "I", "A"], ["A", "B", "0"]]


def test_uor_gluing_cover_is_compatible_and_complete_for_both_slots() -> None:
    summary = build_w33_uor_gluing_summary()
    theorem = summary["gluing_theorem"]
    assert summary["status"] == "ok"
    assert theorem["all_pairwise_overlaps_are_compatible_for_both_slots"] is True
    assert theorem["all_cells_are_covered_for_both_slots"] is True


def test_uor_gluing_routes_produce_the_same_unique_global_section() -> None:
    summary = build_w33_uor_gluing_summary()
    theorem = summary["gluing_theorem"]
    assert theorem["forward_route_glues_to_canonical_section_for_both_slots"] is True
    assert theorem["reverse_route_glues_to_canonical_section_for_both_slots"] is True
    assert theorem["full_cover_has_unique_global_section_for_both_slots"] is True
    assert theorem["canonical_global_section_is_slot_independent"] is True


def test_uor_gluing_profiles_record_expected_global_matrix() -> None:
    summary = build_w33_uor_gluing_summary()
    for slot_profile in summary["slot_profiles"].values():
        assert slot_profile["merged_global_section"] == EXPECTED
        assert slot_profile["forward_route_global_section"] == EXPECTED
        assert slot_profile["reverse_route_global_section"] == EXPECTED
        assert slot_profile["canonical_global_section"] == EXPECTED
