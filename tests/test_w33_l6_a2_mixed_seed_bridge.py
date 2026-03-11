from __future__ import annotations

import json
from pathlib import Path

from w33_l6_a2_mixed_seed_bridge import (
    build_l6_a2_mixed_seed_bridge_summary,
    write_summary,
)


def _profile_by_seed_modes(*seed_modes: int) -> dict:
    summary = build_l6_a2_mixed_seed_bridge_summary()
    for profile in summary["profiles"]:
        if tuple(profile["seed_modes"]) == seed_modes:
            return profile
    raise AssertionError(f"missing profile for seed modes {seed_modes}")


def test_base_and_single_edge_profiles_match_exact_unordered_edge_pair_rule() -> None:
    summary = build_l6_a2_mixed_seed_bridge_summary()
    assert summary["base_profile"]["response_rank"] == 9
    assert summary["base_profile"]["augmented_rank"] == 10
    assert summary["base_profile"]["active_a2_modes"] == []
    assert summary["activation_theorems"]["single_edge_seeds_activate_exact_unordered_edge_pair"] is True

    assert _profile_by_seed_modes(8)["active_a2_modes"] == [8, 247]
    assert _profile_by_seed_modes(9)["active_a2_modes"] == [9, 246]
    assert _profile_by_seed_modes(246)["active_a2_modes"] == [9, 246]
    assert _profile_by_seed_modes(247)["active_a2_modes"] == [8, 247]


def test_two_edge_fans_are_the_minimal_full_a2_activation_seeds() -> None:
    summary = build_l6_a2_mixed_seed_bridge_summary()
    theorem = summary["activation_theorems"]
    assert theorem["minimal_full_a2_activation_seed_size"] == 2
    assert sorted(theorem["minimal_full_a2_activation_seed_modes"]) == [[8, 9], [246, 247]]
    assert theorem["minimal_full_activation_profiles_are_exactly_fans"] is True

    assert _profile_by_seed_modes(8, 9)["shape"] == "fan"
    assert _profile_by_seed_modes(8, 9)["active_a2_modes"] == [8, 9, 127, 128, 246, 247]
    assert _profile_by_seed_modes(246, 247)["shape"] == "fan"
    assert _profile_by_seed_modes(246, 247)["active_a2_modes"] == [8, 9, 127, 128, 246, 247]


def test_minimal_rank_lift_appears_at_two_mode_paths_and_bidirected_edges() -> None:
    summary = build_l6_a2_mixed_seed_bridge_summary()
    theorem = summary["activation_theorems"]
    assert theorem["minimal_rank_lift_seed_size"] == 2
    assert sorted(theorem["minimal_rank_lift_seed_modes"]) == [
        [8, 246],
        [8, 247],
        [9, 246],
        [9, 247],
    ]
    assert theorem["minimal_rank_lift_profiles_are_paths_or_bidirected_edges"] is True
    assert theorem["max_response_rank_within_unit_a2_seed_family"] == 11
    assert theorem["max_augmented_rank_within_unit_a2_seed_family"] == 12

    assert _profile_by_seed_modes(8, 246)["shape"] == "directed_path"
    assert _profile_by_seed_modes(8, 246)["response_rank"] == 11
    assert _profile_by_seed_modes(8, 246)["augmented_rank"] == 12
    assert _profile_by_seed_modes(8, 247)["shape"] == "bidirected_edge"
    assert _profile_by_seed_modes(8, 247)["response_rank"] == 11
    assert _profile_by_seed_modes(8, 247)["augmented_rank"] == 12


def test_no_seed_in_the_unit_a2_family_closes_the_linearized_residual() -> None:
    summary = build_l6_a2_mixed_seed_bridge_summary()
    assert summary["activation_theorems"]["no_exact_closure_within_unit_a2_seed_family"] is True
    assert len(summary["activation_classes"]) == 8


def test_fan_closure_seeds_produce_full_block_support_and_isotropic_off_diagonal_shells() -> None:
    summary = build_l6_a2_mixed_seed_bridge_summary()
    theorem = summary["activation_theorems"]
    assert theorem["fan_closure_seeds_have_full_3x3_support"] is True
    assert theorem["fan_closure_seeds_have_slotwise_isotropic_off_diagonal_shell"] is True
    assert theorem["fan_closure_seeds_keep_all_six_a2_modes_active"] is True

    for closure in summary["closure_shell_profiles"]:
        assert closure["forward_fan_modes"] in ([8, 9], [246, 247])
        assert closure["reverse_fan_modes"] in ([246, 247], [8, 9])
        assert closure["response_rank"] == 9
        assert closure["augmented_rank"] == 10
        assert closure["active_a2_modes"] == [8, 9, 127, 128, 246, 247]
        for slot_profile in closure["slot_profiles"].values():
            assert slot_profile["closure_block_union"] == [
                [0, 0],
                [0, 1],
                [0, 2],
                [1, 0],
                [1, 1],
                [1, 2],
                [2, 0],
                [2, 1],
                [2, 2],
            ]
            assert slot_profile["all_off_diagonal_singular_spectra_match"] is True
            assert slot_profile["all_off_diagonal_ranks_match"] is True
            assert slot_profile["off_diagonal_ranks"] == [4, 4, 4, 4, 4, 4]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_a2_mixed_seed_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "circulant-style off-diagonal shell" in data["bridge_verdict"]
