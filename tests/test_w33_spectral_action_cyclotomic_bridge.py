from __future__ import annotations

import json
from pathlib import Path

from w33_spectral_action_cyclotomic_bridge import (
    build_spectral_action_cyclotomic_summary,
    write_summary,
)


def test_spectral_action_cyclotomic_bridge_locks_internal_ratios() -> None:
    summary = build_spectral_action_cyclotomic_summary()
    assert summary["status"] == "ok"
    data = summary["cyclotomic_data"]
    assert data["q"] == 3
    assert data["phi3"] == 13
    assert data["phi6"] == 7
    assert data["four_phi3_plus_q"] == 55
    assert data["q_phi3"] == 39

    internal = summary["internal_spectral_action"]
    assert internal["a0_f"] == 480
    assert internal["a2_f"] == 2240
    assert internal["a4_f"] == 17600
    assert internal["a2_over_a0"]["exact"] == "14/3"
    assert internal["a2_over_a0_matches_formula"] is True
    assert internal["a4_over_a0"]["exact"] == "110/3"
    assert internal["a4_over_a0_matches_formula"] is True
    assert internal["higgs_ratio_square"]["exact"] == "14/55"
    assert internal["higgs_ratio_square_matches_formula"] is True


def test_spectral_action_cyclotomic_bridge_locks_gravity_ratios() -> None:
    summary = build_spectral_action_cyclotomic_summary()
    gravity = summary["gravity_lock"]
    assert gravity["continuum_eh_over_a0"]["exact"] == "2/3"
    assert gravity["continuum_eh_over_a0_matches_formula"] is True
    assert gravity["discrete_6_mode_over_a0"]["exact"] == "26"
    assert gravity["discrete_6_mode_over_a0_matches_formula"] is True
    assert gravity["discrete_to_continuum_ratio"]["exact"] == "39"
    assert gravity["discrete_to_continuum_matches_formula"] is True


def test_spectral_action_cyclotomic_bridge_writes_summary(tmp_path: Path) -> None:
    out = tmp_path / "summary.json"
    write_summary(out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["internal_spectral_action"]["higgs_ratio_square"]["exact"] == "14/55"
