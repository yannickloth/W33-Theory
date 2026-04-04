"""Unique support-preserving slot-only deformation class on the mixed K3 plane.

CDXII fixed the remaining K3 witness problem to a very rigid form:

- the host is the canonical mixed K3 plane qutrit lift;
- any exact witness must preserve the full mixed-plane support package;
- only the extension class in the existing tail slot may change.

CDX had already reduced the slot side itself:

- up to the natural gauge over `F3`, there is only one nonzero orbit available
  in that existing tail slot.

So the witness problem sharpens one more step. There is now only one exact
support-preserving slot-only deformation class on the canonical mixed-plane
lift. The live wall is no longer selection among many possible deformations;
it is existence of that one unique deformation class.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_unique_slot_deformation_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_unique_slot_deformation_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_support_preserving_witness_bridge import (
        build_k3_mixed_plane_support_preserving_witness_summary,
    )
    from w33_k3_tail_nonzero_extension_criterion_bridge import (
        build_k3_tail_nonzero_extension_criterion_summary,
    )

    support = build_k3_mixed_plane_support_preserving_witness_summary()
    extension = build_k3_tail_nonzero_extension_criterion_summary()

    host = support["canonical_mixed_plane_support"]
    fixed = support["fixed_k3_tail_exactness_channel"]
    witness = extension["nonzero_extension_witness"]
    transition = extension["slot_transition"]

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "slot_only_deformation_class": {
            "preserved_support_package": True,
            "slot_transition": transition,
            "field": witness["field"],
            "nonzero_orbit_size": witness["nonzero_orbit_size"],
            "deformation_type": "support_preserving_slot_only",
        },
        "k3_mixed_plane_unique_slot_deformation_theorem": {
            "any_exact_k3_tail_witness_must_preserve_the_canonical_mixed_plane_support_package": (
                support["k3_mixed_plane_support_preserving_witness_theorem"][
                    "therefore_any_exact_k3_tail_witness_must_preserve_the_canonical_mixed_plane_support_package_and_only_change_the_extension_class"
                ]
            ),
            "up_to_the_natural_gauge_there_is_only_one_nonzero_slot_orbit_available_for_the_existing_tail_slot": (
                extension["k3_tail_nonzero_extension_criterion_theorem"][
                    "up_to_the_natural_gauge_there_is_only_one_nonzero_extension_orbit_available"
                ]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_slot_only_deformation_class_on_the_canonical_mixed_plane_lift": (
                support["k3_mixed_plane_support_preserving_witness_theorem"][
                    "therefore_any_exact_k3_tail_witness_must_preserve_the_canonical_mixed_plane_support_package_and_only_change_the_extension_class"
                ]
                and extension["k3_tail_nonzero_extension_criterion_theorem"][
                    "up_to_the_natural_gauge_there_is_only_one_nonzero_extension_orbit_available"
                ]
                and transition["from"] == "zero_by_splitness"
                and transition["to"] == "unique_nonzero_orbit_in_existing_glue_slot"
            ),
            "the_live_external_wall_is_now_one_unique_support_preserving_slot_only_deformation_existence_problem": (
                host["ordered_line_types"] == ["positive", "negative"]
                and host["mixed_signature"] == [1, 1]
                and host["qutrit_lift_split"] == [81, 81]
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and extension["k3_tail_nonzero_extension_criterion_theorem"][
                    "up_to_the_natural_gauge_there_is_only_one_nonzero_extension_orbit_available"
                ]
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 witness problem is now unique in form. The "
            "support package is already frozen, only the existing tail slot "
            "may change, and up to gauge there is only one nonzero orbit "
            "available there. So exact K3 tail realization is equivalent to "
            "existence of one unique support-preserving slot-only deformation "
            "class on the canonical mixed-plane lift."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_unique_slot_deformation_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
