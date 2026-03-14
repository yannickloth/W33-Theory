"""Curved reconstruction of the native SRG and spectral Rosetta data.

The curved bridge already provides three exact inputs:

    x = sin^2(theta_W) = 3/13,
    c_6 / c_EH,cont = 39,
    a2 / c_EH,cont = 2240 / 320 = 7.

At the exceptional level it also gives

    vertices = 2240 / 56 = 40,
    edges    = 12480 / 52 = 240.

This module shows those curved data already reconstruct the internal graph
geometry itself:

    q     = sqrt(x * c_6/c_EH,cont) = 3,
    Phi_3 = (c_6/c_EH,cont) / q = 13,
    Phi_6 = a2 / c_EH,cont = 7,

    k      = Phi_3 - 1 = 12 = 2E / V,
    lambda = q - 1 = 2,
    mu     = k - lambda - Phi_6 + 1 = 4,
    r      = q - 1 = 2,
    s      = 1 + r - Phi_6 = -4.

So the curved tower now reconstructs not only the promoted observables and
exceptional channel data, but also the native SRG(40,12,2,4) and adjacency
spectrum (12,2,-4) from which the internal package started.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from math import isqrt
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "tools", ROOT / "scripts"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_algebraic_spine import build_algebraic_spine
from w33_curved_continuum_extractor_bridge import build_curved_continuum_extractor_summary
from w33_curved_weinberg_lock_bridge import build_curved_weinberg_lock_bridge_summary
from w33_spectral_action_cyclotomic_bridge import build_spectral_action_cyclotomic_summary
from w33_spectral_rosetta_lock_bridge import build_spectral_rosetta_lock_summary
from w33_srg_rosetta_lock_bridge import build_srg_rosetta_lock_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_rosetta_reconstruction_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _integer_square_root(value: Fraction) -> int:
    if value.denominator != 1:
        raise ValueError(f"Expected integer square, got {value}")
    root = isqrt(value.numerator)
    if root * root != value.numerator:
        raise ValueError(f"Expected perfect square, got {value}")
    return root


def _public_observables_from_graph_data(k: int, lam: int, mu: int, r: int, s: int) -> dict[str, Fraction]:
    return {
        "sin2_theta_w_ew": Fraction(lam + 1, k + 1),
        "tan_theta_c": Fraction(lam + 1, k + 1),
        "sin2_theta_12": Fraction(mu, k + 1),
        "sin2_theta_23": Fraction(k - lam - mu + 1, k + 1),
        "sin2_theta_13": Fraction(lam, (k + 1) * (k - lam - mu + 1)),
        "omega_lambda": Fraction((lam + 1) ** 2, k + 1),
        "higgs_ratio_square": Fraction(2 * (k - lam - mu + 1), 4 * (k + 1) + (lam + 1)),
        "a2_over_a0": Fraction(2 * (1 + r - s), r + 1),
        "a4_over_a0": Fraction(2 * (4 * (k + 1) + (r + 1)), r + 1),
        "discrete_6_mode_over_a0": Fraction(2 * (k + 1), 1),
        "discrete_to_continuum_ratio": Fraction((r + 1) * (k + 1), 1),
    }


@lru_cache(maxsize=1)
def build_curved_rosetta_reconstruction_summary() -> dict[str, Any]:
    curved = build_curved_continuum_extractor_summary()
    curved_weinberg = build_curved_weinberg_lock_bridge_summary()
    srg = build_srg_rosetta_lock_summary()
    spectral = build_spectral_rosetta_lock_summary()
    sm = build_standard_model_cyclotomic_summary()
    spectral_action = build_spectral_action_cyclotomic_summary()
    exceptional = build_algebraic_spine().exceptional_parameter_dictionary

    expected_discrete = Fraction(curved["finite_profile"]["expected_discrete_eh"]["exact"])
    expected_continuum = Fraction(curved["finite_profile"]["expected_continuum_eh"]["exact"])
    expected_topological = Fraction(curved["finite_profile"]["a2"]["exact"])
    master_x = Fraction(curved_weinberg["master_variable"]["exact"]["exact"])

    vertex_count = expected_topological // exceptional.e7_fund_dim
    edge_count = expected_discrete // exceptional.f4_dim
    discrete_to_continuum_ratio = expected_discrete / expected_continuum
    phi6 = expected_topological / expected_continuum
    q = _integer_square_root(master_x * discrete_to_continuum_ratio)
    phi3 = discrete_to_continuum_ratio / q
    k_from_geometry = Fraction(2 * edge_count, vertex_count)
    k = int(phi3 - 1)
    lam = q - 1
    mu = int(k - lam - phi6 + 1)
    r = q - 1
    s = int(1 + r - phi6)

    public_exact = {
        "sin2_theta_w_ew": Fraction(sm["promoted_observables"]["sin2_theta_w_ew"]["exact"]),
        "tan_theta_c": Fraction(sm["promoted_observables"]["tan_theta_c"]["exact"]),
        "sin2_theta_12": Fraction(sm["promoted_observables"]["sin2_theta_12"]["exact"]),
        "sin2_theta_23": Fraction(sm["promoted_observables"]["sin2_theta_23"]["exact"]),
        "sin2_theta_13": Fraction(sm["promoted_observables"]["sin2_theta_13"]["exact"]),
        "omega_lambda": Fraction(sm["promoted_observables"]["omega_lambda"]["exact"]),
        "higgs_ratio_square": Fraction(sm["promoted_observables"]["higgs_ratio_square"]["exact"]),
        "a2_over_a0": Fraction(spectral_action["internal_spectral_action"]["a2_over_a0"]["exact"]),
        "a4_over_a0": Fraction(spectral_action["internal_spectral_action"]["a4_over_a0"]["exact"]),
        "discrete_6_mode_over_a0": Fraction(spectral_action["gravity_lock"]["discrete_6_mode_over_a0"]["exact"]),
        "discrete_to_continuum_ratio": Fraction(spectral_action["gravity_lock"]["discrete_to_continuum_ratio"]["exact"]),
    }
    reconstructed_observables = _public_observables_from_graph_data(k, lam, mu, r, s)

    flattened_samples = [
        (seed["seed_name"], sample)
        for seed in curved["seeds"]
        for sample in seed["samples"]
    ]
    sample_reconstructions = []
    for (seed_name, sample), x_entry in zip(flattened_samples, curved_weinberg["curved_samples"], strict=True):
        sample_x = Fraction(x_entry["reconstructed_x"]["exact"])
        sample_discrete = Fraction(sample["discrete_eh"]["exact"])
        sample_continuum = Fraction(sample["continuum_eh"]["exact"])
        sample_topological = Fraction(sample["topological_a2"]["exact"])
        sample_ratio = sample_discrete / sample_continuum
        sample_phi6 = sample_topological / sample_continuum
        sample_q = _integer_square_root(sample_x * sample_ratio)
        sample_phi3 = sample_ratio / sample_q
        sample_vertices = sample_topological // exceptional.e7_fund_dim
        sample_edges = sample_discrete // exceptional.f4_dim
        sample_k = int(sample_phi3 - 1)
        sample_lambda = sample_q - 1
        sample_mu = int(sample_k - sample_lambda - sample_phi6 + 1)
        sample_r = sample_q - 1
        sample_s = int(1 + sample_r - sample_phi6)
        sample_reconstructions.append(
            {
                "seed_name": seed_name,
                "step": sample["step"],
                "q": sample_q,
                "phi3": str(sample_phi3),
                "phi6": str(sample_phi6),
                "v": sample_vertices,
                "k": sample_k,
                "lambda": sample_lambda,
                "mu": sample_mu,
                "r": sample_r,
                "s": sample_s,
            }
        )

    return {
        "status": "ok",
        "curved_inputs": {
            "master_variable": _fraction_dict(master_x),
            "discrete_to_continuum_ratio": _fraction_dict(discrete_to_continuum_ratio),
            "phi6_from_topological_over_continuum": _fraction_dict(phi6),
            "vertex_count_from_topological_over_e7_fund": vertex_count,
            "edge_count_from_discrete_over_f4": edge_count,
            "k_from_two_edges_over_vertices": _fraction_dict(k_from_geometry),
        },
        "reconstructed_cyclotomic_data": {
            "q": q,
            "phi3": _fraction_dict(phi3),
            "phi6": _fraction_dict(phi6),
            "q_from_sqrt_x_times_ratio": q,
            "phi3_from_ratio_over_q": _fraction_dict(phi3),
        },
        "reconstructed_srg_data": {
            "v": vertex_count,
            "k": k,
            "lambda": lam,
            "mu": mu,
        },
        "reconstructed_spectral_data": {
            "k": k,
            "r": r,
            "s": s,
        },
        "promoted_observables_from_reconstructed_graph_data": {
            key: {
                "exact": _fraction_dict(value),
                "matches_public_value": value == public_exact[key],
            }
            for key, value in reconstructed_observables.items()
        },
        "matches_live_rosetta_data": {
            "srg_k_matches": k == srg["srg_data"]["k"],
            "srg_lambda_matches": lam == srg["srg_data"]["lambda"],
            "srg_mu_matches": mu == srg["srg_data"]["mu"],
            "spectral_k_matches": k == spectral["spectral_data"]["k"],
            "spectral_r_matches": r == spectral["spectral_data"]["r"],
            "spectral_s_matches": s == spectral["spectral_data"]["s"],
            "all_promoted_observables_match": all(
                entry["matches_public_value"]
                for entry in {
                    key: {
                        "matches_public_value": reconstructed_observables[key] == public_exact[key]
                    }
                    for key in reconstructed_observables
                }.values()
            ),
        },
        "sample_reconstructions": sample_reconstructions,
        "all_samples_constant": len(
            {
                (entry["q"], entry["phi3"], entry["phi6"], entry["v"], entry["k"], entry["lambda"], entry["mu"], entry["r"], entry["s"])
                for entry in sample_reconstructions
            }
        )
        == 1,
        "bridge_verdict": (
            "The curved tower now reconstructs the native graph geometry itself. "
            "From the curved electroweak lock x = 3/13, the discrete-to-continuum "
            "ratio 39, the topological ratio 7, and the exceptional dimensions 52 "
            "and 56, one recovers q = 3, Phi_3 = 13, Phi_6 = 7, the SRG data "
            "(v,k,lambda,mu) = (40,12,2,4), and the adjacency spectrum "
            "(k,r,s) = (12,2,-4). So the curved refinement tower is already an "
            "inverse Rosetta reconstruction of the internal SRG and spectral data, "
            "not only of the promoted observables."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_rosetta_reconstruction_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
