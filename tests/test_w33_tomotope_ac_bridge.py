from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from w33_tomotope_ac_bridge import (
    build_bridge_level,
    build_bridge_summary,
    cycle_laplacian_eigenvalues,
    external_growth_degree,
    external_heat_trace,
    product_heat_trace,
    product_squared_eigenvalues,
    tomotope_carrier_growth_degree,
    torus4_laplacian_eigenvalues,
    w33_internal_dirac_squared_eigenvalues,
    write_summary,
)


def test_cycle_and_torus_counts_match_4d_cartesian_family() -> None:
    cycle = cycle_laplacian_eigenvalues(5)
    torus = torus4_laplacian_eigenvalues(5)
    assert cycle.shape == (5,)
    assert torus.shape == (5**4,)
    assert np.count_nonzero(np.isclose(torus, 0.0)) == 1


def test_internal_dirac_square_has_expected_dimension() -> None:
    eigs = w33_internal_dirac_squared_eigenvalues()
    assert eigs.shape == (162,)
    assert np.all(eigs >= -1e-10)


def test_product_spectrum_has_tensor_product_dimension() -> None:
    eigs = product_squared_eigenvalues(3)
    assert eigs.shape == (3**4 * 162,)
    assert np.all(eigs >= -1e-10)


def test_product_heat_trace_factorizes_exactly() -> None:
    t = 0.1
    direct = product_heat_trace(4, t)
    factored = external_heat_trace(4, t) * float(np.sum(np.exp(-t * w33_internal_dirac_squared_eigenvalues())))
    assert abs(direct - factored) < 1e-8


def test_external_growth_is_quartic_while_tomotope_growth_is_cubic() -> None:
    assert math.isclose(external_growth_degree(), 4.0, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(tomotope_carrier_growth_degree(), 3.0, rel_tol=0.0, abs_tol=1e-12)


def test_bridge_level_separates_external_and_internal_scales() -> None:
    level = build_bridge_level(external_n=4, tomotope_k=2)
    assert level.external_vertex_count == 4**4
    assert level.external_degree == 8
    assert level.internal_hilbert_dim == 162
    assert level.product_hilbert_dim == (4**4) * 162
    assert level.tomotope_unit_cube_count == 64
    assert level.factorization_error_at_t_0_1 < 1e-8


def test_summary_verdict_keeps_tomotope_internal_and_4d_external_roles_distinct() -> None:
    summary = build_bridge_summary(external_n=4, tomotope_k=2)
    assert summary["product_operator"]["heat_trace_factorizes"] is True
    assert summary["bridge_level"]["external_growth_degree"] == 4.0
    assert summary["bridge_level"]["tomotope_carrier_growth_degree"] == 3.0
    assert "quartic scale parameter" in summary["verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_tomotope_ac_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["bridge_level"]["product_hilbert_dim"] == (4**4) * 162
