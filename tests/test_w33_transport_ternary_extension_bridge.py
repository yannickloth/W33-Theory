from exploration.w33_transport_ternary_extension_bridge import (
    build_transport_ternary_extension_summary,
)


def test_reduced_transport_module_is_nonsplit_extension():
    summary = build_transport_ternary_extension_summary()
    module = summary["reduced_transport_module"]

    assert module["field"] == "F3"
    assert module["holonomy_group_order"] == 6
    assert module["projective_line_count"] == 4
    assert module["unique_invariant_line"] == [1, 2]
    assert module["invariant_projective_line_count"] == 1
    assert module["invariant_complement_count"] == 0
    assert module["is_nonsplit_extension_of_sign_by_trivial"]


def test_module_characters_match_trivial_and_sign_layers():
    summary = build_transport_ternary_extension_summary()
    module = summary["reduced_transport_module"]

    assert module["adapted_group_is_upper_triangular"]
    assert module["top_character_values"] == [1]
    assert module["quotient_character_values"] == [1, 2]
    assert module["quotient_character_equals_determinant_character"]
    assert module["nonsplit_extension_witness_count"] == 4


def test_matter_flavour_short_exact_sequence_has_dimensions_81_162_81():
    summary = build_transport_ternary_extension_summary()
    extension = summary["matter_flavour_extension"]

    assert extension["base_logical_qutrits"] == 81
    assert extension["submodule_dimension"] == 81
    assert extension["total_dimension"] == 162
    assert extension["quotient_dimension"] == 81
    assert extension["short_exact_sequence_dimensions"] == [81, 162, 81]
    assert extension["matches_flat_internal_dimension_exactly"]
