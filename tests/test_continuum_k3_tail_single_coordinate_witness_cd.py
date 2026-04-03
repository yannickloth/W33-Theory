"""
Phase CD — K3 tail single-coordinate witness criterion.

CCCXCIX collapsed the external wall to one unique minimal datum. This phase
reduces it once more: on the fixed K3 tail line, any one promoted coordinate
witness already identifies that datum and therefore exact realization.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_single_coordinate_witness_bridge import (
    build_k3_tail_single_coordinate_witness_summary,
)


def test_phase_cd_any_one_coordinate_witness_is_sufficient_on_fixed_line() -> None:
    theorem = build_k3_tail_single_coordinate_witness_summary()[
        "k3_tail_single_coordinate_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_tail_line_membership_plus_any_one_coordinate_witness"
    ] is True


def test_phase_cd_live_external_wall_is_one_coordinate_witness_existence_problem() -> None:
    theorem = build_k3_tail_single_coordinate_witness_summary()[
        "k3_tail_single_coordinate_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_existence_of_any_one_exact_coordinate_witness_from_genuine_k3_side_data_on_the_fixed_line_class"
    ] is True
