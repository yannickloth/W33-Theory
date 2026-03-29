from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_split_weight_filter_search import (  # noqa: E402
    EXCEPTIONAL_PASS,
    HEAD_LINE,
    HYPERBOLIC_PASS,
    MODE_CURRENT_SHADOW,
    MODE_FORMAL_COMPLETION,
    NONZERO_GLUE,
    ZERO_GLUE,
    build_marked_indices,
    build_split_weight_filter_states,
)


def test_split_weight_filter_product_state_count() -> None:
    support_permutations, factor_permutations, product_states = build_split_weight_filter_states()
    assert len(support_permutations) == 120
    assert len(factor_permutations) == 120
    assert len(product_states) == 120 * 120 * 2 * 2 * 2 * 2


def test_formal_completion_marks_force_head_line_and_both_pass_states() -> None:
    _, _, product_states, marked_indices = build_marked_indices(MODE_FORMAL_COMPLETION)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, glue_state, line_state, hyperbolic_state, exceptional_state = product_states[index]
        assert glue_state == NONZERO_GLUE
        assert line_state == HEAD_LINE
        assert hyperbolic_state == HYPERBOLIC_PASS
        assert exceptional_state == EXCEPTIONAL_PASS


def test_current_shadow_marks_force_head_line_and_both_pass_states() -> None:
    _, _, product_states, marked_indices = build_marked_indices(MODE_CURRENT_SHADOW)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, glue_state, line_state, hyperbolic_state, exceptional_state = product_states[index]
        assert glue_state == ZERO_GLUE
        assert line_state == HEAD_LINE
        assert hyperbolic_state == HYPERBOLIC_PASS
        assert exceptional_state == EXCEPTIONAL_PASS
