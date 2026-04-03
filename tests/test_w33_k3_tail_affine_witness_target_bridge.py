from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_affine_witness_target_bridge import (  # noqa: E402
    build_k3_tail_affine_witness_target_summary,
)


def test_affine_displacement_equals_exact_witness_point_from_zero_current_candidate() -> None:
    summary = build_k3_tail_affine_witness_target_summary()
    assert summary["current_zero_witness_point"] == {
        "C": "0",
        "L": "0",
        "Q_seed": "0",
        "Q_sd1": "0",
    }
    assert summary["affine_witness_displacement"] == summary["exact_witness_point"]


def test_affine_witness_target_theorem_holds() -> None:
    theorem = build_k3_tail_affine_witness_target_summary()[
        "k3_tail_affine_witness_target_theorem"
    ]
    assert theorem[
        "the_present_refined_k3_candidate_is_the_zero_point_in_witness_coordinates"
    ] is True
    assert theorem[
        "the_exact_witness_point_is_the_unique_nonzero_coordinate_target_from_cd"
    ] is True
    assert theorem[
        "the_missing_k3_side_addition_is_exactly_one_affine_displacement_from_the_current_zero_point_to_that_witness_point"
    ] is True
    assert theorem[
        "that_affine_displacement_lies_on_the_fixed_tail_line_with_common_scale_217_over_12"
    ] is True
    assert theorem[
        "therefore_the_live_external_wall_is_one_exact_affine_witness_target_on_the_same_fixed_package"
    ] is True
