"""Exact A2 activation map for minimally mixed three-generation l6 seeds.

The replicated three-generation H_2/Hbar_2 seed explains why the present l6
bridge is Cartan-only, but it does not tell us how the dormant A2 package turns
on once the seed stops being generation-diagonal.

This module studies the smallest exact mixed seeds already native to the repo:
start from the replicated seed and add unit copies of the four nonzero A2
bridge deltas

    8, 9, 246, 247.

These are the four A2 channels that actually act on the replicated seed. The
other two A2 modes, 127 and 128, vanish there exactly.

What is established:
  - a single directed-edge seed activates exactly its unordered A2 edge pair;
  - the two fan seeds (8,9) and (246,247) are the minimal exact seeds that
    activate the full six-mode A2 package, including the formerly dormant
    0<->1 pair (127,128);
  - the two directed-path seeds (8,246) and (9,247), together with the two
    bidirected-edge seeds (8,247) and (9,246), are the minimal exact seeds that
    raise the linear response rank from 9 to 11 and the augmented rank from
    10 to 12;
  - one exact nonlinear closure step turns each minimal fan into a full
    3x3-support mixed seed whose six off-diagonal 8x8 blocks have identical
    singular spectra within each external slot, i.e. a circulant-style
    off-diagonal shell;
  - no seed in this exact unit A2 family closes the l6 linearized residual.

This does not yet build the final physical mixed three-generation seed. It does
show exactly how A2 activation starts once the replicated Cartan lock is broken.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
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
    _bridge_delta,
    _response_matrix,
    build_l6_chiral_gauge_bridge_certificate,
    full_order_one_residual_vector_48,
    generation_diagonal_induced_yukawa_24,
    l6_chiral_mode_indices,
)
from w33_transport_lie_tower_bridge import l6_a2_generation_channels


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_a2_mixed_seed_bridge_summary.json"
NONZERO_A2_SEED_MODES = (8, 9, 246, 247)


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


@lru_cache(maxsize=1)
def _a2_channel_map() -> dict[int, tuple[int, int]]:
    return {
        channel.mode_index: (channel.source_generation, channel.target_generation)
        for channel in l6_a2_generation_channels()
    }


@lru_cache(maxsize=1)
def _reverse_a2_mode_map() -> dict[int, int]:
    channel_map = _a2_channel_map()
    reverse = {}
    for mode_index, (source_generation, target_generation) in channel_map.items():
        for other_mode, other_pair in channel_map.items():
            if other_pair == (target_generation, source_generation):
                reverse[mode_index] = other_mode
                break
        else:
            raise AssertionError("missing reverse A2 channel")
    return reverse


def _shape_label(seed_modes: tuple[int, ...]) -> str:
    if not seed_modes:
        return "replicated"
    if len(seed_modes) == 1:
        return "single_edge"

    edges = [_a2_channel_map()[mode_index] for mode_index in seed_modes]
    if len(seed_modes) == 2:
        left, right = edges
        if frozenset(left) == frozenset(right):
            return "bidirected_edge"
        if len({source for source, _ in edges}) == 1 or len(
            {target for _, target in edges}
        ) == 1:
            return "fan"
        return "directed_path"
    return "multi_edge"


def _unit_mixed_seed(external_slot: str, seed_modes: tuple[int, ...]) -> np.ndarray:
    seed = generation_diagonal_induced_yukawa_24(external_slot)
    for mode_index in seed_modes:
        seed = seed + _bridge_delta(mode_index, generation_diagonal_induced_yukawa_24(external_slot))
    return seed


def _apply_modes_to_seed(seed: np.ndarray, seed_modes: tuple[int, ...]) -> np.ndarray:
    updated = seed.copy()
    for mode_index in seed_modes:
        updated = updated + _bridge_delta(mode_index, seed)
    return updated


def _profile(seed_modes: tuple[int, ...]) -> dict[str, Any]:
    certificate = build_l6_chiral_gauge_bridge_certificate()
    up_seed = _unit_mixed_seed("H_2", seed_modes)
    down_seed = _unit_mixed_seed("Hbar_2", seed_modes)
    response = _response_matrix(up_seed, down_seed)
    residual = np.concatenate(
        [full_order_one_residual_vector_48(up_seed), full_order_one_residual_vector_48(down_seed)]
    )
    response_real = np.vstack([response.real, response.imag])
    target_real = np.concatenate([-residual.real, -residual.imag])
    coefficients, *_ = np.linalg.lstsq(response_real, target_real, rcond=None)

    active_modes = tuple(
        mode_index
        for mode_index, coefficient in zip(l6_chiral_mode_indices(), coefficients)
        if abs(float(coefficient)) > FLOAT_TOL
    )
    active_a2_modes = tuple(
        mode_index for mode_index in active_modes if mode_index in certificate.a2_mode_indices
    )
    active_cartan_modes = tuple(
        mode_index for mode_index in active_modes if mode_index in certificate.cartan_mode_indices
    )
    fit_residual = response_real @ coefficients - target_real

    return {
        "seed_modes": list(seed_modes),
        "seed_size": len(seed_modes),
        "shape": _shape_label(seed_modes),
        "seed_generation_edges": [list(_a2_channel_map()[mode_index]) for mode_index in seed_modes],
        "seed_reverse_modes": [_reverse_a2_mode_map()[mode_index] for mode_index in seed_modes],
        "up_seed_block_union": [list(block) for block in _generation_block_union(up_seed)],
        "down_seed_block_union": [list(block) for block in _generation_block_union(down_seed)],
        "response_rank": int(np.linalg.matrix_rank(response_real)),
        "augmented_rank": int(np.linalg.matrix_rank(np.column_stack([response_real, target_real]))),
        "seed_total_residual_norm": float(np.linalg.norm(residual)),
        "best_fit_residual_norm": float(np.linalg.norm(fit_residual)),
        "active_a2_modes": list(active_a2_modes),
        "active_cartan_modes": list(active_cartan_modes),
        "zero_a2_modes_activated": [
            mode_index for mode_index in active_a2_modes if mode_index in (127, 128)
        ],
        "all_six_a2_modes_activated": active_a2_modes == certificate.a2_mode_indices,
    }


def _closure_shell_profile(forward_fan_modes: tuple[int, int]) -> dict[str, Any]:
    if forward_fan_modes not in {(8, 9), (246, 247)}:
        raise ValueError("closure shell is defined only for the two minimal fan seeds")

    reverse_fan_modes = tuple(sorted(_reverse_a2_mode_map()[mode_index] for mode_index in forward_fan_modes))
    certificate = build_l6_chiral_gauge_bridge_certificate()

    profiles = {}
    for external_slot in ("H_2", "Hbar_2"):
        base = generation_diagonal_induced_yukawa_24(external_slot)
        fan_seed = _apply_modes_to_seed(base, forward_fan_modes)
        closure_seed = _apply_modes_to_seed(fan_seed, reverse_fan_modes)
        off_diagonal_singular_spectra = []
        off_diagonal_ranks = []
        for target_generation in range(3):
            row = slice(8 * target_generation, 8 * (target_generation + 1))
            for source_generation in range(3):
                if target_generation == source_generation:
                    continue
                col = slice(8 * source_generation, 8 * (source_generation + 1))
                block = closure_seed[row, col]
                singular_values = tuple(
                    round(float(value), 12)
                    for value in np.linalg.svd(block, compute_uv=False)
                )
                off_diagonal_singular_spectra.append(singular_values)
                off_diagonal_ranks.append(int(np.linalg.matrix_rank(block)))
        profiles[external_slot] = {
            "fan_block_union": [list(block) for block in _generation_block_union(fan_seed)],
            "closure_block_union": [list(block) for block in _generation_block_union(closure_seed)],
            "off_diagonal_singular_spectra": [list(values) for values in off_diagonal_singular_spectra],
            "off_diagonal_ranks": off_diagonal_ranks,
            "all_off_diagonal_singular_spectra_match": len(set(off_diagonal_singular_spectra)) == 1,
            "all_off_diagonal_ranks_match": len(set(off_diagonal_ranks)) == 1,
        }

    up_seed = _apply_modes_to_seed(
        _apply_modes_to_seed(generation_diagonal_induced_yukawa_24("H_2"), forward_fan_modes),
        reverse_fan_modes,
    )
    down_seed = _apply_modes_to_seed(
        _apply_modes_to_seed(generation_diagonal_induced_yukawa_24("Hbar_2"), forward_fan_modes),
        reverse_fan_modes,
    )
    response = _response_matrix(up_seed, down_seed)
    residual = np.concatenate(
        [full_order_one_residual_vector_48(up_seed), full_order_one_residual_vector_48(down_seed)]
    )
    response_real = np.vstack([response.real, response.imag])
    target_real = np.concatenate([-residual.real, -residual.imag])
    coefficients, *_ = np.linalg.lstsq(response_real, target_real, rcond=None)
    active_a2_modes = tuple(
        mode_index
        for mode_index, coefficient in zip(l6_chiral_mode_indices(), coefficients)
        if abs(float(coefficient)) > FLOAT_TOL and mode_index in certificate.a2_mode_indices
    )

    return {
        "forward_fan_modes": list(forward_fan_modes),
        "reverse_fan_modes": list(reverse_fan_modes),
        "slot_profiles": profiles,
        "response_rank": int(np.linalg.matrix_rank(response_real)),
        "augmented_rank": int(np.linalg.matrix_rank(np.column_stack([response_real, target_real]))),
        "active_a2_modes": list(active_a2_modes),
        "all_six_a2_modes_activated": active_a2_modes == certificate.a2_mode_indices,
        "best_fit_residual_norm": float(np.linalg.norm(response_real @ coefficients - target_real)),
    }


@lru_cache(maxsize=1)
def build_l6_a2_mixed_seed_bridge_summary() -> dict[str, Any]:
    base_certificate = build_l6_chiral_gauge_bridge_certificate()
    profiles = []
    for size in range(len(NONZERO_A2_SEED_MODES) + 1):
        for seed_modes in combinations(NONZERO_A2_SEED_MODES, size):
            profiles.append(_profile(seed_modes))

    activation_classes: dict[tuple[Any, ...], list[tuple[int, ...]]] = {}
    for profile in profiles:
        key = (
            tuple(profile["active_a2_modes"]),
            profile["response_rank"],
            profile["augmented_rank"],
        )
        activation_classes.setdefault(key, []).append(tuple(profile["seed_modes"]))

    class_rows = [
        {
            "active_a2_modes": list(active_modes),
            "response_rank": response_rank,
            "augmented_rank": augmented_rank,
            "seed_mode_subsets": [list(seed_modes) for seed_modes in seed_mode_subsets],
            "minimal_seed_size": min(len(seed_modes) for seed_modes in seed_mode_subsets),
        }
        for (active_modes, response_rank, augmented_rank), seed_mode_subsets in sorted(
            activation_classes.items(),
            key=lambda item: (item[0][1], item[0][2], len(item[0][0]), item[0][0]),
        )
    ]

    full_activation_profiles = [
        profile for profile in profiles if profile["all_six_a2_modes_activated"]
    ]
    rank_lift_profiles = [
        profile for profile in profiles if profile["response_rank"] > base_certificate.response_rank
    ]
    minimal_full_activation_size = min(profile["seed_size"] for profile in full_activation_profiles)
    minimal_rank_lift_size = min(profile["seed_size"] for profile in rank_lift_profiles)

    minimal_full_activation_profiles = [
        profile for profile in full_activation_profiles if profile["seed_size"] == minimal_full_activation_size
    ]
    minimal_rank_lift_profiles = [
        profile for profile in rank_lift_profiles if profile["seed_size"] == minimal_rank_lift_size
    ]
    single_edge_profiles = [profile for profile in profiles if profile["shape"] == "single_edge"]
    closure_shells = [
        _closure_shell_profile((8, 9)),
        _closure_shell_profile((246, 247)),
    ]

    return {
        "status": "ok",
        "base_profile": {
            "response_rank": base_certificate.response_rank,
            "augmented_rank": base_certificate.augmented_rank,
            "active_a2_modes": list(base_certificate.active_a2_mode_indices),
            "total_residual_norm": base_certificate.original_total_residual_norm,
            "best_fit_residual_norm": base_certificate.bridged_total_residual_norm,
        },
        "nonzero_a2_seed_modes": list(NONZERO_A2_SEED_MODES),
        "seed_mode_dictionary": [
            {
                "mode_index": mode_index,
                "source_generation": source_generation,
                "target_generation": target_generation,
                "reverse_mode_index": _reverse_a2_mode_map()[mode_index],
            }
            for mode_index, (source_generation, target_generation) in sorted(_a2_channel_map().items())
        ],
        "profiles": profiles,
        "closure_shell_profiles": closure_shells,
        "activation_classes": class_rows,
        "activation_theorems": {
            "single_edge_seeds_activate_exact_unordered_edge_pair": all(
                sorted(profile["active_a2_modes"])
                == sorted(
                    [profile["seed_modes"][0], _reverse_a2_mode_map()[profile["seed_modes"][0]]]
                )
                for profile in single_edge_profiles
            ),
            "minimal_full_a2_activation_seed_size": minimal_full_activation_size,
            "minimal_full_a2_activation_seed_modes": [
                profile["seed_modes"] for profile in minimal_full_activation_profiles
            ],
            "minimal_full_activation_profiles_are_exactly_fans": all(
                profile["shape"] == "fan" for profile in minimal_full_activation_profiles
            ),
            "minimal_rank_lift_seed_size": minimal_rank_lift_size,
            "minimal_rank_lift_seed_modes": [
                profile["seed_modes"] for profile in minimal_rank_lift_profiles
            ],
            "minimal_rank_lift_profiles_are_paths_or_bidirected_edges": all(
                profile["shape"] in {"directed_path", "bidirected_edge"}
                for profile in minimal_rank_lift_profiles
            ),
            "max_response_rank_within_unit_a2_seed_family": max(
                profile["response_rank"] for profile in profiles
            ),
            "max_augmented_rank_within_unit_a2_seed_family": max(
                profile["augmented_rank"] for profile in profiles
            ),
            "fan_closure_seeds_have_full_3x3_support": all(
                slot_profile["closure_block_union"]
                == [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
                for closure in closure_shells
                for slot_profile in closure["slot_profiles"].values()
            ),
            "fan_closure_seeds_have_slotwise_isotropic_off_diagonal_shell": all(
                slot_profile["all_off_diagonal_singular_spectra_match"]
                and slot_profile["all_off_diagonal_ranks_match"]
                for closure in closure_shells
                for slot_profile in closure["slot_profiles"].values()
            ),
            "fan_closure_seeds_keep_all_six_a2_modes_active": all(
                closure["all_six_a2_modes_activated"] for closure in closure_shells
            ),
            "no_exact_closure_within_unit_a2_seed_family": all(
                profile["augmented_rank"] > profile["response_rank"] for profile in profiles
            ),
        },
        "bridge_verdict": (
            "The replicated Cartan lock can now be broken exactly inside the repo's "
            "native A2 seed family. A single directed A2 seed turns on exactly its "
            "unordered edge pair. A two-edge fan through generation 2 is the minimal "
            "exact seed that activates the full six-mode A2 package, including the "
            "previously dormant 0<->1 pair. A two-edge directed path or bidirected "
            "edge is the minimal exact seed that raises the l6 linear response rank "
            "from 9 to 11 and the augmented rank from 10 to 12. One exact nonlinear "
            "closure step then turns each minimal fan into a full 3x3-support mixed "
            "seed whose six off-diagonal 8x8 blocks have identical singular spectra "
            "within each external slot, i.e. a circulant-style off-diagonal shell. "
            "But no seed in this unit A2 family closes the linearized residual "
            "exactly, so exact A2 activation has been mapped without yet producing "
            "the final quark seed."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_l6_a2_mixed_seed_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
