from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_weight_filter_search import (  # noqa: E402
    HEAD_LINE,
    MODE_CURRENT_SHADOW,
    MODE_FORMAL_COMPLETION,
    WEIGHT_FILTER_PASS,
    build_marked_indices,
    build_weight_filter_states,
)


def test_weight_filter_product_state_count() -> None:
    support_permutations, factor_permutations, product_states = build_weight_filter_states()
    assert len(support_permutations) == 120
    assert len(factor_permutations) == 120
    assert len(product_states) == 120 * 120 * 2 * 2 * 2


def test_formal_completion_marks_force_head_line_and_weight_filter() -> None:
    _, _, product_states, marked_indices = build_marked_indices(MODE_FORMAL_COMPLETION)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, glue_state, line_state, weight_filter_state = product_states[index]
        assert glue_state == "unique_nonzero_orbit"
        assert line_state == HEAD_LINE
        assert weight_filter_state == WEIGHT_FILTER_PASS


def test_current_shadow_marks_force_head_line_and_weight_filter() -> None:
    _, _, product_states, marked_indices = build_marked_indices(MODE_CURRENT_SHADOW)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, glue_state, line_state, weight_filter_state = product_states[index]
        assert glue_state == "zero_split_shadow"
        assert line_state == HEAD_LINE
        assert weight_filter_state == WEIGHT_FILTER_PASS
