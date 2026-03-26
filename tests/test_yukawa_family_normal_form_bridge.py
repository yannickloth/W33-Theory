from exploration.w33_yukawa_family_normal_form_bridge import (
    build_yukawa_family_normal_form_summary,
)


def test_yukawa_family_normal_form_summary():
    summary = build_yukawa_family_normal_form_summary()
    theorem = summary["finite_family_theorem"]

    assert theorem["transport_a2_slice_is_complete_oriented_triangle"] is True
    assert theorem["replicated_seed_current_packet_is_exact_4_plus_2_split"] is True
    assert theorem["active_quartet_is_star_at_distinguished_generation"] is True
    assert theorem["dormant_pair_is_opposite_bidirectional_edge"] is True
    assert theorem["generation_matrices_commute_exactly"] is True
    assert theorem["flag_basis_conjugates_generation_matrices_to_upper_unitriangular_form"] is True
    assert theorem["common_square_is_exact_central_e13_channel"] is True
    assert theorem["normal_form_is_exact_standard_upper_triangular_packet"] is True
    assert theorem["finite_family_side_has_exact_one_vs_two_normal_form"] is True

    graph = summary["a2_channel_graph"]
    assert graph["distinguished_generation"] == 2
    assert graph["doublet_generations"] == [0, 1]
    assert graph["active_quartet"] == [[0, 2], [1, 2], [2, 0], [2, 1]]
    assert graph["dormant_pair"] == [[0, 1], [1, 0]]

    normal = summary["generation_normal_form"]
    assert normal["plus_minus"] == [[1, 1, -2], [0, 1, 2], [0, 0, 1]]
    assert normal["minus_plus"] == [[1, -1, -2], [0, 1, -2], [0, 0, 1]]
    assert normal["common_square"] == [[0, 0, 2], [0, 0, 0], [0, 0, 0]]
