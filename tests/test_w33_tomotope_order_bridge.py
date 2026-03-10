from __future__ import annotations

import json
from pathlib import Path

from w33_tomotope_order_bridge import (
    build_tomotope_order_summary,
    minimal_regular_cover_order,
    rank4_flags_from_edge_local_incidence,
    tomotope_data,
    universal_tetrahedron_hemioctahedron_data,
    write_summary,
)


def test_edge_local_flag_count_is_16_per_edge() -> None:
    assert rank4_flags_from_edge_local_incidence(1) == 16
    assert rank4_flags_from_edge_local_incidence(12) == 192
    assert rank4_flags_from_edge_local_incidence(24) == 384


def test_universal_and_tomotope_orders_match_paper_counts() -> None:
    universal = universal_tetrahedron_hemioctahedron_data()
    tomotope = tomotope_data()
    assert universal.edges == 24
    assert universal.flags == 384
    assert universal.automorphism_group_order == 192
    assert universal.monodromy_group_order == 73728
    assert tomotope.edges == 12
    assert tomotope.flags == 192
    assert tomotope.automorphism_group_order == 96
    assert tomotope.monodromy_group_order == 18432


def test_both_uniform_polytopes_have_two_flag_orbits() -> None:
    universal = universal_tetrahedron_hemioctahedron_data()
    tomotope = tomotope_data()
    assert universal.flag_orbits_under_automorphisms == 2
    assert tomotope.flag_orbits_under_automorphisms == 2


def test_exact_cover_identities_hold() -> None:
    universal = universal_tetrahedron_hemioctahedron_data()
    tomotope = tomotope_data()
    cover_order = minimal_regular_cover_order()
    assert universal.automorphism_group_order == tomotope.flags
    assert tomotope.monodromy_group_order == tomotope.automorphism_group_order * tomotope.flags
    assert universal.monodromy_group_order == universal.automorphism_group_order * universal.flags
    assert cover_order == tomotope.flags**2
    assert cover_order == universal.automorphism_group_order**2
    assert cover_order == 2 * tomotope.monodromy_group_order


def test_summary_records_order_tower() -> None:
    summary = build_tomotope_order_summary()
    assert summary["status"] == "ok"
    assert summary["uniform_cover"]["flag_orbits_under_automorphisms"] == 2
    assert summary["tomotope"]["flag_orbits_under_automorphisms"] == 2
    assert summary["exact_identities"]["aut_universal_equals_flags_tomotope"] is True
    assert summary["exact_identities"]["regular_cover_equals_flags_t_squared"] is True
    assert summary["fano_tetra_bridge"]["matches_tomotope_flags"] is True


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_tomotope_order_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["minimal_regular_cover"]["automorphism_group_order"] == 36864
