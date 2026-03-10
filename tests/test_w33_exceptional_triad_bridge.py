from __future__ import annotations

import json
from pathlib import Path

from w33_exceptional_triad_bridge import (
    best_classical_overlaps,
    build_exceptional_triad_summary,
    classical_exceptional_trio,
    direct_classical_analogy,
    projective_exceptional_trio,
    write_summary,
)


def test_no_projective_member_is_a_direct_classical_match() -> None:
    projective = projective_exceptional_trio()
    classical = classical_exceptional_trio()
    assert not any(direct_classical_analogy(left, right) for left in projective for right in classical)


def test_component_overlap_patterns_match_the_expected_channels() -> None:
    overlaps = best_classical_overlaps()
    assert overlaps["11-cell"]["best_matches"] == ["120-cell", "600-cell"]
    assert overlaps["11-cell"]["best_score"] == 1
    assert overlaps["57-cell"]["best_matches"] == ["120-cell", "600-cell"]
    assert overlaps["57-cell"]["best_score"] == 1
    assert overlaps["tomotope"]["best_matches"] == ["120-cell", "24-cell", "600-cell"]
    assert overlaps["tomotope"]["best_score"] == 1


def test_summary_records_nuanced_triad_verdict() -> None:
    summary = build_exceptional_triad_summary()
    assert summary["status"] == "ok"
    assert summary["direct_analogy_matrix"]["11-cell"]["600-cell"] is False
    assert summary["direct_analogy_matrix"]["57-cell"]["120-cell"] is False
    assert summary["direct_analogy_matrix"]["tomotope"]["24-cell"] is False
    assert "Closest to the 24-cell channel" in summary["triad_verdict"]["tomotope"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_exceptional_triad_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "global_verdict" in data
