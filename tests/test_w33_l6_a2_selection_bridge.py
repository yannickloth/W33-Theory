from __future__ import annotations

import json
from pathlib import Path

from w33_l6_a2_selection_bridge import (
    build_l6_a2_selection_bridge_summary,
    write_summary,
)


def test_replicated_seed_and_residual_stay_generation_diagonal() -> None:
    summary = build_l6_a2_selection_bridge_summary()
    seed = summary["seed_generation_structure"]
    assert seed["seed_block_unions"]["H_2"] == [[0, 0], [1, 1], [2, 2]]
    assert seed["seed_block_unions"]["Hbar_2"] == [[0, 0], [1, 1], [2, 2]]
    assert seed["seed_residual_block_unions"]["H_2"] == [[0, 0], [1, 1], [2, 2]]
    assert seed["seed_residual_block_unions"]["Hbar_2"] == [[0, 0], [1, 1], [2, 2]]
    assert seed["seed_yukawas_are_generation_diagonal"] is True
    assert seed["seed_residuals_are_generation_diagonal"] is True


def test_a2_modes_split_into_four_off_diagonal_channels_plus_two_zero_modes() -> None:
    summary = build_l6_a2_selection_bridge_summary()
    theorem = summary["selection_theorem"]
    assert theorem["a2_zero_response_mode_indices"] == [127, 128]
    assert theorem["a2_nonzero_mode_indices"] == [8, 9, 246, 247]
    assert theorem["all_nonzero_a2_seed_blocks_are_single_off_diagonal_channels"] is True
    assert theorem["all_nonzero_a2_response_blocks_stay_single_off_diagonal_channels"] is True
    assert theorem["replicated_seed_only_realizes_generation_2_star_in_a2_slice"] is True


def test_cartan_modes_remain_generation_diagonal() -> None:
    summary = build_l6_a2_selection_bridge_summary()
    theorem = summary["selection_theorem"]
    assert theorem["all_cartan_seed_blocks_are_generation_diagonal"] is True
    assert theorem["all_cartan_response_blocks_are_generation_diagonal"] is True


def test_a2_sector_decouples_from_rhs_and_cartan_sector() -> None:
    summary = build_l6_a2_selection_bridge_summary()
    theorem = summary["selection_theorem"]
    assert theorem["a2_rhs_inner_products"] == [0.0] * 6
    assert theorem["a2_rhs_is_exactly_zero"] is True
    assert theorem["a2_cartan_cross_gram_max_abs"] == 0.0
    assert theorem["a2_cartan_cross_gram_is_zero"] is True
    assert theorem["current_l6_solution_has_no_active_a2_modes"] is True
    assert theorem["cartan_only_selection_is_structurally_forced"] is True


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_l6_a2_selection_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "structural, not an optimizer accident" in data["bridge_verdict"]
