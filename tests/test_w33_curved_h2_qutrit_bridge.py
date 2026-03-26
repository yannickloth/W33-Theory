from __future__ import annotations

from w33_curved_h2_qutrit_bridge import build_curved_h2_qutrit_bridge_summary


def _profile(summary: dict, name: str) -> dict:
    for profile in summary["seed_profiles"]:
        if profile["name"] == name:
            return profile
    raise AssertionError(f"missing seed profile {name}")


def test_curved_h2_qutrit_bridge_localizes_middle_degree_host() -> None:
    summary = build_curved_h2_qutrit_bridge_summary()
    assert summary["status"] == "ok"

    cp2 = _profile(summary, "CP2_9")
    k3 = _profile(summary, "K3_16")

    assert cp2["logical_qutrits"] == 81
    assert cp2["h2_dimension"] == 1
    assert cp2["b2_plus"] == 1
    assert cp2["b2_minus"] == 0
    assert cp2["total_middle_degree_qutrit_channel"] == 81
    assert cp2["positive_middle_degree_qutrit_channel"] == 81
    assert cp2["negative_middle_degree_qutrit_channel"] == 0
    assert cp2["rank2_h2_qutrit_branch_available"] is False
    assert cp2["mixed_sign_middle_degree_qutrit_channel_available"] is False

    assert k3["logical_qutrits"] == 81
    assert k3["h2_dimension"] == 22
    assert k3["b2_plus"] == 3
    assert k3["b2_minus"] == 19
    assert k3["total_middle_degree_qutrit_channel"] == 1782
    assert k3["positive_middle_degree_qutrit_channel"] == 243
    assert k3["negative_middle_degree_qutrit_channel"] == 1539
    assert k3["rank2_h2_qutrit_branch_available"] is True
    assert k3["mixed_sign_middle_degree_qutrit_channel_available"] is True

    constraints = summary["bridge_constraints"]
    assert constraints["logical_qutrits"] == 81
    assert constraints["cp2_middle_degree_qutrit_channel"] == 81
    assert constraints["k3_middle_degree_qutrit_channel"] == 1782
    assert constraints["k3_minus_cp2_middle_degree_gap"] == 1701
    assert constraints["cp2_is_not_rank2_middle_degree_host"] is True
    assert constraints["k3_is_rank2_middle_degree_host"] is True
    assert constraints["k3_has_both_middle_degree_sign_channels"] is True
    assert constraints["first_exact_middle_degree_qutrit_host_is_k3"] is True
