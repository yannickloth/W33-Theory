from w33_transport_full_rank_glue_normal_form_bridge import (
    build_transport_full_rank_glue_normal_form_bridge_summary,
)


def test_transport_full_rank_glue_normal_form_bridge_summary() -> None:
    summary = build_transport_full_rank_glue_normal_form_bridge_summary()
    theorem = summary["transport_full_rank_glue_normal_form_theorem"]

    assert summary["fixed_polarized_shell"]["head_dimension"] == 81
    assert summary["fixed_polarized_shell"]["middle_dimension"] == 162
    assert summary["fixed_polarized_shell"]["tail_dimension"] == 81
    assert summary["fixed_polarized_shell"]["slot_direction"] == "tail_to_head"
    assert summary["fixed_polarized_shell"]["slot_shape"] == [81, 81]
    assert summary["fixed_polarized_shell"]["required_rank"] == 81
    assert summary["canonical_full_rank_completion_normal_form"][
        "slot_matrix_normal_form"
    ] == "I_81"
    assert summary["canonical_full_rank_completion_normal_form"][
        "polarized_nilpotent_normal_form"
    ] == "J2^81"
    assert theorem[
        "any_exact_completion_in_the_fixed_polarized_81_to_162_to_81_shell_has_full_rank_glue"
    ] is True
    assert theorem[
        "up_to_independent_head_tail_basis_change_any_full_rank_glue_completion_has_identity_slot_matrix"
    ] is True
    assert theorem[
        "up_to_polarized_isomorphism_any_exact_completion_has_canonical_jordan_normal_form_two_power_81"
    ] is True
    assert theorem[
        "the_remaining_transport_wall_is_existence_of_a_nonsplit_completion_not_glue_shape"
    ] is True
