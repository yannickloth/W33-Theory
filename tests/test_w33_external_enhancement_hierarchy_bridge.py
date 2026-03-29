from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_external_enhancement_hierarchy_bridge import (  # noqa: E402
    CURRENT_K3_ZERO_ORBIT,
    FORMAL_COMPLETION_AVATAR,
    MINIMAL_EXTERNAL_ENHANCEMENT,
    build_external_enhancement_hierarchy_bridge_summary,
)


def test_enhancement_hierarchy_states_are_present() -> None:
    summary = build_external_enhancement_hierarchy_bridge_summary()
    states = summary["enhancement_states"]
    assert set(states) == {
        CURRENT_K3_ZERO_ORBIT,
        MINIMAL_EXTERNAL_ENHANCEMENT,
        FORMAL_COMPLETION_AVATAR,
    }


def test_enhancement_hierarchy_theorem_holds() -> None:
    theorem = build_external_enhancement_hierarchy_bridge_summary()[
        "external_enhancement_hierarchy_theorem"
    ]
    assert theorem[
        "the_current_refined_k3_side_is_exactly_the_zero_orbit_state"
    ]
    assert theorem[
        "the_minimal_exact_enhancement_is_one_nonzero_slot_replacement_not_a_new_shell"
    ]
    assert theorem[
        "the_formal_completion_avatar_is_the_resulting_minimal_common_object"
    ]
    assert theorem[
        "the_live_external_wall_is_exactly_current_object_vs_minimal_enhancement_vs_formal_completion"
    ]
