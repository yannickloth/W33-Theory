from exploration.w33_truncated_dirac_shell_bridge import build_truncated_dirac_shell_summary


def test_truncated_dirac_shell_zero_modes_and_betti() -> None:
    data = build_truncated_dirac_shell_summary()
    truncated = data["truncated_sector"]

    assert truncated["chain_dimensions"] == [40, 240, 160]
    assert truncated["total_dimension"] == 440
    assert truncated["boundary_ranks"] == [39, 120]
    assert truncated["betti_numbers"] == [1, 81, 40]
    assert truncated["zero_mode_count"] == 122
    assert truncated["lovasz_theta"] == 10
    assert truncated["zero_mode_formula"] == "k^2 - k - Theta(W33)"
    assert truncated["zero_mode_formula_value"] == 122
    assert truncated["zero_modes_equal_graph_formula"] is True


def test_truncated_dirac_shell_moments_and_ratios() -> None:
    data = build_truncated_dirac_shell_summary()
    shell = data["spectral_shell"]

    assert shell["d2_spectrum"] == {"0": 122, "4": 240, "10": 48, "16": 30}
    assert shell["f0"] == 440
    assert shell["f2"] == 1920
    assert shell["f4"] == 16320
    assert shell["f6"] == 186240
    assert shell["f2_over_f0"] == "48/11"
    assert shell["f4_over_f2"] == "17/2"
    assert shell["f6_over_f4"] == "194/17"
    assert shell["f2_over_f0_formula"] == "mu*k/(k-1)"
    assert shell["f4_over_f2_formula"] == "(k+mu+1)/2"
    assert shell["f2_over_f0_matches_formula"] is True
    assert shell["f4_over_f2_matches_formula"] is True
    assert shell["f2_equals_k_times_triangle_count"] is True
