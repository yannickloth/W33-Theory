from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_tail_exactness_failure_bridge import (  # noqa: E402
    build_current_k3_tail_exactness_failure_summary,
)


def test_current_k3_zero_tail_candidate_is_syzygy_trivial_but_arithmetically_zero() -> None:
    summary = build_current_k3_tail_exactness_failure_summary()
    candidate = summary["current_refined_k3_zero_tail_candidate"]

    assert candidate["coordinates"] == {
        "C": "0",
        "L": "0",
        "Q_seed": "0",
        "Q_sd1": "0",
    }
    assert candidate["syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    }
    assert candidate["arithmetic"] == {
        "denominator_lcm": 1,
        "cleared_coordinate_gcd": 0,
        "recovered_scale": "0",
    }


def test_current_k3_failure_theorem_is_exact() -> None:
    theorem = build_current_k3_tail_exactness_failure_summary()[
        "current_k3_tail_exactness_failure_theorem"
    ]

    assert theorem[
        "the_current_refined_k3_object_already_sits_on_the_fixed_carrier_package_before_tail_realization"
    ] is True
    assert theorem[
        "the_current_refined_k3_tail_data_satisfies_the_exact_syzygies_only_trivially_at_the_zero_point"
    ] is True
    assert theorem[
        "the_current_refined_k3_tail_data_fails_the_transport_pair_lcm12_gcd217"
    ] is True
    assert theorem[
        "therefore_the_current_refined_k3_object_fails_the_exact_tail_realization_test_on_the_fixed_carrier_package"
    ] is True
    assert theorem[
        "the_failure_is_localized_to_missing_nonzero_tail_data_not_to_carrier_ambiguity"
    ] is True
    assert theorem[
        "therefore_any_exact_k3_tail_realization_requires_genuine_new_k3_side_data_on_the_same_fixed_carrier_package"
    ] is True
