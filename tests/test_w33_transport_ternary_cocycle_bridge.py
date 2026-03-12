from exploration.w33_transport_ternary_cocycle_bridge import (
    build_transport_ternary_cocycle_summary,
)


def test_extension_cocycle_is_exact_and_not_a_coboundary():
    summary = build_transport_ternary_cocycle_summary()
    cocycle = summary["extension_cocycle"]

    assert cocycle["field"] == "F3"
    assert cocycle["adapted_group_order"] == 6
    assert cocycle["adapted_matrices_upper_triangular"] is True
    assert cocycle["twisted_cocycle_identity_exact"] is True
    assert cocycle["cocycle_values_on_sign_trivial_subgroup"] == [0, 1, 2]
    assert cocycle["cocycle_values_on_sign_nontrivial_coset"] == [0, 1, 2]
    assert cocycle["cocycle_is_not_a_coboundary"] is True


def test_fiber_shift_realizes_the_extension_operatorially():
    summary = build_transport_ternary_cocycle_summary()
    operator = summary["fiber_nilpotent_operator"]

    assert operator["matrix"] == [[0, 1], [0, 0]]
    assert operator["rank"] == 1
    assert operator["square_zero"] is True
    assert operator["kernel_equals_image_equals_invariant_line"] is True
    assert operator["left_action_fixes_shift"] is True
    assert operator["right_action_twists_by_sign"] is True


def test_matter_extension_operator_has_rank_81_and_square_zero():
    summary = build_transport_ternary_cocycle_summary()
    operator = summary["matter_extension_operator"]

    assert operator["dimension"] == 162
    assert operator["rank"] == 81
    assert operator["nullity"] == 81
    assert operator["square_zero"] is True
    assert operator["image_dimension"] == 81
    assert operator["kernel_dimension"] == 81
    assert operator["image_equals_kernel"] is True
    assert operator["logical_qutrits"] == 81
