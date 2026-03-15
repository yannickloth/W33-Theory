from w33_theta_hierarchy_bridge import build_theta_hierarchy_summary


def test_theta_dictionary_is_exact() -> None:
    summary = build_theta_hierarchy_summary()
    theta = summary["theta_dictionary"]
    assert theta["srg_parameters"] == [40, 12, 2, 4]
    assert theta["least_eigenvalue"] == -4
    assert theta["lovasz_theta_formula"] == "-v*s/(k-s)"
    assert theta["lovasz_theta_alternate_formula"] == "v*mu/(k+mu)"
    assert theta["lovasz_theta"] == "10"
    assert theta["theta_complement"] == "4"
    assert theta["theta_times_theta_complement"] == "40"
    assert theta["theta_times_theta_complement_equals_v"] is True


def test_small_selector_is_inverse_theta_and_mu_over_v() -> None:
    summary = build_theta_hierarchy_summary()
    selector = summary["hierarchy_selector"]
    assert selector["small_selector_formula"] == "1/Theta(W33) = mu/v"
    assert selector["small_selector"] == "1/10"
    assert selector["mu_over_v"] == "1/10"
    assert selector["selector_matches_mu_over_v"] is True
    assert selector["selector_times_theta_is_unity"] is True


def test_truncated_shell_lock_matches_122_identity() -> None:
    summary = build_theta_hierarchy_summary()
    shell = summary["truncated_shell_lock"]
    assert shell["betti_numbers"] == [1, 81, 40]
    assert shell["zero_mode_count"] == 122
    assert shell["zero_mode_formula"] == "k^2 - k - Theta(W33)"
    assert shell["zero_mode_formula_value"] == 122
    assert shell["betti_sum_equals_formula"] is True
