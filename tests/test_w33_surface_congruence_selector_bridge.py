from __future__ import annotations

import json
from pathlib import Path

from w33_surface_congruence_selector_bridge import (
    build_surface_congruence_selector_summary,
    write_summary,
)


def test_surface_selector_residue_classes_are_exact() -> None:
    summary = build_surface_congruence_selector_summary()
    selector = summary["surface_selector"]
    assert selector["vertex_genus_formula"] == "g = (v - 3)(v - 4) / 12"
    assert selector["face_genus_formula"] == "g = (f - 3)(f - 4) / 12"
    assert selector["vertex_integral_residues_mod_12"] == [0, 3, 4, 7]
    assert selector["face_integral_residues_mod_12"] == [0, 3, 4, 7]
    assert selector["residue_classes_match_exactly"] is True
    assert selector["admissible_residues_are_0_3_4_7"] is True
    assert selector["first_positive_admissible_values"][:6] == [4, 7, 12, 15, 16, 19]


def test_tetrahedron_and_torus_values_are_selected_exactly() -> None:
    summary = build_surface_congruence_selector_summary()
    values = summary["fixed_and_first_torus_values"]
    assert values["tetrahedron_fixed_point_value"] == 4
    assert values["tetrahedron_vertex_genus"] == 0
    assert values["tetrahedron_face_genus"] == 0
    assert values["tetrahedron_is_self_dual_fixed_point"] is True
    assert values["first_toroidal_dual_value"] == 7
    assert values["csaszar_vertex_value"] == 7
    assert values["szilassi_face_value"] == 7
    assert values["first_toroidal_dual_value_is_7"] is True
    assert values["csaszar_and_szilassi_share_first_toroidal_value"] is True
    assert "0,3,4,7 mod 12" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_surface_congruence_selector_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["surface_selector"]["vertex_integral_residues_mod_12"] == [0, 3, 4, 7]
