from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_permutation_search import (  # noqa: E402
    MODE_FIVE_FACTOR,
    MODE_SUPPORT,
    marked_permutations,
)


def test_five_factor_hierarchy_mark_count_and_constraints() -> None:
    items, constraints, sources, marks = marked_permutations(MODE_FIVE_FACTOR)
    assert items == ["U1", "U2", "U3", "E8_1", "E8_2"]
    assert len(constraints) == 2
    assert len(sources) == 2
    assert len(marks) == 10
    for mark in marks:
        pos = {name: idx for idx, name in enumerate(mark)}
        assert pos["U3"] < pos["U1"] < pos["U2"]
        assert pos["E8_2"] < pos["E8_1"]


def test_support_hierarchy_mark_count_and_constraints() -> None:
    items, constraints, sources, marks = marked_permutations(MODE_SUPPORT)
    assert items == ["head_line", "u1_plane", "transport_avatar", "u3_local", "e8_2_local"]
    assert len(constraints) == 2
    assert len(sources) == 2
    assert len(marks) == 20
    for mark in marks:
        pos = {name: idx for idx, name in enumerate(mark)}
        assert pos["head_line"] < pos["u1_plane"] < pos["transport_avatar"]
