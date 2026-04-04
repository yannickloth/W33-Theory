from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_splitness_breaking_criterion_bridge import (  # noqa: E402
    build_k3_tail_splitness_breaking_criterion_summary,
)


def test_slot_transition_is_zero_to_unique_nonzero() -> None:
    summary = build_k3_tail_splitness_breaking_criterion_summary()
    transition = summary["slot_transition"]
    assert transition["from"] == "zero_by_splitness"
    assert transition["to"] == "unique_nonzero_orbit_in_existing_glue_slot"
    assert transition["canonical_chart_requirement"] == "14105"


def test_splitness_breaking_theorem_holds() -> None:
    theorem = build_k3_tail_splitness_breaking_criterion_summary()[
        "k3_tail_splitness_breaking_criterion_theorem"
    ]
    assert theorem[
        "the_current_refined_k3_shadow_is_split_with_zero_extension_class_and_zero_slot"
    ] is True
    assert theorem[
        "the_exact_target_slot_is_the_unique_nonzero_orbit_in_the_existing_slot"
    ] is True
    assert theorem[
        "solving_the_canonical_chart_equation_is_equivalent_to_nonzero_slot_activation"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_breaking_splitness_in_the_existing_tail_slot"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_splitness_breaking_problem_on_the_same_fixed_carrier_package"
    ] is True
