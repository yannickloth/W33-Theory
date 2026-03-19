from __future__ import annotations

from w33_affine_middle_shell_bridge import build_affine_middle_shell_summary


def test_affine_middle_shell_bridge_closes_exactly() -> None:
    summary = build_affine_middle_shell_summary()
    assert summary["status"] == "ok"

    shell = summary["affine_middle_shell_dictionary"]
    factors = summary["exact_factorizations"]

    assert shell["duality_factor"] == 2
    assert shell["q"] == 3
    assert shell["phi6"] == 7
    assert shell["ag21_length"] == 21
    assert shell["g2_dimension"] == 14
    assert shell["shared_six_channel"] == 6
    assert shell["affine_shell_order"] == 42

    assert factors["affine_shell_equals_2_times_ag21"] is True
    assert factors["affine_shell_equals_q_times_g2"] is True
    assert factors["affine_shell_equals_shared_six_times_phi6"] is True
    assert factors["ag21_equals_3_times_phi6"] is True
    assert factors["g2_equals_2_times_phi6"] is True
    assert factors["shared_six_equals_2_times_q"] is True
