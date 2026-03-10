from __future__ import annotations

import json
from pathlib import Path

from w33_tomotope_klitzing_ladder import (
    build_klitzing_ladder_summary,
    leading_counts,
    successive_doublings,
    tomotope_base_incidence_rows,
    tomotope_klitzing_operations,
    write_summary,
)


def test_operation_names_and_counts_match_klitzing_tomotope_rows() -> None:
    rows = tomotope_klitzing_operations()
    assert [row.name for row in rows] == [
        "rectified tomotope",
        "truncated tomotope",
        "maximal expanded tomotope",
        "omnitruncated tomotope",
    ]
    assert [row.leading_count for row in rows] == [12, 24, 48, 96]
    assert rows[0].row_text.startswith("mids(mod_b")
    assert rows[1].row_text.startswith("trops(mod_b")


def test_base_incidence_rows_reproduce_core_tomotope_counts() -> None:
    rows = tomotope_base_incidence_rows()
    assert len(rows) == 5
    assert "| 12 |" in rows[1]
    assert "| 16 |" in rows[2]
    assert rows[1].endswith("2 2")
    assert rows[2].endswith("1 1")


def test_klitzing_ladder_is_a_pure_doubling_chain() -> None:
    assert leading_counts() == (12, 24, 48, 96)
    assert successive_doublings() == (2, 2, 2)


def test_summary_records_exact_arithmetic_matches() -> None:
    summary = build_klitzing_ladder_summary()
    assert summary["status"] == "ok"
    assert summary["base_matrix_reference"]["gc_symbol"] == "x3o3o *b4o"
    assert summary["base_count_checks"]["vertices_match"] is True
    assert summary["base_count_checks"]["edges_match"] is True
    assert summary["base_count_checks"]["triangles_match"] is True
    assert summary["exact_matches"]["rectified_leading_count_matches_tomotope_edges"] is True
    assert summary["exact_matches"]["truncated_leading_count_matches_tetrahedron_flags"] is True
    assert summary["exact_matches"]["truncated_leading_count_matches_fano_point_stabilizer"] is True
    assert summary["exact_matches"]["omnitruncated_leading_count_matches_tomotope_automorphism_order"] is True


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_tomotope_klitzing_ladder_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["leading_count_ladder"] == [12, 24, 48, 96]
