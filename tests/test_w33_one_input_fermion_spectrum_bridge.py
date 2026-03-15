from __future__ import annotations

import json
from pathlib import Path

from w33_one_input_fermion_spectrum_bridge import (
    build_one_input_fermion_spectrum_summary,
    write_summary,
)


def test_one_input_fermion_spectrum_bridge_closes_quarks_and_leptons() -> None:
    summary = build_one_input_fermion_spectrum_summary()
    assert summary["status"] == "ok"

    graph_seed = summary["graph_fixed_seed"]
    assert graph_seed["vev_ew_gev"] == 246
    assert graph_seed["mt_over_vew"]["exact"] == "sqrt(2)/2"
    assert graph_seed["mc_over_vew"]["exact"] == "sqrt(2)/272"
    assert graph_seed["mu_over_vew"]["exact"] == "sqrt(2)/147968"
    assert graph_seed["mb_over_vew"]["exact"] == "13*sqrt(2)/1088"

    ladder = summary["dimensionless_fermion_ladder"]
    assert ladder["mc_over_mt"]["exact"] == "1/136"
    assert ladder["mu_over_mc"]["exact"] == "1/544"
    assert ladder["mu_over_mt"]["exact"] == "1/73984"
    assert ladder["mb_over_mc"]["exact"] == "13/4"
    assert ladder["ms_over_mb"]["exact"] == "1/44"
    assert ladder["md_over_ms"]["exact"] == "1/20"
    assert ladder["mmu_over_me"]["exact"] == "208"

    leptons = summary["charged_lepton_one_seed_closure"]
    assert leptons["residual_seed"] == "m_e"
    assert leptons["koide_q"]["exact"] == "2/3"
    assert leptons["sqrt_mtau_over_me"]["exact"] == "2 + sqrt(48*sqrt(13) + 627) + 8*sqrt(13)"
    assert leptons["mtau_over_me_minpoly"] == "y**4 - 5852*y**3 + 8322694*y**2 - 302918748*y + 1628364609"


def test_one_input_fermion_spectrum_bridge_reduces_neutrino_side_to_same_seed(tmp_path: Path) -> None:
    summary = build_one_input_fermion_spectrum_summary()
    neutrino = summary["exceptional_neutrino_closure"]
    theorem = summary["fermion_spectrum_theorem"]

    assert neutrino["residual_seed"] == "m_e"
    assert neutrino["mnu_over_me_squared_if_dirac_seed_is_electron"]["exact"] == "26/123"
    assert neutrino["f4_dimension"] == 52
    assert neutrino["mr_over_vew"]["exact"] == "1/52"

    assert theorem["quark_ladder_fixed_by_graph_scale_and_q3_ratios"] is True
    assert theorem["charged_lepton_ladder_reduced_to_one_electron_seed"] is True
    assert theorem["koide_packet_closes_tau_over_e_algebraically"] is True
    assert theorem["neutrino_scale_reduced_to_same_electron_seed_plus_f4_coefficient"] is True
    assert theorem["remaining_fermion_frontier_is_one_seed_plus_final_internal_spectral_packet"] is True

    out = tmp_path / "summary.json"
    write_summary(out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["charged_lepton_one_seed_closure"]["mmu_over_me"]["exact"] == "208"
