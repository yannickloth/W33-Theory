from exploration.w33_curved_mode_projector_bridge import build_curved_mode_projector_bridge_summary


def test_projector_formulas_recover_all_three_modes() -> None:
    summary = build_curved_mode_projector_bridge_summary()
    cp2, k3 = summary["seeds"]

    for seed in (cp2, k3):
        assert seed["recurrence_holds"] is True
        for sample in seed["projector_samples"]:
            assert sample["projected_120"]["exact"] == sample["expected_120"]["exact"]
            assert sample["projected_6"]["exact"] == sample["expected_6"]["exact"]
            assert sample["projected_1"]["exact"] == sample["expected_1"]["exact"]


def test_eh_coefficient_is_step_independent_and_exact() -> None:
    summary = build_curved_mode_projector_bridge_summary()
    cp2, k3 = summary["seeds"]
    assert cp2["eh_extracted_coefficient"]["exact"] == "12480"
    assert k3["eh_extracted_coefficient"]["exact"] == "12480"
    assert cp2["continuum_eh_from_rank_39_lock"]["exact"] == "320"
    assert k3["continuum_eh_from_rank_39_lock"]["exact"] == "320"


def test_finite_profile_records_eh_coefficient() -> None:
    summary = build_curved_mode_projector_bridge_summary()
    finite = summary["finite_profile"]
    assert finite["a0"]["exact"] == "480"
    assert finite["a2"]["exact"] == "2240"
    assert finite["einstein_hilbert_coefficient"]["exact"] == "12480"
