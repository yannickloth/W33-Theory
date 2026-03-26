from exploration.w33_external_exceptional_quanta_bridge import (
    build_external_exceptional_quanta_summary,
)


def test_external_exceptional_quanta_summary():
    summary = build_external_exceptional_quanta_summary()

    data = summary["promoted_residue_data"]
    assert data["internal_exceptional_ranks"] == [40, 6, 8]
    assert data["continuum_eh_coefficient"] == 320
    assert data["curved_six_mode_coefficient"] == 12480
    assert data["topological_coefficient"] == 2240
    assert data["curved_weinberg_lock"] == "3/13"
    assert data["topological_to_eh_ratio"] == "7"

    quanta = summary["external_quanta"]
    assert quanta["Q_curv"] == "52"
    assert quanta["Q_top"] == "56"

    theorem = summary["external_quantum_theorem"]
    assert theorem["continuum_eh_equals_40_times_8"] is True
    assert theorem["curved_six_mode_equals_40_times_6_times_Q_curv"] is True
    assert theorem["topological_coefficient_equals_40_times_Q_top"] is True
    assert theorem["weinberg_lock_reconstructs_Q_curv"] is True
    assert theorem["topological_ratio_reconstructs_Q_top"] is True
    assert theorem["external_exceptional_quanta_are_fixed_as_52_and_56"] is True
    assert theorem["global_branch_activation_count_remains_open"] is True
