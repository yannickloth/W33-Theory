"""Exact compatibility factor for the external cocycle-realization wall.

The enhancement wall is not just a free 3-label family. It can be resolved
into a compatibility problem between:

- the wall layer
  ``{current_refined_k3_object, slot_replacement_datum, formal_completion_object}``
- the orbit state
  ``{zero_orbit, unique_nonzero_orbit}``

This gives 6 discrete wall states. Exactly 3 are admissible under the current
bridge theorems, and only 2 of those carry the unique nonzero orbit.
"""

from __future__ import annotations

from functools import lru_cache
import itertools
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

from w33_external_enhancement_hierarchy_bridge import (  # noqa: E402
    CURRENT_K3_ZERO_ORBIT,
    FORMAL_COMPLETION_AVATAR,
    MINIMAL_EXTERNAL_ENHANCEMENT,
    build_external_enhancement_hierarchy_bridge_summary,
)
from w33_formal_external_completion_avatar_bridge import (  # noqa: E402
    build_formal_external_completion_avatar_bridge_summary,
)
from w33_minimal_external_completion_data_bridge import (  # noqa: E402
    build_minimal_external_completion_data_bridge_summary,
)
from w33_refined_k3_zero_orbit_bridge import (  # noqa: E402
    build_refined_k3_zero_orbit_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_cocycle_realization_compatibility_bridge_summary.json"
)

CURRENT_REFINED_K3_OBJECT = "current_refined_k3_object"
SLOT_REPLACEMENT_DATUM = "slot_replacement_datum"
FORMAL_COMPLETION_OBJECT = "formal_completion_object"

ZERO_ORBIT = "zero_orbit"
UNIQUE_NONZERO_ORBIT = "unique_nonzero_orbit"


def wall_layers() -> list[str]:
    return [
        CURRENT_REFINED_K3_OBJECT,
        SLOT_REPLACEMENT_DATUM,
        FORMAL_COMPLETION_OBJECT,
    ]


def orbit_states() -> list[str]:
    return [ZERO_ORBIT, UNIQUE_NONZERO_ORBIT]


def wall_states() -> list[tuple[str, str]]:
    return list(itertools.product(wall_layers(), orbit_states()))


def admissible_wall_states() -> list[tuple[str, str]]:
    return [
        (CURRENT_REFINED_K3_OBJECT, ZERO_ORBIT),
        (SLOT_REPLACEMENT_DATUM, UNIQUE_NONZERO_ORBIT),
        (FORMAL_COMPLETION_OBJECT, UNIQUE_NONZERO_ORBIT),
    ]


def nonzero_admissible_wall_states() -> list[tuple[str, str]]:
    return [
        (SLOT_REPLACEMENT_DATUM, UNIQUE_NONZERO_ORBIT),
        (FORMAL_COMPLETION_OBJECT, UNIQUE_NONZERO_ORBIT),
    ]


@lru_cache(maxsize=1)
def build_cocycle_realization_compatibility_bridge_summary() -> dict[str, Any]:
    current = build_refined_k3_zero_orbit_bridge_summary()
    minimal = build_minimal_external_completion_data_bridge_summary()
    formal = build_formal_external_completion_avatar_bridge_summary()
    hierarchy = build_external_enhancement_hierarchy_bridge_summary()

    admissible = admissible_wall_states()
    all_states = wall_states()
    forbidden = [state for state in all_states if state not in admissible]
    nonzero_admissible = nonzero_admissible_wall_states()

    return {
        "status": "ok",
        "wall_layer_states": wall_layers(),
        "orbit_states": orbit_states(),
        "wall_state_count": len(all_states),
        "wall_states": [list(state) for state in all_states],
        "admissible_wall_states": [list(state) for state in admissible],
        "nonzero_admissible_wall_states": [list(state) for state in nonzero_admissible],
        "forbidden_wall_states": [list(state) for state in forbidden],
        "cocycle_realization_compatibility_theorem": {
            "the_current_refined_k3_object_is_compatible_only_with_zero_orbit": (
                current["refined_k3_zero_orbit_theorem"][
                    "the_unique_nonzero_ternary_orbit_is_not_realized_on_the_current_refined_k3_side"
                ]
                and [CURRENT_REFINED_K3_OBJECT, ZERO_ORBIT]
                in [list(state) for state in admissible]
                and [CURRENT_REFINED_K3_OBJECT, UNIQUE_NONZERO_ORBIT]
                in [list(state) for state in forbidden]
            ),
            "the_slot_replacement_datum_is_compatible_only_with_the_unique_nonzero_orbit": (
                minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
                and [SLOT_REPLACEMENT_DATUM, UNIQUE_NONZERO_ORBIT]
                in [list(state) for state in admissible]
                and [SLOT_REPLACEMENT_DATUM, ZERO_ORBIT]
                in [list(state) for state in forbidden]
            ),
            "the_formal_completion_object_is_compatible_only_with_the_unique_nonzero_orbit": (
                formal["formal_external_completion_avatar_theorem"][
                    "that_common_formal_object_has_unique_nonzero_completion_normal_form_j2_power_81"
                ]
                and [FORMAL_COMPLETION_OBJECT, UNIQUE_NONZERO_ORBIT]
                in [list(state) for state in admissible]
                and [FORMAL_COMPLETION_OBJECT, ZERO_ORBIT]
                in [list(state) for state in forbidden]
            ),
            "the_wall_factor_has_exact_size_6_with_exactly_3_admissible_states": (
                len(all_states) == 6 and len(admissible) == 3
            ),
            "the_live_nonzero_wall_is_exactly_the_two_state_subset_slot_replacement_or_formal_completion": (
                len(nonzero_admissible) == 2
                and [SLOT_REPLACEMENT_DATUM, UNIQUE_NONZERO_ORBIT]
                in [list(state) for state in nonzero_admissible]
                and [FORMAL_COMPLETION_OBJECT, UNIQUE_NONZERO_ORBIT]
                in [list(state) for state in nonzero_admissible]
            ),
            "this_is_not_a_free_three_label_axis_but_a_compatibility_theorem_with_forbidden_corners": (
                hierarchy["external_enhancement_hierarchy_theorem"][
                    "the_live_external_wall_is_exactly_current_object_vs_minimal_enhancement_vs_formal_completion"
                ]
                and len(forbidden) == 3
            ),
        },
        "bridge_verdict": (
            "The external enhancement wall is now sharper than a three-label "
            "mode family. It is an exact 6-state compatibility factor between "
            "wall layer and orbit state, with 3 admissible states and 3 "
            "forbidden corners. The live nonzero wall is the 2-state subset "
            "consisting of the slot-replacement datum and the formal "
            "completion object, both paired with the unique nonzero orbit."
        ),
        "compatibility_label_bridge": {
            CURRENT_K3_ZERO_ORBIT: [CURRENT_REFINED_K3_OBJECT, ZERO_ORBIT],
            MINIMAL_EXTERNAL_ENHANCEMENT: [SLOT_REPLACEMENT_DATUM, UNIQUE_NONZERO_ORBIT],
            FORMAL_COMPLETION_AVATAR: [FORMAL_COMPLETION_OBJECT, UNIQUE_NONZERO_ORBIT],
        },
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_cocycle_realization_compatibility_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
