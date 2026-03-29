from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_product_search import (  # noqa: E402
    MODE_CURRENT_SHADOW,
    MODE_FORMAL_COMPLETION,
    NONZERO_GLUE,
    SUPPORT_ITEMS,
    ZERO_GLUE,
    build_marked_indices,
    strict_support_marked_permutations,
)
from toe_bridge_permutation_search import five_factor_predicate  # noqa: E402


def _assert_marked_state_shape(
    support_permutations: list[tuple[str, ...]],
    factor_permutations: list[tuple[str, ...]],
    product_states: list[tuple[int, int, str]],
    marked_indices: set[int],
    glue_state: str,
) -> None:
    support_marks = {perm for perm in strict_support_marked_permutations(support_permutations)}
    assert len(marked_indices) == 20
    for index in marked_indices:
        support_idx, factor_idx, state = product_states[index]
        assert isinstance(support_idx, int)
        assert isinstance(factor_idx, int)
        assert state == glue_state
        assert support_permutations[support_idx] in support_marks
        assert five_factor_predicate(factor_permutations[factor_idx])


def test_current_shadow_mark_count_and_glue_state() -> None:
    support_permutations, factor_permutations, product_states, marked_indices = build_marked_indices(
        MODE_CURRENT_SHADOW
    )
    assert len(support_permutations) == 120
    assert support_permutations[0] == tuple(SUPPORT_ITEMS)
    assert len(factor_permutations) == 120
    assert len(product_states) == 28800
    _assert_marked_state_shape(
        support_permutations, factor_permutations, product_states, marked_indices, ZERO_GLUE
    )


def test_formal_completion_mark_count_and_glue_state() -> None:
    support_permutations, factor_permutations, product_states, marked_indices = build_marked_indices(
        MODE_FORMAL_COMPLETION
    )
    assert len(support_permutations) == 120
    assert len(factor_permutations) == 120
    assert len(product_states) == 28800
    _assert_marked_state_shape(
        support_permutations, factor_permutations, product_states, marked_indices, NONZERO_GLUE
    )
