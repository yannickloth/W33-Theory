from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_enhancement_slot_hierarchy_bridge import (  # noqa: E402
    UNIQUE_NONZERO_SLOT,
    ZERO_SLOT,
    build_enhancement_slot_hierarchy_bridge_summary,
)
from w33_external_enhancement_hierarchy_bridge import (  # noqa: E402
    CURRENT_K3_ZERO_ORBIT,
    FORMAL_COMPLETION_AVATAR,
    MINIMAL_EXTERNAL_ENHANCEMENT,
)


def test_enhancement_slot_mapping_is_exact() -> None:
    summary = build_enhancement_slot_hierarchy_bridge_summary()
    mapping = summary["enhancement_to_slot_mapping"]

    assert mapping == {
        CURRENT_K3_ZERO_ORBIT: ZERO_SLOT,
        MINIMAL_EXTERNAL_ENHANCEMENT: UNIQUE_NONZERO_SLOT,
        FORMAL_COMPLETION_AVATAR: UNIQUE_NONZERO_SLOT,
    }


def test_enhancement_slot_hierarchy_theorem_holds() -> None:
    theorem = build_enhancement_slot_hierarchy_bridge_summary()[
        "enhancement_slot_hierarchy_theorem"
    ]

    assert theorem["current_k3_zero_orbit_lives_on_the_zero_slot"] is True
    assert theorem["minimal_external_enhancement_lives_on_the_unique_nonzero_slot"] is True
    assert theorem["formal_completion_avatar_lives_on_the_unique_nonzero_slot"] is True
    assert theorem["the_three_state_enhancement_hierarchy_refines_the_two_state_slot_wall"] is True
    assert theorem["the_current_state_is_separated_from_both_completion_states_by_slot_status"] is True
    assert theorem["minimal_and_formal_states_share_the_same_nonzero_slot_but_not_the_same_support_role"] is True

