from __future__ import annotations

from exploration.w33_transport_curved_dirac_refinement_bridge import (
    build_transport_curved_dirac_refinement_summary,
)


def test_transport_curved_dirac_profile_is_exact() -> None:
    summary = build_transport_curved_dirac_refinement_summary()
    bridge = summary["transport_curved_dirac"]

    assert bridge["c0_dimension"] == 90
    assert bridge["c1_dimension"] == 1440
    assert bridge["c2_dimension"] == 10560
    assert bridge["total_dimension"] == 12090
    assert bridge["trace_l0"] == 3276
    assert bridge["trace_l1"] == 37386
    assert bridge["trace_l2"] == 34110
    assert bridge["trace_d_squared"] == 74772
    assert bridge["curvature_corner_rank"] == 42
    assert bridge["cocycle_corner_rank"] == 36
    assert bridge["symmetric_dirac_by_construction"] is True


def test_matter_coupled_curved_dirac_profile_scales_exactly() -> None:
    summary = build_transport_curved_dirac_refinement_summary()
    bridge = summary["matter_coupled_curved_dirac"]

    assert bridge["logical_qutrits"] == 81
    assert bridge["total_dimension"] == 979290
    assert bridge["trace_d_squared"] == 6056532
    assert bridge["curvature_corner_rank"] == 3402
    assert bridge["protected_flat_subsector_dimension"] == 81
    assert bridge["protected_flat_curved_harmonic_lifts"] == {
        "CP2_9": 243,
        "K3_16": 1944,
    }


def test_transport_first_order_curved_refinement_limits_and_cp2_values() -> None:
    summary = build_transport_curved_dirac_refinement_summary()
    cp2 = summary["curved_refinement_first_order_bridge"]["transport"][0]

    assert cp2["constant_term_formula"]["limit"]["exact"] == "1450800/19"
    assert cp2["constant_term_formula"]["corr_20_power_r"]["exact"] == "157170/19"
    assert cp2["constant_term_formula"]["corr_120_power_r"]["exact"] == "2015/2"
    assert cp2["linear_term_formula"]["limit"]["exact"] == "19370040/19"
    assert cp2["linear_term_formula"]["corr_20_power_r"]["exact"] == "1600716/19"
    assert cp2["linear_term_formula"]["corr_120_power_r"]["exact"] == "6231"
    assert cp2["samples"][0]["constant_term"]["exact"] == "171275/2"
    assert cp2["samples"][0]["linear_term"]["exact"] == "1109955"


def test_matter_coupled_first_order_curved_refinement_limits_and_k3_values() -> None:
    summary = build_transport_curved_dirac_refinement_summary()
    k3 = summary["curved_refinement_first_order_bridge"]["matter_coupled"][1]

    assert k3["constant_term_formula"]["limit"]["exact"] == "117514800/19"
    assert k3["constant_term_formula"]["corr_20_power_r"]["exact"] == "-8976825/19"
    assert k3["constant_term_formula"]["corr_120_power_r"]["exact"] == "163215/2"
    assert k3["linear_term_formula"]["limit"]["exact"] == "1568973240/19"
    assert k3["linear_term_formula"]["corr_20_power_r"]["exact"] == "-91425510/19"
    assert k3["linear_term_formula"]["corr_120_power_r"]["exact"] == "504711"
    assert k3["samples"][0]["constant_term"]["exact"] == "11588265/2"
    assert k3["samples"][0]["linear_term"]["exact"] == "78270381"
