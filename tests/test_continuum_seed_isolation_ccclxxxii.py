"""
Phase CCCLXXXII — Continuum seed isolation and refinement contraction.

CCCLXXXI localized the remaining continuum wall to the curvature-sensitive tail
channel on the fixed avatar shell. This phase sharpens that claim: the
universal and topological first-order sectors are already seed-independent, and
the residual CP2/K3 gap sits only in the local r^20 channel while the
quadratic gap contracts at first refinement.
"""

from __future__ import annotations

from exploration.w33_continuum_seed_isolation_bridge import (
    build_continuum_seed_isolation_bridge_summary,
)


def test_phase_ccclxxxii_first_order_seed_universality() -> None:
    summary = build_continuum_seed_isolation_bridge_summary()
    transport = summary["first_order_seed_isolation"]["transport"]
    matter = summary["first_order_seed_isolation"]["matter_coupled"]

    assert transport["constant_limit_gap"]["exact"] == "0"
    assert transport["constant_corr120_gap"]["exact"] == "0"
    assert transport["linear_limit_gap"]["exact"] == "0"
    assert transport["linear_corr120_gap"]["exact"] == "0"

    assert matter["constant_limit_gap"]["exact"] == "0"
    assert matter["constant_corr120_gap"]["exact"] == "0"
    assert matter["linear_limit_gap"]["exact"] == "0"
    assert matter["linear_corr120_gap"]["exact"] == "0"


def test_phase_ccclxxxii_all_first_order_seed_dependence_sits_in_r20() -> None:
    summary = build_continuum_seed_isolation_bridge_summary()
    transport = summary["first_order_seed_isolation"]["transport"]
    matter = summary["first_order_seed_isolation"]["matter_coupled"]

    assert transport["constant_corr20_gap"]["exact"] == "14105"
    assert transport["linear_corr20_gap"]["exact"] == "143654"
    assert matter["constant_corr20_gap"]["exact"] == "1142505"
    assert matter["linear_corr20_gap"]["exact"] == "11635974"


def test_phase_ccclxxxii_quadratic_seed_gap_contracts_under_sd1() -> None:
    theorem = build_continuum_seed_isolation_bridge_summary()[
        "quadratic_gap_contraction"
    ]

    assert theorem["transport_seed_gap"]["exact"] == "3396050/3"
    assert theorem["transport_sd1_gap"]["exact"] == "3904481/4"
    assert theorem["transport_first_refinement_contracts_gap"] is True

    assert theorem["matter_seed_gap"]["exact"] == "91693350"
    assert theorem["matter_sd1_gap"]["exact"] == "316262961/4"
    assert theorem["matter_first_refinement_contracts_gap"] is True


def test_phase_ccclxxxii_remaining_wall_is_contracting_local_tail_effect() -> None:
    theorem = build_continuum_seed_isolation_bridge_summary()[
        "continuum_seed_isolation_theorem"
    ]
    assert theorem[
        "therefore_the_remaining_continuum_seed_dependence_is_a_contracting_local_tail_channel_effect"
    ] is True
