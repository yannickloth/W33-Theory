from exploration.w33_curved_continuum_extractor_bridge import build_curved_continuum_extractor_summary


def test_extractors_recover_same_discrete_and_continuum_eh_values() -> None:
    summary = build_curved_continuum_extractor_summary()
    for seed in summary["seeds"]:
        for sample in seed["samples"]:
            assert sample["discrete_eh"]["exact"] == "12480"
            assert sample["continuum_eh"]["exact"] == "320"


def test_extractors_recover_topological_coefficient() -> None:
    summary = build_curved_continuum_extractor_summary()
    for seed in summary["seeds"]:
        for sample in seed["samples"]:
            assert sample["topological_a2"]["exact"] == "2240"


def test_finite_profile_expected_values_are_recorded() -> None:
    summary = build_curved_continuum_extractor_summary()
    finite = summary["finite_profile"]
    assert finite["a0"]["exact"] == "480"
    assert finite["a2"]["exact"] == "2240"
    assert finite["expected_discrete_eh"]["exact"] == "12480"
    assert finite["expected_continuum_eh"]["exact"] == "320"
