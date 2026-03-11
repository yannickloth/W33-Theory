"""Matrix-level V4 character refinement of the canonical l6 Delta(27) seed.

The previous Delta(27) bridge was intentionally cautious: it only claimed that
the canonical nonlinear fan-closure seed has the right 3x3 generation-envelope
shape. This module strengthens that statement to matrix level.

What is established:

  - for each external slot H_2 and Hbar_2, all six off-diagonal 8x8 blocks of
    the canonical closure seed share the same exact support pattern;
  - fixing the (0,1) block as reference, every other off-diagonal block is
    exactly the reference block multiplied on the right by a diagonal sign
    character;
  - the realized sign characters form a four-element commuting involution group
    V4 = {I, A, B, AB};
  - the ordered-generation-pair to V4-character label map is identical for
    H_2 and Hbar_2, so the generation-side pattern is slot-independent;
  - the only slot dependence is which active right-handed states carry the two
    generators:
      * H_2 acts on u_c_1, u_c_2, u_c_3, nu_c;
      * Hbar_2 acts on d_c_1, d_c_2, d_c_3, e_c.

So the canonical closure seed is no longer only an envelope-level
Delta(27)-type texture. It is an exact matrix-level flavour texture torsor
under a native V4 right-character action.
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

from w33_fermionic_connes_sector import right_spinor_basis
from w33_l6_chiral_gauge_bridge import FLOAT_TOL
from w33_l6_delta27_texture_bridge import _canonical_closure_seed, _generation_cycle_permutation_24


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_delta27_v4_bridge_summary.json"
REFERENCE_PAIR = (0, 1)


def _off_diagonal_blocks(matrix_24: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    return {
        (target_generation, source_generation): matrix_24[
            8 * target_generation : 8 * (target_generation + 1),
            8 * source_generation : 8 * (source_generation + 1),
        ]
        for target_generation in range(3)
        for source_generation in range(3)
        if target_generation != source_generation
    }


def _shared_support_pattern(blocks: dict[tuple[int, int], np.ndarray]) -> np.ndarray:
    first = next(iter(blocks.values()))
    support = np.abs(first) > FLOAT_TOL
    for block in blocks.values():
        if not np.array_equal(np.abs(block) > FLOAT_TOL, support):
            raise AssertionError("expected a shared off-diagonal support pattern")
    return support


def _solve_row_column_signs(reference: np.ndarray, block: np.ndarray) -> tuple[tuple[int, ...], tuple[int, ...]]:
    support = np.abs(reference) > FLOAT_TOL
    if not np.array_equal(np.abs(block) > FLOAT_TOL, support):
        raise AssertionError("expected the same support pattern")

    sign_ratio = np.zeros(reference.shape, dtype=int)
    sign_ratio[support] = np.rint(block[support] / reference[support]).astype(int)

    row_signs: list[int | None] = [None] * reference.shape[0]
    col_signs: list[int | None] = [None] * reference.shape[1]

    def propagate_from_row(start_row: int) -> None:
        row_signs[start_row] = 1
        stack: list[tuple[str, int]] = [("row", start_row)]
        while stack:
            kind, index = stack.pop()
            if kind == "row":
                for col in np.where(support[index])[0]:
                    value = int(sign_ratio[index, col] * row_signs[index])
                    if col_signs[col] is None:
                        col_signs[col] = value
                        stack.append(("col", col))
                    elif col_signs[col] != value:
                        raise AssertionError("inconsistent sign decomposition")
            else:
                for row in np.where(support[:, index])[0]:
                    value = int(sign_ratio[row, index] * col_signs[index])
                    if row_signs[row] is None:
                        row_signs[row] = value
                        stack.append(("row", row))
                    elif row_signs[row] != value:
                        raise AssertionError("inconsistent sign decomposition")

    for row in range(reference.shape[0]):
        if row_signs[row] is None and np.any(support[row]):
            propagate_from_row(row)

    normalized_rows = tuple(1 if value is None else int(value) for value in row_signs)
    normalized_cols = tuple(1 if value is None else int(value) for value in col_signs)

    reconstructed = np.diag(normalized_rows) @ reference @ np.diag(normalized_cols)
    if not np.allclose(reconstructed, block, atol=FLOAT_TOL):
        raise AssertionError("failed to reconstruct block from sign decomposition")
    return normalized_rows, normalized_cols


def _hamming_weight(signs: tuple[int, ...]) -> int:
    return sum(1 for value in signs if value == -1)


def _character_generators(sign_vectors: set[tuple[int, ...]]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    identity = tuple(1 for _ in range(8))
    nontrivial = sorted(
        (vector for vector in sign_vectors if vector != identity),
        key=lambda vector: (_hamming_weight(vector), vector),
    )
    generator_a = nontrivial[0]
    for candidate in nontrivial[1:]:
        if candidate != generator_a:
            generator_b = candidate
            break
    else:
        raise AssertionError("expected two independent nontrivial characters")
    return generator_a, generator_b


def _multiply_sign_vectors(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(int(a * b) for a, b in zip(left, right))


def _sign_vector_label(
    sign_vector: tuple[int, ...],
    generator_a: tuple[int, ...],
    generator_b: tuple[int, ...],
) -> str:
    identity = tuple(1 for _ in range(8))
    if sign_vector == identity:
        return "I"
    if sign_vector == generator_a:
        return "A"
    if sign_vector == generator_b:
        return "B"
    if sign_vector == _multiply_sign_vectors(generator_a, generator_b):
        return "AB"
    raise AssertionError("unexpected sign character outside the generated V4")


def _pair_key(pair: tuple[int, int]) -> str:
    return f"{pair[0]}->{pair[1]}"


def _active_right_support_labels(reference: np.ndarray) -> list[str]:
    labels = [state.slot for state in right_spinor_basis()]
    return [labels[index] for index in range(reference.shape[1]) if np.any(np.abs(reference[:, index]) > FLOAT_TOL)]


def _slot_profile(external_slot: str) -> dict[str, Any]:
    matrix = _canonical_closure_seed(external_slot)
    blocks = _off_diagonal_blocks(matrix)
    reference = blocks[REFERENCE_PAIR]
    support = _shared_support_pattern(blocks)

    row_signs_by_pair: dict[tuple[int, int], tuple[int, ...]] = {}
    col_signs_by_pair: dict[tuple[int, int], tuple[int, ...]] = {}
    for pair, block in blocks.items():
        row_signs, col_signs = _solve_row_column_signs(reference, block)
        row_signs_by_pair[pair] = row_signs
        col_signs_by_pair[pair] = col_signs

    sign_vectors = set(col_signs_by_pair.values())
    generator_a, generator_b = _character_generators(sign_vectors)
    pair_character_labels = {
        _pair_key(pair): _sign_vector_label(col_signs, generator_a, generator_b)
        for pair, col_signs in sorted(col_signs_by_pair.items())
    }
    identity = tuple(1 for _ in range(8))
    generator_ab = _multiply_sign_vectors(generator_a, generator_b)
    cycle = _generation_cycle_permutation_24()

    current = matrix.copy()
    cycle_profiles = []
    for power in range(3):
        current_blocks = _off_diagonal_blocks(current)
        current_reference = current_blocks[REFERENCE_PAIR]
        current_rows = []
        current_cols = []
        for pair, block in current_blocks.items():
            row_signs, col_signs = _solve_row_column_signs(current_reference, block)
            current_rows.append(row_signs)
            current_cols.append(col_signs)
        cycle_profiles.append(
            {
                "cycle_power": power,
                "all_row_signs_trivial": all(
                    row_signs == identity for row_signs in current_rows
                ),
                "realized_character_count": len(set(current_cols)),
            }
        )
        current = cycle @ current @ cycle.T

    return {
        "reference_pair": list(REFERENCE_PAIR),
        "reference_rank": int(np.linalg.matrix_rank(reference)),
        "reference_support_count": int(np.count_nonzero(support)),
        "active_right_support_labels": _active_right_support_labels(reference),
        "all_off_diagonal_blocks_share_exact_support": True,
        "all_relative_row_signs_are_trivial": all(row_signs == identity for row_signs in row_signs_by_pair.values()),
        "all_off_diagonal_blocks_are_exact_right_sign_twists": True,
        "realized_right_sign_vectors": [list(vector) for vector in sorted(sign_vectors)],
        "generator_a": list(generator_a),
        "generator_b": list(generator_b),
        "generator_ab": list(generator_ab),
        "generator_a_flipped_labels": [
            label
            for label, sign in zip((state.slot for state in right_spinor_basis()), generator_a)
            if sign == -1
        ],
        "generator_b_flipped_labels": [
            label
            for label, sign in zip((state.slot for state in right_spinor_basis()), generator_b)
            if sign == -1
        ],
        "generators_are_commuting_involutions": (
            _multiply_sign_vectors(generator_a, generator_a) == identity
            and _multiply_sign_vectors(generator_b, generator_b) == identity
            and _multiply_sign_vectors(generator_a, generator_b)
            == _multiply_sign_vectors(generator_b, generator_a)
        ),
        "four_v4_characters_realized": sign_vectors == {identity, generator_a, generator_b, generator_ab},
        "pair_character_labels": pair_character_labels,
        "cycle_orbit_profiles": cycle_profiles,
    }


@lru_cache(maxsize=1)
def build_l6_delta27_v4_bridge_summary() -> dict[str, Any]:
    slot_profiles = {
        external_slot: _slot_profile(external_slot)
        for external_slot in ("H_2", "Hbar_2")
    }
    pair_character_maps = [
        profile["pair_character_labels"]
        for profile in slot_profiles.values()
    ]

    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "matrix_level_v4_theorem": {
            "all_off_diagonal_blocks_share_exact_support_for_both_slots": all(
                profile["all_off_diagonal_blocks_share_exact_support"]
                for profile in slot_profiles.values()
            ),
            "all_relative_row_signs_are_trivial_for_both_slots": all(
                profile["all_relative_row_signs_are_trivial"]
                for profile in slot_profiles.values()
            ),
            "all_off_diagonal_blocks_are_exact_right_sign_twists_for_both_slots": all(
                profile["all_off_diagonal_blocks_are_exact_right_sign_twists"]
                for profile in slot_profiles.values()
            ),
            "four_v4_characters_realized_for_both_slots": all(
                profile["four_v4_characters_realized"] for profile in slot_profiles.values()
            ),
            "generators_are_commuting_involutions_for_both_slots": all(
                profile["generators_are_commuting_involutions"] for profile in slot_profiles.values()
            ),
            "pair_character_pattern_is_slot_independent": pair_character_maps[0] == pair_character_maps[1],
            "cycle_orbit_preserves_v4_structure_for_both_slots": all(
                all(
                    cycle_profile["all_row_signs_trivial"]
                    and cycle_profile["realized_character_count"] == 4
                    for cycle_profile in profile["cycle_orbit_profiles"]
                )
                for profile in slot_profiles.values()
            ),
        },
        "bridge_verdict": (
            "The canonical l6 fan-closure seed already lifts the Delta(27) "
            "envelope bridge to matrix level. In each external slot, every "
            "off-diagonal 8x8 block is exactly one reference block multiplied "
            "on the right by one of four diagonal sign characters forming a "
            "V4 subgroup. The ordered-generation-pair to character-label map is "
            "the same for H_2 and Hbar_2, so the generation-side pattern is "
            "slot-independent while the slot dependence sits only in which "
            "active right-handed states carry the two commuting involution "
            "generators."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_l6_delta27_v4_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
