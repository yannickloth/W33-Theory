from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_support_diagnostic_relaxation_search import (  # noqa: E402
    RELAXATION_BOTH,
    RELAXATION_CORE_ORDER,
    RELAXATION_EXACT,
    RELAXATION_INTERLEAVING,
    build_marked_indices,
    expected_marked_count,
)


def test_expected_marked_counts_are_exact() -> None:
    assert expected_marked_count(RELAXATION_EXACT) == 2
    assert expected_marked_count(RELAXATION_INTERLEAVING) == 20
    assert expected_marked_count(RELAXATION_CORE_ORDER) == 12
    assert expected_marked_count(RELAXATION_BOTH) == 120


def test_marked_count_formula_holds_in_all_relaxation_modes() -> None:
    for relaxation in [
        RELAXATION_EXACT,
        RELAXATION_INTERLEAVING,
        RELAXATION_CORE_ORDER,
        RELAXATION_BOTH,
    ]:
        _states, marked_indices = build_marked_indices(relaxation)
        assert len(marked_indices) == expected_marked_count(relaxation)
