from __future__ import annotations

import json
from pathlib import Path

from w33_transport_ternary_line_bridge import (
    build_transport_ternary_line_summary,
    write_summary,
)


def test_transport_ternary_line_selects_canonical_qutrit_sector() -> None:
    summary = build_transport_ternary_line_summary()
    transport = summary["transport_side"]
    matter = summary["matter_side"]
    combined = summary["combined_sector"]
    assert summary["status"] == "ok"
    assert transport["real_flat_section_dimension"] == 0
    assert transport["ternary_flat_section_dimension"] == 1
    assert transport["invariant_line"] == [1, 2]
    assert transport["quotient_character_values"] == [1, 2]
    assert matter["homological_field"] == "F3"
    assert matter["logical_qutrits"] == 81
    assert matter["canonical_transport_stable_sector_dimension"] == 81
    assert combined["full_reduced_a2_fiber_rank"] == 2
    assert combined["matter_flavour_dimension"] == 162
    assert combined["flat_internal_dimension"] == 162
    assert combined["matches_flat_internal_dimension_exactly"] is True


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_transport_ternary_line_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["combined_sector"]["matter_flavour_dimension"] == 162
