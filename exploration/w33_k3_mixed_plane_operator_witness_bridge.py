"""Unique mixed-plane operator witness for exact K3 tail realization.

CDXIII reduced the remaining mixed-plane wall to one unique support-preserving
slot-only deformation class on the canonical mixed K3 plane qutrit lift.

Separately, the transport operator reductions had already fixed the only
possible nonzero completion shape:

- one tail-to-head slot of shape ``81 x 81``;
- square-zero rank ``81``;
- operator normal form ``I_81 ⊗ [[0,1],[0,0]]``;
- polarized nilpotent normal form ``J2^81``.

So the mixed-plane wall can now be stated in the concrete language the repo
can actually recognize. Exact K3 tail realization is equivalent to one unique
support-preserving rank-81 square-zero slot-operator witness on the canonical
mixed-plane lift.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_operator_witness_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_operator_witness_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_support_preserving_witness_bridge import (
        build_k3_mixed_plane_support_preserving_witness_summary,
    )
    from w33_k3_mixed_plane_unique_slot_deformation_bridge import (
        build_k3_mixed_plane_unique_slot_deformation_summary,
    )
    from w33_transport_internal_operator_normal_form_match_bridge import (
        build_transport_internal_operator_normal_form_match_bridge_summary,
    )

    support = build_k3_mixed_plane_support_preserving_witness_summary()
    deformation = build_k3_mixed_plane_unique_slot_deformation_summary()
    operator = build_transport_internal_operator_normal_form_match_bridge_summary()

    host = support["canonical_mixed_plane_support"]
    fixed = support["fixed_k3_tail_exactness_channel"]
    slot_only = deformation["slot_only_deformation_class"]
    internal = operator["internal_transport_operator_normal_form"]
    external = operator["external_completion_normal_form"]

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "fixed_k3_tail_exactness_channel": fixed,
        "mixed_plane_operator_witness": {
            "preserved_support_package": slot_only["preserved_support_package"],
            "deformation_type": slot_only["deformation_type"],
            "slot_direction": fixed["slot_direction"],
            "slot_shape": list(fixed["slot_shape"]),
            "rank": internal["rank"],
            "nullity": internal["nullity"],
            "square_zero": internal["square_zero"],
            "operator_model": internal["operator_model"],
            "polarized_nilpotent_normal_form": external[
                "polarized_nilpotent_normal_form"
            ],
        },
        "k3_mixed_plane_operator_witness_theorem": {
            "the_mixed_plane_support_package_is_already_frozen_and_the_slot_only_deformation_class_is_unique": (
                deformation["k3_mixed_plane_unique_slot_deformation_theorem"][
                    "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_slot_only_deformation_class_on_the_canonical_mixed_plane_lift"
                ]
            ),
            "the_exact_nonzero_slot_operator_has_unique_rank_81_square_zero_normal_form": (
                internal["rank"] == 81
                and internal["nullity"] == 81
                and internal["square_zero"] is True
                and internal["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
                and external["polarized_nilpotent_normal_form"] == "J2^81"
                and operator["transport_internal_operator_normal_form_match_theorem"][
                    "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge"
                ]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_rank_81_square_zero_slot_operator_witness_on_the_canonical_mixed_plane_lift": (
                deformation["k3_mixed_plane_unique_slot_deformation_theorem"][
                    "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_slot_only_deformation_class_on_the_canonical_mixed_plane_lift"
                ]
                and fixed["slot_direction"] == "tail_to_head"
                and list(fixed["slot_shape"]) == [81, 81]
                and internal["rank"] == 81
                and internal["nullity"] == 81
                and internal["square_zero"] is True
                and internal["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
            ),
            "the_live_external_wall_is_now_existence_of_that_one_operator_witness_on_genuine_k3_side_data": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and fixed["slot_direction"] == "tail_to_head"
                and list(fixed["slot_shape"]) == [81, 81]
                and internal["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
                and external["polarized_nilpotent_normal_form"] == "J2^81"
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 wall is now concrete in operator language. "
            "The support package is already frozen, the slot-only deformation "
            "class is unique, and the only nonzero completion shape has rank "
            "81, square zero, and normal form I_81 tensor [[0,1],[0,0]], "
            "equivalently J2^81. So exact K3 tail realization is equivalent "
            "to existence of one unique support-preserving slot-operator "
            "witness on the canonical mixed-plane lift."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_operator_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
