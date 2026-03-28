"""Minimal new external data needed for a non-split transport completion.

The current bridge has already fixed almost everything about the external
transport shell:

- the ordered dimensions ``81 -> 162 -> 81``;
- the head-compatible and tail-biased ``U1`` lines;
- the unique tail-to-head glue slot;
- the full-rank normal form ``I_81`` / ``J2^81`` for any exact completion;
- and the fact that over ``F3`` there is only one nonzero cocycle orbit up to
  the natural head/tail gauge.

So the minimal new external data is no longer another geometric package. It is
exactly one formal choice: replacing the current zero slot by the unique
nonzero orbit in that already-fixed slot.
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
from w33_transport_rigid_split_avatar_bridge import (
    build_transport_rigid_split_avatar_bridge_summary,
)
from w33_transport_single_glue_slot_bridge import (
    build_transport_single_glue_slot_bridge_summary,
)
from w33_transport_unique_nonzero_cocycle_orbit_bridge import (
    build_transport_unique_nonzero_cocycle_orbit_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_minimal_external_completion_data_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_minimal_external_completion_data_bridge_summary() -> dict[str, Any]:
    avatar = build_transport_rigid_split_avatar_bridge_summary()
    slot = build_transport_single_glue_slot_bridge_summary()
    normal_form = build_transport_full_rank_glue_normal_form_bridge_summary()
    orbit = build_transport_unique_nonzero_cocycle_orbit_bridge_summary()

    return {
        "status": "ok",
        "locked_external_transport_shell": {
            "head_line": avatar["canonical_external_transport_avatar"]["head_line"],
            "tail_line": avatar["canonical_external_transport_avatar"]["tail_line"],
            "ordered_filtration_dimensions": avatar[
                "canonical_external_transport_avatar"
            ]["ordered_filtration_dimensions"],
            "slot_direction": slot["internal_transport_operator_slot"]["slot_direction"],
            "slot_shape": slot["internal_transport_operator_slot"]["slot_shape"],
            "current_external_slot_state": slot["external_current_slot_state"][
                "current_external_slot_state"
            ],
        },
        "minimal_new_external_data": {
            "required_new_state": "unique_nonzero_orbit_in_existing_glue_slot",
            "slot_matrix_normal_form": normal_form[
                "canonical_full_rank_completion_normal_form"
            ]["slot_matrix_normal_form"],
            "polarized_nilpotent_normal_form": normal_form[
                "canonical_full_rank_completion_normal_form"
            ]["polarized_nilpotent_normal_form"],
            "unique_nonzero_fiber_shift_orbit": orbit["ternary_fiber_shift_orbit"][
                "base_shift"
            ],
            "gauge_equivalent_nonzero_scalar_multiple": orbit[
                "ternary_fiber_shift_orbit"
            ]["other_nonzero_scalar_multiple"],
        },
        "minimal_external_completion_data_theorem": {
            "the_external_shell_already_fixes_where_new_data_can_enter": (
                avatar["canonical_external_transport_avatar"][
                    "ordered_filtration_dimensions"
                ]
                == [81, 162, 81]
                and slot["internal_transport_operator_slot"]["slot_direction"]
                == "tail_to_head"
                and slot["internal_transport_operator_slot"]["slot_shape"] == [81, 81]
            ),
            "the_current_bridge_already_fixes_the_zero_orbit_of_that_slot": (
                slot["external_current_slot_state"]["current_external_slot_state"]
                == "zero_by_splitness"
            ),
            "there_is_only_one_nonzero_orbit_available_for_exact_completion": (
                orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
            "that_unique_nonzero_orbit_has_full_rank_identity_slot_normal_form": (
                normal_form["transport_full_rank_glue_normal_form_theorem"][
                    "up_to_independent_head_tail_basis_change_any_full_rank_glue_completion_has_identity_slot_matrix"
                ]
            ),
            "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot": (
                slot["external_current_slot_state"]["current_external_slot_state"]
                == "zero_by_splitness"
                and orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
                and normal_form["transport_full_rank_glue_normal_form_theorem"][
                    "up_to_independent_head_tail_basis_change_any_full_rank_glue_completion_has_identity_slot_matrix"
                ]
            ),
            "no_additional_line_plane_or_dimension_choice_remains_after_the_current_bridge_reductions": (
                avatar["transport_rigid_split_avatar_theorem"][
                    "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet"
                ]
                and orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
        },
        "bridge_verdict": (
            "The minimal new external data is no longer mysterious. The current "
            "bridge has already fixed the shell, lines, slot shape, and "
            "completion normal form. So exact non-split completion requires "
            "exactly one new datum: replace the present zero slot by the "
            "unique nonzero ternary orbit in that already-fixed tail-to-head "
            "81x81 slot."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_minimal_external_completion_data_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
