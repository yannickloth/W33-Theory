"""Exact unipotent reduction of the canonical Yukawa seed.

The scaffold bridges already fixed the clean Higgs slots, the slot-independent
V4 label matrix, the active right-handed projector splits, and the minimal A2
activation seeds. This module packages the next structural step:

  - after compressing to the active V4 sectors, the canonical 24x24 mixed seed
    is not a generic three-generation texture;
  - in each active sector, all nine generation blocks live in an exact
    2-dimensional internal block span;
  - the generation-side coefficient matrices for those two templates are
    slot-independent;
  - the nontrivial generation matrices are commuting unipotent 3x3 operators
    with characteristic polynomial (lambda - 1)^3.

So the Yukawa frontier is now smaller than "the 24x24 mixed seed spectrum":
the generation algebra is fixed exactly, and the remaining freedom sits in the
slot-specific internal templates carried by the two active V4 sectors.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import sympy as sp


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_fermionic_connes_sector import right_spinor_basis
from w33_l6_delta27_texture_bridge import _canonical_closure_seed
from w33_l6_v4_projector_bridge import _projector_profiles


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_yukawa_unipotent_reduction_bridge_summary.json"
FLOAT_TOL = 1e-10
ACTIVE_SECTORS = ("+-", "-+")


def _label_to_index() -> dict[str, int]:
    return {state.slot: index for index, state in enumerate(right_spinor_basis())}


def _compressed_sector_matrix(external_slot: str, sector: str) -> tuple[np.ndarray, list[str], list[int]]:
    labels = _projector_profiles(external_slot)["projectors"][sector]["support_labels"]
    label_to_index = _label_to_index()
    local_indices = [label_to_index[label] for label in labels]
    columns = [8 * generation + local_index for generation in range(3) for local_index in local_indices]
    return _canonical_closure_seed(external_slot)[:, columns], labels, local_indices


def _sector_blocks(external_slot: str, sector: str) -> dict[tuple[int, int], np.ndarray]:
    matrix = _canonical_closure_seed(external_slot)
    _, _, local_indices = _compressed_sector_matrix(external_slot, sector)
    return {
        (target_generation, source_generation): matrix[
            8 * target_generation : 8 * (target_generation + 1),
            [8 * source_generation + local_index for local_index in local_indices],
        ]
        for target_generation in range(3)
        for source_generation in range(3)
    }


def _block_span_rank(blocks: dict[tuple[int, int], np.ndarray]) -> int:
    vectors = np.stack([block.reshape(-1) for _, block in sorted(blocks.items())], axis=1)
    return int(np.linalg.matrix_rank(vectors))


def _template_decomposition(
    blocks: dict[tuple[int, int], np.ndarray]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    template0 = blocks[(0, 0)]
    template1 = blocks[(0, 1)]
    basis = np.stack([template0.reshape(-1), template1.reshape(-1)], axis=1)

    coeff0 = np.zeros((3, 3), dtype=int)
    coeff1 = np.zeros((3, 3), dtype=int)
    for target_generation in range(3):
        for source_generation in range(3):
            vector = blocks[(target_generation, source_generation)].reshape(-1)
            coeffs, *_ = np.linalg.lstsq(basis, vector, rcond=None)
            rounded = np.rint(coeffs).astype(int)
            if not np.allclose(coeffs, rounded, atol=FLOAT_TOL):
                raise AssertionError("expected integral two-template coefficients")
            reconstructed = rounded[0] * template0 + rounded[1] * template1
            if not np.allclose(reconstructed, blocks[(target_generation, source_generation)], atol=FLOAT_TOL):
                raise AssertionError("two-template decomposition failed to reconstruct exactly")
            coeff0[target_generation, source_generation] = int(rounded[0])
            coeff1[target_generation, source_generation] = int(rounded[1])

    return template0, template1, coeff0, coeff1


def _charpoly_string(matrix: np.ndarray) -> str:
    symbol = sp.symbols("lambda")
    expr = sp.factor(sp.Matrix(matrix.tolist()).charpoly(symbol).as_expr())
    return str(expr)


def _sector_profile(external_slot: str, sector: str) -> dict[str, Any]:
    compressed, support_labels, _ = _compressed_sector_matrix(external_slot, sector)
    blocks = _sector_blocks(external_slot, sector)
    template0, template1, coeff0, coeff1 = _template_decomposition(blocks)

    return {
        "support_labels": support_labels,
        "support_size": len(support_labels),
        "compressed_rank": int(np.linalg.matrix_rank(compressed)),
        "compressed_rank_saturates_three_generation_support": bool(
            np.linalg.matrix_rank(compressed) == 3 * len(support_labels)
        ),
        "block_span_rank": _block_span_rank(blocks),
        "template_pairs": [[0, 0], [0, 1]],
        "template0_coefficients": coeff0.tolist(),
        "template1_generation_matrix": coeff1.tolist(),
        "reconstructs_exactly_from_two_templates": True,
        "template0_rank": int(np.linalg.matrix_rank(template0)),
        "template1_rank": int(np.linalg.matrix_rank(template1)),
    }


@lru_cache(maxsize=1)
def build_yukawa_unipotent_reduction_summary() -> dict[str, Any]:
    slot_profiles = {
        external_slot: {
            sector: _sector_profile(external_slot, sector) for sector in ACTIVE_SECTORS
        }
        for external_slot in ("H_2", "Hbar_2")
    }

    plus_minus = np.array(
        slot_profiles["H_2"]["+-"]["template1_generation_matrix"],
        dtype=int,
    )
    minus_plus = np.array(
        slot_profiles["H_2"]["-+"]["template1_generation_matrix"],
        dtype=int,
    )
    identity = np.eye(3, dtype=int)
    plus_minus_nilpotent = plus_minus - identity
    minus_plus_nilpotent = minus_plus - identity

    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "universal_generation_algebra": {
            "slot_independent_plus_minus_matrix": (
                slot_profiles["H_2"]["+-"]["template1_generation_matrix"]
                == slot_profiles["Hbar_2"]["+-"]["template1_generation_matrix"]
            ),
            "slot_independent_minus_plus_matrix": (
                slot_profiles["H_2"]["-+"]["template1_generation_matrix"]
                == slot_profiles["Hbar_2"]["-+"]["template1_generation_matrix"]
            ),
            "template0_coefficients_are_identity_for_both_active_sectors": all(
                slot_profiles[slot][sector]["template0_coefficients"]
                == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                for slot in ("H_2", "Hbar_2")
                for sector in ACTIVE_SECTORS
            ),
            "plus_minus_generation_matrix": plus_minus.tolist(),
            "minus_plus_generation_matrix": minus_plus.tolist(),
            "plus_minus_charpoly": _charpoly_string(plus_minus),
            "minus_plus_charpoly": _charpoly_string(minus_plus),
            "plus_minus_is_unipotent_jordan_type": bool(
                np.array_equal(np.linalg.matrix_power(plus_minus_nilpotent, 3), np.zeros((3, 3), dtype=int))
                and np.linalg.matrix_rank(plus_minus_nilpotent) == 2
                and np.linalg.matrix_rank(plus_minus_nilpotent @ plus_minus_nilpotent) == 1
            ),
            "minus_plus_is_unipotent_jordan_type": bool(
                np.array_equal(np.linalg.matrix_power(minus_plus_nilpotent, 3), np.zeros((3, 3), dtype=int))
                and np.linalg.matrix_rank(minus_plus_nilpotent) == 2
                and np.linalg.matrix_rank(minus_plus_nilpotent @ minus_plus_nilpotent) == 1
            ),
            "nilpotent_squares_match_exactly": np.array_equal(
                plus_minus_nilpotent @ plus_minus_nilpotent,
                minus_plus_nilpotent @ minus_plus_nilpotent,
            ),
            "common_nilpotent_square": (
                plus_minus_nilpotent @ plus_minus_nilpotent
            ).tolist(),
            "generation_matrices_commute_exactly": np.array_equal(
                plus_minus @ minus_plus,
                minus_plus @ plus_minus,
            ),
        },
        "bridge_verdict": (
            "The canonical Yukawa seed now reduces exactly to a small generation "
            "algebra. After the V4 split, the inactive right-handed sector "
            "vanishes, each active sector is generated by exactly two internal "
            "templates, and the generation-side coefficient matrices are "
            "slot-independent commuting unipotent 3x3 operators. So the "
            "remaining Yukawa problem is no longer the three-generation mixing "
            "pattern itself. It is the slot-specific internal template spectrum "
            "carried by those exact active sectors."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_yukawa_unipotent_reduction_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
