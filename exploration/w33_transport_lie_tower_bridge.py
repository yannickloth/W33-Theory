"""Exact bridge from the transport A2 local system into the l6 Lie tower.

This module ties together two exact structures that were previously living in
separate layers of the repo:

1. the native transport A2 local system over the 45-point quotient transport
   graph, where every edge carries a Weyl(A2) matrix;
2. the corrected l6 gauge-return slice, where the Lie tower splits as
   72 E6 roots + 6 A2 roots + 8 Cartan directions.

The new exact bridge is operator-level:

- on the transport side, all six Weyl(A2) elements are realized on edges, with
  exact conjugacy-class counts on the 720-edge quotient graph;
- on the l6 side, the six A2 modes are exactly the six ordered generation
  transfers on the 48-spinor space;
- each A2 transfer is a single 16x16 signed permutation block of full rank 16;
- the eight Cartan modes are strictly generation-diagonal;
- the current linearized l6 bridge activates only Cartan directions, so the A2
  generation-mixing channels are exact but not yet dynamically selected on the
  present Yukawa seed.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
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

from w33_center_quad_transport_a2_bridge import a2_weyl_matrix
from w33_center_quad_transport_bridge import reconstructed_quotient_graph
from w33_center_quad_transport_holonomy_bridge import edge_line_matching
from w33_l6_chiral_gauge_bridge import (
    build_l6_chiral_gauge_bridge_certificate,
    l6_spinor_operator_48,
)
from w33_l6_exceptional_gauge_return import build_l6_exceptional_gauge_return_certificate


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_lie_tower_bridge_summary.json"
FLOAT_TOL = 1e-10


@dataclass(frozen=True)
class TransportWeylClassProfile:
    trace: int
    determinant: int
    order: int
    edge_count: int
    class_name: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class L6A2GenerationChannel:
    mode_index: int
    source_generation: int
    target_generation: int
    block_rank: int
    nonzero_entries: int
    signed_permutation: bool
    orthogonal_block: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CartanDiagonalProfile:
    mode_index: int
    diagonal_nonzeros: int
    off_diagonal_nonzeros: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _weyl_matrix_order(matrix: np.ndarray) -> int:
    identity = np.eye(matrix.shape[0], dtype=int)
    power = np.eye(matrix.shape[0], dtype=int)
    for order in range(1, 7):
        power = power @ matrix
        if np.array_equal(power, identity):
            return order
    raise AssertionError("unexpected Weyl(A2) element order")


def _weyl_class_name(trace: int, determinant: int, order: int) -> str:
    if order == 1:
        return "identity"
    if order == 2 and determinant == -1:
        return "reflection"
    if order == 3 and determinant == 1:
        return "three_cycle"
    raise AssertionError("unexpected Weyl(A2) conjugacy class")


@lru_cache(maxsize=1)
def transport_weyl_class_profiles() -> tuple[TransportWeylClassProfile, ...]:
    graph, _ = reconstructed_quotient_graph()
    class_counts: Counter[tuple[int, int, int]] = Counter()
    for left, right in sorted(graph.edges()):
        matrix = a2_weyl_matrix(edge_line_matching(left, right))
        trace = int(round(float(np.trace(matrix))))
        determinant = int(round(float(np.linalg.det(matrix))))
        order = _weyl_matrix_order(matrix)
        class_counts[(trace, determinant, order)] += 1

    profiles = []
    for (trace, determinant, order), count in sorted(class_counts.items()):
        profiles.append(
            TransportWeylClassProfile(
                trace=trace,
                determinant=determinant,
                order=order,
                edge_count=int(count),
                class_name=_weyl_class_name(trace, determinant, order),
            )
        )
    return tuple(profiles)


def _generation_block(operator: np.ndarray, target_generation: int, source_generation: int) -> np.ndarray:
    return operator[
        16 * target_generation : 16 * (target_generation + 1),
        16 * source_generation : 16 * (source_generation + 1),
    ]


def _is_signed_permutation(block: np.ndarray) -> bool:
    nonzero_mask = np.abs(block) > FLOAT_TOL
    return bool(
        np.all(np.sum(nonzero_mask, axis=0) == 1)
        and np.all(np.sum(nonzero_mask, axis=1) == 1)
        and set(np.unique(block[nonzero_mask]).tolist()).issubset({-1.0, 1.0})
    )


@lru_cache(maxsize=1)
def l6_a2_generation_channels() -> tuple[L6A2GenerationChannel, ...]:
    certificate = build_l6_chiral_gauge_bridge_certificate()
    channels = []
    for mode_index in certificate.a2_mode_indices:
        operator = l6_spinor_operator_48(mode_index)
        found = []
        for target_generation in range(3):
            for source_generation in range(3):
                block = _generation_block(operator, target_generation, source_generation)
                if np.count_nonzero(np.abs(block) > FLOAT_TOL):
                    found.append((target_generation, source_generation, block))
        if len(found) != 1:
            raise AssertionError("expected exactly one nonzero generation block per A2 mode")
        target_generation, source_generation, block = found[0]
        channels.append(
            L6A2GenerationChannel(
                mode_index=mode_index,
                source_generation=source_generation,
                target_generation=target_generation,
                block_rank=int(np.linalg.matrix_rank(block)),
                nonzero_entries=int(np.count_nonzero(np.abs(block) > FLOAT_TOL)),
                signed_permutation=_is_signed_permutation(block),
                orthogonal_block=bool(
                    np.array_equal(block.T @ block, np.eye(16))
                    and np.array_equal(block @ block.T, np.eye(16))
                ),
            )
        )
    return tuple(channels)


@lru_cache(maxsize=1)
def l6_cartan_diagonal_profiles() -> tuple[CartanDiagonalProfile, ...]:
    certificate = build_l6_chiral_gauge_bridge_certificate()
    profiles = []
    for mode_index in certificate.cartan_mode_indices:
        operator = l6_spinor_operator_48(mode_index)
        diagonal_nonzeros = 0
        off_diagonal_nonzeros = 0
        for target_generation in range(3):
            for source_generation in range(3):
                block = _generation_block(operator, target_generation, source_generation)
                count = int(np.count_nonzero(np.abs(block) > FLOAT_TOL))
                if target_generation == source_generation:
                    diagonal_nonzeros += count
                else:
                    off_diagonal_nonzeros += count
        profiles.append(
            CartanDiagonalProfile(
                mode_index=mode_index,
                diagonal_nonzeros=diagonal_nonzeros,
                off_diagonal_nonzeros=off_diagonal_nonzeros,
            )
        )
    return tuple(profiles)


@lru_cache(maxsize=1)
def build_transport_lie_tower_bridge_summary() -> dict[str, Any]:
    l6_exceptional = build_l6_exceptional_gauge_return_certificate()
    l6_chiral = build_l6_chiral_gauge_bridge_certificate()
    channels = l6_a2_generation_channels()
    cartan = l6_cartan_diagonal_profiles()
    return {
        "status": "ok",
        "transport_weyl_classes": [profile.to_dict() for profile in transport_weyl_class_profiles()],
        "l6_exceptional_split": {
            "e6_root_support_size": l6_exceptional.e6_root_support_size,
            "a2_root_support_size": l6_exceptional.a2_root_support_size,
            "cartan_support_size": l6_exceptional.cartan_support_size,
            "spinor_action_ranks": l6_exceptional.spinor_action_ranks,
            "full_matter_action_ranks": l6_exceptional.full_matter_action_ranks,
        },
        "l6_a2_generation_channels": [channel.to_dict() for channel in channels],
        "l6_cartan_diagonal_profiles": [profile.to_dict() for profile in cartan],
        "generation_channel_theorem": {
            "ordered_generation_pairs": [
                [channel.source_generation, channel.target_generation] for channel in channels
            ],
            "complete_oriented_three_generation_graph": sorted(
                [channel.source_generation, channel.target_generation] for channel in channels
            )
            == sorted(
                [[0, 1], [1, 0], [1, 2], [2, 1], [0, 2], [2, 0]]
            ),
            "all_a2_channels_are_signed_permutation_blocks": all(
                channel.signed_permutation for channel in channels
            ),
            "all_a2_channels_have_full_rank_16": all(channel.block_rank == 16 for channel in channels),
            "all_cartan_modes_are_generation_diagonal": all(
                profile.off_diagonal_nonzeros == 0 for profile in cartan
            ),
            "current_l6_bridge_activates_only_cartan_modes": (
                l6_chiral.a2_coefficients_all_zero
                and l6_chiral.active_a2_mode_indices == ()
                and l6_chiral.active_cartan_mode_indices == (0, 1, 2, 3, 4, 5, 6)
            ),
        },
        "bridge_verdict": (
            "The transport A2 local system and the l6 Lie tower now meet at the "
            "operator level. On the 45-point quotient transport graph, edges "
            "realize the full Weyl(A2) group with exact identity / reflection / "
            "three-cycle counts 192 / 396 / 132. On the l6 side, the six A2 "
            "modes are exactly the six ordered generation-transfer channels on "
            "the 48-spinor space, each a single 16x16 signed permutation block "
            "of full rank 16, while the eight Cartan modes are strictly "
            "generation-diagonal. So the Lie tower's A2 slice is no longer just "
            "a count in the exceptional dictionary: it is an exact generation "
            "mixing operator package. The current linearized l6 bridge still "
            "activates only Cartan directions, so the A2 channels are exact but "
            "not yet dynamically selected on the present Yukawa seed."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_lie_tower_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
