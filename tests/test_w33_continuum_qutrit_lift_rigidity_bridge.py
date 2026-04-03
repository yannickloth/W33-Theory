from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_qutrit_lift_rigidity_bridge import (  # noqa: E402
    build_continuum_qutrit_lift_rigidity_summary,
)


def test_logical_qutrit_lift_is_exact() -> None:
    summary = build_continuum_qutrit_lift_rigidity_summary()
    lift = summary["logical_qutrit_lift"]

    assert lift["logical_qutrit_factor"] == 81
    assert lift["all_residual_gap_ratios_equal_logical_qutrit_factor"] is True


def test_continuum_qutrit_lift_rigidity_theorem_is_exact() -> None:
    theorem = build_continuum_qutrit_lift_rigidity_summary()[
        "continuum_qutrit_lift_rigidity_theorem"
    ]

    assert theorem[
        "matter_coupled_residual_seed_dependence_introduces_no_new_continuum_scale_beyond_transport"
    ] is True
    assert theorem[
        "the_family_sensitive_continuum_wall_is_exactly_the_transport_tail_wall_tensored_by_81"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_existence_problem_is_transport_first_and_only_after_that_matter_coupled_by_exact_replication"
    ] is True
