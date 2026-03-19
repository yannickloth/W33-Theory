from __future__ import annotations

from w33_mod7_fano_duality_bridge import build_mod7_fano_duality_summary


def test_mod7_unit_partition_and_decimal_orbit() -> None:
    summary = build_mod7_fano_duality_summary()
    data = summary["mod7_dictionary"]
    assert data["modulus"] == 7
    assert data["quadratic_residues"] == [1, 2, 4]
    assert data["quadratic_nonresidues"] == [3, 5, 6]
    assert data["decimal_generator_mod_7"] == 3
    assert data["decimal_generator_order"] == 6
    assert data["decimal_square_mod_7"] == 2
    assert data["decimal_square_order"] == 3
    assert data["point_cycle_type"] == {"fixed": [0], "six_cycle": [1, 3, 2, 6, 4, 5]}


def test_residues_preserve_heptads_and_nonresidues_swap() -> None:
    summary = build_mod7_fano_duality_summary()
    action = summary["heptad_action"]
    assert action["standard_heptad_size"] == 7
    assert action["dual_heptad_size"] == 7
    assert action["residues_preserve_each_heptad"] is True
    assert action["nonresidues_swap_heptads"] is True
    for a in ("1", "2", "4"):
        assert action["affine_unit_actions"][a]["preserves_each_heptad"] is True
        assert action["affine_unit_actions"][a]["A_target_is_translation_invariant"] is True
        assert action["affine_unit_actions"][a]["B_target_is_translation_invariant"] is True
    for a in ("3", "5", "6"):
        assert action["affine_unit_actions"][a]["swaps_the_two_heptads"] is True
        assert action["affine_unit_actions"][a]["A_target_is_translation_invariant"] is True
        assert action["affine_unit_actions"][a]["B_target_is_translation_invariant"] is True


def test_decimal_and_translation_generate_full_affine_split() -> None:
    summary = build_mod7_fano_duality_summary()
    affine = summary["affine_group"]
    assert affine["full_affine_group_order"] == 42
    assert affine["heptad_preserver_subgroup_order"] == 21
    assert affine["heptad_duality_coset_order"] == 21
    assert affine["preserver_plus_duality_coset_equals_full_group"] is True
    assert affine["preserver_subgroup_matches_fano_flag_count"] is True
    assert affine["preserver_subgroup_matches_torus_edge_count"] is True
    assert affine["decimal_and_translation_generate_full_affine_group"] is True


def test_decimal_generator_is_the_duality_shadow() -> None:
    summary = build_mod7_fano_duality_summary()
    bridge = summary["decimal_duality_bridge"]
    assert bridge["repetend"] == "142857"
    assert bridge["decimal_powers_mod_7"] == [1, 3, 2, 6, 4, 5]
    assert bridge["decimal_power_targets_on_A"] == ["A", "B", "A", "B", "A", "B"]
    assert bridge["odd_decimal_powers_swap_heptads"] is True
    assert bridge["even_decimal_powers_preserve_heptads"] is True
    assert bridge["duality_quotient_pattern"] == [
        "preserve",
        "swap",
        "preserve",
        "swap",
        "preserve",
        "swap",
    ]
    assert bridge["c6_splits_into_c3_and_z2_shadow"] is True
