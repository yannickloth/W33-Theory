from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_enhancement_factor_search import (  # noqa: E402
    MODE_CURRENT_K3,
    MODE_FORMAL_COMPLETION,
    MODE_MINIMAL_ENHANCEMENT,
)
from toe_support_enhancement_relaxation_search import (  # noqa: E402
    build_marked_indices,
    build_mode_conjugacy_permutation,
    build_states,
    marked_enhancement_projection,
    marked_support_projection,
)
from toe_support_diagnostic_relaxation_search import (  # noqa: E402
    RELAXATION_BOTH,
    RELAXATION_CORE_ORDER,
    RELAXATION_EXACT,
    RELAXATION_INTERLEAVING,
    expected_marked_count,
)


def test_support_enhancement_state_space_is_exact() -> None:
    assert len(build_states()) == 360


def test_marked_count_formula_is_invariant_across_enhancement_modes() -> None:
    for mode in [MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION]:
        for relaxation in [
            RELAXATION_EXACT,
            RELAXATION_INTERLEAVING,
            RELAXATION_CORE_ORDER,
            RELAXATION_BOTH,
        ]:
            _states, marked_indices = build_marked_indices(mode, relaxation)
            assert len(marked_indices) == expected_marked_count(relaxation)


def test_support_projection_is_invariant_across_enhancement_modes() -> None:
    modes = [MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION]
    for relaxation in [
        RELAXATION_EXACT,
        RELAXATION_INTERLEAVING,
        RELAXATION_CORE_ORDER,
        RELAXATION_BOTH,
    ]:
        projections = [marked_support_projection(mode, relaxation) for mode in modes]
        assert projections[0] == projections[1] == projections[2]
        assert len(projections[0]) == expected_marked_count(relaxation)


def test_each_mode_keeps_exactly_one_enhancement_label() -> None:
    expected = {
        MODE_CURRENT_K3: {"current_k3_zero_orbit"},
        MODE_MINIMAL_ENHANCEMENT: {"minimal_external_enhancement"},
        MODE_FORMAL_COMPLETION: {"formal_completion_avatar"},
    }
    for mode, target in expected.items():
        for relaxation in [
            RELAXATION_EXACT,
            RELAXATION_INTERLEAVING,
            RELAXATION_CORE_ORDER,
            RELAXATION_BOTH,
        ]:
            assert marked_enhancement_projection(mode, relaxation) == target


def test_enhancement_modes_are_basis_conjugate_in_every_relaxation() -> None:
    modes = [MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION]
    relaxations = [
        RELAXATION_EXACT,
        RELAXATION_INTERLEAVING,
        RELAXATION_CORE_ORDER,
        RELAXATION_BOTH,
    ]

    for src_mode in modes:
        for dst_mode in modes:
            for relaxation in relaxations:
                states, src_marked = build_marked_indices(src_mode, relaxation)
                _states, dst_marked = build_marked_indices(dst_mode, relaxation)
                permutation = build_mode_conjugacy_permutation(src_mode, dst_mode, relaxation)

                assert len(permutation) == len(states)
                assert sorted(permutation) == list(range(len(states)))
                assert {permutation[idx] for idx in src_marked} == dst_marked
