from __future__ import annotations

import json
from pathlib import Path

from w33_fano_group_bridge import dihedral_square_permutations, fano_flags, flag_stabilizer
from w33_fano_square_tomotope_bridge import (
    all_flag_line_matchings,
    build_fano_square_tomotope_summary,
    canonical_square_edges,
    diagonal_matching,
    induced_flag_stabilizer_square_permutations,
    local_tomotope_edge_flag_count,
    off_line_points,
    preserves_square_edges,
    write_summary,
)


def test_flag_induces_three_perfect_matchings_of_k4() -> None:
    flag_point, flag_line = fano_flags()[0]
    matchings = all_flag_line_matchings(flag_point, flag_line)
    assert len(matchings) == 3
    off_points = set(off_line_points(flag_line))
    seen_edges = set()
    for matching in matchings.values():
        assert len(matching) == 2
        covered = set()
        for left, right in matching:
            assert left in off_points
            assert right in off_points
            assert left != right
            covered.add(left)
            covered.add(right)
            seen_edges.add((left, right))
        assert covered == off_points
    assert len(seen_edges) == 6


def test_flag_point_matching_becomes_square_diagonals() -> None:
    flag_point, flag_line = fano_flags()[0]
    diagonal = diagonal_matching(flag_point, flag_line)
    square_edges = canonical_square_edges(flag_point, flag_line)
    assert len(diagonal) == 2
    assert len(square_edges) == 4
    assert set(diagonal).isdisjoint(square_edges)


def test_flag_stabilizer_is_exact_square_automorphism_group() -> None:
    flag_point, flag_line = fano_flags()[0]
    stabilizer = flag_stabilizer(flag_point, flag_line)
    assert len(stabilizer) == 8
    assert induced_flag_stabilizer_square_permutations(flag_point, flag_line) == dihedral_square_permutations()
    assert all(preserves_square_edges(matrix, flag_point, flag_line) for matrix in stabilizer)


def test_local_tomotope_edge_model_has_16_flags() -> None:
    assert local_tomotope_edge_flag_count() == 16


def test_summary_records_square_and_tomotope_bridge() -> None:
    summary = build_fano_square_tomotope_summary()
    assert summary["status"] == "ok"
    assert summary["summary"]["off_line_point_count"] == 4
    assert summary["summary"]["square_edge_count"] == 4
    assert summary["summary"]["flag_stabilizer_order"] == 8
    assert summary["stabilizer_checks"]["induced_permutations_are_d8"] is True
    assert summary["tomotope_local_bridge"]["flags_around_edge"] == 16


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_fano_square_tomotope_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["summary"]["square_automorphism_group_order"] == 8
