from __future__ import annotations

import json
from pathlib import Path

from w33_tomotope_partial_sheet_bridge import (
    build_tomotope_partial_sheet_summary,
    partial_a_principal_counts,
    partial_b_principal_counts,
    partial_a_rows,
    partial_b_rows,
    write_summary,
)


def test_partial_packets_are_exact() -> None:
    assert partial_a_principal_counts() == (8, 24, 32, 8, 8)
    assert partial_b_principal_counts() == (4, 12, 16, 4, 4)
    assert len(partial_a_rows()) == 5
    assert len(partial_b_rows()) == 5


def test_partial_a_is_exactly_twice_partial_b() -> None:
    summary = build_tomotope_partial_sheet_summary()
    packets = summary["principal_packets"]
    assert packets["entrywise_ratio"] == [2, 2, 2, 2, 2]
    assert packets["partial_a_equals_two_times_partial_b"] is True
    assert packets["partial_difference_equals_partial_b"] is True


def test_partial_sheet_bridge_matches_live_count_and_order_data() -> None:
    summary = build_tomotope_partial_sheet_summary()
    bridge = summary["live_count_alignment"]
    assert bridge["partial_b_matches_tomotope_edge_triangle_cell_counts"] is True
    assert bridge["partial_a_matches_universal_edge_triangle_cell_counts"] is True
    assert bridge["automorphism_ratio_matches_sheet_doubling"] is True
    assert bridge["flag_ratio_matches_sheet_doubling"] is True
    assert bridge["monodromy_ratio_is_quadratic_not_linear"] is True
    assert "two-sheet count collapse" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_tomotope_partial_sheet_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["principal_packets"]["partial_a"] == [8, 24, 32, 8, 8]
