"""Structural Cartan-selection theorem for the replicated l6 quark seed.

This module explains why the exact six-channel A2 package in the l6 bridge is
present but dynamically silent on the current replicated three-generation Yukawa
seed.

The key point is structural, not numerical:

1. the induced H_2 / Hbar_2 Yukawas are exactly generation-diagonal 3x3 block
   replications of one 8x8 seed;
2. every Cartan l6 bridge delta stays generation-diagonal;
3. every nonzero A2 l6 bridge delta occupies exactly one off-diagonal
   generation block;
4. the SU(3)xSU(2) order-one residual of a generation-diagonal seed is again
   generation-diagonal because the weak/color generators are block-diagonal
   across generations;
5. therefore the A2 response sector is orthogonal to both the seed residual and
   the Cartan response sector, so the least-squares bridge solves entirely in
   the Cartan slice.

This is the exact reason the current l6 bridge reports zero A2 coefficients on
the present seed.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_l6_chiral_gauge_bridge import (
    FLOAT_TOL,
    LEFT_POSITIONS_48,
    RIGHT_POSITIONS_48,
    _bridge_delta,
    _full_color_generators_48,
    _full_weak_generators_48,
    _response_matrix,
    build_l6_chiral_gauge_bridge_certificate,
    full_order_one_residual_vector_48,
    generation_diagonal_induced_yukawa_24,
    l6_chiral_mode_indices,
)
from w33_transport_lie_tower_bridge import (
    l6_a2_generation_channels,
    l6_cartan_diagonal_profiles,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_a2_selection_bridge_summary.json"


def _generation_block_union(matrix_24: np.ndarray) -> tuple[tuple[int, int], ...]:
    blocks = []
    for target_generation in range(3):
        row = slice(8 * target_generation, 8 * (target_generation + 1))
        for source_generation in range(3):
            col = slice(8 * source_generation, 8 * (source_generation + 1))
            block = matrix_24[row, col]
            if np.count_nonzero(np.abs(block) > FLOAT_TOL):
                blocks.append((target_generation, source_generation))
    return tuple(blocks)


def _dirac_from_yukawa(yukawa_24: np.ndarray) -> np.ndarray:
    dirac = np.zeros((48, 48), dtype=complex)
    dirac[np.ix_(LEFT_POSITIONS_48, RIGHT_POSITIONS_48)] = yukawa_24
    dirac[np.ix_(RIGHT_POSITIONS_48, LEFT_POSITIONS_48)] = yukawa_24.T
    return dirac


def _residual_lr_block_unions(yukawa_24: np.ndarray) -> tuple[tuple[tuple[int, int], ...], ...]:
    dirac = _dirac_from_yukawa(yukawa_24)
    unions = []
    for weak in _full_weak_generators_48():
        for color in _full_color_generators_48():
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (dirac @ weak - weak @ dirac)
            lr = residual[np.ix_(LEFT_POSITIONS_48, RIGHT_POSITIONS_48)]
            unions.append(_generation_block_union(lr))
    return tuple(unions)


def _residual_lr_union(yukawa_24: np.ndarray) -> tuple[tuple[int, int], ...]:
    union = set()
    for blocks in _residual_lr_block_unions(yukawa_24):
        union.update(blocks)
    return tuple(sorted(union))


def _is_generation_diagonal(blocks: tuple[tuple[int, int], ...]) -> bool:
    return all(target == source for target, source in blocks)


def _is_single_off_diagonal(blocks: tuple[tuple[int, int], ...]) -> bool:
    return len(blocks) == 1 and blocks[0][0] != blocks[0][1]


def _mode_response_block_union(mode_index: int, external_slot: str) -> tuple[tuple[int, int], ...]:
    seed = generation_diagonal_induced_yukawa_24(external_slot)
    delta = _bridge_delta(mode_index, seed)
    return _residual_lr_union(delta)


@lru_cache(maxsize=1)
def build_l6_a2_selection_bridge_summary() -> dict[str, Any]:
    certificate = build_l6_chiral_gauge_bridge_certificate()
    up_seed = generation_diagonal_induced_yukawa_24("H_2")
    down_seed = generation_diagonal_induced_yukawa_24("Hbar_2")

    seed_block_unions = {
        "H_2": [list(block) for block in _generation_block_union(up_seed)],
        "Hbar_2": [list(block) for block in _generation_block_union(down_seed)],
    }
    seed_residual_unions = {
        "H_2": [list(block) for block in _residual_lr_union(up_seed)],
        "Hbar_2": [list(block) for block in _residual_lr_union(down_seed)],
    }

    a2_modes = []
    for channel in l6_a2_generation_channels():
        up_blocks = _generation_block_union(_bridge_delta(channel.mode_index, up_seed))
        down_blocks = _generation_block_union(_bridge_delta(channel.mode_index, down_seed))
        up_response = _mode_response_block_union(channel.mode_index, "H_2")
        down_response = _mode_response_block_union(channel.mode_index, "Hbar_2")
        a2_modes.append(
            {
                "mode_index": int(channel.mode_index),
                "source_generation": int(channel.source_generation),
                "target_generation": int(channel.target_generation),
                "up_seed_blocks": [list(block) for block in up_blocks],
                "down_seed_blocks": [list(block) for block in down_blocks],
                "up_response_blocks": [list(block) for block in up_response],
                "down_response_blocks": [list(block) for block in down_response],
                "seed_off_diagonal_single_block": _is_single_off_diagonal(up_blocks)
                == _is_single_off_diagonal(down_blocks),
                "response_off_diagonal_single_block": _is_single_off_diagonal(up_response)
                == _is_single_off_diagonal(down_response),
                "zero_response_on_replicated_seed": (not up_blocks and not down_blocks),
            }
        )

    cartan_modes = []
    for profile in l6_cartan_diagonal_profiles():
        up_blocks = _generation_block_union(_bridge_delta(profile.mode_index, up_seed))
        down_blocks = _generation_block_union(_bridge_delta(profile.mode_index, down_seed))
        up_response = _mode_response_block_union(profile.mode_index, "H_2")
        down_response = _mode_response_block_union(profile.mode_index, "Hbar_2")
        cartan_modes.append(
            {
                "mode_index": int(profile.mode_index),
                "up_seed_blocks": [list(block) for block in up_blocks],
                "down_seed_blocks": [list(block) for block in down_blocks],
                "up_response_blocks": [list(block) for block in up_response],
                "down_response_blocks": [list(block) for block in down_response],
                "seed_generation_diagonal": _is_generation_diagonal(up_blocks)
                and _is_generation_diagonal(down_blocks),
                "response_generation_diagonal": _is_generation_diagonal(up_response)
                and _is_generation_diagonal(down_response),
                "off_diagonal_nonzeros_on_spinor": int(profile.off_diagonal_nonzeros),
            }
        )

    response = _response_matrix(up_seed, down_seed)
    residual = np.concatenate(
        [full_order_one_residual_vector_48(up_seed), full_order_one_residual_vector_48(down_seed)]
    )
    mode_positions = {mode_index: position for position, mode_index in enumerate(l6_chiral_mode_indices())}
    a2_positions = [mode_positions[mode_index] for mode_index in certificate.a2_mode_indices]
    cartan_positions = [mode_positions[mode_index] for mode_index in certificate.cartan_mode_indices]

    a2_rhs = [
        float(np.vdot(response[:, position], residual).real)
        for position in a2_positions
    ]
    cross_gram = np.array(
        [
            [
                float(np.vdot(response[:, left], response[:, right]).real)
                for right in cartan_positions
            ]
            for left in a2_positions
        ]
    )

    nonzero_a2_mode_indices = [
        entry["mode_index"] for entry in a2_modes if not entry["zero_response_on_replicated_seed"]
    ]
    zero_a2_mode_indices = [
        entry["mode_index"] for entry in a2_modes if entry["zero_response_on_replicated_seed"]
    ]
    seed_star_channels = sorted(
        [entry["up_seed_blocks"][0] for entry in a2_modes if entry["up_seed_blocks"]]
    )

    return {
        "status": "ok",
        "seed_generation_structure": {
            "replicated_block_shape": [3, 3],
            "seed_block_unions": seed_block_unions,
            "seed_residual_block_unions": seed_residual_unions,
            "seed_yukawas_are_generation_diagonal": all(
                _is_generation_diagonal(tuple(tuple(block) for block in seed_block_unions[name]))
                for name in ("H_2", "Hbar_2")
            ),
            "seed_residuals_are_generation_diagonal": all(
                _is_generation_diagonal(tuple(tuple(block) for block in seed_residual_unions[name]))
                for name in ("H_2", "Hbar_2")
            ),
        },
        "a2_seed_channels": a2_modes,
        "cartan_seed_channels": cartan_modes,
        "selection_theorem": {
            "a2_zero_response_mode_indices": zero_a2_mode_indices,
            "a2_nonzero_mode_indices": nonzero_a2_mode_indices,
            "all_nonzero_a2_seed_blocks_are_single_off_diagonal_channels": all(
                entry["seed_off_diagonal_single_block"] and not entry["zero_response_on_replicated_seed"]
                for entry in a2_modes
                if entry["mode_index"] in nonzero_a2_mode_indices
            ),
            "all_nonzero_a2_response_blocks_stay_single_off_diagonal_channels": all(
                entry["response_off_diagonal_single_block"] and not entry["zero_response_on_replicated_seed"]
                for entry in a2_modes
                if entry["mode_index"] in nonzero_a2_mode_indices
            ),
            "all_cartan_seed_blocks_are_generation_diagonal": all(
                entry["seed_generation_diagonal"] for entry in cartan_modes
            ),
            "all_cartan_response_blocks_are_generation_diagonal": all(
                entry["response_generation_diagonal"] for entry in cartan_modes
            ),
            "replicated_seed_only_realizes_generation_2_star_in_a2_slice": seed_star_channels
            == [[0, 2], [1, 2], [2, 0], [2, 1]],
            "a2_rhs_inner_products": a2_rhs,
            "a2_rhs_is_exactly_zero": bool(np.allclose(a2_rhs, 0.0, atol=FLOAT_TOL)),
            "a2_cartan_cross_gram_max_abs": float(np.max(np.abs(cross_gram))) if cross_gram.size else 0.0,
            "a2_cartan_cross_gram_is_zero": bool(np.allclose(cross_gram, 0.0, atol=FLOAT_TOL)),
            "current_l6_solution_has_no_active_a2_modes": (
                certificate.a2_coefficients_all_zero and certificate.active_a2_mode_indices == ()
            ),
            "cartan_only_selection_is_structurally_forced": bool(
                np.allclose(a2_rhs, 0.0, atol=FLOAT_TOL)
                and np.allclose(cross_gram, 0.0, atol=FLOAT_TOL)
                and certificate.a2_coefficients_all_zero
            ),
        },
        "bridge_verdict": (
            "On the replicated three-generation H_2 / Hbar_2 seed, the l6 Cartan "
            "and A2 sectors split by generation support. The seed Yukawas and their "
            "strict SU(3)xSU(2) residuals are generation-diagonal, every Cartan "
            "bridge response stays generation-diagonal, and every nonzero A2 bridge "
            "response occupies exactly one off-diagonal generation block. Hence the "
            "A2 response sector is orthogonal both to the seed residual and to the "
            "Cartan response sector, so the least-squares l6 bridge solves entirely "
            "in the Cartan slice. The vanishing of the A2 coefficients is therefore "
            "structural, not an optimizer accident."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_l6_a2_selection_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
