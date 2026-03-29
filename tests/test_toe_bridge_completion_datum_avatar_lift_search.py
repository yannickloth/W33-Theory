from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_QISKIT = ROOT / "tools" / "qiskit"
if str(TOOLS_QISKIT) not in sys.path:
    sys.path.insert(0, str(TOOLS_QISKIT))

from toe_bridge_completion_datum_avatar_lift_search import (  # noqa: E402
    FORMAL_COMPLETION_OBJECT,
    MODE_FORMAL_COMPLETION_OBJECT,
    MODE_SLOT_REPLACEMENT_DATUM,
    SLOT_REPLACEMENT_DATUM,
    build_marked_indices,
    build_mode_conjugacy_permutation,
    build_states,
    expected_marked_count,
    marked_lift_projection,
)
from toe_bridge_diagnostic_relaxation_search import (  # noqa: E402
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
)


def test_completion_datum_avatar_lift_state_space_is_exact() -> None:
    _support_permutations, _diagnostic_states, bridge_states = build_states()
    assert len(bridge_states) == 115200


def test_marked_count_formula_is_invariant_across_lift_modes() -> None:
    relaxations = [
        RELAXATION_EXACT,
        RELAXATION_EXCEPTIONAL,
        RELAXATION_HYPERBOLIC,
        RELAXATION_BOTH,
    ]
    for mode in [MODE_SLOT_REPLACEMENT_DATUM, MODE_FORMAL_COMPLETION_OBJECT]:
        for relaxation in relaxations:
            _support_permutations, _diagnostic_states, _bridge_states, marked = (
                build_marked_indices(mode, relaxation)
            )
            assert len(marked) == expected_marked_count(relaxation)


def test_lift_projection_matches_mode() -> None:
    assert marked_lift_projection(MODE_SLOT_REPLACEMENT_DATUM, RELAXATION_EXACT) == {
        SLOT_REPLACEMENT_DATUM
    }
    assert marked_lift_projection(MODE_FORMAL_COMPLETION_OBJECT, RELAXATION_EXACT) == {
        FORMAL_COMPLETION_OBJECT
    }


def test_mode_conjugacy_is_a_permutation_of_the_fixed_shell() -> None:
    permutation = build_mode_conjugacy_permutation(
        MODE_SLOT_REPLACEMENT_DATUM,
        MODE_FORMAL_COMPLETION_OBJECT,
    )
    assert sorted(permutation) == list(range(len(permutation)))
