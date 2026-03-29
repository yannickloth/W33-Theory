from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_diagnostic_order_search import (  # noqa: E402
    EXCEPTIONAL_PASS,
    HEAD_LINE,
    HYPERBOLIC_PASS,
    MODE_CURRENT_SHADOW,
    MODE_FORMAL_COMPLETION,
    NONZERO_GLUE,
    ZERO_GLUE,
    build_marked_indices,
    exceptional_orderings,
    hyperbolic_orderings,
    interleaving_patterns,
    marked_exceptional_order,
    marked_hyperbolic_order,
    merge_factor_permutation,
)
from toe_bridge_permutation_search import five_factor_predicate  # noqa: E402


def test_factorization_has_exact_120_state_space() -> None:
    factor_permutations = {
        merge_factor_permutation(hyper, exceptional, interleaving)
        for interleaving in interleaving_patterns()
        for hyper in hyperbolic_orderings()
        for exceptional in exceptional_orderings()
    }
    assert len(interleaving_patterns()) == 10
    assert len(hyperbolic_orderings()) == 6
    assert len(exceptional_orderings()) == 2
    assert len(factor_permutations) == 120


def test_factorization_preserves_five_factor_predicate() -> None:
    marked = {
        merge_factor_permutation(hyper, exceptional, interleaving)
        for interleaving in interleaving_patterns()
        for hyper in hyperbolic_orderings()
        for exceptional in exceptional_orderings()
        if hyper == marked_hyperbolic_order() and exceptional == marked_exceptional_order()
    }
    predicate_marked = {
        merge_factor_permutation(hyper, exceptional, interleaving)
        for interleaving in interleaving_patterns()
        for hyper in hyperbolic_orderings()
        for exceptional in exceptional_orderings()
        if five_factor_predicate(merge_factor_permutation(hyper, exceptional, interleaving))
    }
    assert marked == predicate_marked
    assert len(marked) == 10


def test_formal_completion_marks_force_diagnostic_bridge_sector() -> None:
    _, diagnostic_states, marked_indices = build_marked_indices(MODE_FORMAL_COMPLETION)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, hyper_idx, exceptional_idx, glue_state, line_state, hyper_weight, exceptional_weight = diagnostic_states[index]
        assert hyperbolic_orderings()[hyper_idx] == marked_hyperbolic_order()
        assert exceptional_orderings()[exceptional_idx] == marked_exceptional_order()
        assert glue_state == NONZERO_GLUE
        assert line_state == HEAD_LINE
        assert hyper_weight == HYPERBOLIC_PASS
        assert exceptional_weight == EXCEPTIONAL_PASS


def test_current_shadow_marks_force_diagnostic_bridge_sector() -> None:
    _, diagnostic_states, marked_indices = build_marked_indices(MODE_CURRENT_SHADOW)
    assert len(marked_indices) == 20
    for index in marked_indices:
        _, _, hyper_idx, exceptional_idx, glue_state, line_state, hyper_weight, exceptional_weight = diagnostic_states[index]
        assert hyperbolic_orderings()[hyper_idx] == marked_hyperbolic_order()
        assert exceptional_orderings()[exceptional_idx] == marked_exceptional_order()
        assert glue_state == ZERO_GLUE
        assert line_state == HEAD_LINE
        assert hyper_weight == HYPERBOLIC_PASS
        assert exceptional_weight == EXCEPTIONAL_PASS
