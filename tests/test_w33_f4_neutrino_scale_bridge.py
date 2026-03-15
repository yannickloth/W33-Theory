from __future__ import annotations

from w33_f4_neutrino_scale_bridge import build_f4_neutrino_scale_summary


def test_f4_neutrino_scale_is_exact_exceptional_coefficient() -> None:
    summary = build_f4_neutrino_scale_summary()
    data = summary["exceptional_scale_dictionary"]
    theorem = summary["exceptional_scale_theorem"]

    assert data["f4_dimension"] == 52
    assert data["mr_over_vew"]["exact"] == "1/52"
    assert data["mnu_over_me_squared_if_dirac_seed_is_electron"]["exact"] == "26/123"

    assert theorem["f4_dimension_equals_phi3_times_mu"] is True
    assert theorem["f4_dimension_equals_v_plus_k"] is True
    assert theorem["majorana_scale_is_inverse_f4_dimension"] is True
    assert theorem["seesaw_coefficient_is_exact_f4_over_vew"] is True
    assert theorem["seesaw_coefficient_reduces_to_26_over_123"] is True
