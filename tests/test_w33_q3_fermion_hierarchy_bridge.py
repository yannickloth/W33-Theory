from __future__ import annotations

from w33_q3_fermion_hierarchy_bridge import build_q3_fermion_hierarchy_summary


def test_alpha_tree_and_fermion_hierarchy_lock() -> None:
    summary = build_q3_fermion_hierarchy_summary()
    lock = summary["electromagnetic_to_flavour_lock"]
    ratios = summary["dimensionless_hierarchy_ratios"]
    theorem = summary["fermion_hierarchy_theorem"]

    assert lock["alpha_tree_inverse"]["exact"] == "137"
    assert lock["gaussian_norm_mu_plus_i"]["exact"] == "17"
    assert lock["up_sector_suppressor"]["exact"] == "136"
    assert lock["vertex_correction_term"]["exact"] == "40/1111"
    assert lock["alpha_tree_minus_one_equals_up_sector_suppressor"] is True
    assert theorem["charm_suppressor_is_alpha_tree_minus_one"] is True

    assert ratios["mc_over_mt"]["exact"] == "1/136"
    assert ratios["mu_over_mc"]["exact"] == "1/544"
    assert theorem["up_second_step_is_extra_mu_factor"] is True


def test_down_and_lepton_hierarchy_ratios_are_exact_graph_packets() -> None:
    summary = build_q3_fermion_hierarchy_summary()
    ratios = summary["dimensionless_hierarchy_ratios"]
    theorem = summary["fermion_hierarchy_theorem"]

    assert ratios["mb_over_mc"]["exact"] == "13/4"
    assert ratios["ms_over_mb"]["exact"] == "1/44"
    assert ratios["md_over_ms"]["exact"] == "1/20"
    assert ratios["mmu_over_me"]["exact"] == "208"

    assert theorem["bottom_ratio_is_projective_plane_over_line"] is True
    assert theorem["strange_ratio_is_inverse_nonbacktracking_degree_times_mu"] is True
    assert theorem["down_ratio_is_lambda_over_v"] is True
    assert theorem["muon_ratio_is_phi3_mu_squared"] is True
