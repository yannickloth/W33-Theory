from __future__ import annotations

import json
from pathlib import Path

from w33_explicit_curved_4d_complexes import (
    build_explicit_curved_4d_complexes_summary,
    cp2_facets,
    cp2_profile,
    k3_facets,
    k3_profile,
    write_summary,
)


def test_cp2_explicit_complex_matches_classical_counts() -> None:
    facets = cp2_facets()
    profile = cp2_profile()
    assert len(facets) == 36
    assert profile.vertices == 9
    assert profile.facets == 36
    assert profile.f_vector == (9, 36, 84, 90, 36)
    assert profile.betti_numbers == (1, 0, 1, 0, 1)
    assert profile.harmonic_form_total == 3
    assert profile.euler_characteristic == 3


def test_k3_explicit_complex_matches_classical_counts() -> None:
    facets = k3_facets()
    profile = k3_profile()
    assert len(facets) == 288
    assert profile.vertices == 16
    assert profile.facets == 288
    assert profile.f_vector == (16, 120, 560, 720, 288)
    assert profile.betti_numbers == (1, 0, 22, 0, 1)
    assert profile.harmonic_form_total == 24
    assert profile.euler_characteristic == 24


def test_boundary_ranks_recover_middle_betti_numbers() -> None:
    cp2 = cp2_profile()
    k3 = k3_profile()
    assert cp2.boundary_ranks == (8, 28, 55, 35)
    assert k3.boundary_ranks == (15, 105, 433, 287)


def test_summary_records_explicit_external_chain_complexes() -> None:
    summary = build_explicit_curved_4d_complexes_summary()
    assert summary["status"] == "ok"
    assert summary["construction_notes"]["cp2_base_facets"] == 12
    assert summary["construction_notes"]["k3_orbit_group_order"] == 240
    assert summary["profiles"][0]["betti_numbers"] == (1, 0, 1, 0, 1)
    assert summary["profiles"][1]["betti_numbers"] == (1, 0, 22, 0, 1)
    assert "explicit simplicial complexes" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_explicit_curved_4d_complexes_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["profiles"][0]["facets"] == 36
    assert data["profiles"][1]["facets"] == 288
