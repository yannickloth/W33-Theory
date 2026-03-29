from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_cocycle_compatibility_relaxation_search import (  # noqa: E402
    FOCUS_ALL,
    FOCUS_NONZERO,
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
    build_marked_indices,
    build_states,
    expected_marked_count,
)


def test_diagnostic_cocycle_relaxation_state_space_is_exact() -> None:
    _support, _diagnostic, _walls, bridge_states = build_states()
    assert len(bridge_states) == 345600


def test_diagnostic_cocycle_relaxation_marked_count_profile() -> None:
    expected_all = {
        RELAXATION_EXACT: 60,
        RELAXATION_EXCEPTIONAL: 120,
        RELAXATION_HYPERBOLIC: 360,
        RELAXATION_BOTH: 720,
    }
    expected_nonzero = {
        RELAXATION_EXACT: 40,
        RELAXATION_EXCEPTIONAL: 80,
        RELAXATION_HYPERBOLIC: 240,
        RELAXATION_BOTH: 480,
    }

    for relaxation, expected in expected_all.items():
        _support, _diagnostic, _walls, _bridge, marked = build_marked_indices(FOCUS_ALL, relaxation)
        assert len(marked) == expected_marked_count(FOCUS_ALL, relaxation) == expected

    for relaxation, expected in expected_nonzero.items():
        _support, _diagnostic, _walls, _bridge, marked = build_marked_indices(FOCUS_NONZERO, relaxation)
        assert len(marked) == expected_marked_count(FOCUS_NONZERO, relaxation) == expected
