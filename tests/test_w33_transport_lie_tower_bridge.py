from __future__ import annotations

import json
from pathlib import Path

from w33_transport_lie_tower_bridge import (
    build_transport_lie_tower_bridge_summary,
    l6_a2_generation_channels,
    l6_cartan_diagonal_profiles,
    transport_weyl_class_profiles,
    write_summary,
)


def test_transport_weyl_classes_match_exact_edge_counts() -> None:
    profiles = {profile.class_name: profile for profile in transport_weyl_class_profiles()}
    assert profiles["identity"].edge_count == 192
    assert profiles["reflection"].edge_count == 396
    assert profiles["three_cycle"].edge_count == 132


def test_l6_a2_modes_realize_all_six_ordered_generation_channels() -> None:
    channels = l6_a2_generation_channels()
    assert {(channel.source_generation, channel.target_generation) for channel in channels} == {
        (0, 1),
        (1, 0),
        (1, 2),
        (2, 1),
        (0, 2),
        (2, 0),
    }


def test_l6_a2_generation_channels_are_signed_permutation_blocks() -> None:
    for channel in l6_a2_generation_channels():
        assert channel.block_rank == 16
        assert channel.nonzero_entries == 16
        assert channel.signed_permutation is True
        assert channel.orthogonal_block is True


def test_l6_cartan_modes_are_generation_diagonal_only() -> None:
    profiles = l6_cartan_diagonal_profiles()
    assert len(profiles) == 8
    assert all(profile.off_diagonal_nonzeros == 0 for profile in profiles)
    assert profiles[0].diagonal_nonzeros == 18
    assert profiles[-1].diagonal_nonzeros == 32


def test_summary_records_transport_lie_tower_bridge() -> None:
    summary = build_transport_lie_tower_bridge_summary()
    theorem = summary["generation_channel_theorem"]
    split = summary["l6_exceptional_split"]
    assert split["e6_root_support_size"] == 72
    assert split["a2_root_support_size"] == 6
    assert split["cartan_support_size"] == 8
    assert split["spinor_action_ranks"] == (40, 6, 8)
    assert theorem["complete_oriented_three_generation_graph"] is True
    assert theorem["all_a2_channels_are_signed_permutation_blocks"] is True
    assert theorem["all_cartan_modes_are_generation_diagonal"] is True
    assert theorem["current_l6_bridge_activates_only_cartan_modes"] is True


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_transport_lie_tower_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["transport_weyl_classes"][0]["edge_count"] == 132
    assert "operator level" in data["bridge_verdict"]
