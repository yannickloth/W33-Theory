from __future__ import annotations

import json
from pathlib import Path

from w33_curved_a2_heat_density_asymptotics import (
    a2_product_chain_density_formula,
    a2_product_trace_density_formula,
    build_curved_a2_heat_density_asymptotics_summary,
    step_zero_heat_checks,
    write_summary,
)


def test_exact_closed_forms_match_step_zero_cp2_and_k3_data() -> None:
    assert a2_product_chain_density_formula(9, 0) == 1275 / 2
    assert a2_product_trace_density_formula(9, 0) == 24720
    assert a2_product_chain_density_formula(16, 0) == 1065 / 2
    assert a2_product_trace_density_formula(16, 0) == 20940


def test_universal_limits_and_first_corrections_are_exact() -> None:
    summary = build_curved_a2_heat_density_asymptotics_summary()
    cp2 = summary["seed_closed_forms"][0]
    k3 = summary["seed_closed_forms"][1]
    assert summary["persistent_gap_theorem"]["product_gap_for_all_refinement_steps"] == 24
    assert summary["universal_limits"]["constant_term_per_top_simplex"]["exact"] == "10800/19"
    assert summary["universal_limits"]["linear_term_per_top_simplex"]["exact"] == "423000/19"
    assert cp2["constant_term_formula"]["corr_20_power_r"]["exact"] == "1170/19"
    assert cp2["constant_term_formula"]["corr_120_power_r"]["exact"] == "15/2"
    assert cp2["linear_term_formula"]["corr_20_power_r"]["exact"] == "42120/19"
    assert cp2["linear_term_formula"]["corr_120_power_r"]["exact"] == "240"
    assert k3["constant_term_formula"]["corr_20_power_r"]["exact"] == "-825/19"
    assert k3["constant_term_formula"]["corr_120_power_r"]["exact"] == "15/2"
    assert k3["linear_term_formula"]["corr_20_power_r"]["exact"] == "-29700/19"
    assert k3["linear_term_formula"]["corr_120_power_r"]["exact"] == "240"


def test_density_samples_converge_to_universal_limits() -> None:
    summary = build_curved_a2_heat_density_asymptotics_summary()
    for seed in summary["seed_closed_forms"]:
        constant_errors = [sample["constant_abs_error"]["float"] for sample in seed["samples"]]
        linear_errors = [sample["linear_abs_error"]["float"] for sample in seed["samples"]]
        assert constant_errors[-1] < constant_errors[0]
        assert linear_errors[-1] < linear_errors[0]


def test_step_zero_direct_heat_density_matches_first_order_prediction_at_small_t() -> None:
    checks = step_zero_heat_checks()
    by_name = {}
    for check in checks:
        by_name.setdefault(check.external_name, []).append(check)
    for rows in by_name.values():
        rows.sort(key=lambda row: row.t)
        assert rows[0].abs_error < rows[-1].abs_error


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_curved_a2_heat_density_asymptotics_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["persistent_gap_theorem"]["internal_gap"] == 24
    assert "exact first-order heat-density asymptotics" in data["bridge_verdict"]
