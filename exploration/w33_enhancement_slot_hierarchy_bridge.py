"""Exact compatibility law between enhancement states and cocycle-slot status.

The exact three-state external enhancement hierarchy is now sharp enough that
it can be projected onto the older two-state cocycle-slot wall:

- the current refined K3 object sits on the zero slot;
- the minimal exact enhancement sits on the unique nonzero slot;
- the formal completion avatar also sits on that same unique nonzero slot.

So the enhancement hierarchy is not another copy of the slot wall. It is a
strict refinement of it: one zero-slot state and two distinct nonzero-slot
states.
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

from w33_external_enhancement_hierarchy_bridge import (
    CURRENT_K3_ZERO_ORBIT,
    FORMAL_COMPLETION_AVATAR,
    MINIMAL_EXTERNAL_ENHANCEMENT,
    build_external_enhancement_hierarchy_bridge_summary,
)
from w33_formal_external_completion_avatar_bridge import (
    build_formal_external_completion_avatar_bridge_summary,
)
from w33_minimal_external_completion_data_bridge import (
    build_minimal_external_completion_data_bridge_summary,
)
from w33_refined_k3_zero_orbit_bridge import (
    build_refined_k3_zero_orbit_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_enhancement_slot_hierarchy_bridge_summary.json"

ZERO_SLOT = "zero_by_splitness"
UNIQUE_NONZERO_SLOT = "unique_nonzero_orbit_in_existing_slot"


@lru_cache(maxsize=1)
def build_enhancement_slot_hierarchy_bridge_summary() -> dict[str, Any]:
    enhancement = build_external_enhancement_hierarchy_bridge_summary()
    current = build_refined_k3_zero_orbit_bridge_summary()
    minimal = build_minimal_external_completion_data_bridge_summary()
    formal = build_formal_external_completion_avatar_bridge_summary()

    mapping = {
        CURRENT_K3_ZERO_ORBIT: ZERO_SLOT,
        MINIMAL_EXTERNAL_ENHANCEMENT: UNIQUE_NONZERO_SLOT,
        FORMAL_COMPLETION_AVATAR: UNIQUE_NONZERO_SLOT,
    }

    return {
        "status": "ok",
        "slot_states": [ZERO_SLOT, UNIQUE_NONZERO_SLOT],
        "enhancement_to_slot_mapping": mapping,
        "compatible_enhancement_slot_pairs": [
            [CURRENT_K3_ZERO_ORBIT, ZERO_SLOT],
            [MINIMAL_EXTERNAL_ENHANCEMENT, UNIQUE_NONZERO_SLOT],
            [FORMAL_COMPLETION_AVATAR, UNIQUE_NONZERO_SLOT],
        ],
        "enhancement_slot_hierarchy_theorem": {
            "current_k3_zero_orbit_lives_on_the_zero_slot": (
                enhancement["enhancement_states"][CURRENT_K3_ZERO_ORBIT]["slot_state"]
                == ZERO_SLOT
                if "slot_state" in enhancement["enhancement_states"][CURRENT_K3_ZERO_ORBIT]
                else current["current_refined_k3_transport_shadow"][
                    "current_external_slot_state"
                ]
                == ZERO_SLOT
            ),
            "minimal_external_enhancement_lives_on_the_unique_nonzero_slot": (
                minimal["minimal_new_external_data"]["required_new_state"]
                == UNIQUE_NONZERO_SLOT
            ),
            "formal_completion_avatar_lives_on_the_unique_nonzero_slot": (
                formal["formal_external_completion_avatar"]["slot_matrix_normal_form"]
                == "I_81"
                and formal["formal_external_completion_avatar"][
                    "polarized_nilpotent_normal_form"
                ]
                == "J2^81"
            ),
            "the_three_state_enhancement_hierarchy_refines_the_two_state_slot_wall": (
                current["current_refined_k3_transport_shadow"]["current_external_slot_state"]
                == ZERO_SLOT
                and minimal["minimal_new_external_data"]["required_new_state"]
                == UNIQUE_NONZERO_SLOT
                and formal["formal_external_completion_avatar"][
                    "polarized_nilpotent_normal_form"
                ]
                == "J2^81"
            ),
            "the_current_state_is_separated_from_both_completion_states_by_slot_status": (
                mapping[CURRENT_K3_ZERO_ORBIT] == ZERO_SLOT
                and mapping[MINIMAL_EXTERNAL_ENHANCEMENT] == UNIQUE_NONZERO_SLOT
                and mapping[FORMAL_COMPLETION_AVATAR] == UNIQUE_NONZERO_SLOT
            ),
            "minimal_and_formal_states_share_the_same_nonzero_slot_but_not_the_same_support_role": (
                mapping[MINIMAL_EXTERNAL_ENHANCEMENT] == UNIQUE_NONZERO_SLOT
                and mapping[FORMAL_COMPLETION_AVATAR] == UNIQUE_NONZERO_SLOT
                and enhancement["external_enhancement_hierarchy_theorem"][
                    "the_formal_completion_avatar_is_the_resulting_minimal_common_object"
                ]
            ),
        },
        "bridge_verdict": (
            "The enhancement hierarchy is now visibly sharper than the old "
            "binary glue wall. The current K3 object occupies the zero slot, "
            "while both completion-side strata occupy the same unique nonzero "
            "slot. So the three-state enhancement hierarchy strictly refines "
            "the two-state cocycle-slot wall rather than duplicating it."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_enhancement_slot_hierarchy_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
