from __future__ import annotations

from w33_exceptional_residue_bridge import build_exceptional_residue_bridge_summary


def test_exceptional_residue_bridge_recovers_same_exceptional_dictionary_on_both_seeds() -> None:
    summary = build_exceptional_residue_bridge_summary()
    internal = summary["internal_exceptional_data"]
    pole = summary["pole_dictionary"]

    assert internal["e6_projector_rank"] == 40
    assert internal["a2_projector_rank"] == 6
    assert internal["cartan_projector_rank"] == 8
    assert internal["f4_dimension"] == 52
    assert internal["e7_fundamental_dimension"] == 56
    assert internal["edge_or_e8_root_count"] == 240
    assert pole["discrete_curvature_from_6_pole"] == 12480
    assert pole["continuum_eh_from_rank39_normalized_6_pole"] == 320
    assert pole["topological_from_1_pole"] == 2240
    assert pole["discrete_equals_e6_times_a2_times_f4"] is True
    assert pole["discrete_equals_edges_times_f4"] is True
    assert pole["continuum_equals_e6_times_cartan"] is True
    assert pole["topological_equals_e6_times_e7_fund"] is True


def test_seed_checks_are_constant_across_cp2_and_k3() -> None:
    summary = build_exceptional_residue_bridge_summary()
    cp2, k3 = summary["seed_checks"]

    assert cp2["seed_name"] == "CP2_9"
    assert k3["seed_name"] == "K3_16"
    assert cp2["r6_over_six_mode"] == 12480
    assert k3["r6_over_six_mode"] == 12480
    assert cp2["r6_over_six_mode_over_rank39"] == 320
    assert k3["r6_over_six_mode_over_rank39"] == 320
    assert cp2["r1_over_chi_mode"] == 2240
    assert k3["r1_over_chi_mode"] == 2240
    assert summary["all_seed_checks_pass"] is True
