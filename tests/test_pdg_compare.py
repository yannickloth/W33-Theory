def test_pdg_compare_runs():
    from scripts.w33_pdg_compare import compare_to_pdg

    cmp = compare_to_pdg()

    # basic structure
    assert "prediction_MZ_GeV" in cmp
    assert "pdg_reference" in cmp
    assert "ratios_model_over_pdg" in cmp

    ratios = cmp["ratios_model_over_pdg"]
    # ratios should be finite and positive
    assert all(r > 0 and r == r for r in ratios.values())

    # sanity: top prediction should be order‑of‑magnitude comparable to PDG
    assert 0.01 < ratios["top_rel"] < 100.0
