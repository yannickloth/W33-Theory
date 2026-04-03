"""
Phase CCCLXXXV — Continuum tail-profile rigidity.

CCCLXXXIV reduced the live continuum wall to the transport tail channel. This
phase sharpens that further: the remaining first-order local seed data already
lies on one exact primitive profile ray, and the first-refinement quadratic
contraction law is universal. So the live wall is a one-parameter realization
problem, not a free channel-valued ambiguity.
"""

from __future__ import annotations

from exploration.w33_continuum_tail_profile_rigidity_bridge import (
    build_continuum_tail_profile_rigidity_summary,
)


def test_phase_ccclxxxv_tail_profile_is_one_exact_ray() -> None:
    profile = build_continuum_tail_profile_rigidity_summary()["transport_tail_profile"]
    assert profile["primitive_transport_profile"] == [65, 662]
    assert profile["primitive_matter_profile"] == [65, 662]


def test_phase_ccclxxxv_live_wall_is_one_parameter_realization_problem() -> None:
    theorem = build_continuum_tail_profile_rigidity_summary()[
        "continuum_tail_profile_rigidity_theorem"
    ]
    assert theorem[
        "therefore_the_live_continuum_existence_problem_is_a_one_parameter_tail_profile_realization_problem"
    ] is True
