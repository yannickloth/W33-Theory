from __future__ import annotations

import json
from pathlib import Path

from w33_curved_a2_quadratic_seed_bridge import (
    build_curved_a2_quadratic_seed_bridge_summary,
    external_second_moment_profile,
    product_quadratic_seed_profile,
    step_zero_second_order_heat_checks,
    write_summary,
)


def test_external_second_moments_match_combinatorial_recovery() -> None:
    cp2 = external_second_moment_profile("CP2")
    k3 = external_second_moment_profile("K3")
    assert cp2.external_trace == 1728
    assert cp2.external_second_moment == 13392
    assert cp2.combinatorial_equals_spectral is True
    assert k3.external_trace == 12480
    assert k3.external_second_moment == 128640
    assert k3.combinatorial_equals_spectral is True


def test_triangle_tetrahedron_degree_distributions_are_exact() -> None:
    cp2 = external_second_moment_profile("CP2")
    k3 = external_second_moment_profile("K3")
    assert cp2.boundary_square_layers[2].degree_distribution == {3: 21, 4: 27, 5: 27, 6: 9}
    assert k3.boundary_square_layers[2].degree_distribution == {3: 80, 4: 240, 7: 240}


def test_seed_level_quadratic_coefficients_are_exact() -> None:
    cp2 = product_quadratic_seed_profile("CP2")
    k3 = product_quadratic_seed_profile("K3")
    assert cp2.product_second_moment == 35393760
    assert cp2.constant_density == 1275 / 2
    assert cp2.linear_density == 24720
    assert cp2.quadratic_density_coefficient == 491580
    assert k3.product_second_moment == 245410560
    assert k3.constant_density == 1065 / 2
    assert k3.linear_density == 20940
    assert k3.quadratic_density_coefficient == 426060


def test_second_order_heat_prediction_improves_first_order() -> None:
    checks = step_zero_second_order_heat_checks()
    by_name = {}
    for check in checks:
        by_name.setdefault(check.external_name, []).append(check)
    for rows in by_name.values():
        for row in rows:
            assert row.second_order_abs_error < row.first_order_abs_error


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_curved_a2_quadratic_seed_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["product_quadratic_seed_profiles"][0]["quadratic_density_coefficient"]["exact"] == "491580"
    assert data["product_quadratic_seed_profiles"][1]["quadratic_density_coefficient"]["exact"] == "426060"
    assert "exact second-order seed data" in data["bridge_verdict"]


def test_summary_records_external_layers() -> None:
    summary = build_curved_a2_quadratic_seed_bridge_summary()
    cp2 = summary["external_second_moment_profiles"][0]
    k3 = summary["external_second_moment_profiles"][1]
    assert cp2["boundary_square_layers"][0]["coface_degree_square_sum"] == 576
    assert cp2["boundary_square_layers"][2]["boundary_square_trace"] == 2700
    assert k3["boundary_square_layers"][1]["coface_degree_square_sum"] == 23520
    assert k3["boundary_square_layers"][3]["boundary_square_trace"] == 8640
