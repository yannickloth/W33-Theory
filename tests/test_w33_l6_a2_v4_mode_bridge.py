from __future__ import annotations

import json
from pathlib import Path

from w33_l6_a2_v4_mode_bridge import (
    build_l6_a2_v4_mode_bridge_summary,
    write_summary,
)


def test_a2_modes_refine_to_v4_theorem() -> None:
    summary = build_l6_a2_v4_mode_bridge_summary()
    theorem = summary["a2_v4_mode_theorem"]
    assert theorem["all_mode_blocks_are_pure_right_character_twists"] is True
    assert theorem["pure_a_modes_are_exactly_8_and_128"] is True
    assert theorem["pure_b_modes_are_exactly_9_and_127"] is True
    assert theorem["mixed_i_a_ab_modes_are_exactly_246_and_247"] is True
    assert theorem["all_four_v4_characters_already_realized_on_fan_seed"] is True
    assert theorem["dormant_modes_127_128_awaken_as_single_block_channels"] is True


def test_slot_profiles_match_expected_mode_classes() -> None:
    summary = build_l6_a2_v4_mode_bridge_summary()
    for slot_profile in summary["slot_profiles"].values():
        assert slot_profile["pure_a_modes"] == [8, 128]
        assert slot_profile["pure_b_modes"] == [9, 127]
        assert slot_profile["mixed_i_a_ab_modes"] == [246, 247]
        assert slot_profile["all_realized_characters"] == ["A", "AB", "B", "I"]


def test_dormant_modes_awaken_as_single_block_channels() -> None:
    summary = build_l6_a2_v4_mode_bridge_summary()
    for slot_profile in summary["slot_profiles"].values():
        dormant = slot_profile["dormant_modes_awaken_as_single_block_channels"]
        assert dormant == {"127": True, "128": True}


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_a2_v4_mode_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "V4 flavour torsor" in data["bridge_verdict"]
