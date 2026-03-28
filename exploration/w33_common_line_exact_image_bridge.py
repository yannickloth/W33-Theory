"""Exact image-line theorem for the internal common line in any exact completion.

The current split bridge object still does not literally realize the internal
line ``span(1,1,0)`` as an external image line, because it has zero glue. But
after the transport reductions now on the repo, the exact-completion image is
no longer ambiguous.

Internally:
- the common line is exactly the image of the common square ``2E13``;
- the transport operator has model ``I_81 ⊗ [[0,1],[0,0]]``, so its image is
  the head/invariant line.

Externally:
- any exact completion has the same operator normal form up to head/tail gauge;
- the bridge already fixes one head-compatible line inside ``U1``.

So in any exact external completion of the current bridge shell, the bridge
image of the internal common line is exactly the head-compatible ``U1`` line.
What remains open is existence of that non-split completion on the K3 side.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_transport_internal_operator_normal_form_match_bridge import (
    build_transport_internal_operator_normal_form_match_bridge_summary,
)
from w33_transport_unique_nonzero_cocycle_orbit_bridge import (
    build_transport_unique_nonzero_cocycle_orbit_bridge_summary,
)
from w33_u1_head_compatible_line_bridge import (
    build_u1_head_compatible_line_bridge_summary,
)
from w33_yukawa_generation_flag_bridge import build_yukawa_generation_flag_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_common_line_exact_image_bridge_summary.json"


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


@lru_cache(maxsize=1)
def build_common_line_exact_image_bridge_summary() -> dict[str, Any]:
    cocycle = _transport_cocycle_summary()
    operator_match = build_transport_internal_operator_normal_form_match_bridge_summary()
    orbit = build_transport_unique_nonzero_cocycle_orbit_bridge_summary()
    head_line = build_u1_head_compatible_line_bridge_summary()
    flag = build_yukawa_generation_flag_summary()

    return {
        "status": "ok",
        "internal_common_line": {
            "generator": flag["common_flag"]["line_generator"],
            "role": "image_of_common_square",
            "fiber_shift_matrix": cocycle["fiber_nilpotent_operator"]["matrix"],
        },
        "forced_external_image_line": {
            "line_coefficients": head_line["external_u1_line_roles"][
                "head_compatible_line_candidate"
            ],
            "carrier_plane": "U1",
            "role": "head_image_line_in_any_exact_completion",
        },
        "common_line_exact_image_theorem": {
            "internal_common_line_is_exactly_the_image_of_the_common_square": (
                flag["generation_flag_theorem"]["common_line_equals_image_of_common_square"]
            ),
            "internal_transport_operator_image_is_the_head_invariant_line": (
                cocycle["fiber_nilpotent_operator"][
                    "kernel_equals_image_equals_invariant_line"
                ]
                is True
                and cocycle["matter_extension_operator"]["image_equals_kernel"] is True
            ),
            "any_exact_external_completion_has_the_same_transport_operator_normal_form_up_to_basis_gauge": (
                operator_match[
                    "transport_internal_operator_normal_form_match_theorem"
                ][
                    "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge"
                ]
            ),
            "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion": (
                head_line["u1_head_compatible_line_theorem"][
                    "the_current_external_line_ambiguity_collapses_to_one_head_compatible_candidate"
                ]
                and cocycle["fiber_nilpotent_operator"][
                    "kernel_equals_image_equals_invariant_line"
                ]
                is True
                and operator_match[
                    "transport_internal_operator_normal_form_match_theorem"
                ][
                    "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge"
                ]
                and orbit[
                    "transport_unique_nonzero_cocycle_orbit_theorem"
                ][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
            "what_remains_open_is_existence_of_that_exact_completion_not_choice_of_image_line": (
                orbit[
                    "transport_unique_nonzero_cocycle_orbit_theorem"
                ][
                    "the_remaining_external_wall_is_existence_of_that_unique_nonzero_orbit_not_selection_among_several_nonzero_types"
                ]
            ),
        },
        "bridge_verdict": (
            "The bridge image line is now fixed at the exact-completion level. "
            "If the current K3 bridge shell admits the required non-split "
            "completion at all, then the image of the internal common line "
            "span(1,1,0) is forced to be the head-compatible line inside U1. "
            "The remaining wall is existence of that completion, not image-line "
            "choice."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_common_line_exact_image_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
