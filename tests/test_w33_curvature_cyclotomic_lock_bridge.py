from __future__ import annotations

from w33_curvature_cyclotomic_lock_bridge import build_curvature_cyclotomic_lock_summary


def test_gravity_and_topology_coefficients_have_exact_cyclotomic_factors() -> None:
    summary = build_curvature_cyclotomic_lock_summary()
    factors = summary["cyclotomic_factors"]
    gravity = summary["gravity_lock"]
    topology = summary["topology_lock"]

    assert factors == {
        "q": 3,
        "phi3": 13,
        "phi6": 7,
        "q_phi3": 39,
        "q_plus_1_phi6": 28,
        "q_cubic_plus_1": 28,
    }
    assert gravity["continuum_eh_coefficient"] == 320
    assert gravity["discrete_6_mode_coefficient"] == 12480
    assert gravity["q_phi3_factor"] == 39
    assert gravity["discrete_equals_q_phi3_times_continuum"] is True
    assert topology["absolute_euler_characteristic"] == 80
    assert topology["topological_1_mode_coefficient"] == 2240
    assert topology["q_plus_1_phi6_factor"] == 28
    assert topology["topological_equals_q_plus_1_phi6_times_abs_chi"] is True
    assert topology["equals_q_cubic_plus_1_times_abs_chi"] is True
