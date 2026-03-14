from __future__ import annotations

from w33_klein_quartic_ag21_bridge import build_klein_quartic_ag21_summary


def test_klein_quartic_ag21_matches_live_surface_and_fano_counts() -> None:
    summary = build_klein_quartic_ag21_summary()
    bridge = summary["ag21_coding_shadow"]
    assert bridge["klein_quartic_ag_code_length"] == 21
    assert bridge["fano_flags"] == 21
    assert bridge["heawood_edges"] == 21
    assert bridge["csaszar_edges"] == 21
    assert bridge["szilassi_edges"] == 21
    assert bridge["ag21_equals_fano_flags"] is True
    assert bridge["ag21_equals_heawood_edges"] is True
    assert bridge["ag21_equals_csaszar_edges"] is True
    assert bridge["ag21_equals_szilassi_edges"] is True
    assert bridge["all_promoted_21_counts_agree"] is True


def test_klein_quartic_ag21_matches_q_phi6() -> None:
    summary = build_klein_quartic_ag21_summary()
    bridge = summary["ag21_coding_shadow"]
    assert bridge["q"] == 3
    assert bridge["phi6"] == 7
    assert bridge["ag21_equals_q_times_phi6"] is True
