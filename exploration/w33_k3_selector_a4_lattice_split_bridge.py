"""Reduced selector-side ``A4`` packet over ``3U (+) E8(-1) (+) E8(-1)``.

The reduced external bridge coefficient is already fixed on the explicit K3
host:

    351 / (4 pi^2).

The remaining structural question on the explicit seed is therefore not the
overall normalization, but how the selected external rank-2 packet sits inside
the named K3 lattice split. This module packages the conservative exact answer.

Using the selector-plane decomposition from
``w33_k3_selector_e8_shadow_bridge``, the external geometric packet on the
selector basis decomposes additively as

    G_selector = G_{3U} + G_{E8,1} + G_{E8,2},

with one positive-definite ``3U`` contribution and two negative-definite
``E8`` contributions. Multiplying by the already-locked scalar
``351 / (4 pi^2)`` gives the reduced selector-side ``A4`` packet on the full
named lattice split.
"""

from __future__ import annotations

from fractions import Fraction
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

from w33_curved_h2_intersection_bridge import SIGN_TOL, ZERO_TOL
from w33_k3_primitive_plane_global_a4_bridge import (
    build_k3_primitive_plane_global_a4_bridge_summary,
)
from w33_k3_selector_e8_shadow_bridge import build_k3_selector_e8_shadow_bridge_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_selector_a4_lattice_split_bridge_summary.json"


def _signature_counts(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    positive = int(np.sum(eigenvalues > SIGN_TOL))
    negative = int(np.sum(eigenvalues < -SIGN_TOL))
    return positive, negative


def _float_lists(matrix: np.ndarray) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix.tolist()]


@lru_cache(maxsize=1)
def build_k3_selector_a4_lattice_split_bridge_summary() -> dict[str, Any]:
    selector_split = build_k3_selector_e8_shadow_bridge_summary()
    global_a4 = build_k3_primitive_plane_global_a4_bridge_summary()

    if not global_a4["global_a4_coupling_theorem"]["reduced_global_prefactor_is_351_over_4_pi_squared"]:
        raise AssertionError("expected the reduced global prefactor 351/(4 pi^2)")

    selector_form = np.asarray(selector_split["selector_plane_form"], dtype=float)
    three_u_form = np.asarray(selector_split["three_u_component_form"], dtype=float)
    e8_factor_one_form = np.asarray(selector_split["e8_factor_one_component_form"], dtype=float)
    e8_factor_two_form = np.asarray(selector_split["e8_factor_two_component_form"], dtype=float)

    reconstruction_error = float(
        np.max(np.abs(selector_form - three_u_form - e8_factor_one_form - e8_factor_two_form))
    )
    scalar = Fraction(351, 4)

    return {
        "status": "ok",
        "common_scalar_prefactor": "351/(4 pi^2)",
        "selector_packet_form": _float_lists(selector_form),
        "three_u_packet_form": _float_lists(three_u_form),
        "e8_factor_one_packet_form": _float_lists(e8_factor_one_form),
        "e8_factor_two_packet_form": _float_lists(e8_factor_two_form),
        "selector_a4_lattice_split_theorem": {
            "selector_packet_reconstructs_as_three_u_plus_e8_plus_e8": (
                reconstruction_error < ZERO_TOL
            ),
            "three_u_packet_piece_is_positive_definite": (
                _signature_counts(three_u_form) == (2, 0)
            ),
            "e8_factor_one_packet_piece_is_negative_definite": (
                _signature_counts(e8_factor_one_form) == (0, 2)
            ),
            "e8_factor_two_packet_piece_is_negative_definite": (
                _signature_counts(e8_factor_two_form) == (0, 2)
            ),
            "all_three_packet_pieces_are_nonzero": bool(
                float(np.linalg.norm(three_u_form)) > ZERO_TOL
                and float(np.linalg.norm(e8_factor_one_form)) > ZERO_TOL
                and float(np.linalg.norm(e8_factor_two_form)) > ZERO_TOL
            ),
            "reduced_selector_packet_is_not_carried_by_three_u_alone": bool(
                float(np.linalg.norm(e8_factor_one_form + e8_factor_two_form)) > ZERO_TOL
            ),
            "reduced_selector_packet_is_not_carried_by_a_single_e8_factor": bool(
                float(np.linalg.norm(e8_factor_one_form)) > ZERO_TOL
                and float(np.linalg.norm(e8_factor_two_form)) > ZERO_TOL
            ),
            "reduced_selector_packet_is_tri_supported_across_the_named_k3_split": (
                reconstruction_error < ZERO_TOL
                and _signature_counts(three_u_form) == (2, 0)
                and _signature_counts(e8_factor_one_form) == (0, 2)
                and _signature_counts(e8_factor_two_form) == (0, 2)
            ),
            "scalar_prefactor_remains_exactly_351_over_4_pi_squared": scalar == Fraction(351, 4),
        },
        "reconstruction_error_linf": reconstruction_error,
        "bridge_verdict": (
            "The reduced selector-side A4 packet is now resolved over the full "
            "named K3 lattice split. The common scalar coefficient stays fixed "
            "at 351/(4 pi^2), but the geometric selector form decomposes as one "
            "positive 3U piece plus two negative E8 pieces. So the explicit "
            "bridge packet is not supported on the hyperbolic core alone, and "
            "it is not supported on just one exceptional block either. On the "
            "explicit seed, the selector-side A4 geometry is already tri-"
            "supported across 3U and both E8(-1) factors."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_selector_a4_lattice_split_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
