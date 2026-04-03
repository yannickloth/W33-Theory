from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_scalar_closure_bridge import (  # noqa: E402
    build_continuum_tail_scalar_closure_summary,
)


def test_tail_scalar_generator_is_exact() -> None:
    summary = build_continuum_tail_scalar_closure_summary()
    generator = summary["tail_scalar_generator"]

    assert generator["transport_amplitude"] == 217
    assert generator["primitive_transport_profile"] == [65, 662]
    assert generator["transport_first_order_constant_gap"] == 14105
    assert generator["transport_first_order_linear_gap"] == 143654
    assert generator["transport_quadratic_seed_gap"] == "3396050/3"
    assert generator["transport_quadratic_sd1_gap"] == "3904481/4"
    assert generator["transport_quadratic_seed_coefficient"] == "15650/3"
    assert generator["transport_quadratic_sd1_coefficient"] == "17993/4"


def test_tail_scalar_closure_theorem_is_exact() -> None:
    summary = build_continuum_tail_scalar_closure_summary()
    theorem = summary["tail_scalar_closure_theorem"]
    matter = summary["matter_qutrit_lift_generator"]

    assert theorem[
        "all_promoted_transport_residual_data_is_generated_by_one_scalar_amplitude"
    ] is True
    assert theorem[
        "the_matter_coupled_residual_package_is_the_exact_81_fold_lift_of_the_same_scalar_family"
    ] is True
    assert theorem["the_seed_to_sd1_quadratic_contraction_law_is_amplitude_independent"] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_existence_of_one_scalar_tail_realization_on_a_fixed_avatar"
    ] is True
    assert matter["matter_amplitude"] == 17577
    assert matter["matter_quadratic_seed_gap"] == "91693350"
    assert matter["matter_quadratic_sd1_gap"] == "316262961/4"
