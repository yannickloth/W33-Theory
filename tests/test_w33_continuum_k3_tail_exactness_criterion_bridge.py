from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_k3_tail_exactness_criterion_bridge import (  # noqa: E402
    build_continuum_k3_tail_exactness_criterion_summary,
)


def test_sample_candidates_separate_exactness_correctly() -> None:
    summary = build_continuum_k3_tail_exactness_criterion_summary()
    candidates = summary["sample_candidates"]

    assert candidates["exact_transport_candidate"]["syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    }
    assert candidates["exact_transport_candidate"]["arithmetic"] == {
        "denominator_lcm": 12,
        "cleared_coordinate_gcd": 217,
        "recovered_scale": "217/12",
    }
    assert candidates["wrong_scale_on_exact_line_candidate"]["syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    }
    assert candidates["wrong_scale_on_exact_line_candidate"]["arithmetic"] == {
        "denominator_lcm": 1,
        "cleared_coordinate_gcd": 18,
        "recovered_scale": "18",
    }
    assert candidates["broken_syzygy_candidate"]["syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "-260",
    }


def test_k3_tail_exactness_criterion_theorem_is_exact() -> None:
    theorem = build_continuum_k3_tail_exactness_criterion_summary()[
        "continuum_k3_tail_exactness_criterion_theorem"
    ]
    assert theorem[
        "on_the_fixed_k3_carrier_package_exact_tail_realization_implies_tail_line_syzygies"
    ] is True
    assert theorem[
        "on_the_fixed_k3_carrier_package_exact_tail_realization_implies_arithmetic_pair_lcm12_gcd217"
    ] is True
    assert theorem[
        "on_the_fixed_k3_carrier_package_tail_line_syzygies_plus_pair_lcm12_gcd217_are_sufficient_for_exact_transport_realization"
    ] is True
    assert theorem[
        "therefore_exact_transport_realization_on_the_fixed_k3_carrier_package_is_equivalent_to_syzygies_plus_the_transport_pair"
    ] is True
    assert theorem[
        "the_induced_matter_realization_then_follows_with_pair_lcm4_gcd5859"
    ] is True
