from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_cocycle_witness_bridge import (  # noqa: E402
    build_k3_mixed_plane_cocycle_witness_summary,
)


def test_mixed_plane_cocycle_witness_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_cocycle_witness_summary()
    witness = summary["mixed_plane_cocycle_witness"]
    assert witness["field"] == "F3"
    assert witness["adapted_group_order"] > 0
    assert witness["sign_trivial_cocycle_values"] != [0]
    assert witness["fiber_shift_matrix"] == [[0, 1], [0, 0]]
    assert witness["forced_slot_operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"


def test_mixed_plane_cocycle_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_cocycle_witness_summary()[
        "k3_mixed_plane_cocycle_witness_theorem"
    ]
    assert theorem[
        "the_exact_mixed_plane_fiber_shift_is_already_forced_by_the_transport_cocycle_package"
    ] is True
    assert theorem[
        "the_cocycle_is_nontrivial_precisely_because_it_is_nonzero_on_sign_trivial_elements"
    ] is True
    assert theorem[
        "a_single_support_preserving_nonzero_sign_trivial_cocycle_value_already_forces_the_nonzero_fiber_shift_witness"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_cocycle_value_witness_on_the_canonical_mixed_plane_host"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_sign_trivial_cocycle_witness_on_the_same_fixed_host"
    ] is True
