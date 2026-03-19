from __future__ import annotations

import json
from pathlib import Path

from w33_heawood_shell_ladder_bridge import (
    build_heawood_shell_ladder_summary,
    write_summary,
)


def test_heawood_shell_counts_close_across_phi6_g2_ag21_and_d4() -> None:
    summary = build_heawood_shell_ladder_summary()
    shell = summary["heawood_shell_dictionary"]
    assert shell["heptad_size"] == 7
    assert shell["phi6"] == 7
    assert shell["heawood_vertices"] == 14
    assert shell["g2_dimension"] == 14
    assert shell["heawood_edges"] == 21
    assert shell["ag21_length"] == 21
    assert shell["hurwitz_unit_order"] == 24
    assert shell["d4_seed_order"] == 24
    assert shell["affine_order"] == 42
    assert shell["preserving_order"] == 168
    assert shell["full_order"] == 336
    assert shell["preserving_edge_stabilizer"] == 8
    assert shell["full_edge_stabilizer"] == 16


def test_exact_shell_factorizations_hold() -> None:
    summary = build_heawood_shell_ladder_summary()
    factors = summary["exact_factorizations"]
    assert factors["heptad_size_equals_phi6"] is True
    assert factors["vertices_equal_2_times_phi6"] is True
    assert factors["vertices_equal_g2_dimension"] is True
    assert factors["edges_equal_3_times_phi6"] is True
    assert factors["edges_equal_ag21_length"] is True
    assert factors["affine_order_equals_2_times_ag21"] is True
    assert factors["affine_preserver_equals_ag21"] is True
    assert factors["hurwitz_units_equal_d4_seed"] is True
    assert factors["preserving_order_equals_hurwitz_units_times_phi6"] is True
    assert factors["preserving_order_equals_d4_seed_times_phi6"] is True
    assert factors["preserving_order_equals_ag21_times_preserving_edge_stabilizer"] is True
    assert factors["full_order_equals_2_times_preserving"] is True
    assert factors["full_order_equals_hurwitz_units_times_g2_dimension"] is True
    assert factors["full_order_equals_d4_seed_times_g2_dimension"] is True
    assert factors["full_order_equals_ag21_times_full_edge_stabilizer"] is True
    assert factors["full_order_equals_affine_order_times_preserving_edge_stabilizer"] is True
    assert "|Hurwitz units|*dim(G2)" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_heawood_shell_ladder_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["heawood_shell_dictionary"]["full_order"] == 336
