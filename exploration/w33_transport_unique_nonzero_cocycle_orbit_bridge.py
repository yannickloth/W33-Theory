"""Unique nonzero ternary transport cocycle orbit up to the natural gauge.

The remaining transport wall has already been reduced to realization of the
nontrivial ternary cocycle class on the external side. Over ``F3`` that can be
sharpened one step further.

The internal fiber shift is

    N = [[0,1],[0,0]]

and the only nonzero scalar multiples are ``N`` and ``2N``. Those are not
different gauge orbits: they are conjugate by the diagonal basis change
``diag(1,2)`` on the adapted transport fiber. So up to the natural head/tail
basis gauge there is only one nonzero ternary glue orbit.

Therefore the remaining wall is not selection among several nonzero ternary
cocycle types. It is existence of the unique nonzero ternary cocycle orbit on
the external side.
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

from w33_transport_internal_operator_normal_form_match_bridge import (
    build_transport_internal_operator_normal_form_match_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_transport_unique_nonzero_cocycle_orbit_bridge_summary.json"
)
MODULUS = 3


def _transport_cocycle_summary() -> dict[str, Any]:
    try:
        from w33_transport_ternary_cocycle_bridge import (
            build_transport_ternary_cocycle_summary,
        )
    except ModuleNotFoundError as exc:
        if exc.name != "networkx":
            raise
        fallback_path = ROOT / "data" / "w33_transport_ternary_cocycle_bridge_summary.json"
        return json.loads(fallback_path.read_text(encoding="utf-8"))
    return build_transport_ternary_cocycle_summary()


def _conjugate(matrix: np.ndarray, basis_change: np.ndarray) -> np.ndarray:
    determinant = int(round(float(np.linalg.det(basis_change)))) % MODULUS
    if determinant == 0:
        raise AssertionError("expected invertible basis change")
    inverse = np.array(
        [
            [basis_change[1, 1], -basis_change[0, 1]],
            [-basis_change[1, 0], basis_change[0, 0]],
        ],
        dtype=int,
    )
    inverse = (pow(determinant, -1, MODULUS) * inverse) % MODULUS
    return (inverse @ matrix @ basis_change) % MODULUS


@lru_cache(maxsize=1)
def build_transport_unique_nonzero_cocycle_orbit_bridge_summary() -> dict[str, Any]:
    cocycle = _transport_cocycle_summary()
    operator_match = build_transport_internal_operator_normal_form_match_bridge_summary()

    shift = np.array(cocycle["fiber_nilpotent_operator"]["matrix"], dtype=int) % MODULUS
    scaled_shift = (2 * shift) % MODULUS
    basis_change = np.array([[1, 0], [0, 2]], dtype=int)
    conjugated = _conjugate(shift, basis_change)

    nonzero_orbit = {
        tuple(tuple(int(entry) for entry in row) for row in shift.tolist()),
        tuple(tuple(int(entry) for entry in row) for row in scaled_shift.tolist()),
    }

    return {
        "status": "ok",
        "ternary_fiber_shift_orbit": {
            "field": "F3",
            "base_shift": shift.tolist(),
            "other_nonzero_scalar_multiple": scaled_shift.tolist(),
            "conjugating_basis_change": basis_change.tolist(),
            "conjugated_shift": conjugated.tolist(),
            "nonzero_scalar_orbit_size": len(nonzero_orbit),
        },
        "transport_unique_nonzero_cocycle_orbit_theorem": {
            "the_internal_transport_cocycle_is_nontrivial": (
                cocycle["extension_cocycle"]["cocycle_is_not_a_coboundary"] is True
            ),
            "the_only_nonzero_scalar_multiples_of_the_fiber_shift_over_f3_are_n_and_2n": (
                shift.tolist() == [[0, 1], [0, 0]]
                and scaled_shift.tolist() == [[0, 2], [0, 0]]
                and len(nonzero_orbit) == 2
            ),
            "the_two_nonzero_scalar_multiples_are_gauge_equivalent_by_adapted_diagonal_basis_change": (
                conjugated.tolist() == scaled_shift.tolist()
            ),
            "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit": (
                conjugated.tolist() == scaled_shift.tolist()
                and operator_match[
                    "transport_internal_operator_normal_form_match_theorem"
                ][
                    "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge"
                ]
            ),
            "the_remaining_external_wall_is_existence_of_that_unique_nonzero_orbit_not_selection_among_several_nonzero_types": (
                cocycle["extension_cocycle"]["cocycle_is_not_a_coboundary"] is True
                and conjugated.tolist() == scaled_shift.tolist()
            ),
        },
        "bridge_verdict": (
            "Over F3 the internal transport cocycle has only one nonzero gauge "
            "orbit. The two nonzero scalar multiples of the fiber shift, N and "
            "2N, are conjugate by the natural adapted diagonal basis change. "
            "So the remaining external wall is existence of that unique "
            "nonzero ternary cocycle orbit, not selection among several "
            "different nonzero ternary types."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_unique_nonzero_cocycle_orbit_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
