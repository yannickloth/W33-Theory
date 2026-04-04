"""
Phase CDX — K3 tail nonzero-extension criterion.

CDIX reduced the wall to breaking splitness in the existing tail slot. This
phase makes the positive existence condition explicit: on the fixed
carrier-preserving K3 package, exact tail realization is equivalent to any
nonzero extension-class witness in that same existing slot.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_nonzero_extension_criterion_bridge import (
    build_k3_tail_nonzero_extension_criterion_summary,
)


def test_phase_cdx_realization_equals_nonzero_extension_witness() -> None:
    theorem = build_k3_tail_nonzero_extension_criterion_summary()[
        "k3_tail_nonzero_extension_criterion_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_any_nonzero_extension_class_witness_in_the_existing_tail_slot"
    ] is True


def test_phase_cdx_live_wall_is_nonzero_extension_problem() -> None:
    theorem = build_k3_tail_nonzero_extension_criterion_summary()[
        "k3_tail_nonzero_extension_criterion_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_nonzero_extension_witness_problem_on_the_same_fixed_k3_package"
    ] is True
