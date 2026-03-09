from w33_algebraic_spine import build_algebraic_spine


def test_local_qutrit_shell_matches_heisenberg_mub_picture():
    spine = build_algebraic_spine()
    local = spine.local_qutrit_shell

    assert local.base_vertex == 0
    assert local.neighbor_count == 12
    assert local.nonneighbor_count == 27
    assert local.mub_class_count == 4
    assert local.mub_class_sizes == (3, 3, 3, 3)
    assert local.h27_induced_degree == 8
    assert local.schlafli_parameters == (27, 16, 10, 8)
    assert local.fiber_count == 9
    assert local.fiber_size == 3
    assert local.missing_tritangent_count == 9
    assert local.generation_fiber_sizes == (9, 9, 9)
    assert local.omega_adjacency == (36, 36, 36)
    assert local.omega_non_adjacency == (99, 72, 72)


def test_global_pauli_geometry_is_exactly_w33():
    spine = build_algebraic_spine()
    global_geometry = spine.global_pauli_geometry

    assert global_geometry.projective_point_count == 40
    assert global_geometry.vertex_degree == 12
    assert global_geometry.edge_count == 240
    assert global_geometry.line_count == 40
    assert global_geometry.line_size == 4
    assert global_geometry.lines_per_point == 4
    assert global_geometry.srg_parameters == (40, 12, 2, 4)
    assert global_geometry.identity_isomorphism_holds is True
    assert global_geometry.label_match_count == 40


def test_s12_golay_monster_layer_closes_at_three_qutrit_sl27():
    spine = build_algebraic_spine()
    closure = spine.universal_closure

    assert closure.s12_total_nonzero_dim == 728
    assert closure.s12_grade_dimensions == (242, 243, 243)
    assert closure.s12_jacobi_failure_count == 6
    assert closure.s12_ad3_holds is True
    assert closure.golay_lie_dim == 24
    assert closure.golay_lie_is_perfect is True
    assert closure.golay_lie_center_dim == 0
    assert closure.golay_cartan_like_dim == 6
    assert closure.monster_extraspecial_order == 3**13
    assert closure.heisenberg_irrep_dim == 729
    assert closure.sl27_traceless_dim == 728
    assert closure.golay_lagrangian_isotropic is True


def test_tomotope_reye_bridge_carries_the_exact_12_16_obstruction_pattern():
    spine = build_algebraic_spine()
    bridge = spine.tomotope_reye_bridge

    assert bridge.tomotope_edges == 12
    assert bridge.tomotope_faces == 16
    assert bridge.tomotope_automorphism_order == 96
    assert bridge.reye_points == 12
    assert bridge.reye_lines == 16
    assert bridge.reye_point_degree == 4
    assert bridge.reye_valid_configs == 4
    assert bridge.tomotope_signature == (48, 6, 6, 6)
    assert bridge.axis_signature == (48, 12, 6)
    assert bridge.signatures_differ is True


def test_vogel_position_rules_out_naive_728_as_exceptional_line_hit():
    spine = build_algebraic_spine()
    vogel = spine.vogel_position

    assert 248 in vogel.positive_hit_dims
    assert 484 in vogel.positive_hit_dims
    assert 782 in vogel.positive_hit_dims
    assert vogel.grade0_dim == 242
    assert vogel.quotient_dim == 486
    assert vogel.total_nonzero_dim == 728
    assert vogel.grade0_in_positive_hit_set is False
    assert vogel.quotient_in_positive_hit_set is False
    assert vogel.total_in_positive_hit_set is False
    assert vogel.nearest_grade0_hit == 248
    assert vogel.nearest_quotient_hit == 484
    assert vogel.nearest_total_hit == 782
    assert vogel.total_classical_a_hits == (26,)


def test_exceptional_parameter_dictionary_matches_rosetta_tables_and_magic_square():
    spine = build_algebraic_spine()
    exceptional = spine.exceptional_parameter_dictionary

    assert exceptional.srg_parameters == (40, 12, 2, 4)
    assert exceptional.qutrit_order == 3
    assert exceptional.cubic_line_count == 27
    assert exceptional.complement_schlafli_edge_count == 135
    assert exceptional.tritangent_plane_count == 45
    assert exceptional.directed_meeting_edge_count == 270
    assert exceptional.stabilizer_order == 192
    assert exceptional.phi3_q == 13
    assert exceptional.a2_dim == 8
    assert exceptional.g2_dim == 14
    assert exceptional.f4_dim == 52
    assert exceptional.e6_dim == 78
    assert exceptional.e7_fund_dim == 56
    assert exceptional.e7_dim == 133
    assert exceptional.e8_dim == 248
    assert exceptional.z3_grade_dims == (86, 81, 81)
    assert exceptional.full_magic_square_dims == (
        (3, 8, 21, 52),
        (8, 16, 35, 78),
        (21, 35, 66, 133),
        (52, 78, 133, 248),
    )
    assert exceptional.octonionic_magic_square_dims == (52, 78, 133, 248)
    assert exceptional.full_magic_square_is_symmetric is True
    assert exceptional.formulas_match_magic_square is True


def test_route_recommendation_orders_the_qutrit_ladder_correctly():
    spine = build_algebraic_spine()
    route = spine.route_recommendation

    assert "local H27 Heisenberg/MUB shell (1 qutrit)" in route
    assert "W33 two-qutrit Pauli geometry" in route
    assert "three-qutrit sl(27) layer" in route
    assert "(40,12,2,4; q=3)" in route
    assert "octonionic magic-square row" in route
    assert "Vogel should be applied after Jacobi is resolved" in route
