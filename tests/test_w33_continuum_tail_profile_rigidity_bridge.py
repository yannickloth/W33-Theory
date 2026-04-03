from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_profile_rigidity_bridge import (  # noqa: E402
    build_continuum_tail_profile_rigidity_summary,
)


def test_transport_tail_profile_is_primitive_and_shared() -> None:
    summary = build_continuum_tail_profile_rigidity_summary()
    profile = summary["transport_tail_profile"]

    assert profile["transport_local_r20_gap_vector"] == [14105, 143654]
    assert profile["transport_profile_amplitude"] == 217
    assert profile["primitive_transport_profile"] == [65, 662]
    assert profile["matter_local_r20_gap_vector"] == [1142505, 11635974]
    assert profile["matter_profile_amplitude"] == 17577
    assert profile["primitive_matter_profile"] == [65, 662]
    assert profile["matter_amplitude_is_qutrit_factor_times_transport_amplitude"] is True
    assert profile["transport_and_matter_share_the_same_primitive_profile"] is True


def test_tail_profile_rigidity_theorem_is_exact() -> None:
    theorem = build_continuum_tail_profile_rigidity_summary()[
        "continuum_tail_profile_rigidity_theorem"
    ]
    contraction = build_continuum_tail_profile_rigidity_summary()[
        "transport_tail_contraction"
    ]

    assert theorem[
        "the_residual_transport_tail_has_one_exact_primitive_first_order_profile"
    ] is True
    assert theorem[
        "the_matter_coupled_tail_has_the_same_profile_with_exact_81_fold_amplitude"
    ] is True
    assert theorem["the_first_refinement_quadratic_contraction_law_is_universal"] is True
    assert theorem[
        "therefore_the_live_continuum_existence_problem_is_a_one_parameter_tail_profile_realization_problem"
    ] is True
    assert contraction["seed_to_sd1_quadratic_contraction_ratio"] == "53979/62600"
    assert contraction["seed_to_sd1_quadratic_contraction_is_strict"] is True
