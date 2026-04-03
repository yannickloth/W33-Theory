"""
Phase CCCXCIX — Minimal K3 tail realization equivalence.

CCCXCVIII fixed the unique minimal K3-side tail datum. This phase collapses the
remaining wall one step further: on the fixed carrier package, exact K3 tail
realization is equivalent to realizing that one datum.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_minimal_k3_tail_realization_equivalence_bridge import (
    build_minimal_k3_tail_realization_equivalence_summary,
)


def test_phase_cccxcix_minimal_datum_is_sufficient() -> None:
    theorem = build_minimal_k3_tail_realization_equivalence_summary()[
        "minimal_k3_tail_realization_equivalence_theorem"
    ]
    assert theorem[
        "therefore_realizing_the_unique_minimal_tail_datum_is_sufficient_for_exact_tail_realization_on_the_fixed_package"
    ] is True


def test_phase_cccxcix_live_wall_is_one_existence_question() -> None:
    theorem = build_minimal_k3_tail_realization_equivalence_summary()[
        "minimal_k3_tail_realization_equivalence_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_exactly_existence_of_that_one_minimal_datum"
    ] is True
