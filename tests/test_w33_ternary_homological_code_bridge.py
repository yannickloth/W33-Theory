from __future__ import annotations

import json
from pathlib import Path

from w33_ternary_homological_code_bridge import (
    build_ternary_homological_code_summary,
    write_summary,
)


def test_ternary_homological_code_parameters_are_exact() -> None:
    summary = build_ternary_homological_code_summary()
    chain = summary["chain_complex"]
    code = summary["ternary_css_code"]
    assert summary["status"] == "ok"
    assert chain["vertices"] == 40
    assert chain["edges"] == 240
    assert chain["triangles"] == 160
    assert chain["tetrahedra"] == 40
    assert chain["boundary_of_boundary_vanishes_mod_3"] is True
    assert code["field"] == "F3"
    assert code["physical_qutrits"] == 240
    assert code["x_check_rank"] == 39
    assert code["z_check_rank"] == 120
    assert code["logical_qutrits"] == 81
    assert code["logical_hilbert_dimension_log_3"] == 81
    assert code["stabilizer_rank_total"] == 159


def test_primal_logical_distance_is_exactly_four() -> None:
    summary = build_ternary_homological_code_summary()
    distance = summary["homological_distance"]
    assert distance["no_nontrivial_logical_cycles_of_weight_1_or_2"] is True
    assert distance["all_weight_3_cycles_are_triangle_boundaries"] is True
    assert distance["primal_logical_distance"] == 4
    assert distance["witness_cycle_vertices"] == [0, 4, 1, 13]
    assert distance["witness_cycle_edges"] == [[0, 4], [1, 4], [1, 13], [0, 13]]
    assert sorted(distance["witness_cycle_coefficients_mod_3"]) == [1, 1, 2, 2]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_ternary_homological_code_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["ternary_css_code"]["logical_qutrits"] == 81
