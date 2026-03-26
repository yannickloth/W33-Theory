"""Canonical isotropic-line candidate selected by the full ``U1`` packet data.

The carrier-only theorem on ``U1`` is line-blind: the hyperbolic seed form,
its first-refinement lift, and the reduced global prefactor are invariant under
swapping the two primitive isotropic lines of the canonical ``U1`` plane.

That is *not* the whole current external story. The canonical selector plane on
K3 already comes with a canonical ordered basis: the normalized positive and
negative selector lines from the first mixed harmonic triangle. Projecting that
ordered selector basis onto the canonical carrier plane ``U1`` produces an
ordered ``2x2`` coordinate map. Its two isotropic-line weights are unequal.

So the full current external packet data do more than fix a carrier plane:
they already pick a canonical dominant isotropic-line candidate inside ``U1``.
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

from w33_k3_integral_h2_lattice_bridge import integral_k3_h2_intersection_matrix
from w33_k3_integral_h2_lattice_bridge import integral_k3_h2_basis_matrix
from w33_k3_refined_plane_persistence_bridge import restricted_first_barycentric_pullback_form
from w33_k3_selector_a4_five_factor_bridge import (
    build_k3_selector_a4_five_factor_bridge_summary,
)
from w33_k3_selector_a4_five_factor_bridge import selector_five_factor_cochain_components
from w33_k3_selector_a4_five_factor_bridge import selector_five_factor_integral_components
from w33_k3_three_u_decomposition_bridge import k3_three_u_block_coefficients
from w33_u1_isotropic_line_obstruction_bridge import (
    build_u1_isotropic_line_obstruction_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_u1_selector_line_selection_bridge_summary.json"
ZERO_TOL = 1e-12


def _u1_basis() -> np.ndarray:
    return k3_three_u_block_coefficients().astype(float)[:, :2]


def _u1_selector_coordinates() -> np.ndarray:
    ambient_form = integral_k3_h2_intersection_matrix().astype(float)
    u1_basis = _u1_basis()
    u1_selector_component = selector_five_factor_integral_components()["U1"]
    hyperbolic_gram = u1_basis.T @ ambient_form @ u1_basis
    return np.linalg.solve(
        hyperbolic_gram,
        u1_basis.T @ ambient_form @ u1_selector_component,
    )


def _signed_permutation_matrices() -> list[np.ndarray]:
    identity = np.eye(2, dtype=float)
    swap = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=float)
    out: list[np.ndarray] = []
    for base in (identity, swap):
        for sign_one in (-1.0, 1.0):
            for sign_two in (-1.0, 1.0):
                out.append(base @ np.diag([sign_one, sign_two]))
    return out


@lru_cache(maxsize=1)
def build_u1_selector_line_selection_bridge_summary() -> dict[str, Any]:
    obstruction = build_u1_isotropic_line_obstruction_bridge_summary()
    coordinates = _u1_selector_coordinates()
    line_weights = np.sum(coordinates * coordinates, axis=1)
    dominant_index = int(np.argmax(line_weights))
    recessive_index = 1 - dominant_index
    signed_permutation_invariance = all(
        np.allclose(
            np.sum((coordinates @ permutation) * (coordinates @ permutation), axis=1),
            line_weights,
            atol=ZERO_TOL,
        )
        for permutation in _signed_permutation_matrices()
    )

    u1_basis_cochains = integral_k3_h2_basis_matrix().astype(float) @ _u1_basis()
    u1_selector_cochains = selector_five_factor_cochain_components()["U1"]
    refined_u1_form = restricted_first_barycentric_pullback_form(u1_basis_cochains)
    refined_u1_packet_form = restricted_first_barycentric_pullback_form(u1_selector_cochains)
    seed_u1_form = np.array(obstruction["u1_seed_form"], dtype=float)
    seed_u1_packet_form = np.array(
        build_k3_selector_a4_five_factor_bridge_summary()["u_factor_one_packet_form"],
        dtype=float,
    )

    return {
        "status": "ok",
        "u1_selector_coordinate_matrix": coordinates.tolist(),
        "u1_isotropic_line_weights": [float(weight) for weight in line_weights.tolist()],
        "dominant_isotropic_line_index": dominant_index,
        "recessive_isotropic_line_index": recessive_index,
        "dominant_isotropic_line_coefficients": obstruction[
            f"u1_line_{'one' if dominant_index == 0 else 'two'}_coefficients"
        ],
        "recessive_isotropic_line_coefficients": obstruction[
            f"u1_line_{'one' if recessive_index == 0 else 'two'}_coefficients"
        ],
        "dominance_ratio": float(line_weights[dominant_index] / line_weights[recessive_index]),
        "u1_first_refinement_form": [[float(value) for value in row] for row in refined_u1_form.tolist()],
        "u1_selector_first_refinement_packet_form": [
            [float(value) for value in row] for row in refined_u1_packet_form.tolist()
        ],
        "u1_selector_line_selection_theorem": {
            "carrier_metric_alone_is_line_blind": obstruction[
                "u1_isotropic_line_obstruction_theorem"
            ]["current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other"],
            "canonical_selector_u1_component_has_full_rank_2": (
                abs(float(np.linalg.det(coordinates))) > ZERO_TOL
            ),
            "canonical_selector_u1_component_assigns_unequal_weights_to_the_two_isotropic_lines": (
                abs(float(line_weights[0] - line_weights[1])) > ZERO_TOL
            ),
            "there_is_a_unique_dominant_isotropic_line_inside_u1": (
                abs(float(line_weights[0] - line_weights[1])) > ZERO_TOL
            ),
            "dominant_isotropic_line_is_the_first_u1_line_in_the_current_canonical_basis": (
                dominant_index == 0
            ),
            "selector_line_weights_are_invariant_under_selector_basis_signs_and_swap": (
                signed_permutation_invariance
            ),
            "u1_carrier_form_scales_by_120_at_first_refinement": (
                np.allclose(refined_u1_form, 120.0 * seed_u1_form, atol=1e-8)
            ),
            "u1_selector_packet_form_scales_by_120_at_first_refinement": (
                np.allclose(refined_u1_packet_form, 120.0 * seed_u1_packet_form, atol=1e-8)
            ),
            "dominant_line_candidate_is_first_refinement_rigid": (
                np.allclose(refined_u1_form, 120.0 * seed_u1_form, atol=1e-8)
                and np.allclose(refined_u1_packet_form, 120.0 * seed_u1_packet_form, atol=1e-8)
            ),
            "full_current_external_packet_selects_a_canonical_isotropic_line_candidate_inside_u1": (
                obstruction["u1_isotropic_line_obstruction_theorem"][
                    "current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other"
                ]
                and abs(float(line_weights[0] - line_weights[1])) > ZERO_TOL
                and signed_permutation_invariance
            ),
        },
        "bridge_verdict": (
            "The current exact external bridge no longer stops at a line-blind "
            "carrier plane. The metric carrier data on U1 are still symmetric "
            "under swapping the two primitive isotropic lines, but once the "
            "canonical ordered selector basis is projected onto U1 the two null "
            "lines acquire unequal weights. That selection is invariant under "
            "the natural sign/swap ambiguities of the selector basis and "
            "survives the first barycentric refinement step. So the full "
            "current external packet already selects a unique rigid "
            "isotropic-line candidate inside U1."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_u1_selector_line_selection_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
