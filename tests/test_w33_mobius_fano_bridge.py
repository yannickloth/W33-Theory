from __future__ import annotations

import json
from pathlib import Path

from w33_mobius_fano_bridge import (
    build_mobius_fano_summary,
    complementary_fano_heptad,
    complementary_fano_heptad_alias,
    edge_multiplicities,
    is_steiner_triple_system,
    mobius_torus_faces,
    standard_fano_heptad,
    torus_edge_membership_by_heptad,
    torus_euler_characteristic,
    write_summary,
)


def test_standard_heptad_is_fano_line_set_on_seven_vertices() -> None:
    heptad = standard_fano_heptad()
    assert len(heptad) == 7
    assert is_steiner_triple_system(heptad) is True
    assert len(edge_multiplicities(heptad)) == 21


def test_complementary_heptad_is_second_steiner_system() -> None:
    heptad = complementary_fano_heptad()
    assert len(heptad) == 7
    assert is_steiner_triple_system(heptad) is True
    assert heptad == complementary_fano_heptad_alias()
    assert set(heptad) != set(standard_fano_heptad())


def test_union_of_the_two_heptads_is_the_mobius_torus_seed() -> None:
    faces = mobius_torus_faces()
    counts = edge_multiplicities(faces)
    assert len(faces) == 14
    assert len(counts) == 21
    assert set(counts.values()) == {2}
    assert torus_euler_characteristic() == 0


def test_every_edge_appears_once_in_each_fano_heptad() -> None:
    memberships = torus_edge_membership_by_heptad()
    assert len(memberships) == 21
    assert set(memberships.values()) == {(1, 1)}


def test_summary_records_two_fano_planes_make_the_torus_seed() -> None:
    summary = build_mobius_fano_summary()
    assert summary["status"] == "ok"
    assert summary["steiner_system_checks"]["standard_is_sts_7"] is True
    assert summary["steiner_system_checks"]["complementary_is_sts_7"] is True
    assert summary["mobius_torus_checks"]["face_count"] == 14
    assert summary["mobius_torus_checks"]["each_edge_seen_once_per_heptad"] is True
    assert summary["incidence_lift"]["triangle_vertex_incidences"] == 42
    assert summary["incidence_lift"]["equals_two_fano_flag_sets"] is True
    assert summary["incidence_lift"]["rank3_flags"] == 84
    assert "union of two Fano heptads" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_mobius_fano_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["summary"]["euler_characteristic"] == 0
