"""
Phase CCCXCVIII — Minimal K3 tail enhancement datum.

CCCXCVII proved the current refined K3 object fails the exact tail-realization
test only because the required nonzero tail datum is absent. This phase turns
that into a positive target: on the same fixed carrier package, there is one
unique minimal tail datum that any exact realization must first add.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_minimal_k3_tail_enhancement_datum_bridge import (
    build_minimal_k3_tail_enhancement_datum_summary,
)


def test_phase_cccxcviii_minimal_target_is_unique() -> None:
    theorem = build_minimal_k3_tail_enhancement_datum_summary()[
        "minimal_k3_tail_enhancement_datum_theorem"
    ]
    assert theorem[
        "the_missing_minimal_tail_datum_is_exactly_the_unique_nonzero_existing_slot_state_with_primitive_direction_and_pair_lcm12_gcd217"
    ] is True


def test_phase_cccxcviii_any_exact_realization_factors_through_that_datum() -> None:
    theorem = build_minimal_k3_tail_enhancement_datum_summary()[
        "minimal_k3_tail_enhancement_datum_theorem"
    ]
    assert theorem[
        "any_exact_k3_side_realization_must_factor_through_that_unique_minimal_tail_datum_before_any_formal_completion_avatar"
    ] is True
