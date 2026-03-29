from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_line_factor_search import (  # noqa: E402
    HEAD_LINE,
    MODE_CURRENT_SHADOW,
    MODE_FORMAL_COMPLETION,
    TAIL_LINE,
    build_marked_indices,
    build_line_factor_states,
)


def test_line_factor_product_state_count() -> None:
    support_permutations, factor_permutations, product_states = build_line_factor_states()
    assert len(support_permutations) == 120
    assert len(factor_permutations) == 120
    assert len(product_states) == 120 * 120 * 2 * 2


def test_formal_completion_marks_force_head_line() -> None:
    _, _, product_states, marked_indices = build_marked_indices(MODE_FORMAL_COMPLETION)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, glue_state, line_state = product_states[index]
        assert glue_state == "unique_nonzero_orbit"
        assert line_state == HEAD_LINE


def test_current_shadow_marks_force_head_line_not_tail_line() -> None:
    _, _, product_states, marked_indices = build_marked_indices(MODE_CURRENT_SHADOW)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, glue_state, line_state = product_states[index]
        assert glue_state == "zero_split_shadow"
        assert line_state == HEAD_LINE
        assert line_state != TAIL_LINE
