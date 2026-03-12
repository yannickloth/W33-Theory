from __future__ import annotations

import json
from pathlib import Path

from w33_transport_path_groupoid_bridge import (
    build_transport_path_groupoid_summary,
    write_summary,
)


def test_path_groupoid_functor_and_tree_gauge_are_exact() -> None:
    summary = build_transport_path_groupoid_summary()
    assert summary["status"] == "ok"
    groupoid = summary["path_groupoid"]
    gauge = summary["spanning_tree_gauge"]
    assert groupoid["objects"] == 45
    assert groupoid["undirected_generating_edges"] == 720
    assert groupoid["directed_generating_morphisms"] == 1440
    assert groupoid["path_transport_respects_inversion"] is True
    assert gauge["tree_edges"] == 44
    assert gauge["fundamental_cycles"] == 676
    assert gauge["all_tree_edges_gauge_trivialized"] is True
    assert gauge["fundamental_cycle_holonomy_group_order"] == 6
    assert gauge["fundamental_cycle_holonomies_realize_full_weyl_a2"] is True


def test_transport_local_system_changes_exactly_at_mod_3() -> None:
    summary = build_transport_path_groupoid_summary()
    real_local = summary["real_local_system"]
    ternary = summary["ternary_reduction"]
    assert real_local["common_fixed_subspace_dimension"] == 0
    assert real_local["has_nonzero_flat_section"] is False
    assert ternary["common_fixed_subspace_dimension"] == 1
    assert ternary["unique_invariant_projective_line"] == [1, 2]
    assert ternary["adapted_group_is_upper_triangular"] is True
    assert ternary["quotient_character_values"] == [1, 2]
    assert ternary["quotient_character_is_exact_binary_shadow"] is True


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_transport_path_groupoid_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["ternary_reduction"]["common_fixed_subspace_dimension"] == 1
