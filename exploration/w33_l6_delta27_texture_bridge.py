"""Envelope-level Delta(27) texture bridge for the canonical l6 mixed seed.

The exact mixed-seed activation map shows that the two minimal fan seeds

    (8,9) and (246,247)

are the first exact seeds that activate the full six-mode A2 package, and one
nonlinear closure step turns them into a full 3x3-support mixed seed.

This module packages the next structural observation:

  - both minimal fans close to the same canonical 24x24 mixed seed;
  - that seed is not invariant under the generation 3-cycle;
  - but its 3x3 generation envelope is exactly of the Delta(27)
    circulant-plus-diagonal type at the envelope level:
      * all off-diagonal block norms are equal;
      * two diagonal block norms are equal;
      * one diagonal block norm is distinguished;
  - cyclic generation conjugation therefore gives a clean 3-element orbit of
    distinguished-generation textures.

This does not claim the full 24x24 seed is literally a Delta(27) Yukawa
matrix in the model-building sense. The precise statement is envelope-level:
the canonical closure seed has the same generation-texture shape that appears
in Delta(27) circulant-plus-diagonal ansatze.
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

from w33_l6_chiral_gauge_bridge import FLOAT_TOL, _bridge_delta, generation_diagonal_induced_yukawa_24


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_l6_delta27_texture_bridge_summary.json"
FAN_MODE_PAIRS = ((8, 9), (246, 247))


def _generation_cycle_permutation_24() -> np.ndarray:
    permutation = np.zeros((24, 24), dtype=float)
    for generation in range(3):
        source = slice(8 * generation, 8 * (generation + 1))
        target_generation = (generation + 1) % 3
        target = slice(8 * target_generation, 8 * (target_generation + 1))
        permutation[target, source] = np.eye(8)
    return permutation


def _fan_seed(external_slot: str, fan_modes: tuple[int, int]) -> np.ndarray:
    base = generation_diagonal_induced_yukawa_24(external_slot)
    seed = base.copy()
    for mode_index in fan_modes:
        seed = seed + _bridge_delta(mode_index, base)
    return seed


def _canonical_closure_seed(external_slot: str) -> np.ndarray:
    forward = _fan_seed(external_slot, (8, 9))
    closed = forward.copy()
    for mode_index in (246, 247):
        closed = closed + _bridge_delta(mode_index, forward)
    return closed


def _other_fan_closure_seed(external_slot: str) -> np.ndarray:
    forward = _fan_seed(external_slot, (246, 247))
    closed = forward.copy()
    for mode_index in (8, 9):
        closed = closed + _bridge_delta(mode_index, forward)
    return closed


def _block_frobenius_envelope(matrix_24: np.ndarray) -> tuple[tuple[float, ...], ...]:
    rows = []
    for target_generation in range(3):
        row = []
        for source_generation in range(3):
            block = matrix_24[
                8 * target_generation : 8 * (target_generation + 1),
                8 * source_generation : 8 * (source_generation + 1),
            ]
            row.append(float(np.linalg.norm(block)))
        rows.append(tuple(row))
    return tuple(rows)


def _all_off_diagonal_values(envelope: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    values = []
    for row_index in range(3):
        for col_index in range(3):
            if row_index != col_index:
                values.append(envelope[row_index][col_index])
    return tuple(values)


def _diagonal_values(envelope: tuple[tuple[float, ...], ...]) -> tuple[float, float, float]:
    return tuple(envelope[index][index] for index in range(3))


def _distinguished_generation(envelope: tuple[tuple[float, ...], ...]) -> int:
    diagonal = _diagonal_values(envelope)
    for index in range(3):
        others = [diagonal[j] for j in range(3) if j != index]
        if np.isclose(others[0], others[1], atol=FLOAT_TOL) and not np.isclose(
            diagonal[index], others[0], atol=FLOAT_TOL
        ):
            return index
    raise AssertionError("expected one distinguished generation and one degenerate pair")


def _texture_shape_profile(envelope: tuple[tuple[float, ...], ...]) -> dict[str, Any]:
    diagonal = _diagonal_values(envelope)
    off_diagonal = _all_off_diagonal_values(envelope)
    distinguished = _distinguished_generation(envelope)
    degenerate_value = next(diagonal[index] for index in range(3) if index != distinguished)
    return {
        "envelope": [list(row) for row in envelope],
        "distinguished_generation": distinguished,
        "distinguished_diagonal_norm": diagonal[distinguished],
        "degenerate_diagonal_norm": degenerate_value,
        "uniform_off_diagonal_norm": off_diagonal[0],
        "off_diagonal_uniform": bool(np.allclose(off_diagonal, off_diagonal[0], atol=FLOAT_TOL)),
        "twofold_diagonal_degeneracy": bool(
            np.isclose(
                [diagonal[index] for index in range(3) if index != distinguished][0],
                [diagonal[index] for index in range(3) if index != distinguished][1],
                atol=FLOAT_TOL,
            )
        ),
        "distinguished_diagonal_is_unique": bool(
            not np.isclose(diagonal[distinguished], degenerate_value, atol=FLOAT_TOL)
        ),
    }


def _cycle_orbit_profiles(matrix_24: np.ndarray) -> list[dict[str, Any]]:
    permutation = _generation_cycle_permutation_24()
    orbit = []
    current = matrix_24.copy()
    for power in range(3):
        envelope = _block_frobenius_envelope(current)
        orbit.append(
            {
                "cycle_power": power,
                **_texture_shape_profile(envelope),
            }
        )
        current = permutation @ current @ permutation.T
    return orbit


@lru_cache(maxsize=1)
def build_l6_delta27_texture_bridge_summary() -> dict[str, Any]:
    slot_profiles = {}
    for external_slot in ("H_2", "Hbar_2"):
        canonical = _canonical_closure_seed(external_slot)
        alternate = _other_fan_closure_seed(external_slot)
        slot_profiles[external_slot] = {
            "fan_closures_match_exactly": bool(np.allclose(canonical, alternate, atol=FLOAT_TOL)),
            "fan_closure_max_abs_difference": float(np.max(np.abs(canonical - alternate))),
            "cycle_invariant": bool(
                np.allclose(
                    _generation_cycle_permutation_24() @ canonical @ _generation_cycle_permutation_24().T,
                    canonical,
                    atol=FLOAT_TOL,
                )
            ),
            "canonical_texture": _texture_shape_profile(_block_frobenius_envelope(canonical)),
            "cycle_orbit": _cycle_orbit_profiles(canonical),
        }

    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "delta27_envelope_theorem": {
            "fan_closures_match_for_both_slots": all(
                profile["fan_closures_match_exactly"] for profile in slot_profiles.values()
            ),
            "canonical_closure_is_not_cycle_invariant": all(
                not profile["cycle_invariant"] for profile in slot_profiles.values()
            ),
            "canonical_closure_has_delta27_envelope_shape": all(
                profile["canonical_texture"]["off_diagonal_uniform"]
                and profile["canonical_texture"]["twofold_diagonal_degeneracy"]
                and profile["canonical_texture"]["distinguished_diagonal_is_unique"]
                for profile in slot_profiles.values()
            ),
            "cycle_orbit_has_three_distinguished_generations": all(
                sorted(
                    orbit_item["distinguished_generation"]
                    for orbit_item in profile["cycle_orbit"]
                )
                == [0, 1, 2]
                for profile in slot_profiles.values()
            ),
        },
        "bridge_verdict": (
            "The two minimal fan closures coincide to one canonical mixed seed. "
            "That seed is not Z3-cycle invariant, but its 3x3 generation envelope "
            "has the exact Delta(27) circulant-plus-diagonal shape at the envelope "
            "level: one distinguished diagonal generation, a degenerate diagonal "
            "pair, and a uniform off-diagonal shell. Cyclic generation conjugation "
            "therefore produces a clean 3-element orbit of distinguished-generation "
            "textures."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_l6_delta27_texture_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
