from __future__ import annotations

from w33_jones_mu4_selector_bridge import build_jones_mu4_selector_summary


def test_mu_equals_the_jones_boundary_value() -> None:
    summary = build_jones_mu4_selector_summary()
    data = summary["jones_dictionary"]
    selector = summary["selector_bridge"]

    assert data["jones_value_set"] == "{4 cos^2(pi/n) : n >= 3} union [4, infinity)"
    assert data["critical_boundary"]["exact"] == "4"
    assert data["mu"]["exact"] == "4"
    assert data["spectral_gap"]["exact"] == "4"
    assert data["external_dimension"]["exact"] == "4"
    assert selector["mu_equals_q_plus_one"] is True
    assert selector["mu_hits_jones_boundary"] is True
    assert selector["mu_equals_spectral_gap"] is True
    assert selector["mu_equals_external_dimension"] is True
    assert selector["positive_integer_solution_of_q_plus_one_equals_4"] == [3]
