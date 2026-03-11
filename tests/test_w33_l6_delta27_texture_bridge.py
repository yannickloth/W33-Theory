from __future__ import annotations

import json
from pathlib import Path

from w33_l6_delta27_texture_bridge import (
    build_l6_delta27_texture_bridge_summary,
    write_summary,
)


def test_fan_closures_match_exactly_for_both_external_slots() -> None:
    summary = build_l6_delta27_texture_bridge_summary()
    theorem = summary["delta27_envelope_theorem"]
    assert theorem["fan_closures_match_for_both_slots"] is True
    for profile in summary["slot_profiles"].values():
        assert profile["fan_closures_match_exactly"] is True
        assert profile["fan_closure_max_abs_difference"] < 1e-12


def test_canonical_closure_has_delta27_envelope_shape() -> None:
    summary = build_l6_delta27_texture_bridge_summary()
    theorem = summary["delta27_envelope_theorem"]
    assert theorem["canonical_closure_has_delta27_envelope_shape"] is True
    for profile in summary["slot_profiles"].values():
        texture = profile["canonical_texture"]
        assert texture["distinguished_generation"] == 0
        assert texture["off_diagonal_uniform"] is True
        assert texture["twofold_diagonal_degeneracy"] is True
        assert texture["distinguished_diagonal_is_unique"] is True


def test_cycle_orbit_rotates_the_distinguished_generation() -> None:
    summary = build_l6_delta27_texture_bridge_summary()
    theorem = summary["delta27_envelope_theorem"]
    assert theorem["canonical_closure_is_not_cycle_invariant"] is True
    assert theorem["cycle_orbit_has_three_distinguished_generations"] is True
    for profile in summary["slot_profiles"].values():
        assert profile["cycle_invariant"] is False
        assert [item["distinguished_generation"] for item in profile["cycle_orbit"]] == [0, 1, 2]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_delta27_texture_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "circulant-plus-diagonal shape" in data["bridge_verdict"]
