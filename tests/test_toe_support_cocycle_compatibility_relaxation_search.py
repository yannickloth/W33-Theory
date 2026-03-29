from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QISKIT_TOOLS = ROOT / "tools" / "qiskit"
if str(QISKIT_TOOLS) not in sys.path:
    sys.path.insert(0, str(QISKIT_TOOLS))

from toe_support_cocycle_compatibility_relaxation_search import (  # noqa: E402
    FOCUS_ALL,
    FOCUS_NONZERO,
    RELAXATION_BOTH,
    RELAXATION_CORE_ORDER,
    RELAXATION_EXACT,
    RELAXATION_INTERLEAVING,
    build_marked_indices,
    expected_marked_count,
)


def test_support_cocycle_marked_count_profile() -> None:
    expected_all = {
        RELAXATION_EXACT: 6,
        RELAXATION_INTERLEAVING: 60,
        RELAXATION_CORE_ORDER: 36,
        RELAXATION_BOTH: 360,
    }
    expected_nonzero = {
        RELAXATION_EXACT: 4,
        RELAXATION_INTERLEAVING: 40,
        RELAXATION_CORE_ORDER: 24,
        RELAXATION_BOTH: 240,
    }

    for relaxation, expected in expected_all.items():
        _support, _states, marked = build_marked_indices(FOCUS_ALL, relaxation)
        assert len(marked) == expected_marked_count(FOCUS_ALL, relaxation) == expected

    for relaxation, expected in expected_nonzero.items():
        _support, _states, marked = build_marked_indices(FOCUS_NONZERO, relaxation)
        assert len(marked) == expected_marked_count(FOCUS_NONZERO, relaxation) == expected
