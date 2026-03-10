from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path

from w33_fano_group_bridge import (
    build_fano_group_summary,
    dihedral_square_permutations,
    fano_flags,
    fano_lines,
    fano_points,
    flag_stabilizer,
    flag_stabilizer_is_dihedral_square,
    flag_stabilizer_off_line_point_permutations,
    gl32_group,
    induced_tetrahedral_permutations,
    line_stabilizer,
    off_line_points,
    point_stabilizer,
    tetrahedral_action_is_full_s4,
    tomotope_factorization_via_tetra_and_flag_stabilizer,
    write_summary,
)


def test_gl32_group_has_order_168() -> None:
    assert len(gl32_group()) == 168


def test_fano_plane_has_7_points_7_lines_and_21_flags() -> None:
    assert len(fano_points()) == 7
    assert len(fano_lines()) == 7
    assert len(fano_flags()) == 21


def test_point_line_and_flag_stabilizers_have_expected_orders() -> None:
    point = fano_points()[0]
    line = next(line for line in fano_lines() if point in line)
    assert len(point_stabilizer(point)) == 24
    assert len(line_stabilizer(line)) == 24
    assert len(flag_stabilizer(point, line)) == 8


def test_point_stabilizer_induces_full_s4_on_four_lines_not_through_point() -> None:
    point = fano_points()[0]
    perms = induced_tetrahedral_permutations(point)
    assert len(perms) == 24
    assert set(perms) == set(permutations(range(4)))
    assert tetrahedral_action_is_full_s4(point) is True


def test_tomotope_factorization_matches_24_times_8() -> None:
    assert tomotope_factorization_via_tetra_and_flag_stabilizer() == 192


def test_flag_stabilizer_is_dihedral_square_on_four_off_line_points() -> None:
    point, line = fano_flags()[0]
    assert len(off_line_points(line)) == 4
    assert flag_stabilizer_off_line_point_permutations(point, line) == dihedral_square_permutations()
    assert flag_stabilizer_is_dihedral_square(point, line) is True


def test_summary_records_group_and_tomotope_bridge() -> None:
    summary = build_fano_group_summary()
    assert summary["status"] == "ok"
    assert summary["summary"]["group_order"] == 168
    assert summary["summary"]["point_stabilizer_order"] == 24
    assert summary["summary"]["flag_stabilizer_order"] == 8
    assert summary["summary"]["tomotope_factorization_via_tetra_and_flag_stabilizer"] == 192
    assert summary["tetrahedral_bridge"]["point_stabilizer_induces_full_s4"] is True
    assert summary["local_square_bridge"]["flag_stabilizer_is_dihedral_square"] is True
    assert summary["local_square_bridge"]["dihedral_square_group_order"] == 8
    assert summary["tomotope_bridge"]["matches_tomotope_flags"] is True


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_fano_group_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["summary"]["group_order"] == 168
