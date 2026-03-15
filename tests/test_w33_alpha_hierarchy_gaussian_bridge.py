from __future__ import annotations

from w33_alpha_hierarchy_gaussian_bridge import build_alpha_hierarchy_gaussian_summary


def test_nested_gaussian_shells_and_selector_split_are_exact() -> None:
    summary = build_alpha_hierarchy_gaussian_summary()
    shells = summary["nested_gaussian_shells"]
    split = summary["selector_split"]
    theorem = summary["gaussian_selector_theorem"]

    assert shells["outer_alpha_formula"] == "|(k-1) + i mu|^2"
    assert shells["outer_alpha_vector"] == [11, 4]
    assert shells["outer_alpha_norm"]["exact"] == "137"
    assert shells["inner_hierarchy_formula"] == "|mu + i|^2"
    assert shells["inner_hierarchy_vector"] == [4, 1]
    assert shells["inner_hierarchy_norm"]["exact"] == "17"
    assert shells["transport_prefactor"]["exact"] == "8"
    assert shells["up_sector_suppressor"]["exact"] == "136"

    assert split["alpha_tree_inverse"]["exact"] == "137"
    assert split["selector_line_dimension"]["exact"] == "1"
    assert split["vertex_correction_term"]["exact"] == "40/1111"
    assert split["alpha_tree_equals_up_sector_plus_selector"] is True
    assert split["alpha_tree_minus_one_equals_up_sector"] is True
    assert split["alpha_full_inverse"]["exact"] == "152247/1111"
    assert split["alpha_full_equals_nested_shell_plus_vertex_correction"] is True

    assert theorem["alpha_tree_is_outer_gaussian_norm"] is True
    assert theorem["up_sector_is_transport_times_inner_gaussian_norm"] is True
    assert theorem["vacuum_selector_supplies_the_missing_one"] is True
    assert theorem["full_alpha_is_selector_split_plus_vertex_correction"] is True


def test_charm_ratio_is_inverse_selector_reduced_tree_alpha() -> None:
    summary = build_alpha_hierarchy_gaussian_summary()
    lock = summary["hierarchy_lock"]

    assert lock["mc_over_mt"]["exact"] == "1/136"
    assert lock["mu_over_mc"]["exact"] == "1/544"
    assert lock["charm_ratio_is_inverse_selector_reduced_tree_alpha"] is True
    assert lock["second_up_step_is_extra_mu_factor"] is True
