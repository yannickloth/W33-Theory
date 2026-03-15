"""Exact Kronecker reduction of the canonical Yukawa sectors.

This module upgrades the Yukawa unipotent reduction bridge from a block-span
statement to an operator theorem.

After compressing the canonical 24x24 mixed seed to each active V4 sector, the
result is exactly of the form

    M_sector = I_3 ⊗ T0 + C_sector ⊗ T1,

where:

  - T0 and T1 are two slot/sector-specific internal templates;
  - C_sector is one of two universal 3x3 generation matrices;
  - the two generation matrices are conjugate over GL(3,Z), both unipotent of
    Jordan type (lambda - 1)^3.

Consequently the full singular-value problem reduces exactly to a structured
Gram problem

    M^* M
      = I ⊗ (T0^* T0)
        + C ⊗ (T0^* T1)
        + C^T ⊗ (T1^* T0)
        + C^T C ⊗ (T1^* T1),

so the remaining Yukawa frontier is not the full mixed seed. It is the small
internal template Gram data carried by the active sectors.
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

from w33_l6_delta27_texture_bridge import _canonical_closure_seed
from w33_l6_v4_projector_bridge import _projector_profiles
from w33_fermionic_connes_sector import right_spinor_basis


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_yukawa_kronecker_reduction_bridge_summary.json"
FLOAT_TOL = 1e-12

PLUS_MINUS_MATRIX = np.array(
    [[0, 1, 1], [-1, 2, 1], [1, -1, 1]],
    dtype=float,
)
MINUS_PLUS_MATRIX = np.array(
    [[0, 1, -1], [-1, 2, -1], [-1, 1, 1]],
    dtype=float,
)
CONJUGATING_MATRIX = np.array(
    [[-2, 1, 0], [-1, 0, 0], [0, 0, 1]],
    dtype=float,
)
SECTOR_GENERATION_MATRIX = {
    "+-": PLUS_MINUS_MATRIX,
    "-+": MINUS_PLUS_MATRIX,
}


def _label_to_index() -> dict[str, int]:
    return {state.slot: index for index, state in enumerate(right_spinor_basis())}


def _compressed_sector_matrix(external_slot: str, sector: str) -> tuple[np.ndarray, list[str], int]:
    matrix = _canonical_closure_seed(external_slot)
    support_labels = _projector_profiles(external_slot)["projectors"][sector]["support_labels"]
    label_to_index = _label_to_index()
    local_indices = [label_to_index[label] for label in support_labels]
    columns = [8 * generation + local_index for generation in range(3) for local_index in local_indices]
    return matrix[:, columns], support_labels, len(local_indices)


def _sector_templates(external_slot: str, sector: str) -> tuple[np.ndarray, np.ndarray]:
    compressed, _, width = _compressed_sector_matrix(external_slot, sector)
    template0 = compressed[0:8, 0:width]
    template1 = compressed[0:8, width : 2 * width]
    return template0, template1


def _kronecker_reconstruction(external_slot: str, sector: str) -> dict[str, Any]:
    compressed, support_labels, width = _compressed_sector_matrix(external_slot, sector)
    template0, template1 = _sector_templates(external_slot, sector)
    generation_matrix = SECTOR_GENERATION_MATRIX[sector]

    reconstructed = np.kron(np.eye(3), template0) + np.kron(generation_matrix, template1)
    gram_direct = compressed.T @ compressed
    gram_reduced = (
        np.kron(np.eye(3), template0.T @ template0)
        + np.kron(generation_matrix, template0.T @ template1)
        + np.kron(generation_matrix.T, template1.T @ template0)
        + np.kron(generation_matrix.T @ generation_matrix, template1.T @ template1)
    )

    singular_values = np.linalg.svd(compressed, compute_uv=False)
    reduced_gram_eigs = np.linalg.eigvalsh(gram_reduced)

    return {
        "support_labels": support_labels,
        "sector_width": width,
        "compressed_rank": int(np.linalg.matrix_rank(compressed)),
        "template0_rank": int(np.linalg.matrix_rank(template0)),
        "template1_rank": int(np.linalg.matrix_rank(template1)),
        "exact_kronecker_reconstruction": bool(np.allclose(compressed, reconstructed, atol=FLOAT_TOL)),
        "max_abs_kronecker_reconstruction_error": float(np.max(np.abs(compressed - reconstructed))),
        "exact_reduced_gram_formula": bool(np.allclose(gram_direct, gram_reduced, atol=FLOAT_TOL)),
        "max_abs_reduced_gram_error": float(np.max(np.abs(gram_direct - gram_reduced))),
        "singular_spectrum_matches_reduced_gram_exactly": bool(
            np.allclose(
                np.sort(singular_values * singular_values),
                np.sort(reduced_gram_eigs),
                atol=FLOAT_TOL,
            )
        ),
        "nonzero_singular_values": [
            float(value) for value in singular_values if value > FLOAT_TOL
        ],
    }


def _charpoly_string(matrix: np.ndarray) -> str:
    symbol = sp.symbols("lambda")
    integer_matrix = sp.Matrix([[int(round(value)) for value in row] for row in matrix.tolist()])
    return str(sp.factor(integer_matrix.charpoly(symbol).as_expr()))


@lru_cache(maxsize=1)
def build_yukawa_kronecker_reduction_summary() -> dict[str, Any]:
    slot_profiles = {
        external_slot: {
            sector: _kronecker_reconstruction(external_slot, sector)
            for sector in ("+-", "-+")
        }
        for external_slot in ("H_2", "Hbar_2")
    }

    conjugacy_residual = CONJUGATING_MATRIX @ PLUS_MINUS_MATRIX - MINUS_PLUS_MATRIX @ CONJUGATING_MATRIX
    jordan_form = [[1, 1, 0], [0, 1, 1], [0, 0, 1]]

    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "generation_algebra": {
            "plus_minus_matrix": PLUS_MINUS_MATRIX.astype(int).tolist(),
            "minus_plus_matrix": MINUS_PLUS_MATRIX.astype(int).tolist(),
            "conjugating_matrix": CONJUGATING_MATRIX.astype(int).tolist(),
            "conjugating_matrix_determinant": int(round(np.linalg.det(CONJUGATING_MATRIX))),
            "exact_integer_conjugacy_between_generation_matrices": bool(
                np.allclose(conjugacy_residual, np.zeros((3, 3)), atol=FLOAT_TOL)
            ),
            "plus_minus_charpoly": _charpoly_string(PLUS_MINUS_MATRIX),
            "minus_plus_charpoly": _charpoly_string(MINUS_PLUS_MATRIX),
            "common_jordan_form": jordan_form,
        },
        "kronecker_reduction_theorem": {
            "all_active_sectors_have_exact_kronecker_form": all(
                slot_profiles[slot][sector]["exact_kronecker_reconstruction"]
                for slot in ("H_2", "Hbar_2")
                for sector in ("+-", "-+")
            ),
            "all_active_sectors_have_exact_reduced_gram_formula": all(
                slot_profiles[slot][sector]["exact_reduced_gram_formula"]
                for slot in ("H_2", "Hbar_2")
                for sector in ("+-", "-+")
            ),
            "all_active_sector_singular_spectra_match_reduced_gram_exactly": all(
                slot_profiles[slot][sector]["singular_spectrum_matches_reduced_gram_exactly"]
                for slot in ("H_2", "Hbar_2")
                for sector in ("+-", "-+")
            ),
            "template_ranks_match_active_sector_widths": all(
                slot_profiles[slot][sector]["template0_rank"] == slot_profiles[slot][sector]["sector_width"]
                and slot_profiles[slot][sector]["template1_rank"] == slot_profiles[slot][sector]["sector_width"]
                for slot in ("H_2", "Hbar_2")
                for sector in ("+-", "-+")
            ),
        },
        "bridge_verdict": (
            "The canonical Yukawa seed now has an exact operator reduction. "
            "Each active V4 sector is exactly of the form I⊗T0 + C⊗T1, with one "
            "universal generation matrix C and two internal templates. The two "
            "generation matrices are conjugate integer unipotent operators of "
            "the same Jordan type, and the full singular spectrum reduces "
            "exactly to a structured Gram built from T0, T1, C, and C^T C. So "
            "the remaining Yukawa problem has collapsed to the small internal "
            "template Gram data, not the full mixed-seed geometry."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_yukawa_kronecker_reduction_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
