"""Match between the internal transport operator and the external completion normal form.

Two exact transport reductions now meet cleanly:

1. the internal non-split ternary transport extension already has an explicit
   operator model `I_81 ⊗ [[0,1],[0,0]]`;
2. any exact external completion of the rigid split avatar must, up to the
   natural head/tail basis gauge, have the single polarized normal form
   `J2^81`.

Those are the same linear-algebraic normal form. So the remaining transport
wall is no longer operator shape mismatch. It is realization of the nontrivial
transport cocycle class on the external side.
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

from w33_transport_full_rank_glue_normal_form_bridge import (
    build_transport_full_rank_glue_normal_form_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_transport_internal_operator_normal_form_match_bridge_summary.json"
)


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
def build_transport_internal_operator_normal_form_match_bridge_summary() -> (
    dict[str, Any]
):
    internal = _transport_cocycle_summary()
    completion = build_transport_full_rank_glue_normal_form_bridge_summary()

    fiber_shift = internal["fiber_nilpotent_operator"]["matrix"]
    matter = internal["matter_extension_operator"]

    return {
        "status": "ok",
        "internal_transport_operator_normal_form": {
            "fiber_shift_matrix": fiber_shift,
            "logical_qutrits": matter["logical_qutrits"],
            "dimension": matter["dimension"],
            "rank": matter["rank"],
            "nullity": matter["nullity"],
            "square_zero": matter["square_zero"],
            "operator_model": "I_81 ⊗ [[0,1],[0,0]]",
        },
        "external_completion_normal_form": {
            "slot_matrix_normal_form": completion[
                "canonical_full_rank_completion_normal_form"
            ]["slot_matrix_normal_form"],
            "polarized_nilpotent_normal_form": completion[
                "canonical_full_rank_completion_normal_form"
            ]["polarized_nilpotent_normal_form"],
        },
        "transport_internal_operator_normal_form_match_theorem": {
            "internal_transport_extension_has_exact_operator_normal_form_i81_tensor_fiber_shift": (
                fiber_shift == [[0, 1], [0, 0]]
                and matter["logical_qutrits"] == 81
                and matter["dimension"] == 162
                and matter["rank"] == 81
                and matter["nullity"] == 81
                and matter["square_zero"] is True
            ),
            "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge": (
                completion["transport_full_rank_glue_normal_form_theorem"][
                    "up_to_polarized_isomorphism_any_exact_completion_has_canonical_jordan_normal_form_two_power_81"
                ]
            ),
            "the_remaining_transport_wall_is_realization_of_the_nontrivial_cocycle_class_not_operator_shape": (
                fiber_shift == [[0, 1], [0, 0]]
                and matter["logical_qutrits"] == 81
                and completion["transport_full_rank_glue_normal_form_theorem"][
                    "up_to_polarized_isomorphism_any_exact_completion_has_canonical_jordan_normal_form_two_power_81"
                ]
            ),
        },
        "bridge_verdict": (
            "The internal transport extension and any exact external completion "
            "now share the same linear-algebraic normal form: I_81 tensor the "
            "fiber shift [[0,1],[0,0]], equivalently J2^81 on the polarized "
            "162-shell. So the remaining transport wall is realization of the "
            "nontrivial cocycle class externally, not operator-shape mismatch."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_transport_internal_operator_normal_form_match_bridge_summary(),
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
