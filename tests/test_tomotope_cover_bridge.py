from __future__ import annotations

import json
import math
from pathlib import Path

from tools.tomotope_cover_bridge import (
    build_cover_bridge_summary,
    monodromy_growth_degree,
    native_cover_dimension,
    qk_covers_qm,
    qk_level,
    theorem_5_9_pair,
    write_summary,
)


def test_q1_is_special_prepolytope_level() -> None:
    level = qk_level(1)
    assert level.regular_polytope is False
    assert level.block_side == 2
    assert level.unit_cube_count == 8
    assert level.quotient_group_order == 192
    assert level.monodromy_order == 36864
    assert level.vertices is None


def test_qk_regular_level_counts_match_paper_formulas() -> None:
    level = qk_level(2)
    assert level.regular_polytope is True
    assert level.vertices == 32
    assert level.edges == 192
    assert level.triangles == 256
    assert level.tetrahedra == 64
    assert level.octahedra == 32


def test_divisibility_is_the_cover_relation() -> None:
    assert qk_covers_qm(15, 3) is True
    assert qk_covers_qm(15, 5) is True
    assert qk_covers_qm(15, 4) is False


def test_theorem_5_9_detects_coprime_odd_pairs() -> None:
    assert theorem_5_9_pair(3, 5) is True
    assert theorem_5_9_pair(5, 7) is True
    assert theorem_5_9_pair(3, 9) is False
    assert theorem_5_9_pair(2, 5) is False


def test_native_carrier_growth_is_cubic() -> None:
    assert math.isclose(native_cover_dimension(), 3.0, rel_tol=0.0, abs_tol=1e-12)


def test_monodromy_growth_is_degree_six() -> None:
    assert math.isclose(monodromy_growth_degree(), 6.0, rel_tol=0.0, abs_tol=1e-12)


def test_summary_keeps_reye_and_24_cell_bridge_visible() -> None:
    summary = build_cover_bridge_summary()
    bridge = summary["reye_24cell_bridge"]
    assert bridge["tomotope_edges"] == 12
    assert bridge["tomotope_faces"] == 16
    assert bridge["reye_points"] == 12
    assert bridge["reye_lines"] == 16
    assert bridge["cell24_axes"] == 12
    assert bridge["cell24_hexagons"] == 16
    assert bridge["d4_root_count"] == 24


def test_summary_explicitly_rules_out_native_four_dimensional_scaling() -> None:
    summary = build_cover_bridge_summary()
    scaling = summary["native_scaling"]
    assert scaling["carrier_dimension_is_four"] is False
    assert scaling["needs_external_4d_factor"] is True
    assert "3D refinement tower" in scaling["verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "tomotope_cover_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["qk_family"]["sample_levels"][0]["k"] == 1
    assert data["native_scaling"]["carrier_growth_degree"] == 3.0
