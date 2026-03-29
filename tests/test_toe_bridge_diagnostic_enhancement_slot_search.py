from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_diagnostic_enhancement_slot_search import (  # noqa: E402
    UNIQUE_NONZERO_SLOT,
    ZERO_SLOT,
    build_marked_indices,
    build_states,
    compatible_enhancement_slot_pairs,
    marked_pair_projection,
    target_slot_state,
)
from toe_bridge_diagnostic_relaxation_search import (  # noqa: E402
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
    expected_marked_count,
)
from toe_bridge_enhancement_factor_search import (  # noqa: E402
    CURRENT_K3_ZERO_ORBIT,
    FORMAL_COMPLETION_AVATAR,
    MINIMAL_EXTERNAL_ENHANCEMENT,
    MODE_CURRENT_K3,
    MODE_FORMAL_COMPLETION,
    MODE_MINIMAL_ENHANCEMENT,
    target_enhancement_state,
)


def test_diagnostic_enhancement_slot_state_space_is_exact() -> None:
    _support_permutations, states = build_states()
    assert len(states) == 172800


def test_enhancement_slot_pairs_are_exact() -> None:
    assert compatible_enhancement_slot_pairs() == [
        (CURRENT_K3_ZERO_ORBIT, ZERO_SLOT),
        (MINIMAL_EXTERNAL_ENHANCEMENT, UNIQUE_NONZERO_SLOT),
        (FORMAL_COMPLETION_AVATAR, UNIQUE_NONZERO_SLOT),
    ]


def test_marked_count_formula_is_invariant_across_modes() -> None:
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


def test_marked_pair_projection_matches_exact_mode_slot_law() -> None:
    for mode in [MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION]:
        pair_projection = marked_pair_projection(mode, RELAXATION_EXACT)
        assert pair_projection == {
            (target_enhancement_state(mode), target_slot_state(mode))
        }

