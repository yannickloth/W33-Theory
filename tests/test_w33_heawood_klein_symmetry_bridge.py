from __future__ import annotations

import json
from pathlib import Path

from w33_heawood_klein_symmetry_bridge import (
    build_heawood_klein_symmetry_summary,
    write_summary,
)


def test_heawood_preserving_and_full_symmetry_orders_are_exact() -> None:
    summary = build_heawood_klein_symmetry_summary()
    graph = summary["heawood_graph"]
    preserving = summary["bipartition_preserving_symmetry"]
    full = summary["full_symmetry"]
    assert graph["vertex_count"] == 14
    assert graph["edge_count"] == 21
    assert graph["bipartition_sizes"] == [7, 7]
    assert graph["connected_bipartition_unique_up_to_swap"] is True
    assert preserving["point_collineation_order"] == 168
    assert preserving["heawood_bipartition_preserving_order"] == 168
    assert preserving["flag_edge_stabilizer_order"] == 8
    assert preserving["matches_fano_collineation_order"] is True
    assert preserving["matches_fano_flag_stabilizer_order"] is True
    assert preserving["matches_dual_toroidal_pair_flag_count"] is True
    assert full["full_heawood_automorphism_order"] == 336
    assert full["full_equals_two_times_bipartition_preserving"] is True
    assert full["edge_stabilizer_order"] == 16
    assert full["generated_by_collineations_and_polarity"] is True
    assert full["all_generated_permutations_preserve_edges"] is True
    assert full["full_order_equals_two_times_dual_toroidal_pair_flags"] is True


def test_explicit_polarity_doubles_to_the_full_heawood_group() -> None:
    summary = build_heawood_klein_symmetry_summary()
    duality = summary["point_line_duality"]
    klein = summary["klein_quartic_bridge"]
    assert duality["polarity_formula"] == "i -> -i mod 7"
    assert duality["polarity_permutation"] == [0, 6, 5, 4, 3, 2, 1]
    assert duality["polarity_is_incidence_duality"] is True
    assert duality["polarity_swap_is_edge_automorphism"] is True
    assert duality["polarity_swap_is_involution"] is True
    assert klein["klein_quartic_orientation_preserving_order"] == 168
    assert klein["matches_klein_quartic_orientation_preserving_order"] is True
    assert klein["full_heawood_order_is_double_klein_order"] is True
    assert klein["preserving_order_equals_8_times_21"] is True
    assert klein["full_order_equals_16_times_21"] is True
    assert "168/336 symmetry ladder as the Klein-quartic side" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_heawood_klein_symmetry_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["full_symmetry"]["full_heawood_automorphism_order"] == 336
