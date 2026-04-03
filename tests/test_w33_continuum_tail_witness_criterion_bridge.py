from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_witness_criterion_bridge import (  # noqa: E402
    build_continuum_tail_witness_criterion_summary,
)


def test_all_transport_witnesses_recover_same_scalar() -> None:
    summary = build_continuum_tail_witness_criterion_summary()
    witnesses = summary["transport_tail_witnesses"]

    assert witnesses["scalar_amplitude"] == 217
    assert witnesses["amplitude_from_first_order_constant_gap"] == "217"
    assert witnesses["amplitude_from_first_order_linear_gap"] == "217"
    assert witnesses["amplitude_from_quadratic_seed_gap"] == "217"
    assert witnesses["amplitude_from_quadratic_sd1_gap"] == "217"
    assert witnesses["all_witnesses_recover_the_same_scalar"] is True


def test_tail_witness_criterion_theorem_is_exact() -> None:
    theorem = build_continuum_tail_witness_criterion_summary()[
        "continuum_tail_witness_criterion_theorem"
    ]
    assert theorem[
        "any_one_promoted_nonzero_transport_tail_observable_recovers_the_exact_scalar_amplitude"
    ] is True
    assert theorem[
        "once_that_scalar_is_fixed_the_entire_transport_residual_package_is_forced"
    ] is True
    assert theorem["the_matter_coupled_package_then_follows_by_exact_81_fold_lift"] is True
    assert theorem[
        "the_head_channel_remains_protected_and_the_witness_lives_only_on_the_fixed_tail_avatar"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_existence_of_one_nonzero_tail_witness_on_the_fixed_avatar"
    ] is True
