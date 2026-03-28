from w33_refined_k3_zero_orbit_bridge import (
    build_refined_k3_zero_orbit_bridge_summary,
)


def test_refined_k3_zero_orbit_bridge_summary() -> None:
    summary = build_refined_k3_zero_orbit_bridge_summary()
    theorem = summary["refined_k3_zero_orbit_theorem"]

    assert summary["current_refined_k3_transport_shadow"][
        "ordered_filtration_dimensions"
    ] == [81, 162, 81]
    assert summary["current_refined_k3_transport_shadow"]["extension_class_zero"] is True
    assert summary["current_refined_k3_transport_shadow"][
        "current_external_slot_state"
    ] == "zero_by_splitness"
    assert summary["current_refined_k3_transport_shadow"][
        "first_refinement_scale_factor"
    ] == 120
    assert theorem[
        "current_refined_k3_shadow_is_split_with_zero_extension_class"
    ] is True
    assert theorem[
        "current_refined_k3_shadow_remains_refinement_rigid_at_first_barycentric_step"
    ] is True
    assert theorem[
        "the_unique_nonzero_ternary_orbit_is_not_realized_on_the_current_refined_k3_side"
    ] is True
    assert theorem[
        "any_realization_of_the_unique_nonzero_orbit_requires_new_external_data_beyond_the_current_refined_k3_bridge"
    ] is True
