from __future__ import annotations

from w33_lie_tower_s12_bridge import build_lie_tower_s12_bridge_summary


def test_s12_grade_only_obstruction_is_exactly_six_oriented_channels() -> None:
    summary = build_lie_tower_s12_bridge_summary()
    s12_bridge = summary["s12_grade_only_model"]

    assert s12_bridge["total_nonzero_dimension"] == 728
    assert s12_bridge["grade_split"] == [242, 243, 243]
    assert s12_bridge["jacobi_failure_count"] == 6
    assert s12_bridge["nonuniform_grade_failures_are_exactly_six"] is True
    assert s12_bridge["oriented_generation_graph_complete"] is True
    assert {tuple(row["grades"]) for row in s12_bridge["jacobi_failures"]} == {
        (1, 1, 2),
        (1, 2, 1),
        (1, 2, 2),
        (2, 1, 1),
        (2, 1, 2),
        (2, 2, 1),
    }
    assert {tuple(row["oriented_generation_channel"]) for row in s12_bridge["jacobi_failures"]} == {
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
    }


def test_s12_grade_split_is_uniquely_the_sl27_block_cyclic_partition() -> None:
    summary = build_lie_tower_s12_bridge_summary()
    sl27_bridge = summary["sl27_z3_bridge"]

    assert sl27_bridge["match_count"] == 1
    assert sl27_bridge["unique_partition"] == [9, 9, 9]
    assert sl27_bridge["n"] == 27
    assert sl27_bridge["a_family_rank"] == 26
    assert sl27_bridge["grade0"] == 242
    assert sl27_bridge["grade1"] == 243
    assert sl27_bridge["grade2"] == 243
    assert sl27_bridge["total_dimension"] == 728
    assert sl27_bridge["bridge_claim_holds"] is True


def test_l6_asymmetric_sectors_and_a2_modes_share_the_same_channel_set() -> None:
    summary = build_lie_tower_s12_bridge_summary()
    l6_bridge = summary["l6_asymmetric_a2_bridge"]
    shared = summary["shared_channel_dictionary"]

    assert l6_bridge["democratic_pattern"] == [0, 0, 1, 1, 2, 2]
    assert l6_bridge["asymmetric_patterns_are_all_123_multiplicity_permutations"] is True
    assert l6_bridge["a2_mode_indices"] == [8, 9, 127, 128, 246, 247]
    assert l6_bridge["current_linearized_l6_bridge_activates_only_cartan_modes"] is True
    assert shared["exact_channel_set_matches_across_layers"] is True
    assert shared["complete_oriented_generation_graph"] == [
        [0, 1],
        [0, 2],
        [1, 0],
        [1, 2],
        [2, 0],
        [2, 1],
    ]


def test_s12_l6_a2_crosswalk_is_exact() -> None:
    summary = build_lie_tower_s12_bridge_summary()
    crosswalk = summary["shared_channel_dictionary"]["crosswalk"]

    assert crosswalk == [
        {
            "oriented_generation_channel": (0, 1),
            "s12_failure_grades": (1, 1, 2),
            "l6_asymmetric_pattern": (0, 0, 0, 1, 2, 2),
            "l6_a2_mode_index": 127,
        },
        {
            "oriented_generation_channel": (0, 2),
            "s12_failure_grades": (2, 1, 2),
            "l6_asymmetric_pattern": (0, 0, 0, 1, 1, 2),
            "l6_a2_mode_index": 8,
        },
        {
            "oriented_generation_channel": (1, 0),
            "s12_failure_grades": (2, 2, 1),
            "l6_asymmetric_pattern": (0, 1, 1, 1, 2, 2),
            "l6_a2_mode_index": 128,
        },
        {
            "oriented_generation_channel": (1, 2),
            "s12_failure_grades": (2, 1, 1),
            "l6_asymmetric_pattern": (0, 0, 1, 1, 1, 2),
            "l6_a2_mode_index": 9,
        },
        {
            "oriented_generation_channel": (2, 0),
            "s12_failure_grades": (1, 2, 1),
            "l6_asymmetric_pattern": (0, 1, 1, 2, 2, 2),
            "l6_a2_mode_index": 247,
        },
        {
            "oriented_generation_channel": (2, 1),
            "s12_failure_grades": (1, 2, 2),
            "l6_asymmetric_pattern": (0, 0, 1, 2, 2, 2),
            "l6_a2_mode_index": 246,
        },
    ]


def test_monster_heisenberg_closure_supplies_the_phase_resolution_mechanism() -> None:
    summary = build_lie_tower_s12_bridge_summary()
    closure = summary["monster_heisenberg_closure"]

    assert closure["available"] is True
    assert closure["monster_class"] == "3B"
    assert closure["extraspecial_order"] == 3**13
    assert closure["heisenberg_irrep_dimension"] == 729
    assert closure["golay_codewords"] == 729
    assert closure["golay_nonzero_codewords"] == 728
    assert closure["sl27_traceless_dimension"] == 728
    assert closure["two_suz_sp12_dimension"] == 12
    assert closure["golay_is_lagrangian"] is True
    assert closure["phase_resolution_mechanism_exact"] is True
