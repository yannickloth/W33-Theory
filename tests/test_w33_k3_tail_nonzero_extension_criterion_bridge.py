from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_nonzero_extension_criterion_bridge import (  # noqa: E402
    build_k3_tail_nonzero_extension_criterion_summary,
)


def test_nonzero_extension_witness_orbit_is_unique_up_to_gauge() -> None:
    summary = build_k3_tail_nonzero_extension_criterion_summary()
    witness = summary["nonzero_extension_witness"]
    assert witness["field"] == "F3"
    assert witness["nonzero_orbit_size"] == 2


def test_nonzero_extension_criterion_theorem_holds() -> None:
    theorem = build_k3_tail_nonzero_extension_criterion_summary()[
        "k3_tail_nonzero_extension_criterion_theorem"
    ]
    assert theorem[
        "the_current_k3_state_still_has_zero_extension_class_in_the_existing_tail_slot"
    ] is True
    assert theorem[
        "the_exact_target_is_the_unique_nonzero_orbit_in_that_same_existing_tail_slot"
    ] is True
    assert theorem[
        "up_to_the_natural_gauge_there_is_only_one_nonzero_extension_orbit_available"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_any_nonzero_extension_class_witness_in_the_existing_tail_slot"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_nonzero_extension_witness_problem_on_the_same_fixed_k3_package"
    ] is True
