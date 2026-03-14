"""Curved reconstruction of the full finite Dirac/Hodge package.

The curved Rosetta reconstruction already recovers

    q = 3,
    SRG(40,12,2,4),
    adjacency spectrum (12,2,-4).

This module closes the next gap. Using the live internal topological law

    b1 = q^4,

and the already-promoted clique regularity channel

    coexact/high-degree eigenvalue = q + 1,

the curved data now reconstructs the full finite W33 Dirac/Hodge spectrum:

    D_F^2 spectrum = {0^82, 4^320, 10^48, 16^30}.

Equivalently, the curved tower already recovers the finite spectral-action
moments

    a0 = 480,  a2 = 2240,  a4 = 17600,

and therefore the internal matter/Higgs spectral package itself, not only the
SRG and Rosetta layers that sit underneath it.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from math import comb
from pathlib import Path
from typing import Any

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_curved_rosetta_reconstruction_bridge import build_curved_rosetta_reconstruction_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_finite_spectral_reconstruction_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _solve_nontrivial_multiplicities(v: int, r: int, s: int, k: int) -> tuple[int, int]:
    # 1 + m_r + m_s = v and k + m_r r + m_s s = 0
    m_r = Fraction(-(k + (v - 1) * s), r - s)
    m_s = Fraction(v - 1) - m_r
    return int(m_r), int(m_s)


@lru_cache(maxsize=1)
def build_curved_finite_spectral_reconstruction_summary() -> dict[str, Any]:
    curved = build_curved_rosetta_reconstruction_summary()
    live = build_adjacency_dirac_closure_summary()

    q = int(curved["reconstructed_cyclotomic_data"]["q"])
    v = int(curved["reconstructed_srg_data"]["v"])
    k = int(curved["reconstructed_srg_data"]["k"])
    r = int(curved["reconstructed_spectral_data"]["r"])
    s = int(curved["reconstructed_spectral_data"]["s"])

    line_size = q + 1
    line_count = (q + 1) * (q**2 + 1)
    edge_count = line_count * comb(line_size, 2)
    triangle_count = line_count * comb(line_size, 3)
    tetrahedron_count = line_count * comb(line_size, 4)

    b0 = 1
    b1 = q**4
    b2 = 0
    b3 = 0
    rank_d1 = v - b0
    rank_d2 = edge_count - rank_d1 - b1
    rank_d3 = tetrahedron_count - b3

    m_r, m_s = _solve_nontrivial_multiplicities(v, r, s, k)
    vertex_lambda_r = k - r
    vertex_lambda_s = k - s
    scalar_channel = q + 1

    df2_spectrum = {
        0: b0 + b1,
        scalar_channel: rank_d2 + triangle_count + tetrahedron_count,
        vertex_lambda_r: 2 * m_r,
        vertex_lambda_s: 2 * m_s,
    }
    a0 = sum(df2_spectrum.values())
    a2 = sum(Fraction(eigen) * mult for eigen, mult in df2_spectrum.items())
    a4 = sum(Fraction(eigen * eigen) * mult for eigen, mult in df2_spectrum.items())

    live_finite = live["finite_dirac_closure"]
    live_hodge = live["hodge_lift_theorem"]
    live_high = live["high_degree_regularities"]

    sample_reconstructions = []
    for sample in curved["sample_reconstructions"]:
        sample_q = int(sample["q"])
        sample_v = int(sample["v"])
        sample_k = int(sample["k"])
        sample_r = int(sample["r"])
        sample_s = int(sample["s"])
        sample_line_count = (sample_q + 1) * (sample_q**2 + 1)
        sample_edge_count = sample_line_count * comb(sample_q + 1, 2)
        sample_triangle_count = sample_line_count * comb(sample_q + 1, 3)
        sample_tetrahedron_count = sample_line_count * comb(sample_q + 1, 4)
        sample_b1 = sample_q**4
        sample_rank_d1 = sample_v - 1
        sample_rank_d2 = sample_edge_count - sample_rank_d1 - sample_b1
        sample_mr, sample_ms = _solve_nontrivial_multiplicities(sample_v, sample_r, sample_s, sample_k)
        sample_df2 = {
            0: 1 + sample_b1,
            sample_q + 1: sample_rank_d2 + sample_triangle_count + sample_tetrahedron_count,
            sample_k - sample_r: 2 * sample_mr,
            sample_k - sample_s: 2 * sample_ms,
        }
        sample_reconstructions.append(
            {
                "seed_name": sample["seed_name"],
                "step": sample["step"],
                "chain_dimensions": {
                    "c0": sample_v,
                    "c1": sample_edge_count,
                    "c2": sample_triangle_count,
                    "c3": sample_tetrahedron_count,
                    "total": sample_v + sample_edge_count + sample_triangle_count + sample_tetrahedron_count,
                },
                "betti_numbers": {"b0": 1, "b1": sample_b1, "b2": 0, "b3": 0},
                "df2_spectrum": sample_df2,
            }
        )

    return {
        "status": "ok",
        "reconstructed_graph_geometry": {
            "q": q,
            "line_size": line_size,
            "line_count": line_count,
            "edge_count": edge_count,
            "triangle_count": triangle_count,
            "tetrahedron_count": tetrahedron_count,
            "edge_count_matches_srg_formula_vk_over_2": edge_count == v * k // 2,
        },
        "reconstructed_hodge_data": {
            "betti_numbers": {"b0": b0, "b1": b1, "b2": b2, "b3": b3},
            "boundary_ranks": {"rank_d1": rank_d1, "rank_d2": rank_d2, "rank_d3": rank_d3},
            "exact_one_form_dimension": rank_d1,
            "coexact_one_form_dimension": rank_d2,
            "coexact_and_high_degree_scalar_channel": scalar_channel,
        },
        "reconstructed_vertex_channels": {
            "adjacency_nontrivial_multiplicities": {str(r): m_r, str(s): m_s},
            "vertex_laplacian_spectrum": {0: 1, vertex_lambda_r: m_r, vertex_lambda_s: m_s},
            "exact_one_form_nonzero_spectrum": {vertex_lambda_r: m_r, vertex_lambda_s: m_s},
        },
        "reconstructed_finite_dirac_package": {
            "df2_spectrum": df2_spectrum,
            "seeley_dewitt_moments": {
                "a0_f": int(a0),
                "a2_f": int(a2),
                "a4_f": int(a4),
            },
            "spectral_action_ratios": {
                "mu_squared": _fraction_dict(a2 / a0),
                "lambda": _fraction_dict(a4 / a0),
                "higgs_ratio_square": _fraction_dict(Fraction(2) * a2 / a4),
            },
        },
        "matches_live_internal_package": {
            "triangle_count_matches": triangle_count == live_high["triangle_count"],
            "tetrahedron_count_matches": tetrahedron_count == live_high["tetrahedron_count"],
            "betti_numbers_match": {"b0": b0, "b1": b1, "b2": b2, "b3": b3} == {
                "b0": live_finite["betti_numbers"]["b0"],
                "b1": live_finite["betti_numbers"]["b1"],
                "b2": live_finite["betti_numbers"]["b2"],
                "b3": live_finite["betti_numbers"]["b3"],
            },
            "boundary_ranks_match": {"rank_d1": rank_d1, "rank_d2": rank_d2, "rank_d3": rank_d3}
            == live_finite["boundary_ranks"],
            "vertex_channels_match": {0: 1, vertex_lambda_r: m_r, vertex_lambda_s: m_s}
            == live["adjacency_side"]["vertex_laplacian_spectrum"],
            "exact_one_form_channels_match": {vertex_lambda_r: m_r, vertex_lambda_s: m_s}
            == live_hodge["exact_one_form_spectrum"],
            "df2_spectrum_match": df2_spectrum == live_finite["df2_spectrum"],
            "moments_match": {
                "a0_f": int(a0),
                "a2_f": int(a2),
                "a4_f": int(a4),
            }
            == live_finite["seeley_dewitt_moments"],
        },
        "sample_reconstructions": sample_reconstructions,
        "all_samples_constant": len(
            {
                (
                    tuple(sample["chain_dimensions"].items()),
                    tuple(sample["betti_numbers"].items()),
                    tuple(sample["df2_spectrum"].items()),
                )
                for sample in sample_reconstructions
            }
        )
        == 1,
        "bridge_verdict": (
            "The curved refinement tower now reconstructs the full finite "
            "Dirac/Hodge package, not only the graph Rosetta data underneath it. "
            "From q = 3, SRG(40,12,2,4), the adjacency spectrum (12,2,-4), the "
            "live Betti law b1 = q^4 = 81, and the scalar coexact/high-degree "
            "channel q+1 = 4, one recovers the chain dimensions "
            "(40,240,160,40), the boundary ranks (39,120,40), the Hodge/Dirac "
            "spectrum {0^82, 4^320, 10^48, 16^30}, and the exact moments "
            "a0 = 480, a2 = 2240, a4 = 17600. So the curved bridge already "
            "recovers the internal finite spectral-action package itself."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_finite_spectral_reconstruction_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
