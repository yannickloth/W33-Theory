from __future__ import annotations

from w33_mod12_selector_closure_bridge import build_mod12_selector_closure_summary


def test_mod12_selector_closure_bridge_closes_exactly() -> None:
    summary = build_mod12_selector_closure_summary()
    assert summary["status"] == "ok"

    shell = summary["mod12_selector_dictionary"]
    closures = summary["exact_closures"]

    assert shell["modulus"] == 12
    assert shell["nonzero_surface_residues_mod_12"] == [3, 4, 7]
    assert shell["q"] == 3
    assert shell["mu"] == 4
    assert shell["phi6"] == 7
    assert shell["theta_w33"] == 10
    assert shell["k_minus_one"] == 11
    assert shell["g2_dimension"] == 14
    assert shell["single_surface_flags"] == 84

    assert closures["residues_equal_q_mu_phi6"] is True
    assert closures["q_plus_mu_equals_phi6"] is True
    assert closures["q_plus_phi6_equals_theta"] is True
    assert closures["mu_plus_phi6_equals_k_minus_one"] is True
    assert closures["q_plus_mu_plus_phi6_equals_g2_dimension"] is True
    assert closures["q_times_mu_times_phi6_equals_single_surface_flags"] is True
    assert closures["modulus_equals_gauge_dimension"] is True
