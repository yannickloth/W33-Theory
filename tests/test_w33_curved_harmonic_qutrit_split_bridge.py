from __future__ import annotations

from w33_curved_harmonic_qutrit_split_bridge import (
    build_curved_harmonic_qutrit_split_bridge_summary,
)


def _profile(summary: dict, name: str) -> dict:
    for profile in summary["seed_profiles"]:
        if profile["name"] == name:
            return profile
    raise AssertionError(f"missing seed profile {name}")


def test_curved_harmonic_qutrit_split_bridge_is_middle_degree_exact() -> None:
    summary = build_curved_harmonic_qutrit_split_bridge_summary()
    assert summary["status"] == "ok"

    cp2 = _profile(summary, "CP2_9")
    k3 = _profile(summary, "K3_16")

    assert tuple(cp2["zero_modes_by_degree"]) == (1, 0, 1, 0, 1)
    assert cp2["endpoint_qutrit_channel"] == 162
    assert cp2["middle_degree_qutrit_channel"] == 81
    assert cp2["total_harmonic_qutrit_channel"] == 243
    assert cp2["seed_dependent_growth_above_endpoints"] == 81
    assert cp2["middle_fraction_of_total"]["exact"] == "1/3"

    assert tuple(k3["zero_modes_by_degree"]) == (1, 0, 22, 0, 1)
    assert k3["endpoint_qutrit_channel"] == 162
    assert k3["middle_degree_qutrit_channel"] == 1782
    assert k3["total_harmonic_qutrit_channel"] == 1944
    assert k3["seed_dependent_growth_above_endpoints"] == 1782
    assert k3["middle_fraction_of_total"]["exact"] == "11/12"

    constraints = summary["bridge_constraints"]
    assert constraints["logical_qutrits"] == 81
    assert constraints["universal_endpoint_qutrit_channel"] == 162
    assert constraints["endpoint_qutrit_channel_matches_on_all_explicit_seeds"] is True
    assert constraints["cp2_total_harmonic_qutrit_channel"] == 243
    assert constraints["k3_total_harmonic_qutrit_channel"] == 1944
    assert constraints["cp2_middle_degree_qutrit_channel"] == 81
    assert constraints["k3_middle_degree_qutrit_channel"] == 1782
    assert constraints["all_seed_dependence_is_middle_degree"] is True
    assert constraints["k3_minus_cp2_total_harmonic_gap"] == 1701
    assert constraints["k3_minus_cp2_middle_degree_gap"] == 1701
