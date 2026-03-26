from exploration.w33_yukawa_generation_flag_bridge import (
    build_yukawa_generation_flag_summary,
)


def test_yukawa_generation_flag_summary():
    summary = build_yukawa_generation_flag_summary()
    theorem = summary["generation_flag_theorem"]

    assert theorem["both_nilpotent_parts_have_rank_2"] is True
    assert theorem["common_nilpotent_square_has_rank_1"] is True
    assert theorem["common_nilpotent_square_is_shared_exactly"] is True
    assert theorem["nilpotent_cubes_vanish"] is True
    assert theorem["common_line_equals_kernel_of_both_nilpotents"] is True
    assert theorem["common_line_equals_image_of_common_square"] is True
    assert theorem["common_plane_equals_kernel_of_common_square"] is True
    assert theorem["both_generation_matrices_preserve_common_line"] is True
    assert theorem["both_generation_matrices_preserve_common_plane"] is True
    assert theorem["orthogonal_heavy_line_is_complement_of_common_plane"] is True

    flag = summary["common_flag"]
    assert flag["line_generator"] == [1, 1, 0]
    assert flag["plane_basis"] == [[1, 1, 0], [0, 0, 1]]
    assert flag["orthogonal_heavy_generator"] == [1, -1, 0]
