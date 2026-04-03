"""
Phase CCCLXXXIV — Continuum qutrit-lift rigidity.

CCCLXXXIII showed that all residual CP2/K3 seed gaps scale by 81. This phase
promotes the structural consequence: the matter-coupled continuum ambiguity is
exactly the transport tail ambiguity lifted by the logical-qutrit packet, so
the live existence problem is transport-first rather than a new family-scale
continuum obstruction.
"""

from __future__ import annotations

from exploration.w33_continuum_qutrit_lift_rigidity_bridge import (
    build_continuum_qutrit_lift_rigidity_summary,
)


def test_phase_ccclxxxiv_all_residual_ratios_are_logical_qutrit_lift() -> None:
    lift = build_continuum_qutrit_lift_rigidity_summary()["logical_qutrit_lift"]
    assert lift["logical_qutrit_factor"] == 81
    assert lift["all_residual_gap_ratios_equal_logical_qutrit_factor"] is True


def test_phase_ccclxxxiv_live_continuum_wall_is_transport_first() -> None:
    theorem = build_continuum_qutrit_lift_rigidity_summary()[
        "continuum_qutrit_lift_rigidity_theorem"
    ]
    assert theorem[
        "therefore_the_live_continuum_existence_problem_is_transport_first_and_only_after_that_matter_coupled_by_exact_replication"
    ] is True
