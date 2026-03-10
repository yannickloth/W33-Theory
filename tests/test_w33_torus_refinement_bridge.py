from __future__ import annotations

import json
from pathlib import Path

from w33_torus_refinement_bridge import (
    build_heat_trace_comparisons,
    build_refinement_summary,
    continuum_torus4_heat_trace,
    discrete_circle_heat_trace,
    discrete_torus4_heat_trace,
    product_heat_trace_continuum,
    product_heat_trace_discrete,
    write_summary,
)


def test_discrete_torus4_heat_trace_is_the_fourth_power_of_the_circle_trace() -> None:
    one_d = discrete_circle_heat_trace(12, 0.1)
    four_d = discrete_torus4_heat_trace(12, 0.1)
    assert abs(four_d - one_d**4) < 1e-12


def test_external_heat_trace_error_decreases_with_n_for_each_sample_t() -> None:
    rows = build_heat_trace_comparisons()
    by_t: dict[float, list[float]] = {}
    for row in rows:
        by_t.setdefault(row.t, []).append(row.external_abs_error)
    for errors in by_t.values():
        assert errors == sorted(errors, reverse=True)


def test_product_heat_trace_error_decreases_with_n_for_each_sample_t() -> None:
    rows = build_heat_trace_comparisons()
    by_t: dict[float, list[float]] = {}
    for row in rows:
        by_t.setdefault(row.t, []).append(row.product_abs_error)
    for errors in by_t.values():
        assert errors == sorted(errors, reverse=True)


def test_product_heat_trace_is_external_times_internal_limit() -> None:
    t = 0.1
    discrete = product_heat_trace_discrete(24, t)
    continuum = product_heat_trace_continuum(t)
    assert discrete > 0.0
    assert continuum > 0.0
    assert abs(discrete - continuum) < 0.1


def test_summary_contains_convergence_rows() -> None:
    summary = build_refinement_summary()
    assert summary["status"] == "ok"
    assert len(summary["comparisons"]) == 12
    assert "product factorization" in summary["verdict"]
    first = summary["comparisons"][0]
    assert first["n"] == 8
    assert first["t"] == 0.05


def test_continuum_reference_is_stable_and_positive() -> None:
    assert continuum_torus4_heat_trace(0.05) > 0.0
    assert continuum_torus4_heat_trace(0.2) > 0.0


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_torus_refinement_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert len(data["comparisons"]) == 12
