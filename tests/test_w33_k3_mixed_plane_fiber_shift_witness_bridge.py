from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_fiber_shift_witness_bridge import (  # noqa: E402
    build_k3_mixed_plane_fiber_shift_witness_summary,
)


def test_mixed_plane_fiber_shift_witness_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_fiber_shift_witness_summary()
    witness = summary["mixed_plane_fiber_shift_witness"]
    assert witness["fiber_shift_matrix"] == [[0, 1], [0, 0]]
    assert witness["fiber_rank"] == 1
    assert witness["fiber_square_zero"] is True
    assert witness["fiber_kernel_equals_image_equals_invariant_line"] is True
    assert witness["qutrit_lift_dimension"] == 81
    assert witness["forced_slot_operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
    assert witness["nonzero_orbit_size"] == 2


def test_mixed_plane_fiber_shift_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_fiber_shift_witness_summary()[
        "k3_mixed_plane_fiber_shift_witness_theorem"
    ]
    assert theorem[
        "the_exact_mixed_plane_operator_witness_is_already_the_qutrit_lift_of_the_reduced_fiber_shift"
    ] is True
    assert theorem[
        "the_only_genuinely_nontrivial_part_of_the_operator_witness_is_the_nonzero_fiber_shift_n"
    ] is True
    assert theorem[
        "up_to_the_natural_gauge_there_is_only_one_nonzero_fiber_shift_orbit_available"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_nonzero_fiber_shift_witness_on_the_canonical_mixed_plane_host"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_mixed_plane_fiber_shift_witness_on_the_same_fixed_host"
    ] is True
