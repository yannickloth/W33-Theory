"""Isotropic-line obstruction inside the canonical external carrier ``U1``.

The current K3/Yukawa bridge already isolates ``U1`` as the minimal canonical
external carrier of the first family-sensitive ``A4`` packet. A sharper
question is whether the current external data already pick a distinguished line
inside that hyperbolic plane, so that the internal family line
``span(1,1,0)`` could be identified externally.

They do not. The canonical primitive plane basis itself already exhibits two
primitive isotropic line generators, and the exact seed/refined coefficient
data are invariant under swapping them. So the current ``U1`` package is still
line-blind: it fixes the oriented hyperbolic carrier, not a distinguished
internal family line inside that carrier.
"""

from __future__ import annotations

from functools import lru_cache
import json
from math import gcd
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

from w33_k3_integral_h2_lattice_bridge import (
    integral_k3_h2_basis_matrix,
    integral_k3_h2_intersection_matrix,
    primitive_hyperbolic_plane_coefficients,
)
from w33_k3_primitive_plane_global_a4_bridge import (
    build_k3_primitive_plane_global_a4_bridge_summary,
)
from w33_k3_refined_plane_persistence_bridge import restricted_first_barycentric_pullback_form
from w33_yukawa_generation_flag_bridge import build_yukawa_generation_flag_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_u1_isotropic_line_obstruction_bridge_summary.json"


def _vector_gcd(vector: np.ndarray) -> int:
    entries = [abs(int(value)) for value in vector.tolist() if int(value) != 0]
    return 0 if not entries else gcd(*entries)


@lru_cache(maxsize=1)
def build_u1_isotropic_line_obstruction_bridge_summary() -> dict[str, Any]:
    ambient_form = integral_k3_h2_intersection_matrix().astype(int)
    plane = primitive_hyperbolic_plane_coefficients().astype(int)
    line_one = plane[:, 0]
    line_two = plane[:, 1]
    swapped_plane = plane[:, [1, 0]]

    seed_form = (plane.T @ ambient_form @ plane).astype(int)
    swapped_seed_form = (swapped_plane.T @ ambient_form @ swapped_plane).astype(int)
    cochains = integral_k3_h2_basis_matrix().astype(float)
    refined_form = np.rint(restricted_first_barycentric_pullback_form(cochains @ plane)).astype(int)
    swapped_refined_form = np.rint(
        restricted_first_barycentric_pullback_form(cochains @ swapped_plane)
    ).astype(int)

    global_a4 = build_k3_primitive_plane_global_a4_bridge_summary()
    flag = build_yukawa_generation_flag_summary()

    return {
        "status": "ok",
        "u1_basis_coefficients": plane.tolist(),
        "u1_line_one_coefficients": line_one.astype(int).tolist(),
        "u1_line_two_coefficients": line_two.astype(int).tolist(),
        "u1_seed_form": seed_form.tolist(),
        "u1_swapped_seed_form": swapped_seed_form.tolist(),
        "u1_first_refinement_form": refined_form.tolist(),
        "u1_swapped_first_refinement_form": swapped_refined_form.tolist(),
        "internal_common_line_generator": flag["common_flag"]["line_generator"],
        "u1_isotropic_line_obstruction_theorem": {
            "line_one_is_primitive": _vector_gcd(line_one) == 1,
            "line_two_is_primitive": _vector_gcd(line_two) == 1,
            "line_one_is_isotropic": int(line_one @ ambient_form @ line_one) == 0,
            "line_two_is_isotropic": int(line_two @ ambient_form @ line_two) == 0,
            "line_pair_has_unit_hyperbolic_pairing": int(line_one @ ambient_form @ line_two) == 1,
            "swapping_the_two_isotropic_lines_preserves_the_u1_seed_form": np.array_equal(
                seed_form,
                swapped_seed_form,
            ),
            "swapping_the_two_isotropic_lines_preserves_the_first_refinement_form": (
                np.array_equal(refined_form, swapped_refined_form)
                and global_a4["primitive_plane_first_refinement_form"] == refined_form.tolist()
            ),
            "swapping_the_two_isotropic_lines_preserves_the_reduced_global_prefactor": (
                global_a4["reduced_prefactors"]["normalized_global"] == "351/(4 pi^2)"
            ),
            "current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other": (
                np.array_equal(seed_form, swapped_seed_form)
                and np.array_equal(refined_form, swapped_refined_form)
                and line_one.tolist() != line_two.tolist()
            ),
            "exact_identification_of_the_internal_common_line_with_a_canonical_u1_line_is_not_yet_supported": (
                np.array_equal(seed_form, swapped_seed_form)
                and flag["common_flag"]["line_generator"] == [1, 1, 0]
            ),
        },
        "bridge_verdict": (
            "The current exact external carrier theorem stops at the hyperbolic "
            "plane U1. In the canonical integral basis, U1 already has two "
            "primitive isotropic line generators with unit pairing, but the "
            "seed cup form, the first-refinement cup form, and the reduced "
            "global prefactor are invariant under swapping them. So the present "
            "K3-side data are line-blind inside U1: they do not yet canonically "
            "pick the internal family line span(1,1,0)."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_u1_isotropic_line_obstruction_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
