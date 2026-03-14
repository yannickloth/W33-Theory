from __future__ import annotations

from w33_three_sample_master_closure_bridge import build_three_sample_master_closure_summary


def test_three_sample_master_closure_recovers_full_promoted_package() -> None:
    summary = build_three_sample_master_closure_summary()

    minimal = summary["minimal_curved_data"]
    public = summary["public_generator_layer"]
    rosetta = summary["rosetta_layer"]
    finite = summary["finite_spectral_layer"]
    exceptional = summary["exceptional_layer"]
    closure = summary["closure_checks"]
    assert minimal["seed_name"] == "CP2"
    assert minimal["steps"] == [0, 1, 2]
    assert minimal["discrete_eh"] == "12480"
    assert minimal["continuum_eh"] == "320"
    assert minimal["topological_a2"] == "2240"
    assert minimal["same_on_all_three_steps"] is True
    assert public["master_variable"] == "3/13"
    assert public["tan_theta_c"] == "3/13"
    assert public["sin2_theta_12"] == "4/13"
    assert public["sin2_theta_23"] == "7/13"
    assert public["sin2_theta_13"] == "2/91"
    assert public["omega_lambda"] == "9/13"
    assert public["higgs_ratio_square"] == "14/55"
    assert rosetta["q"] == 3
    assert rosetta["phi3"] == "13"
    assert rosetta["phi6"] == "7"
    assert rosetta["srg_data"] == {"v": 40, "k": 12, "lambda": 2, "mu": 4}
    assert rosetta["spectral_data"] == {"k": 12, "r": 2, "s": -4}
    assert finite["betti_numbers"] == {"b0": 1, "b1": 81, "b2": 0, "b3": 0}
    assert finite["boundary_ranks"] == {"rank_d1": 39, "rank_d2": 120, "rank_d3": 40}
    assert finite["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
    assert finite["a0_f"] == 480
    assert finite["a2_f"] == 2240
    assert finite["a4_f"] == 17600
    assert exceptional == {
        "w33_vertex_count": 40,
        "w33_edge_or_e8_root_count": 240,
        "spinor_cartan_rank": 8,
        "shared_six_channel": 6,
        "tomotope_automorphism_order": 96,
    }
    assert closure["curved_to_generator"] is True
    assert closure["generator_to_rosetta"] is True
    assert closure["rosetta_to_finite"] is True
    assert closure["finite_back_to_curved"] is True
    assert closure["curved_to_exceptional"] is True
    assert closure["full_master_closure"] is True
