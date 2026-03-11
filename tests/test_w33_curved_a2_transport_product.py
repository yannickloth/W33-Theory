from __future__ import annotations

import json
from pathlib import Path

from w33_curved_a2_transport_product import (
    a2_curved_product_profile,
    a2_internal_profile,
    a2_product_chain_density_limit,
    a2_product_heat_trace_direct,
    a2_product_heat_trace_factorized,
    a2_product_trace_density_limit,
    build_curved_a2_transport_product_summary,
    write_summary,
)


def test_a2_internal_profile_has_exact_positive_laplacian_data() -> None:
    profile = a2_internal_profile()
    assert profile.total_dimension == 90
    assert profile.laplacian_spectrum == {24: 20, 33: 64, 48: 6}
    assert profile.spectral_gap == 24
    assert profile.trace_laplacian == 2880
    assert profile.trace_laplacian_squared == 95040


def test_curved_a2_product_profiles_have_exact_dimensions_and_traces() -> None:
    cp2 = a2_curved_product_profile("CP2")
    k3 = a2_curved_product_profile("K3")
    assert cp2.total_dimension == 22950
    assert cp2.spectral_gap == 24
    assert cp2.zero_modes == 0
    assert cp2.trace_product == 889920
    assert k3.total_dimension == 153360
    assert k3.spectral_gap == 24
    assert k3.zero_modes == 0
    assert k3.trace_product == 6030720


def test_curved_a2_product_heat_trace_factorizes_exactly() -> None:
    for name in ("CP2", "K3"):
        for t in (0.05, 0.1, 0.2):
            direct = a2_product_heat_trace_direct(name, t)
            factorized = a2_product_heat_trace_factorized(name, t)
            assert abs(direct - factorized) < 1e-9


def test_a2_product_density_limits_are_exact() -> None:
    assert str(a2_product_chain_density_limit()) == "10800/19"
    assert str(a2_product_trace_density_limit()) == "423000/19"


def test_summary_records_curved_a2_bridge() -> None:
    summary = build_curved_a2_transport_product_summary()
    assert summary["status"] == "ok"
    assert summary["a2_internal_profile"]["spectral_gap"] == 24
    assert summary["curved_product_profiles"][0]["trace_product"] == 889920
    assert summary["curved_product_profiles"][1]["trace_product"] == 6030720
    assert summary["density_limits"]["a2_product_chain_density_per_top_simplex"]["exact"] == "10800/19"
    assert summary["density_limits"]["a2_product_trace_per_top_simplex"]["exact"] == "423000/19"
    assert "native A2 transport local system" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_curved_a2_transport_product_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["a2_internal_profile"]["total_dimension"] == 90
