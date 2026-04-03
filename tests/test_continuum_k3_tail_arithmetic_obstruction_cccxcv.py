"""
Phase CCCXCV — Continuum K3 tail arithmetic obstruction.

CCCXCIV made the exact tail realization arithmetic on the fixed primitive line.
This phase promotes that arithmetic to the external/K3 wall itself: any genuine
K3-side realization must satisfy the fixed transport pair `(12,217)` on the
curvature-sensitive tail channel.
"""

from __future__ import annotations

from exploration.w33_continuum_k3_tail_arithmetic_obstruction_bridge import (
    build_continuum_k3_tail_arithmetic_obstruction_summary,
)


def test_phase_cccxcv_transport_pair_is_forced_on_k3_channel() -> None:
    theorem = build_continuum_k3_tail_arithmetic_obstruction_summary()[
        "continuum_k3_tail_arithmetic_obstruction_theorem"
    ]
    assert theorem[
        "any_exact_k3_side_realization_must_satisfy_the_transport_arithmetic_pair_lcm12_gcd217"
    ] is True


def test_phase_cccxcv_live_external_wall_is_arithmetic_obstruction() -> None:
    theorem = build_continuum_k3_tail_arithmetic_obstruction_summary()[
        "continuum_k3_tail_arithmetic_obstruction_theorem"
    ]
    assert theorem[
        "therefore_the_live_external_wall_is_existence_of_genuine_k3_data_satisfying_the_fixed_tail_arithmetic_obstruction"
    ] is True
