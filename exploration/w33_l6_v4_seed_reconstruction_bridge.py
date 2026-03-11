"""Exact reconstruction of the canonical mixed seed from V4 flavour data.

The previous bridges isolated:

  - a slot-independent ordered-generation-pair V4 character map on the
    off-diagonal shell;
  - an exact simultaneous projector decomposition on the right-handed support.

This module packages the next step: the canonical nonlinear closure seed is
reconstructible exactly from native internal data rather than from the ad hoc
fan-closure recipe.

What is established:

  - after subtracting the replicated generation-diagonal seed, the full
    canonical 24x24 mixed seed is determined by one reference off-diagonal
    block and one slot-independent 3x3 label matrix over {0, I, A, B, AB};
  - that label matrix is exactly
        [[AB, I, A],
         [AB, I, A],
         [ A, B, 0]];
  - generation-0 and generation-1 diagonal corrections equal exact off-diagonal
    blocks, while the generation-2 diagonal block is unchanged;
  - reconstructing from this recipe reproduces the canonical mixed seed
    exactly for both H_2 and Hbar_2.

So the canonical mixed seed is now a native exact flavour seed: base diagonal
Yukawa + one reference block + a slot-independent V4-labelled generation
pattern.
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

from w33_l6_chiral_gauge_bridge import generation_diagonal_induced_yukawa_24
from w33_l6_delta27_texture_bridge import _canonical_closure_seed
from w33_l6_delta27_v4_bridge import _solve_row_column_signs, _slot_profile
from w33_l6_v4_projector_bridge import _projector_profiles


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_v4_seed_reconstruction_bridge_summary.json"


def _character_sign_vectors(external_slot: str) -> dict[str, tuple[int, ...]]:
    profile = _slot_profile(external_slot)
    return {
        "0": tuple(0 for _ in range(8)),
        "I": tuple(1 for _ in range(8)),
        "A": tuple(profile["generator_a"]),
        "B": tuple(profile["generator_b"]),
        "AB": tuple(profile["generator_ab"]),
    }


def _reference_block(external_slot: str) -> np.ndarray:
    canonical = _canonical_closure_seed(external_slot)
    return canonical[0:8, 8:16]


def _label_matrix(external_slot: str) -> tuple[tuple[str, ...], ...]:
    base = generation_diagonal_induced_yukawa_24(external_slot)
    canonical = _canonical_closure_seed(external_slot)
    reference = _reference_block(external_slot)
    sign_to_label = {value: key for key, value in _character_sign_vectors(external_slot).items() if key != "0"}

    labels = []
    for target_generation in range(3):
        row = []
        for source_generation in range(3):
            canonical_block = canonical[
                8 * target_generation : 8 * (target_generation + 1),
                8 * source_generation : 8 * (source_generation + 1),
            ]
            block = canonical_block.copy()
            if target_generation == source_generation:
                block = block - base[
                    8 * target_generation : 8 * (target_generation + 1),
                    8 * source_generation : 8 * (source_generation + 1),
                ]
            if not np.count_nonzero(np.abs(block) > 1e-10):
                row.append("0")
                continue
            _, col_signs = _solve_row_column_signs(reference, block)
            row.append(sign_to_label[tuple(col_signs)])
        labels.append(tuple(row))
    return tuple(labels)


def _character_matrix(external_slot: str, label: str) -> np.ndarray:
    signs = _character_sign_vectors(external_slot)[label]
    if label == "0":
        return np.zeros((8, 8), dtype=float)
    return np.diag(np.array(signs, dtype=float))


def _reconstruct_from_label_matrix(
    external_slot: str,
    label_matrix: tuple[tuple[str, ...], ...],
) -> np.ndarray:
    base = generation_diagonal_induced_yukawa_24(external_slot)
    reference = _reference_block(external_slot)
    reconstructed = base.copy()
    for target_generation in range(3):
        for source_generation in range(3):
            label = label_matrix[target_generation][source_generation]
            if label == "0":
                continue
            block = reference @ _character_matrix(external_slot, label)
            if target_generation == source_generation:
                reconstructed[
                    8 * target_generation : 8 * (target_generation + 1),
                    8 * source_generation : 8 * (source_generation + 1),
                ] += block
            else:
                reconstructed[
                    8 * target_generation : 8 * (target_generation + 1),
                    8 * source_generation : 8 * (source_generation + 1),
                ] = block
    return reconstructed


@lru_cache(maxsize=1)
def build_l6_v4_seed_reconstruction_bridge_summary() -> dict[str, Any]:
    slot_profiles = {}
    label_matrices = {}
    for external_slot in ("H_2", "Hbar_2"):
        label_matrix = _label_matrix(external_slot)
        label_matrices[external_slot] = label_matrix
        reconstructed = _reconstruct_from_label_matrix(external_slot, label_matrix)
        canonical = _canonical_closure_seed(external_slot)
        base = generation_diagonal_induced_yukawa_24(external_slot)
        projectors = _projector_profiles(external_slot)["projectors"]
        right_labels = _projector_profiles(external_slot)["active_support"]

        plus_minus_cols = [state for state in projectors["+-"]["support_labels"]]
        minus_plus_cols = [state for state in projectors["-+"]["support_labels"]]

        slot_profiles[external_slot] = {
            "label_matrix": [list(row) for row in label_matrix],
            "reconstructs_exactly": bool(np.allclose(reconstructed, canonical)),
            "max_abs_reconstruction_error": float(np.max(np.abs(reconstructed - canonical))),
            "diag0_delta_equals_offdiag10": bool(
                np.allclose(
                    canonical[0:8, 0:8] - base[0:8, 0:8],
                    canonical[8:16, 0:8],
                )
            ),
            "diag1_delta_equals_offdiag01": bool(
                np.allclose(
                    canonical[8:16, 8:16] - base[8:16, 8:16],
                    canonical[0:8, 8:16],
                )
            ),
            "diag2_unchanged": bool(
                np.allclose(
                    canonical[16:24, 16:24],
                    base[16:24, 16:24],
                )
            ),
            "reference_projector_rank_split": {
                "+-": len(plus_minus_cols),
                "-+": len(minus_plus_cols),
            },
            "active_support": right_labels,
        }

    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "seed_reconstruction_theorem": {
            "label_matrix_is_slot_independent": label_matrices["H_2"] == label_matrices["Hbar_2"],
            "expected_label_matrix": [list(row) for row in label_matrices["H_2"]],
            "reconstructs_canonical_closure_exactly_for_both_slots": all(
                profile["reconstructs_exactly"] for profile in slot_profiles.values()
            ),
            "generation_0_diagonal_delta_equals_offdiag_1_to_0_for_both_slots": all(
                profile["diag0_delta_equals_offdiag10"] for profile in slot_profiles.values()
            ),
            "generation_1_diagonal_delta_equals_offdiag_0_to_1_for_both_slots": all(
                profile["diag1_delta_equals_offdiag01"] for profile in slot_profiles.values()
            ),
            "generation_2_diagonal_block_is_unchanged_for_both_slots": all(
                profile["diag2_unchanged"] for profile in slot_profiles.values()
            ),
            "reference_projector_rank_split_matches_h2_2_plus_2_and_hbar2_3_plus_1": (
                slot_profiles["H_2"]["reference_projector_rank_split"] == {"+-": 2, "-+": 2}
                and slot_profiles["Hbar_2"]["reference_projector_rank_split"] == {"+-": 3, "-+": 1}
            ),
        },
        "bridge_verdict": (
            "The canonical mixed seed is now reconstructible exactly from native "
            "internal data: replicated base Yukawa, one reference off-diagonal "
            "block, and one slot-independent V4-labelled generation matrix. That "
            "matrix is [[AB,I,A],[AB,I,A],[A,B,0]], the generation-0 and "
            "generation-1 diagonal corrections equal exact off-diagonal blocks, "
            "and the generation-2 diagonal block stays unchanged."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_l6_v4_seed_reconstruction_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
