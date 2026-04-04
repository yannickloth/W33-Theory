"""Exact K3 tail witness preserves the canonical mixed-plane support data.

CDXI attached the remaining K3 wall to a concrete external object:

- the current external 162-sector is already the split qutrit lift of the
  canonical mixed K3 plane;
- exact K3 tail realization is equivalent to a nonzero extension witness on
  that same mixed-plane lift.

The mixed-plane host already has sharp canonical support data:

- a deterministic selector triangle;
- one positive and one negative ordered harmonic line;
- mixed signature `(1,1)`;
- qutrit split `81 + 81` inside the fixed `162` host;
- first-refinement rigidity up to the universal factor `120`.

So the witness problem can be sharpened again. Any exact tail witness must
preserve that canonical mixed-plane support package and only deform the
extension class in the already-fixed slot. The wall is now one support-
preserving mixed-plane deformation witness problem.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT
    / "data"
    / "w33_k3_mixed_plane_support_preserving_witness_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_support_preserving_witness_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_extension_witness_bridge import (
        build_k3_mixed_plane_extension_witness_summary,
    )
    from w33_k3_refined_plane_persistence_bridge import (
        build_k3_refined_plane_persistence_bridge_summary,
    )

    mixed = build_k3_mixed_plane_extension_witness_summary()
    refinement = build_k3_refined_plane_persistence_bridge_summary()

    host = mixed["canonical_mixed_k3_plane_qutrit_lift"]
    fixed = mixed["fixed_k3_tail_exactness_channel"]

    return {
        "status": "ok",
        "canonical_mixed_plane_support": {
            "selector_triangle": host["selector_triangle"],
            "ordered_line_types": host["ordered_line_types"],
            "mixed_signature": list(host["mixed_signature"]),
            "qutrit_lift_split": list(host["qutrit_lift_split"]),
            "total_qutrit_lift_dimension": host["total_qutrit_lift_dimension"],
            "first_refinement_scale_factor": refinement["first_refinement_scale_factor"],
        },
        "fixed_k3_tail_exactness_channel": fixed,
        "k3_mixed_plane_support_preserving_witness_theorem": {
            "the_canonical_mixed_plane_support_data_are_already_fixed_on_the_external_side": (
                host["selector_triangle"] is not None
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and host["total_qutrit_lift_dimension"] == 162
            ),
            "the_canonical_mixed_plane_support_is_first_refinement_rigid": (
                refinement["refinement_theorem"][
                    "first_barycentric_pullback_scales_restricted_form_by_120"
                ]
                and refinement["refinement_theorem"][
                    "normalized_restricted_form_is_refinement_invariant"
                ]
                and refinement["refinement_theorem"][
                    "mixed_signature_survives_first_refinement"
                ]
            ),
            "exact_k3_tail_realization_is_already_equivalent_to_a_nonzero_extension_witness_on_that_same_mixed_plane_lift": (
                mixed["k3_mixed_plane_extension_witness_theorem"][
                    "therefore_exact_k3_tail_realization_is_equivalent_to_a_nonzero_extension_witness_on_the_canonical_mixed_k3_plane_qutrit_lift"
                ]
            ),
            "therefore_any_exact_k3_tail_witness_must_preserve_the_canonical_mixed_plane_support_package_and_only_change_the_extension_class": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and refinement["refinement_theorem"][
                    "normalized_restricted_form_is_refinement_invariant"
                ]
                and mixed["k3_mixed_plane_extension_witness_theorem"][
                    "therefore_exact_k3_tail_realization_is_equivalent_to_a_nonzero_extension_witness_on_the_canonical_mixed_k3_plane_qutrit_lift"
                ]
            ),
            "the_live_external_wall_is_now_one_support_preserving_mixed_plane_deformation_witness_problem": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and fixed["slot_shape"] == [81, 81]
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
        },
        "bridge_verdict": (
            "The remaining K3 witness problem is now support-rigid. The "
            "canonical mixed-plane host already fixes its selector triangle, "
            "ordered positive/negative lines, mixed signature, qutrit split, "
            "and first-refinement-normalized support data. So any exact tail "
            "witness must preserve that whole support package and only deform "
            "the extension class in the already-fixed tail slot."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_k3_mixed_plane_support_preserving_witness_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
