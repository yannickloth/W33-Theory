from __future__ import annotations

import json
from pathlib import Path

from w33_center_quad_transport_bridge import (
    build_center_quad_transport_bridge_summary,
    write_summary,
)


def test_transport_cover_graph_is_regular_90_node_degree_32_cover() -> None:
    summary = build_center_quad_transport_bridge_summary()
    assert summary["status"] == "ok"
    assert summary["cover_graph"] == {
        "vertices": 90,
        "degree_distribution": {32: 90},
    }


def test_transport_quotient_graph_is_regular_45_node_degree_32_graph() -> None:
    summary = build_center_quad_transport_bridge_summary()
    quotient = summary["quotient_graph"]
    assert quotient["vertices"] == 45
    assert quotient["edges"] == 720
    assert quotient["degree_distribution"] == {32: 45}


def test_reconstructed_z2_distributions_match_archived_v14_exactly() -> None:
    summary = build_center_quad_transport_bridge_summary()
    quotient = summary["quotient_graph"]
    expected = {0: 414, 1: 306}
    assert quotient["raw_z2_distribution"] == expected
    assert quotient["canonical_z2_distribution"] == expected
    assert quotient["archived_v14_distributions"] == {
        "raw": expected,
        "canonical": expected,
    }
    assert quotient["matches_archived_exactly"] == {
        "raw": True,
        "canonical": True,
    }


def test_canonical_gauge_and_triangle_parity_match_old_transport_layer() -> None:
    summary = build_center_quad_transport_bridge_summary()
    assert summary["canonical_gauge"] == {
        "root": 0,
        "gauge_flip_distribution": {0: 39, 1: 6},
    }
    parity = summary["triangle_parity"]
    assert parity["reconstructed"]["num_triangles"] == 5280
    assert parity["reconstructed"]["parity0"] == 3120
    assert parity["reconstructed"]["parity1"] == 2160
    assert parity["reconstructed"]["parity1_fraction"] == 9.0 / 22.0
    assert parity["archived_v14"] == {
        "num_triangles": 5280,
        "parity0": 3120,
        "parity1": 2160,
        "parity1_fraction": 9.0 / 22.0,
    }
    assert parity["matches_archived_exactly"] == {
        "num_triangles": True,
        "parity0": True,
        "parity1": True,
    }


def test_transport_refinement_matches_exact_270_edge_and_54_pocket_package() -> None:
    summary = build_center_quad_transport_bridge_summary()
    refinement = summary["transport_refinement"]
    assert refinement["transport_edges_270"] == 270
    assert refinement["transport_generators"] == ["g2", "g3", "g5", "g8", "g9"]
    assert refinement["cocycle_distribution_z3"] == {0: 201, 1: 33, 2: 36}
    assert refinement["s3_sheet_pockets"] == 54
    assert refinement["s3_sheet_transport_exact"] is True
    assert refinement["nonzero_sheet_generator"] == ["g3"]


def test_v16_edge_lift_is_z2_trivial_but_s3_odd() -> None:
    summary = build_center_quad_transport_bridge_summary()
    lifted = summary["v16_edge_lift"]
    assert lifted["archived_edge"] == [41, 7]
    assert lifted["raw_z2_on_reconstructed_edge"] == 0
    assert lifted["archived_canonical_z2_voltage"] == 0
    assert lifted["archived_s3_perm"] == [0, 2, 1]
    assert lifted["archived_s3_perm_parity"] == 1
    assert lifted["z2_trivial_but_s3_odd"] is True


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_center_quad_transport_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["bridge_verdict"].startswith("The old quotient transport layer is real")
