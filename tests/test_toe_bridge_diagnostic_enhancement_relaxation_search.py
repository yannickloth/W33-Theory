from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_diagnostic_enhancement_relaxation_search import (  # noqa: E402
    build_marked_indices,
    build_mode_conjugacy_permutation,
    build_states,
)
from toe_bridge_diagnostic_relaxation_search import (  # noqa: E402
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
    expected_marked_count,
)
from toe_bridge_enhancement_factor_search import (  # noqa: E402
    MODE_CURRENT_K3,
    MODE_FORMAL_COMPLETION,
    MODE_MINIMAL_ENHANCEMENT,
)


def test_diagnostic_enhancement_state_space_is_exact() -> None:
    _support_permutations, states = build_states()
    assert len(states) == 86400


def test_marked_count_formula_is_invariant_across_enhancement_modes() -> None:
    relaxations = [
        RELAXATION_EXACT,
        RELAXATION_EXCEPTIONAL,
        RELAXATION_HYPERBOLIC,
        RELAXATION_BOTH,
    ]
    for mode in [MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION]:
        for relaxation in relaxations:
            _support_permutations, _states, marked_indices = build_marked_indices(mode, relaxation)
            assert len(marked_indices) == expected_marked_count(relaxation)


def test_enhancement_modes_are_basis_conjugate_in_every_relaxation() -> None:
    modes = [MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION]
    relaxations = [
        RELAXATION_EXACT,
        RELAXATION_EXCEPTIONAL,
        RELAXATION_HYPERBOLIC,
        RELAXATION_BOTH,
    ]

    for src_mode in modes:
        for dst_mode in modes:
            for relaxation in relaxations:
                _support_permutations, states, src_marked = build_marked_indices(src_mode, relaxation)
                _support_permutations, _states, dst_marked = build_marked_indices(dst_mode, relaxation)
                permutation = build_mode_conjugacy_permutation(src_mode, dst_mode, relaxation)

                assert len(permutation) == len(states)
                assert sorted(permutation) == list(range(len(states)))
                assert {permutation[idx] for idx in src_marked} == dst_marked
