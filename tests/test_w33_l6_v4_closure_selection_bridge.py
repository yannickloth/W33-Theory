from __future__ import annotations

import json
from pathlib import Path

from w33_l6_v4_closure_selection_bridge import (
    build_l6_v4_closure_selection_bridge_summary,
    write_summary,
)


def test_closure_selection_theorem_holds() -> None:
    summary = build_l6_v4_closure_selection_bridge_summary()
    theorem = summary["closure_selection_theorem"]
    assert theorem["forward_fan_is_exact_generation_2_row_for_both_slots"] is True
    assert theorem["reverse_completion_adds_exact_double_ab_i_a_row_for_both_slots"] is True
    assert theorem["reverse_fan_is_exact_two_row_a_column_shell_for_both_slots"] is True
    assert theorem["forward_completion_supplies_exact_missing_ab_i_and_a_b_entries_for_both_slots"] is True
    assert theorem["forward_route_assembles_canonical_label_matrix_for_both_slots"] is True
    assert theorem["reverse_route_assembles_canonical_label_matrix_for_both_slots"] is True
    assert theorem["canonical_label_matrix_is_slot_independent"] is True


def test_slot_profiles_record_exact_partial_label_matrices() -> None:
    summary = build_l6_v4_closure_selection_bridge_summary()
    for profile in summary["slot_profiles"].values():
        assert profile["forward_fan_seed_labels"] == [
            ["0", "0", "0"],
            ["0", "0", "0"],
            ["A", "B", "0"],
        ]
        assert profile["forward_then_reverse_increment_labels"] == [
            ["AB", "I", "A"],
            ["AB", "I", "A"],
            ["0", "0", "0"],
        ]
        assert profile["assembled_from_forward_route"] == [
            ["AB", "I", "A"],
            ["AB", "I", "A"],
            ["A", "B", "0"],
        ]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_v4_closure_selection_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "selected dynamically by exact l6 closure" in data["bridge_verdict"]
