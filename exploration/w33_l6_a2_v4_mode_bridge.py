"""Exact V4 character refinement of the six l6 A2 modes on the canonical fan seed.

The canonical nonlinear closure seed exhibits an exact matrix-level V4 flavour
torsor. This module pushes that structure one step deeper into the Lie layer by
analyzing the six exact l6 A2 modes on the canonical forward fan seed (8, 9).

What is established:

  - every nonzero A2 block on the canonical fan seed is a pure right-character
    twist of the canonical closure reference block, with trivial row-sign part;
  - the four single-block A2 modes are pure V4-character channels:
      * 8 and 128 are pure A;
      * 9 and 127 are pure B;
  - the two reverse-fan modes 246 and 247 are the first mixed character modes,
    and their blockwise character content is exactly {I, A, AB};
  - across the six exact A2 modes on the fan seed, all four V4 characters
    I, A, B, AB are already realized before the final nonlinear closure.

So the matrix-level V4 flavour texture is not merely a byproduct of the final
closure seed. It is already present as an exact refinement of the six A2 Lie
channels themselves.
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

from w33_l6_a2_mixed_seed_bridge import _apply_modes_to_seed
from w33_l6_chiral_gauge_bridge import _bridge_delta, generation_diagonal_induced_yukawa_24
from w33_l6_delta27_texture_bridge import _canonical_closure_seed
from w33_l6_delta27_v4_bridge import _solve_row_column_signs, _slot_profile
from w33_transport_lie_tower_bridge import l6_a2_generation_channels


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_a2_v4_mode_bridge_summary.json"
CANONICAL_FAN = (8, 9)


def _identity_sign_vector() -> tuple[int, ...]:
    return tuple(1 for _ in range(8))


def _character_label_map(external_slot: str) -> dict[tuple[int, ...], str]:
    profile = _slot_profile(external_slot)
    return {
        _identity_sign_vector(): "I",
        tuple(profile["generator_a"]): "A",
        tuple(profile["generator_b"]): "B",
        tuple(profile["generator_ab"]): "AB",
    }


def _reference_block(external_slot: str) -> np.ndarray:
    canonical = _canonical_closure_seed(external_slot)
    return canonical[0:8, 8:16]


def _mode_character_profile(external_slot: str, mode_index: int) -> dict[str, Any]:
    seed = _apply_modes_to_seed(generation_diagonal_induced_yukawa_24(external_slot), CANONICAL_FAN)
    delta = _bridge_delta(mode_index, seed)
    reference = _reference_block(external_slot)
    character_map = _character_label_map(external_slot)

    blocks = []
    row_signs_all_trivial = True
    for target_generation in range(3):
        for source_generation in range(3):
            block = delta[
                8 * target_generation : 8 * (target_generation + 1),
                8 * source_generation : 8 * (source_generation + 1),
            ]
            if not np.count_nonzero(np.abs(block) > 1e-10):
                continue
            row_signs, col_signs = _solve_row_column_signs(reference, block)
            row_signs_all_trivial = row_signs_all_trivial and row_signs == _identity_sign_vector()
            blocks.append(
                {
                    "pair": [target_generation, source_generation],
                    "character_label": character_map[tuple(col_signs)],
                }
            )

    character_labels = [block["character_label"] for block in blocks]
    return {
        "mode_index": mode_index,
        "generation_channel": next(
            [channel.source_generation, channel.target_generation]
            for channel in l6_a2_generation_channels()
            if channel.mode_index == mode_index
        ),
        "block_count": len(blocks),
        "blocks": blocks,
        "character_labels": character_labels,
        "distinct_character_labels": sorted(set(character_labels)),
        "pure_single_character_mode": len(set(character_labels)) == 1,
        "row_signs_all_trivial": row_signs_all_trivial,
    }


@lru_cache(maxsize=1)
def build_l6_a2_v4_mode_bridge_summary() -> dict[str, Any]:
    slot_profiles = {}
    for external_slot in ("H_2", "Hbar_2"):
        mode_profiles = [
            _mode_character_profile(external_slot, channel.mode_index)
            for channel in l6_a2_generation_channels()
        ]
        by_mode = {profile["mode_index"]: profile for profile in mode_profiles}
        slot_profiles[external_slot] = {
            "mode_profiles": mode_profiles,
            "pure_a_modes": [
                profile["mode_index"]
                for profile in mode_profiles
                if profile["distinct_character_labels"] == ["A"]
            ],
            "pure_b_modes": [
                profile["mode_index"]
                for profile in mode_profiles
                if profile["distinct_character_labels"] == ["B"]
            ],
            "mixed_i_a_ab_modes": [
                profile["mode_index"]
                for profile in mode_profiles
                if profile["distinct_character_labels"] == ["A", "AB", "I"]
            ],
            "all_realized_characters": sorted(
                {
                    label
                    for profile in mode_profiles
                    for label in profile["distinct_character_labels"]
                }
            ),
            "dormant_modes_awaken_as_single_block_channels": {
                str(mode_index): by_mode[mode_index]["block_count"] == 1
                for mode_index in (127, 128)
            },
        }

    return {
        "status": "ok",
        "canonical_fan_modes": list(CANONICAL_FAN),
        "slot_profiles": slot_profiles,
        "a2_v4_mode_theorem": {
            "all_mode_blocks_are_pure_right_character_twists": all(
                all(profile["row_signs_all_trivial"] for profile in slot_profile["mode_profiles"])
                for slot_profile in slot_profiles.values()
            ),
            "pure_a_modes_are_exactly_8_and_128": all(
                slot_profile["pure_a_modes"] == [8, 128]
                for slot_profile in slot_profiles.values()
            ),
            "pure_b_modes_are_exactly_9_and_127": all(
                slot_profile["pure_b_modes"] == [9, 127]
                for slot_profile in slot_profiles.values()
            ),
            "mixed_i_a_ab_modes_are_exactly_246_and_247": all(
                slot_profile["mixed_i_a_ab_modes"] == [246, 247]
                for slot_profile in slot_profiles.values()
            ),
            "all_four_v4_characters_already_realized_on_fan_seed": all(
                slot_profile["all_realized_characters"] == ["A", "AB", "B", "I"]
                for slot_profile in slot_profiles.values()
            ),
            "dormant_modes_127_128_awaken_as_single_block_channels": all(
                all(slot_profile["dormant_modes_awaken_as_single_block_channels"].values())
                for slot_profile in slot_profiles.values()
            ),
        },
        "bridge_verdict": (
            "On the canonical fan seed, the six exact l6 A2 modes already refine "
            "into V4 flavour characters. Modes 8 and 128 are pure A channels, "
            "modes 9 and 127 are pure B channels, and the reverse-fan modes 246 "
            "and 247 are the first mixed character modes with exact blockwise "
            "content {I, A, AB}. So the full V4 flavour torsor is present before "
            "the final nonlinear closure and is carried directly by the exact A2 "
            "Lie channels."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_l6_a2_v4_mode_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
