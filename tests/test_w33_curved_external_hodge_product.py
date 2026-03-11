from __future__ import annotations

import json
from pathlib import Path

from w33_curved_external_hodge_product import (
    build_curved_external_hodge_product_summary,
    build_product_heat_checks,
    external_dirac_kahler_squared_eigenvalues,
    external_heat_trace,
    external_operator_profile,
    product_heat_trace_direct,
    product_heat_trace_factorized,
    write_summary,
)


def test_cp2_external_operator_profile_has_expected_harmonic_sector() -> None:
    profile = external_operator_profile("CP2")
    assert profile.chain_dimensions == (9, 36, 84, 90, 36)
    assert profile.zero_modes_by_degree == (1, 0, 1, 0, 1)
    assert profile.harmonic_form_total == 3
    assert profile.total_chain_dim == 255
    assert profile.total_spectral_gap > 1.9


def test_k3_external_operator_profile_has_expected_harmonic_sector() -> None:
    profile = external_operator_profile("K3")
    assert profile.chain_dimensions == (16, 120, 560, 720, 288)
    assert profile.zero_modes_by_degree == (1, 0, 22, 0, 1)
    assert profile.harmonic_form_total == 24
    assert profile.total_chain_dim == 1704
    assert profile.total_spectral_gap > 0.68


def test_external_zero_mode_counts_match_total_dk_squared_spectrum() -> None:
    cp2_zero = int((abs(external_dirac_kahler_squared_eigenvalues("CP2")) < 1e-8).sum())
    k3_zero = int((abs(external_dirac_kahler_squared_eigenvalues("K3")) < 1e-8).sum())
    assert cp2_zero == external_operator_profile("CP2").harmonic_form_total
    assert k3_zero == external_operator_profile("K3").harmonic_form_total


def test_curved_external_product_heat_trace_factorizes_exactly() -> None:
    for name in ("CP2", "K3"):
        for t in (0.05, 0.1, 0.2):
            direct = product_heat_trace_direct(name, t)
            factorized = product_heat_trace_factorized(name, t)
            assert abs(direct - factorized) < 1e-9


def test_k3_external_heat_trace_exceeds_cp2_for_same_t() -> None:
    for t in (0.05, 0.1, 0.2):
        assert external_heat_trace("K3", t) > external_heat_trace("CP2", t)


def test_summary_records_operator_level_curved_bridge() -> None:
    summary = build_curved_external_hodge_product_summary()
    assert summary["status"] == "ok"
    assert summary["external_profiles"][0]["harmonic_form_total"] == 3
    assert summary["external_profiles"][1]["harmonic_form_total"] == 24
    assert len(build_product_heat_checks()) == 6
    assert "explicit operator package" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_curved_external_hodge_product_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["external_profiles"][0]["total_chain_dim"] == 255
    assert data["external_profiles"][1]["total_chain_dim"] == 1704
