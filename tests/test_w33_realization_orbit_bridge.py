from __future__ import annotations

import json
from pathlib import Path

from w33_realization_orbit_bridge import (
    CSASZAR_REALIZATIONS,
    SZILASSI_REALIZATIONS,
    build_realization_orbit_summary,
    half_turn_vertex_permutation,
    write_summary,
)


def test_all_cataloged_realizations_share_the_same_half_turn_symmetry() -> None:
    for realization in list(CSASZAR_REALIZATIONS.values()) + list(SZILASSI_REALIZATIONS.values()):
        permutation = half_turn_vertex_permutation(realization)
        assert len(permutation) == len(realization)


def test_csaszar_realizations_have_four_vertex_orbits_and_seven_face_orbits() -> None:
    summary = build_realization_orbit_summary()
    family = summary["csaszar_family"]["summary"]
    assert family["realization_count"] == 5
    assert family["vertex_orbit_count"] == 4
    assert family["face_orbit_count"] == 7
    assert family["fixed_vertex_count"] == 1
    assert family["fixed_face_count"] == 0


def test_szilassi_realizations_have_dual_orbit_counts() -> None:
    summary = build_realization_orbit_summary()
    family = summary["szilassi_family"]["summary"]
    assert family["realization_count"] == 2
    assert family["vertex_orbit_count"] == 7
    assert family["face_orbit_count"] == 4
    assert family["fixed_vertex_count"] == 0
    assert family["fixed_face_count"] == 1


def test_summary_records_real_orbit_duality_not_catalog_algebra() -> None:
    summary = build_realization_orbit_summary()
    assert summary["status"] == "ok"
    assert summary["catalog_counts"]["total"] == 7
    assert summary["common_symmetry"]["present_in_all_cataloged_realizations"] is True
    assert summary["dual_orbit_package"]["is_dual_swap"] is True
    assert "do not currently behave like a verified 7-element algebra" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_realization_orbit_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["dual_orbit_package"]["csaszar_face_orbits"] == 7
