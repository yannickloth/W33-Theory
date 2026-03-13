from __future__ import annotations

from w33_q3_curved_selection_bridge import build_q3_curved_selection_summary


def test_curved_gravity_and_topology_compression_select_q3_uniquely() -> None:
    summary = build_q3_curved_selection_summary()
    gravity = summary["curved_selection_equations"]["gravity_compression"]
    topology = summary["curved_selection_equations"]["topology_compression"]

    assert gravity["equation"] == "12 + 6 Phi_6(q) / q = 2 Phi_3(q)"
    assert gravity["polynomial"] == "q^3 - 2q^2 - 2q - 3"
    assert gravity["factorization"] == "(q - 3)(q^2 + q + 1)"
    assert gravity["unique_positive_integer_solution"] == 3

    assert topology["equation"] == "12 / q = q + 1"
    assert topology["polynomial"] == "q^2 + q - 12"
    assert topology["factorization"] == "(q - 3)(q + 4)"
    assert topology["unique_positive_integer_solution"] == 3


def test_sample_checks_only_hit_at_q3() -> None:
    summary = build_q3_curved_selection_summary()
    rows = {row["q"]: row for row in summary["sample_checks"]}
    assert rows[3]["gravity_condition_holds"] is True
    assert rows[3]["topology_condition_holds"] is True
    for q in (1, 2, 4, 5, 7, 11):
        assert rows[q]["gravity_condition_holds"] is False
        assert rows[q]["topology_condition_holds"] is False
