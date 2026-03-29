from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_diagnostic_relaxation_search import (  # noqa: E402
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
    build_relaxation_states,
    build_marked_indices,
    expected_marked_count,
)
from toe_bridge_line_factor_search import MODE_CURRENT_SHADOW, MODE_FORMAL_COMPLETION  # noqa: E402


def test_expected_marked_counts_are_exact() -> None:
    assert expected_marked_count(RELAXATION_EXACT) == 20
    assert expected_marked_count(RELAXATION_EXCEPTIONAL) == 40
    assert expected_marked_count(RELAXATION_HYPERBOLIC) == 120
    assert expected_marked_count(RELAXATION_BOTH) == 240


def test_relaxation_state_space_is_fixed_on_pass_pass_channel() -> None:
    _, diagnostic_states = build_relaxation_states()
    assert len(diagnostic_states) == 230400


def test_marked_count_formula_holds_in_formal_completion_mode() -> None:
    for relaxation in [
        RELAXATION_EXACT,
        RELAXATION_EXCEPTIONAL,
        RELAXATION_HYPERBOLIC,
        RELAXATION_BOTH,
    ]:
        _, _, marked_indices = build_marked_indices(MODE_FORMAL_COMPLETION, relaxation)
        assert len(marked_indices) == expected_marked_count(relaxation)


def test_marked_count_formula_holds_in_current_shadow_mode() -> None:
    for relaxation in [
        RELAXATION_EXACT,
        RELAXATION_EXCEPTIONAL,
        RELAXATION_HYPERBOLIC,
        RELAXATION_BOTH,
    ]:
        _, _, marked_indices = build_marked_indices(MODE_CURRENT_SHADOW, relaxation)
        assert len(marked_indices) == expected_marked_count(relaxation)
