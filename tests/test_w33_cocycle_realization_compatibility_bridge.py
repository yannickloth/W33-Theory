from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_cocycle_realization_compatibility_bridge import (  # noqa: E402
    build_cocycle_realization_compatibility_bridge_summary,
)


def test_cocycle_realization_compatibility_summary() -> None:
    summary = build_cocycle_realization_compatibility_bridge_summary()
    theorem = summary["cocycle_realization_compatibility_theorem"]
    assert theorem["the_current_refined_k3_object_is_compatible_only_with_zero_orbit"]
    assert theorem["the_slot_replacement_datum_is_compatible_only_with_the_unique_nonzero_orbit"]
    assert theorem["the_formal_completion_object_is_compatible_only_with_the_unique_nonzero_orbit"]
    assert theorem["the_wall_factor_has_exact_size_6_with_exactly_3_admissible_states"]
    assert theorem["the_live_nonzero_wall_is_exactly_the_two_state_subset_slot_replacement_or_formal_completion"]
    assert theorem["this_is_not_a_free_three_label_axis_but_a_compatibility_theorem_with_forbidden_corners"]
