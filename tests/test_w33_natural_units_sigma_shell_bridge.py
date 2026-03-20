from exploration.w33_natural_units_sigma_shell_bridge import (
    build_natural_units_sigma_shell_summary,
)


def test_sigma_shell_generates_trace_ladder():
    summary = build_natural_units_sigma_shell_summary()
    shell = summary["sigma_shell_dictionary"]
    ladder = summary["trace_ladder_dictionary"]
    facts = summary["exact_factorizations"]

    assert shell["sigma_formula"] == "sigma = 1 + q + R_K G_0"
    assert shell["sigma"] == 6
    assert shell["phi3_formula"] == "Phi_3 = sigma + Phi_6"

    assert ladder["metrology_trace"] == 12
    assert ladder["toroidal_trace"] == 42
    assert ladder["complement_trace"] == 54
    assert ladder["heawood_middle_rank"] == 12
    assert ladder["heawood_middle_trace"] == 36
    assert ladder["single_surface_flags"] == 84
    assert ladder["dual_pair_flags"] == 168
    assert ladder["full_heawood_order"] == 336

    assert all(facts.values())
