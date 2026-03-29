from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QISKIT_TOOLS = ROOT / "tools" / "qiskit"
if str(QISKIT_TOOLS) not in sys.path:
    sys.path.insert(0, str(QISKIT_TOOLS))

from toe_double_interleaving_shadow_search import (  # noqa: E402
    RELAXATION_EXACT,
    RELAXATION_SUPPORT,
    build_marked_indices,
    build_states,
    expected_marked_count,
)


def test_double_interleaving_state_count() -> None:
    assert len(build_states()) == 100


def test_double_interleaving_marked_counts() -> None:
    _states, marked_exact = build_marked_indices(RELAXATION_EXACT)
    _states, marked_relaxed = build_marked_indices(RELAXATION_SUPPORT)
    assert len(marked_exact) == expected_marked_count(RELAXATION_EXACT) == 10
    assert len(marked_relaxed) == expected_marked_count(RELAXATION_SUPPORT) == 100
