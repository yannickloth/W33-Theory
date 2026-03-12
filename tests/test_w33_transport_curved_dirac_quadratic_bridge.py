from __future__ import annotations

from exploration.w33_transport_curved_dirac_quadratic_bridge import (
    build_transport_curved_dirac_quadratic_bridge_summary,
)


def test_internal_transport_curved_dirac_quadratic_profiles_are_exact() -> None:
    summary = build_transport_curved_dirac_quadratic_bridge_summary()
    transport, matter = summary["internal_profiles"]

    assert transport["name"] == "transport"
    assert transport["total_dimension"] == 12090
    assert transport["trace_d_squared"] == 74772
    assert transport["trace_d_fourth"] == 2116184

    assert matter["name"] == "matter_coupled"
    assert matter["total_dimension"] == 979290
    assert matter["trace_d_squared"] == 6056532
    assert matter["trace_d_fourth"] == 171410904


def test_seed_level_transport_and_matter_quadratic_coefficients_are_exact() -> None:
    summary = build_transport_curved_dirac_quadratic_bridge_summary()
    transport_cp2, transport_k3 = summary["transport_seed_profiles"]
    matter_cp2, matter_k3 = summary["matter_seed_profiles"]

    assert transport_cp2["quadratic_density_coefficient"]["exact"] == "39997843/3"
    assert transport_k3["quadratic_density_coefficient"]["exact"] == "36601793/3"
    assert matter_cp2["quadratic_density_coefficient"]["exact"] == "1079941761"
    assert matter_k3["quadratic_density_coefficient"]["exact"] == "988248411"


def test_sd1_transport_and_matter_quadratic_coefficients_are_exact() -> None:
    summary = build_transport_curved_dirac_quadratic_bridge_summary()
    transport_cp2, transport_k3 = summary["transport_sd1_profiles"]
    matter_cp2, matter_k3 = summary["matter_sd1_profiles"]

    assert transport_cp2["quadratic_density_coefficient"]["exact"] == "4701453583/360"
    assert transport_k3["quadratic_density_coefficient"]["exact"] == "5052856873/360"
    assert matter_cp2["quadratic_density_coefficient"]["exact"] == "42313082247/40"
    assert matter_k3["quadratic_density_coefficient"]["exact"] == "45475711857/40"


def test_first_refinement_contracts_cp2_k3_quadratic_gaps() -> None:
    summary = build_transport_curved_dirac_quadratic_bridge_summary()
    theorem = summary["quadratic_gap_theorem"]

    assert theorem["transport_seed_gap"]["exact"] == "3396050/3"
    assert theorem["transport_sd1_gap"]["exact"] == "3904481/4"
    assert theorem["transport_first_refinement_contracts_gap"] is True
    assert theorem["matter_seed_gap"]["exact"] == "91693350"
    assert theorem["matter_sd1_gap"]["exact"] == "316262961/4"
    assert theorem["matter_first_refinement_contracts_gap"] is True
