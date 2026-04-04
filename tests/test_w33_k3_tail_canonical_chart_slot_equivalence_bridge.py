from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_canonical_chart_slot_equivalence_bridge import (  # noqa: E402
    build_k3_tail_canonical_chart_slot_equivalence_summary,
)


def test_canonical_chart_target_matches_nonzero_slot_datum() -> None:
    summary = build_k3_tail_canonical_chart_slot_equivalence_summary()
    target = summary["canonical_chart_target"]
    assert target["coordinate"] == "dC"
    assert target["required_value"] == "14105"
    assert target["primitive_c_direction"] == "780"
    assert target["transport_scale"] == "217/12"


def test_canonical_chart_slot_equivalence_theorem_holds() -> None:
    theorem = build_k3_tail_canonical_chart_slot_equivalence_summary()[
        "k3_tail_canonical_chart_slot_equivalence_theorem"
    ]
    assert theorem[
        "the_current_k3_state_has_zero_slot_and_zero_canonical_chart_increment"
    ] is True
    assert theorem[
        "the_unique_minimal_exact_tail_datum_activates_the_nonzero_slot"
    ] is True
    assert theorem[
        "the_unique_minimal_exact_tail_datum_has_canonical_chart_coordinate_deltaC_equals_14105"
    ] is True
    assert theorem[
        "therefore_solving_deltaC_equals_14105_on_the_fixed_package_is_equivalent_to_activating_the_unique_nonzero_tail_slot"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_slot_activation_problem_on_the_existing_k3_tail_channel"
    ] is True
