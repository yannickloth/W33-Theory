from __future__ import annotations

import json
from pathlib import Path

from w33_center_quad_transport_complement_bridge import (
    build_center_quad_transport_complement_summary,
    write_summary,
)


def test_transport_graph_is_exact_complement_srg() -> None:
    summary = build_center_quad_transport_complement_summary()
    assert summary["status"] == "ok"
    assert summary["point_graph_srg"] == {
        "vertices": 45,
        "degree": 12,
        "lambda": 3,
        "mu": 3,
        "edge_count": 270,
    }
    assert summary["transport_graph_srg"] == {
        "vertices": 45,
        "degree": 32,
        "lambda": 22,
        "mu": 24,
        "edge_count": 720,
    }


def test_transport_adjacency_is_exact_triangle_disjointness() -> None:
    complement = build_center_quad_transport_complement_summary()["complement_theorem"]
    assert complement["transport_is_complement_of_point_graph"] is True
    assert complement["transport_edges_are_exactly_disjoint_triangle_pairs"] is True
    assert complement["point_graph_edges_are_exactly_one_line_triangle_pairs"] is True
    assert complement["intersection_profile_by_transport_adjacency"] == {
        "True": {0: 720},
        "False": {1: 270},
    }


def test_every_transport_edge_has_unique_local_s3_matching() -> None:
    local = build_center_quad_transport_complement_summary()["local_s3_matching"]
    assert local["every_transport_edge_has_unique_matching"] is True
    assert local["all_six_permutations_realized_under_sorted_labels"] is True
    assert len(local["permutation_counts_under_sorted_labels"]) == 6
    assert sum(local["permutation_counts_under_sorted_labels"].values()) == 720


def test_raw_z2_is_strictly_finer_than_local_matching_data() -> None:
    local = build_center_quad_transport_complement_summary()["local_s3_matching"]
    assert local["raw_z2_not_determined_by_permutation"] is True
    assert local["raw_z2_not_determined_by_permutation_parity"] is True
    assert set(local["raw_z2_distribution_by_permutation_parity"]) == {"0", "1"}
    assert all(
        set(counter) == {0, 1}
        for counter in local["raw_z2_distribution_by_permutation"].values()
    )


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_center_quad_transport_complement_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "exact SRG(45,32,22,24)" in data["bridge_verdict"]
