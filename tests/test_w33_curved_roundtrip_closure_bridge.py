from __future__ import annotations

from w33_curved_roundtrip_closure_bridge import build_curved_roundtrip_closure_summary


def test_roundtrip_recovers_curved_coefficients_from_finite_package() -> None:
    summary = build_curved_roundtrip_closure_summary()

    finite = summary["reconstructed_finite_package"]
    roundtrip = summary["roundtrip_curved_coefficients"]
    matches = summary["matches_curved_extractor_profile"]
    assert finite["a0_f"] == 480
    assert finite["a2_f"] == 2240
    assert finite["a4_f"] == 17600
    assert finite["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
    assert roundtrip["continuum_eh_from_finite"]["exact"] == "320"
    assert roundtrip["discrete_eh_from_finite"]["exact"] == "12480"
    assert roundtrip["topological_from_finite"]["exact"] == "2240"
    assert roundtrip["master_variable_from_roundtrip"]["exact"] == "3/13"
    assert matches["continuum_matches"] is True
    assert matches["discrete_matches"] is True
    assert matches["topological_matches"] is True
    assert matches["master_variable_matches"] is True


def test_all_curved_samples_close_exactly_under_roundtrip() -> None:
    summary = build_curved_roundtrip_closure_summary()

    assert summary["all_samples_close_exactly"] is True
    assert len(summary["sample_roundtrips"]) == 6
    for sample in summary["sample_roundtrips"]:
        assert sample["sample_discrete_eh"] == "12480"
        assert sample["sample_continuum_eh"] == "320"
        assert sample["sample_topological"] == "2240"
        assert sample["matches_roundtrip_discrete"] is True
        assert sample["matches_roundtrip_continuum"] is True
        assert sample["matches_roundtrip_topological"] is True
        assert sample["matches_roundtrip_master_variable"] is True
