from exploration.w33_natural_units_neutral_shell_bridge import (
    build_natural_units_neutral_shell_summary,
)


def test_neutral_shell_closes_on_torus_packet():
    summary = build_natural_units_neutral_shell_summary()
    shell = summary["neutral_shell_dictionary"]
    facts = summary["exact_factorizations"]

    assert shell["neutral_numerator_formula"] == "q Theta(W33)"
    assert shell["neutral_reciprocal_formula"] == "(4 pi alpha) / g_Z^2 = q Theta(W33) / Phi_3^2"
    assert shell["neutral_numerator"] == 30
    assert shell["neutral_reciprocal"]["exact"] == "30/169"
    assert shell["ag21_length"] == 21
    assert shell["single_surface_flags"] == 84
    assert shell["complement_trace"] == 54
    assert all(facts.values())
