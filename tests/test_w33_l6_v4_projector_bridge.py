from __future__ import annotations

import json
from pathlib import Path

from w33_l6_v4_projector_bridge import (
    build_l6_v4_projector_bridge_summary,
    write_summary,
)


def test_v4_projector_theorem_holds() -> None:
    summary = build_l6_v4_projector_bridge_summary()
    theorem = summary["projector_theorem"]
    assert theorem["projectors_are_exact_eigenspace_splitters"] is True
    assert theorem["minus_minus_projector_vanishes_for_both_slots"] is True
    assert theorem["plus_plus_projector_is_exact_inactive_support_for_both_slots"] is True
    assert theorem["h2_active_support_splits_as_2_plus_2"] is True
    assert theorem["hbar2_active_support_splits_as_1_plus_3"] is True


def test_expected_slot_projector_supports() -> None:
    summary = build_l6_v4_projector_bridge_summary()
    h2 = summary["slot_profiles"]["H_2"]["projectors"]
    hbar2 = summary["slot_profiles"]["Hbar_2"]["projectors"]
    assert h2["++"]["support_labels"] == ["d_c_1", "d_c_2", "d_c_3", "e_c"]
    assert h2["+-"]["support_labels"] == ["u_c_2", "nu_c"]
    assert h2["-+"]["support_labels"] == ["u_c_1", "u_c_3"]
    assert h2["--"]["support_labels"] == []
    assert hbar2["++"]["support_labels"] == ["u_c_1", "u_c_2", "u_c_3", "nu_c"]
    assert hbar2["+-"]["support_labels"] == ["d_c_2", "d_c_3", "e_c"]
    assert hbar2["-+"]["support_labels"] == ["d_c_1"]
    assert hbar2["--"]["support_labels"] == []


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_v4_projector_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "2+2" in data["bridge_verdict"]
