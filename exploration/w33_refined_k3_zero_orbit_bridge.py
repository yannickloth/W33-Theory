"""Current refined K3 side still realizes only the zero ternary glue orbit.

The transport wall has now been reduced to existence of the unique nonzero
ternary cocycle orbit on the external side. This module answers the first
obvious question: does the current refined K3 bridge already realize that
orbit?

It does not.

The reason is exact and refinement-stable:

- the current external transport object is split;
- its unique tail-to-head glue slot is structurally zero;
- the canonical mixed K3 plane survives first barycentric refinement with the
  same normalized mixed signature.

So the present refined K3 side still realizes only the zero orbit. Any
realization of the unique nonzero ternary orbit would require genuinely new
external data beyond the current refined K3 bridge package.
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

from w33_external_glue_zero_forcing_bridge import (
    build_external_glue_zero_forcing_bridge_summary,
)
from w33_k3_refined_plane_persistence_bridge import (
    build_k3_refined_plane_persistence_bridge_summary,
)
from w33_transport_unique_nonzero_cocycle_orbit_bridge import (
    build_transport_unique_nonzero_cocycle_orbit_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_refined_k3_zero_orbit_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_refined_k3_zero_orbit_bridge_summary() -> dict[str, Any]:
    zero_glue = build_external_glue_zero_forcing_bridge_summary()
    refinement = build_k3_refined_plane_persistence_bridge_summary()
    nonzero_orbit = build_transport_unique_nonzero_cocycle_orbit_bridge_summary()

    return {
        "status": "ok",
        "current_refined_k3_transport_shadow": {
            "ordered_filtration_dimensions": zero_glue["current_external_transport_object"][
                "ordered_filtration_dimensions"
            ],
            "extension_class_zero": zero_glue["current_external_transport_object"][
                "extension_class_zero"
            ],
            "current_external_slot_state": zero_glue["external_glue_slot"][
                "current_external_state"
            ],
            "first_refinement_scale_factor": refinement["first_refinement_scale_factor"],
        },
        "unique_nonzero_ternary_orbit": {
            "base_shift": nonzero_orbit["ternary_fiber_shift_orbit"]["base_shift"],
            "other_nonzero_scalar_multiple": nonzero_orbit["ternary_fiber_shift_orbit"][
                "other_nonzero_scalar_multiple"
            ],
        },
        "refined_k3_zero_orbit_theorem": {
            "current_refined_k3_shadow_is_split_with_zero_extension_class": (
                zero_glue["current_external_transport_object"]["extension_class_zero"]
                is True
                and zero_glue["external_glue_zero_forcing_theorem"][
                    "the_unique_external_tail_to_head_glue_slot_is_structurally_zero_on_the_present_bridge_object"
                ]
            ),
            "current_refined_k3_shadow_remains_refinement_rigid_at_first_barycentric_step": (
                refinement["refinement_theorem"][
                    "first_barycentric_pullback_scales_restricted_form_by_120"
                ]
                and refinement["refinement_theorem"][
                    "normalized_restricted_form_is_refinement_invariant"
                ]
            ),
            "the_unique_nonzero_ternary_orbit_is_not_realized_on_the_current_refined_k3_side": (
                zero_glue["external_glue_zero_forcing_theorem"][
                    "the_unique_external_tail_to_head_glue_slot_is_structurally_zero_on_the_present_bridge_object"
                ]
                and nonzero_orbit[
                    "transport_unique_nonzero_cocycle_orbit_theorem"
                ][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
            "any_realization_of_the_unique_nonzero_orbit_requires_new_external_data_beyond_the_current_refined_k3_bridge": (
                zero_glue["external_glue_zero_forcing_theorem"][
                    "any_nonzero_external_glue_operator_would_require_new_external_data_beyond_the_current_bridge_objects"
                ]
            ),
        },
        "bridge_verdict": (
            "The current refined K3 bridge still realizes only the zero ternary "
            "glue orbit. That is not a seed artifact: the split shadow remains "
            "refinement-rigid at sd^1. So the unique nonzero ternary cocycle "
            "orbit is not already present on the current refined K3 side, and "
            "any realization of it would require genuinely new external data."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_refined_k3_zero_orbit_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
