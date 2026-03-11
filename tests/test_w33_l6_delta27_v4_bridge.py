from __future__ import annotations

import json
from pathlib import Path

from w33_l6_delta27_v4_bridge import (
    build_l6_delta27_v4_bridge_summary,
    write_summary,
)


def test_matrix_level_v4_theorem_holds_for_both_slots() -> None:
    summary = build_l6_delta27_v4_bridge_summary()
    theorem = summary["matrix_level_v4_theorem"]
    assert theorem["all_off_diagonal_blocks_share_exact_support_for_both_slots"] is True
    assert theorem["all_relative_row_signs_are_trivial_for_both_slots"] is True
    assert theorem["all_off_diagonal_blocks_are_exact_right_sign_twists_for_both_slots"] is True
    assert theorem["four_v4_characters_realized_for_both_slots"] is True
    assert theorem["generators_are_commuting_involutions_for_both_slots"] is True
    assert theorem["pair_character_pattern_is_slot_independent"] is True
    assert theorem["cycle_orbit_preserves_v4_structure_for_both_slots"] is True


def test_active_right_support_matches_expected_slots() -> None:
    summary = build_l6_delta27_v4_bridge_summary()
    h2 = summary["slot_profiles"]["H_2"]
    hbar2 = summary["slot_profiles"]["Hbar_2"]
    assert h2["active_right_support_labels"] == ["u_c_1", "u_c_2", "u_c_3", "nu_c"]
    assert hbar2["active_right_support_labels"] == ["d_c_1", "d_c_2", "d_c_3", "e_c"]


def test_expected_v4_generators_are_realized_in_each_slot() -> None:
    summary = build_l6_delta27_v4_bridge_summary()
    h2 = summary["slot_profiles"]["H_2"]
    hbar2 = summary["slot_profiles"]["Hbar_2"]
    assert h2["generator_a_flipped_labels"] == ["u_c_1", "u_c_3"]
    assert h2["generator_b_flipped_labels"] == ["u_c_2", "nu_c"]
    assert hbar2["generator_a_flipped_labels"] == ["d_c_1"]
    assert hbar2["generator_b_flipped_labels"] == ["d_c_2", "d_c_3", "e_c"]


def test_pair_character_pattern_is_exact_and_slot_independent() -> None:
    summary = build_l6_delta27_v4_bridge_summary()
    expected = {
        "0->1": "I",
        "0->2": "A",
        "1->0": "AB",
        "1->2": "A",
        "2->0": "A",
        "2->1": "B",
    }
    assert summary["slot_profiles"]["H_2"]["pair_character_labels"] == expected
    assert summary["slot_profiles"]["Hbar_2"]["pair_character_labels"] == expected


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_delta27_v4_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "matrix level" in data["bridge_verdict"]
