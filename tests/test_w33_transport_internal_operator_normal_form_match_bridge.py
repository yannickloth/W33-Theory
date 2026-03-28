from w33_transport_internal_operator_normal_form_match_bridge import (
    build_transport_internal_operator_normal_form_match_bridge_summary,
)


def test_transport_internal_operator_normal_form_match_bridge_summary() -> None:
    summary = build_transport_internal_operator_normal_form_match_bridge_summary()
    theorem = summary["transport_internal_operator_normal_form_match_theorem"]

    assert summary["internal_transport_operator_normal_form"][
        "fiber_shift_matrix"
    ] == [[0, 1], [0, 0]]
    assert summary["internal_transport_operator_normal_form"][
        "logical_qutrits"
    ] == 81
    assert summary["internal_transport_operator_normal_form"]["dimension"] == 162
    assert summary["internal_transport_operator_normal_form"]["rank"] == 81
    assert summary["internal_transport_operator_normal_form"]["nullity"] == 81
    assert summary["internal_transport_operator_normal_form"]["operator_model"] == (
        "I_81 ⊗ [[0,1],[0,0]]"
    )
    assert summary["external_completion_normal_form"]["slot_matrix_normal_form"] == (
        "I_81"
    )
    assert summary["external_completion_normal_form"][
        "polarized_nilpotent_normal_form"
    ] == "J2^81"
    assert theorem[
        "internal_transport_extension_has_exact_operator_normal_form_i81_tensor_fiber_shift"
    ] is True
    assert theorem[
        "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge"
    ] is True
    assert theorem[
        "the_remaining_transport_wall_is_realization_of_the_nontrivial_cocycle_class_not_operator_shape"
    ] is True
