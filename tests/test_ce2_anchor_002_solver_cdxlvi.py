"""
Phase CDXLVI — CE2 anchor (0,0,2) row solver.

The cocycle condition kills 161 of 162 candidate coefficients, leaving
exactly one free parameter pinned by the global CE2 transport law.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_ce2_anchor_002_solver_bridge import (
    build_ce2_anchor_002_solver_summary,
)


def test_phase_cdxlvi_002_anchor_has_one_free_parameter() -> None:
    theorem = build_ce2_anchor_002_solver_summary()[
        "ce2_anchor_002_solver_theorem"
    ]
    assert theorem[
        "therefore_the_002_anchor_has_exactly_one_free_parameter_pinned_by_the_global_transport_law"
    ] is True


def test_phase_cdxlvi_cocycle_kills_161_of_162() -> None:
    theorem = build_ce2_anchor_002_solver_summary()[
        "ce2_anchor_002_solver_theorem"
    ]
    assert theorem[
        "the_cocycle_condition_kills_161_of_162_candidate_coefficients"
    ] is True


def test_phase_cdxlvi_five_anchors_already_solved() -> None:
    theorem = build_ce2_anchor_002_solver_summary()[
        "ce2_anchor_002_solver_theorem"
    ]
    assert theorem[
        "the_target_anchor_is_002_and_five_anchors_are_already_solved"
    ] is True
