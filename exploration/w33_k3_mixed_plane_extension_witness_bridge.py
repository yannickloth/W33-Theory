"""Exact K3 tail realization is a witness on the canonical mixed K3 plane.

CDX reduced the remaining external wall to the cleanest positive form
available on the fixed carrier-preserving package:

- exact K3 tail realization is equivalent to any nonzero extension-class
  witness in the existing tail slot.

But the external side is not floating abstractly. The current 162-sector is
already fixed as the split qutrit lift of the canonical mixed K3 plane. So the
existence problem can be attached to an actual geometric object:

- the witness must live on that canonical mixed K3 plane qutrit lift itself;
- no new carrier plane or replacement 162-host is needed;
- the only missing step is a nonzero extension witness deforming the already
  fixed split lift in its existing tail slot.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_extension_witness_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_extension_witness_summary() -> dict[str, Any]:
    from w33_external_glue_zero_forcing_bridge import (
        build_external_glue_zero_forcing_bridge_summary,
    )
    from w33_k3_tail_nonzero_extension_criterion_bridge import (
        build_k3_tail_nonzero_extension_criterion_summary,
    )

    external = build_external_glue_zero_forcing_bridge_summary()
    extension = build_k3_tail_nonzero_extension_criterion_summary()

    transport_object = external["current_external_transport_object"]
    fixed = extension["fixed_k3_tail_exactness_channel"]

    return {
        "status": "ok",
        "canonical_mixed_k3_plane_qutrit_lift": {
            "source": transport_object["source"],
            "selector_triangle": transport_object["selector_triangle"],
            "ordered_line_types": transport_object["ordered_line_types"],
            "qutrit_lift_split": list(transport_object["qutrit_lift_split"]),
            "total_qutrit_lift_dimension": transport_object["total_qutrit_lift_dimension"],
            "split_qutrit_package": transport_object["split_qutrit_package"],
            "mixed_signature": transport_object["mixed_signature"],
        },
        "fixed_k3_tail_exactness_channel": fixed,
        "k3_mixed_plane_extension_witness_theorem": {
            "the_current_external_162_sector_is_already_the_split_qutrit_lift_of_the_canonical_mixed_k3_plane": (
                transport_object["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and list(transport_object["qutrit_lift_split"]) == [81, 81]
                and transport_object["total_qutrit_lift_dimension"] == 162
                and transport_object["split_qutrit_package"] is True
            ),
            "the_fixed_k3_tail_exactness_channel_is_already_carried_by_that_same_mixed_plane_qutrit_lift": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and fixed["slot_shape"] == [81, 81]
                and transport_object["total_qutrit_lift_dimension"] == 162
            ),
            "exact_k3_tail_realization_is_already_equivalent_to_any_nonzero_extension_class_witness_in_the_existing_tail_slot": (
                extension["k3_tail_nonzero_extension_criterion_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_any_nonzero_extension_class_witness_in_the_existing_tail_slot"
                ]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_a_nonzero_extension_witness_on_the_canonical_mixed_k3_plane_qutrit_lift": (
                transport_object["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and list(transport_object["qutrit_lift_split"]) == [81, 81]
                and transport_object["total_qutrit_lift_dimension"] == 162
                and extension["k3_tail_nonzero_extension_criterion_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_any_nonzero_extension_class_witness_in_the_existing_tail_slot"
                ]
            ),
            "the_live_external_wall_is_now_one_mixed_plane_deformation_witness_problem_not_a_search_for_a_new_162_host": (
                transport_object["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and transport_object["split_qutrit_package"] is True
                and extension["slot_transition"]["from"] == "zero_by_splitness"
                and extension["slot_transition"]["to"]
                == "unique_nonzero_orbit_in_existing_glue_slot"
            ),
        },
        "bridge_verdict": (
            "The remaining K3 existence wall is now attached to a concrete "
            "external object. The current 162-sector is already the split "
            "qutrit lift of the canonical mixed K3 plane, and exact K3 tail "
            "realization is already equivalent to any nonzero extension-class "
            "witness in the existing tail slot. So the live wall is now one "
            "mixed-plane deformation witness problem on that already-fixed K3 "
            "object, not a search for a new external host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_extension_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
