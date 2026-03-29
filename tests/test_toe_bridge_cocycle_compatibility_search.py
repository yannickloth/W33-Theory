from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QISKIT_TOOLS = ROOT / "tools" / "qiskit"
if str(QISKIT_TOOLS) not in sys.path:
    sys.path.insert(0, str(QISKIT_TOOLS))

from toe_bridge_cocycle_compatibility_search import (  # noqa: E402
    FOCUS_ALL,
    FOCUS_NONZERO,
    build_marked_indices,
    expected_marked_count,
)


def test_cocycle_compatibility_marked_counts() -> None:
    _support, _diagnostic, _walls, bridge_states, marked_all = build_marked_indices(FOCUS_ALL)
    assert len(bridge_states) == 345600
    assert len(marked_all) == expected_marked_count(FOCUS_ALL) == 60

    _support, _diagnostic, _walls, _bridge_states, marked_nonzero = build_marked_indices(
        FOCUS_NONZERO
    )
    assert len(marked_nonzero) == expected_marked_count(FOCUS_NONZERO) == 40
