"""
Phase CDXLVII — formal completion operator J₂⁸¹.

The 162×162 nilpotent operator is square-zero with image = kernel = 81,
matching the non-split transport extension shell 0 → 81 → 162 → 81 → 0.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_formal_completion_j2_81_bridge import (
    build_formal_completion_j2_81_summary,
)


def test_phase_cdxlvii_j2_81_is_correct_normal_form() -> None:
    theorem = build_formal_completion_j2_81_summary()[
        "formal_completion_j2_81_theorem"
    ]
    assert theorem[
        "therefore_j2_81_is_the_correct_normal_form_for_the_non_split_transport_glue"
    ] is True


def test_phase_cdxlvii_square_zero_image_equals_kernel() -> None:
    theorem = build_formal_completion_j2_81_summary()[
        "formal_completion_j2_81_theorem"
    ]
    assert theorem[
        "the_operator_is_square_zero_with_image_equal_to_kernel"
    ] is True


def test_phase_cdxlvii_dimension_162_rank_81() -> None:
    theorem = build_formal_completion_j2_81_summary()[
        "formal_completion_j2_81_theorem"
    ]
    assert theorem[
        "the_formal_completion_has_dimension_162_and_rank_81"
    ] is True


def test_phase_cdxlvii_minimal_polynomial() -> None:
    theorem = build_formal_completion_j2_81_summary()[
        "formal_completion_j2_81_theorem"
    ]
    assert theorem[
        "the_minimal_polynomial_is_x_squared"
    ] is True


def test_phase_cdxlvii_162_in_e8_branching() -> None:
    summary = build_formal_completion_j2_81_summary()
    srg = summary["srg_consistency"]
    assert srg["b1_equals_q4"] is True
    assert srg["dim_162_equals_2_times_b1"] is True
