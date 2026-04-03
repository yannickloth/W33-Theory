from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_operator_normal_form_bridge import (  # noqa: E402
    build_continuum_tail_operator_normal_form_summary,
)


def test_normalized_tail_operator_profile_is_exact() -> None:
    summary = build_continuum_tail_operator_normal_form_summary()
    normalized = summary["normalized_tail_operator_profile"]
    transport = summary["realized_transport_tail_operator_profile"]
    matter = summary["realized_matter_tail_operator_profile"]

    assert normalized["constant_witness"] == "65"
    assert normalized["linear_witness"] == "662"
    assert normalized["quadratic_seed_witness"] == "15650/3"
    assert normalized["quadratic_sd1_witness"] == "17993/4"

    assert transport["scalar_amplitude"] == 217
    assert transport["constant_witness"] == "14105"
    assert transport["linear_witness"] == "143654"
    assert transport["quadratic_seed_witness"] == "3396050/3"
    assert transport["quadratic_sd1_witness"] == "3904481/4"

    assert matter["qutrit_factor"] == 81
    assert matter["constant_witness"] == "1142505"
    assert matter["linear_witness"] == "11635974"
    assert matter["quadratic_seed_witness"] == "91693350"
    assert matter["quadratic_sd1_witness"] == "316262961/4"


def test_tail_operator_normal_form_theorem_is_exact() -> None:
    theorem = build_continuum_tail_operator_normal_form_summary()[
        "continuum_tail_operator_normal_form_theorem"
    ]
    assert theorem[
        "the_fixed_tail_avatar_has_one_unique_normalized_operator_profile"
    ] is True
    assert theorem[
        "the_realized_transport_tail_operator_is_exactly_217_times_that_normal_form"
    ] is True
    assert theorem[
        "the_realized_matter_tail_operator_is_the_exact_81_fold_lift_of_the_transport_operator"
    ] is True
    assert theorem[
        "the_one_witness_criterion_is_equivalent_to_realization_of_this_unique_operator_normal_form"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_existence_of_one_unique_nonzero_tail_operator_gauge_class"
    ] is True
