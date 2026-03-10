from __future__ import annotations

import json
from pathlib import Path

from w33_mobius_szilassi_dual import (
    all_dual_faces,
    build_mobius_szilassi_dual_summary,
    dual_edge_set,
    dual_neighbors,
    dual_vertices,
    face_adjacency_via_shared_dual_edge,
    mobius_dual_matches_fano_incidence,
    write_summary,
)


def test_dual_graph_has_heawood_size_and_degree() -> None:
    assert len(dual_vertices()) == 14
    assert len(dual_edge_set()) == 21
    assert all(len(dual_neighbors(vertex)) == 3 for vertex in dual_vertices())


def test_dual_faces_are_seven_hexagons() -> None:
    dual_faces = all_dual_faces()
    assert len(dual_faces) == 7
    assert all(len(face) == 6 for face in dual_faces)


def test_dual_face_adjacency_is_complete_k7() -> None:
    adjacency = face_adjacency_via_shared_dual_edge()
    assert len(adjacency) == 21
    assert set(adjacency.values()) == {1}


def test_heawood_incidence_matches_shifted_fano_lines() -> None:
    assert mobius_dual_matches_fano_incidence() is True


def test_summary_records_explicit_abstract_szilassi_dual() -> None:
    summary = build_mobius_szilassi_dual_summary()
    assert summary["status"] == "ok"
    assert summary["summary"]["dual_vertex_count"] == 14
    assert summary["summary"]["dual_edge_count"] == 21
    assert summary["summary"]["dual_face_count"] == 7
    assert summary["heawood_checks"]["matches_shifted_fano_lines"] is True
    assert summary["szilassi_checks"]["every_dual_face_is_hexagon"] is True
    assert summary["szilassi_checks"]["complete_face_adjacency_k7"] is True
    assert "abstract Szilassi dual" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_mobius_szilassi_dual_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["summary"]["dual_face_size"] == 6
