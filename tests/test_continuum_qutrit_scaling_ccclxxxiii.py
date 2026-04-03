"""
Phase CCCLXXXIII — Continuum qutrit scaling of the residual tail channel.

CCCLXXXII isolated the remaining seed dependence to the local tail channel.
This phase shows that the matter-coupled residual is exactly the transport
residual multiplied by the logical qutrit multiplicity 81, both at first order
and in the quadratic seed/sd^1 gaps.
"""

from __future__ import annotations

from exploration.w33_continuum_qutrit_scaling_bridge import (
    build_continuum_qutrit_scaling_bridge_summary,
)


def test_phase_ccclxxxiii_first_order_r20_seed_gaps_scale_by_81() -> None:
    scaling = build_continuum_qutrit_scaling_bridge_summary()["residual_gap_scaling"]

    assert scaling["first_order_constant_r20_ratio"]["exact"] == "81"
    assert scaling["first_order_linear_r20_ratio"]["exact"] == "81"


def test_phase_ccclxxxiii_quadratic_seed_and_sd1_gaps_scale_by_81() -> None:
    scaling = build_continuum_qutrit_scaling_bridge_summary()["residual_gap_scaling"]

    assert scaling["quadratic_seed_gap_ratio"]["exact"] == "81"
    assert scaling["quadratic_sd1_gap_ratio"]["exact"] == "81"


def test_phase_ccclxxxiii_matter_residual_is_not_new_seed_data() -> None:
    theorem = build_continuum_qutrit_scaling_bridge_summary()[
        "continuum_qutrit_scaling_theorem"
    ]
    assert theorem[
        "therefore_the_matter_coupled_residual_seed_dependence_is_transport_tail_dependence_tensored_with_the_exact_logical_qutrit_packet"
    ] is True
