from __future__ import annotations

import json
from pathlib import Path

from w33_l6_v4_seed_reconstruction_bridge import (
    build_l6_v4_seed_reconstruction_bridge_summary,
    write_summary,
)


def test_seed_reconstruction_theorem_holds() -> None:
    summary = build_l6_v4_seed_reconstruction_bridge_summary()
    theorem = summary["seed_reconstruction_theorem"]
    assert theorem["label_matrix_is_slot_independent"] is True
    assert theorem["expected_label_matrix"] == [
        ["AB", "I", "A"],
        ["AB", "I", "A"],
        ["A", "B", "0"],
    ]
    assert theorem["reconstructs_canonical_closure_exactly_for_both_slots"] is True
    assert theorem["generation_0_diagonal_delta_equals_offdiag_1_to_0_for_both_slots"] is True
    assert theorem["generation_1_diagonal_delta_equals_offdiag_0_to_1_for_both_slots"] is True
    assert theorem["generation_2_diagonal_block_is_unchanged_for_both_slots"] is True
    assert theorem["reference_projector_rank_split_matches_h2_2_plus_2_and_hbar2_3_plus_1"] is True


def test_slot_profiles_have_zero_reconstruction_error() -> None:
    summary = build_l6_v4_seed_reconstruction_bridge_summary()
    for profile in summary["slot_profiles"].values():
        assert profile["reconstructs_exactly"] is True
        assert profile["max_abs_reconstruction_error"] < 1e-12


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_v4_seed_reconstruction_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "[[AB,I,A],[AB,I,A],[A,B,0]]" in data["bridge_verdict"]
