"""Dynamic selection of the canonical V4 label matrix from exact l6 closure.

The previous bridges established three facts separately:

1. the minimal full-activation fans are exactly (8, 9) and (246, 247);
2. their nonlinear closures coincide to one canonical mixed seed;
3. that canonical seed carries the slot-independent V4 label matrix
       [[AB, I, A],
        [AB, I, A],
        [ A, B, 0]].

This module turns those observations into an exact dynamic selection theorem.
Instead of reading the label matrix off the final seed, we decompose the
canonical closure into the two exact A2 fan stages themselves.

What is established:

  - the forward fan (8, 9) already selects the bottom row [A, B, 0];
  - the reverse completion (246, 247) adds exactly two identical rows
    [AB, I, A];
  - starting from the reverse fan gives the complementary partial shell, and
    the forward completion adds exactly the missing entries;
  - both routes assemble the same slot-independent canonical label matrix for
    both H_2 and Hbar_2.

So the canonical V4-labelled mixed seed is now selected dynamically by the
exact l6 A2 closure dynamics itself rather than only reconstructed after the
fact.
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
from w33_l6_chiral_gauge_bridge import generation_diagonal_induced_yukawa_24
from w33_l6_delta27_v4_bridge import _solve_row_column_signs
from w33_l6_v4_seed_reconstruction_bridge import (
    _character_sign_vectors,
    _label_matrix,
    _reference_block,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_v4_closure_selection_bridge_summary.json"
FORWARD_FAN = (8, 9)
REVERSE_FAN = (246, 247)
ZERO_LABEL_MATRIX = (("0", "0", "0"), ("0", "0", "0"), ("0", "0", "0"))


def _matrix_labels(external_slot: str, matrix_24: np.ndarray, subtract_base_on_diagonal: bool) -> tuple[tuple[str, ...], ...]:
    base = generation_diagonal_induced_yukawa_24(external_slot)
    reference = _reference_block(external_slot)
    sign_to_label = {
        value: key
        for key, value in _character_sign_vectors(external_slot).items()
        if key != "0"
    }

    rows = []
    for target_generation in range(3):
        row = []
        for source_generation in range(3):
            block = matrix_24[
                8 * target_generation : 8 * (target_generation + 1),
                8 * source_generation : 8 * (source_generation + 1),
            ].copy()
            if subtract_base_on_diagonal and target_generation == source_generation:
                block -= base[
                    8 * target_generation : 8 * (target_generation + 1),
                    8 * source_generation : 8 * (source_generation + 1),
                ]
            if not np.count_nonzero(np.abs(block) > 1e-10):
                row.append("0")
                continue
            _, col_signs = _solve_row_column_signs(reference, block)
            row.append(sign_to_label[tuple(col_signs)])
        rows.append(tuple(row))
    return tuple(rows)


def _combine_label_matrices(
    left: tuple[tuple[str, ...], ...],
    right: tuple[tuple[str, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    rows = []
    for left_row, right_row in zip(left, right):
        row = []
        for left_label, right_label in zip(left_row, right_row):
            if left_label != "0" and right_label != "0" and left_label != right_label:
                raise AssertionError("label matrices overlap inconsistently")
            row.append(left_label if right_label == "0" else right_label)
        rows.append(tuple(row))
    return tuple(rows)


def _fan_seed(external_slot: str, fan_modes: tuple[int, int]) -> np.ndarray:
    base = generation_diagonal_induced_yukawa_24(external_slot)
    return _apply_modes_to_seed(base, fan_modes)


def _completion_delta(
    external_slot: str,
    first_fan_modes: tuple[int, int],
    second_fan_modes: tuple[int, int],
) -> np.ndarray:
    first = _fan_seed(external_slot, first_fan_modes)
    closed = _apply_modes_to_seed(first, second_fan_modes)
    return closed - first


@lru_cache(maxsize=1)
def build_l6_v4_closure_selection_bridge_summary() -> dict[str, Any]:
    slot_profiles = {}
    for external_slot in ("H_2", "Hbar_2"):
        forward_seed_labels = _matrix_labels(
            external_slot,
            _fan_seed(external_slot, FORWARD_FAN),
            subtract_base_on_diagonal=True,
        )
        reverse_seed_labels = _matrix_labels(
            external_slot,
            _fan_seed(external_slot, REVERSE_FAN),
            subtract_base_on_diagonal=True,
        )
        forward_then_reverse_increment = _matrix_labels(
            external_slot,
            _completion_delta(external_slot, FORWARD_FAN, REVERSE_FAN),
            subtract_base_on_diagonal=False,
        )
        reverse_then_forward_increment = _matrix_labels(
            external_slot,
            _completion_delta(external_slot, REVERSE_FAN, FORWARD_FAN),
            subtract_base_on_diagonal=False,
        )
        canonical = _label_matrix(external_slot)

        slot_profiles[external_slot] = {
            "forward_fan_seed_labels": [list(row) for row in forward_seed_labels],
            "reverse_fan_seed_labels": [list(row) for row in reverse_seed_labels],
            "forward_then_reverse_increment_labels": [list(row) for row in forward_then_reverse_increment],
            "reverse_then_forward_increment_labels": [list(row) for row in reverse_then_forward_increment],
            "assembled_from_forward_route": [
                list(row) for row in _combine_label_matrices(forward_seed_labels, forward_then_reverse_increment)
            ],
            "assembled_from_reverse_route": [
                list(row) for row in _combine_label_matrices(reverse_seed_labels, reverse_then_forward_increment)
            ],
            "canonical_label_matrix": [list(row) for row in canonical],
        }

    expected_forward_seed = (("0", "0", "0"), ("0", "0", "0"), ("A", "B", "0"))
    expected_reverse_seed = (("0", "0", "A"), ("0", "0", "A"), ("0", "0", "0"))
    expected_forward_then_reverse_increment = (("AB", "I", "A"), ("AB", "I", "A"), ("0", "0", "0"))
    expected_reverse_then_forward_increment = (("AB", "I", "0"), ("AB", "I", "0"), ("A", "B", "0"))
    canonical = (("AB", "I", "A"), ("AB", "I", "A"), ("A", "B", "0"))

    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "closure_selection_theorem": {
            "forward_fan_is_exact_generation_2_row_for_both_slots": all(
                tuple(tuple(value for value in row) for row in profile["forward_fan_seed_labels"]) == expected_forward_seed
                for profile in slot_profiles.values()
            ),
            "reverse_completion_adds_exact_double_ab_i_a_row_for_both_slots": all(
                tuple(tuple(value for value in row) for row in profile["forward_then_reverse_increment_labels"])
                == expected_forward_then_reverse_increment
                for profile in slot_profiles.values()
            ),
            "reverse_fan_is_exact_two_row_a_column_shell_for_both_slots": all(
                tuple(tuple(value for value in row) for row in profile["reverse_fan_seed_labels"]) == expected_reverse_seed
                for profile in slot_profiles.values()
            ),
            "forward_completion_supplies_exact_missing_ab_i_and_a_b_entries_for_both_slots": all(
                tuple(tuple(value for value in row) for row in profile["reverse_then_forward_increment_labels"])
                == expected_reverse_then_forward_increment
                for profile in slot_profiles.values()
            ),
            "forward_route_assembles_canonical_label_matrix_for_both_slots": all(
                tuple(tuple(value for value in row) for row in profile["assembled_from_forward_route"]) == canonical
                for profile in slot_profiles.values()
            ),
            "reverse_route_assembles_canonical_label_matrix_for_both_slots": all(
                tuple(tuple(value for value in row) for row in profile["assembled_from_reverse_route"]) == canonical
                for profile in slot_profiles.values()
            ),
            "canonical_label_matrix_is_slot_independent": all(
                tuple(tuple(value for value in row) for row in profile["canonical_label_matrix"]) == canonical
                for profile in slot_profiles.values()
            ),
        },
        "bridge_verdict": (
            "The canonical V4 label matrix is now selected dynamically by exact "
            "l6 closure. The minimal forward fan already contributes the bottom "
            "row [A,B,0], the reverse completion adds exactly two identical rows "
            "[AB,I,A], and the reverse route assembles the same matrix in a "
            "complementary way. So [[AB,I,A],[AB,I,A],[A,B,0]] is not merely "
            "read off the final seed after the fact; it is the unique matrix "
            "assembled by the exact two-step A2 closure dynamics for both H_2 "
            "and Hbar_2."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_l6_v4_closure_selection_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
