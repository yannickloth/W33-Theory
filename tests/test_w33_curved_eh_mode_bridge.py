from __future__ import annotations

from w33_curved_eh_mode_bridge import build_curved_eh_mode_bridge_summary


def _profile(summary: dict, name: str) -> dict:
    for profile in summary["profiles"]:
        if profile["name"] == name:
            return profile
    raise AssertionError(f"missing profile {name}")


def test_master_formula_recovers_existing_special_cases() -> None:
    summary = build_curved_eh_mode_bridge_summary()
    assert summary["master_formula"]["exact_scale_separation"] == "120 / 6 = 20"

    chain = _profile(summary, "external_chain")
    trace = _profile(summary, "external_trace")
    a2 = _profile(summary, "a2_transport")
    transport = _profile(summary, "transport_curved_dirac")

    assert chain["global_coefficients"] == {
        "cosmological_density_limit": {"exact": "120/19", "float": 120 / 19},
        "einstein_hilbert_6_mode_coefficient": {"exact": "3", "float": 3.0},
        "topological_1_mode_coefficient": {"exact": "1", "float": 1.0},
    }
    assert trace["global_coefficients"] == {
        "cosmological_density_limit": {"exact": "860/19", "float": 860 / 19},
        "einstein_hilbert_6_mode_coefficient": {"exact": "12", "float": 12.0},
        "topological_1_mode_coefficient": {"exact": "0", "float": 0.0},
    }
    assert a2["global_coefficients"]["cosmological_density_limit"]["exact"] == "423000/19"
    assert a2["global_coefficients"]["einstein_hilbert_6_mode_coefficient"]["exact"] == "9720"
    assert a2["global_coefficients"]["topological_1_mode_coefficient"]["exact"] == "2880"
    assert transport["global_coefficients"]["cosmological_density_limit"]["exact"] == "19370040/19"
    assert transport["global_coefficients"]["einstein_hilbert_6_mode_coefficient"]["exact"] == "369396"
    assert transport["global_coefficients"]["topological_1_mode_coefficient"]["exact"] == "74772"


def test_master_formula_produces_new_finite_df2_eh_channel() -> None:
    summary = build_curved_eh_mode_bridge_summary()
    finite = _profile(summary, "finite_df2_480")
    assert finite["a0"]["exact"] == "480"
    assert finite["a2"]["exact"] == "2240"
    assert finite["global_coefficients"]["cosmological_density_limit"]["exact"] == "681600/19"
    assert finite["global_coefficients"]["einstein_hilbert_6_mode_coefficient"]["exact"] == "12480"
    assert finite["global_coefficients"]["topological_1_mode_coefficient"]["exact"] == "2240"


def test_seed_samples_match_direct_integrated_products_and_curvature_signs() -> None:
    summary = build_curved_eh_mode_bridge_summary()
    finite = _profile(summary, "finite_df2_480")
    cp2_seed, k3_seed = finite["seeds"]

    for seed in (cp2_seed, k3_seed):
        assert seed["samples"][0]["integrated_formula"] == seed["samples"][0]["integrated_direct"]
        assert seed["samples"][1]["integrated_formula"] == seed["samples"][1]["integrated_direct"]
        assert seed["samples"][2]["integrated_formula"] == seed["samples"][2]["integrated_direct"]
        assert seed["sign_matches_signature_for_curvature_mode"] is True

    assert cp2_seed["density_formula"]["einstein_hilbert_density_coefficient"]["exact"] == "54080/19"
    assert k3_seed["density_formula"]["einstein_hilbert_density_coefficient"]["exact"] == "-114400/57"
