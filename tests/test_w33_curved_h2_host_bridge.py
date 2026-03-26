from __future__ import annotations

from w33_curved_h2_host_bridge import build_curved_h2_host_bridge_summary


def _profile(summary: dict, name: str) -> dict:
    for profile in summary["seed_profiles"]:
        if profile["name"] == name:
            return profile
    raise AssertionError(f"missing seed profile {name}")


def test_curved_h2_host_bridge_sharpens_seed_level_host_constraints() -> None:
    summary = build_curved_h2_host_bridge_summary()
    assert summary["status"] == "ok"

    cp2 = _profile(summary, "CP2_9")
    k3 = _profile(summary, "K3_16")

    assert tuple(cp2["betti_numbers"]) == (1, 0, 1, 0, 1)
    assert cp2["signature"] == 1
    assert cp2["h2_dimension"] == 1
    assert cp2["b2_plus"] == 1
    assert cp2["b2_minus"] == 0
    assert cp2["six_mode"]["exact"] == "156/19"
    assert cp2["rank2_h2_branch_available"] is False
    assert cp2["mixed_sign_h2_plane_available"] is False
    assert cp2["six_mode_sign_matches_signature"] is True

    assert tuple(k3["betti_numbers"]) == (1, 0, 22, 0, 1)
    assert k3["signature"] == -16
    assert k3["h2_dimension"] == 22
    assert k3["b2_plus"] == 3
    assert k3["b2_minus"] == 19
    assert k3["six_mode"]["exact"] == "-880/19"
    assert k3["rank2_h2_branch_available"] is True
    assert k3["mixed_sign_h2_plane_available"] is True
    assert k3["six_mode_sign_matches_signature"] is True

    constraints = summary["bridge_constraints"]
    assert constraints["cp2_is_not_rank2_h2_host"] is True
    assert constraints["k3_is_rank2_h2_host"] is True
    assert constraints["cp2_has_definite_h2_signature"] is True
    assert constraints["k3_has_indefinite_h2_signature"] is True
    assert constraints["six_mode_sign_matches_signature_on_both_explicit_seeds"] is True
    assert constraints["first_explicit_rank2_h2_host_is_k3"] is True
