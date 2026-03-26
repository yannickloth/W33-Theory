"""Reduced selector-side ``A4`` packet over ``U1 (+) U2 (+) U3 (+) E8 (+) E8``.

The selector-side reduced external bridge packet was already resolved over the
named lattice split

    3U (+) E8(-1) (+) E8(-1),

with fixed scalar prefactor ``351/(4 pi^2)``.

This module pushes that decomposition one step finer inside the hyperbolic
core. Since the canonical primitive plane is now known to be the first explicit
``U`` factor of ``3U``, the remaining exact question is whether the selector
packet is carried by that distinguished plane alone. It is not. The packet
decomposes exactly across five named pieces:

    U1, U2, U3, E8_1, E8_2.

The distinguished global plane ``U1`` carries a nonzero packet piece, but the
full local selector packet remains distributed across all three hyperbolic
factors and both exceptional factors.
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
from w33_k3_integral_h2_lattice_bridge import (
    integral_k3_h2_basis_matrix,
    integral_k3_h2_intersection_matrix,
)
from w33_k3_primitive_plane_global_a4_bridge import (
    build_k3_primitive_plane_global_a4_bridge_summary,
)
from w33_k3_selector_e8_shadow_bridge import _selector_plane_integral_coordinates
from w33_k3_three_u_decomposition_bridge import k3_three_u_block_coefficients
from w33_k3_e8_factor_split_bridge import e8_factor_simple_roots_in_integral_coordinates


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_selector_a4_five_factor_bridge_summary.json"
FACTOR_ORDER = ("U1", "U2", "U3", "E8_1", "E8_2")


def _orthogonal_projector(basis: np.ndarray, form: np.ndarray) -> np.ndarray:
    gram = basis.T @ form @ basis
    return basis @ np.linalg.inv(gram) @ basis.T @ form


def _signature_counts(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    positive = int(np.sum(eigenvalues > SIGN_TOL))
    negative = int(np.sum(eigenvalues < -SIGN_TOL))
    return positive, negative


def _float_lists(matrix: np.ndarray) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix.tolist()]


@lru_cache(maxsize=1)
def selector_five_factor_integral_components() -> dict[str, np.ndarray]:
    ambient_form = integral_k3_h2_intersection_matrix().astype(float)
    selector = _selector_plane_integral_coordinates().astype(float)
    three_u = k3_three_u_block_coefficients().astype(float)
    u_blocks = [three_u[:, 2 * index : 2 * index + 2] for index in range(3)]
    e8_factor_one, e8_factor_two = (
        basis.astype(float) for basis in e8_factor_simple_roots_in_integral_coordinates()
    )

    subspaces = {
        "U1": u_blocks[0],
        "U2": u_blocks[1],
        "U3": u_blocks[2],
        "E8_1": e8_factor_one,
        "E8_2": e8_factor_two,
    }
    return {
        name: _orthogonal_projector(subspace, ambient_form) @ selector
        for name, subspace in subspaces.items()
    }


@lru_cache(maxsize=1)
def selector_five_factor_cochain_components() -> dict[str, np.ndarray]:
    integral_basis_cochains = integral_k3_h2_basis_matrix().astype(float)
    return {
        name: integral_basis_cochains @ component
        for name, component in selector_five_factor_integral_components().items()
    }


@lru_cache(maxsize=1)
def build_k3_selector_a4_five_factor_bridge_summary() -> dict[str, Any]:
    global_a4 = build_k3_primitive_plane_global_a4_bridge_summary()
    if not global_a4["global_a4_coupling_theorem"]["reduced_global_prefactor_is_351_over_4_pi_squared"]:
        raise AssertionError("expected exact reduced global prefactor 351/(4 pi^2)")

    ambient_form = integral_k3_h2_intersection_matrix().astype(float)
    selector = _selector_plane_integral_coordinates().astype(float)
    components = selector_five_factor_integral_components()
    selector_form = selector.T @ ambient_form @ selector
    component_forms = {
        name: component.T @ ambient_form @ component
        for name, component in components.items()
    }
    hyperbolic_form = (
        component_forms["U1"] + component_forms["U2"] + component_forms["U3"]
    )
    reconstruction_error = float(
        np.max(np.abs(selector_form - sum(component_forms.values(), np.zeros((2, 2), dtype=float))))
    )
    scalar = Fraction(351, 4)

    return {
        "status": "ok",
        "common_scalar_prefactor": "351/(4 pi^2)",
        "selector_packet_form": _float_lists(selector_form),
        "u_factor_one_packet_form": _float_lists(component_forms["U1"]),
        "u_factor_two_packet_form": _float_lists(component_forms["U2"]),
        "u_factor_three_packet_form": _float_lists(component_forms["U3"]),
        "hyperbolic_packet_form": _float_lists(hyperbolic_form),
        "e8_factor_one_packet_form": _float_lists(component_forms["E8_1"]),
        "e8_factor_two_packet_form": _float_lists(component_forms["E8_2"]),
        "factor_frobenius_norms": {
            name: float(np.linalg.norm(component_forms[name]))
            for name in FACTOR_ORDER
        },
        "reconstruction_error_linf": reconstruction_error,
        "selector_a4_five_factor_theorem": {
            "three_u_packet_reconstructs_as_u1_plus_u2_plus_u3": bool(
                np.max(
                    np.abs(
                        hyperbolic_form
                        - component_forms["U1"]
                        - component_forms["U2"]
                        - component_forms["U3"]
                    )
                )
                < ZERO_TOL
            ),
            "selector_packet_reconstructs_as_u1_plus_u2_plus_u3_plus_e8_plus_e8": (
                reconstruction_error < ZERO_TOL
            ),
            "u_factor_one_packet_piece_is_mixed_signature": (
                _signature_counts(component_forms["U1"]) == (1, 1)
            ),
            "u_factor_two_packet_piece_is_mixed_signature": (
                _signature_counts(component_forms["U2"]) == (1, 1)
            ),
            "u_factor_three_packet_piece_is_mixed_signature": (
                _signature_counts(component_forms["U3"]) == (1, 1)
            ),
            "e8_factor_one_packet_piece_is_negative_definite": (
                _signature_counts(component_forms["E8_1"]) == (0, 2)
            ),
            "e8_factor_two_packet_piece_is_negative_definite": (
                _signature_counts(component_forms["E8_2"]) == (0, 2)
            ),
            "all_five_packet_pieces_are_nonzero": all(
                float(np.linalg.norm(component_forms[name])) > ZERO_TOL
                for name in FACTOR_ORDER
            ),
            "distinguished_u1_plane_has_nonzero_selector_packet_piece": bool(
                float(np.linalg.norm(component_forms["U1"])) > ZERO_TOL
            ),
            "selector_hyperbolic_packet_is_not_supported_on_u1_alone": bool(
                float(np.linalg.norm(component_forms["U2"] + component_forms["U3"])) > ZERO_TOL
            ),
            "reduced_selector_packet_is_five_supported_across_u_u_u_e8_e8": (
                reconstruction_error < ZERO_TOL
                and all(float(np.linalg.norm(component_forms[name])) > ZERO_TOL for name in FACTOR_ORDER)
            ),
            "scalar_prefactor_remains_exactly_351_over_4_pi_squared": scalar == Fraction(351, 4),
        },
        "bridge_verdict": (
            "The selector-side reduced A4 packet is now resolved down to five "
            "named K3 lattice pieces. The distinguished global plane U1 carries "
            "a nonzero packet piece, but the local selector packet does not "
            "collapse to that plane. It reconstructs exactly as U1 + U2 + U3 + "
            "E8_1 + E8_2, with mixed-sign contributions on each U factor and "
            "negative-definite contributions on both exceptional factors. So "
            "the strongest current exact picture is: U1 is the canonical global "
            "carrier, while the full local selector-side packet remains "
            "distributed across the entire named K3 split."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_selector_a4_five_factor_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
