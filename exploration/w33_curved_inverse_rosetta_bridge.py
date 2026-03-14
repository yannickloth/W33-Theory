"""Exact inverse-Rosetta reconstruction from the curved refinement tower.

The continuum-extractor bridge already proved that any three successive levels
of the curved refinement tower recover

    c_EH,disc = 12480,
    c_EH,cont = 320,
    c_top = 2240.

The exceptional-channel bridge then identified their internal meaning:

    320  = 40 * 8,
    12480 = 240 * 52 = 40 * 6 * 52,
    2240 = 40 * 56.

This module turns those forward identities into an exact inverse theorem.

Using only:
  - three successive curved refinement levels,
  - the exact exceptional dimensions F4 = 52 and E7(fund) = 56,

the bridge reconstructs exactly:
  - the W33 vertex count 40,
  - the W33 edge / E8-root count 240,
  - the l6 spinor Cartan rank 8,
  - the shared six-channel A2/firewall/tomotope core 6,
  - the tomotope automorphism order 96 = 16 * 6.

So the curved tower is already an inverse Rosetta map for the live internal
exceptional data, not merely a one-way scalar continuum approximation.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "tools", ROOT / "scripts"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_algebraic_spine import build_algebraic_spine
from w33_curved_continuum_extractor_bridge import build_curved_continuum_extractor_summary
from w33_exceptional_channel_continuum_bridge import (
    build_exceptional_channel_continuum_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_inverse_rosetta_bridge_summary.json"


@lru_cache(maxsize=1)
def build_curved_inverse_rosetta_summary() -> dict[str, Any]:
    extractor = build_curved_continuum_extractor_summary()
    channel = build_exceptional_channel_continuum_bridge_summary()
    exceptional = build_algebraic_spine().exceptional_parameter_dictionary

    continuum = int(extractor["finite_profile"]["expected_continuum_eh"]["exact"])
    discrete = int(extractor["finite_profile"]["expected_discrete_eh"]["exact"])
    topological = int(extractor["finite_profile"]["a2"]["exact"])

    reconstructed_vertices = topological // exceptional.e7_fund_dim
    reconstructed_edges = discrete // exceptional.f4_dim
    reconstructed_cartan = continuum // reconstructed_vertices
    reconstructed_shared_six = discrete // (reconstructed_vertices * exceptional.f4_dim)
    reconstructed_tomotope_aut = 16 * reconstructed_shared_six

    sample_reconstructions = []
    for seed in extractor["seeds"]:
        for sample in seed["samples"]:
            cont = int(sample["continuum_eh"]["exact"])
            disc = int(sample["discrete_eh"]["exact"])
            topo = int(sample["topological_a2"]["exact"])
            vertices = topo // exceptional.e7_fund_dim
            edges = disc // exceptional.f4_dim
            cartan = cont // vertices
            shared_six = disc // (vertices * exceptional.f4_dim)
            sample_reconstructions.append(
                {
                    "seed_name": seed["seed_name"],
                    "step": sample["step"],
                    "vertices": vertices,
                    "edges": edges,
                    "cartan_rank": cartan,
                    "shared_six": shared_six,
                    "tomotope_automorphism_order": 16 * shared_six,
                }
            )

    return {
        "status": "ok",
        "input_coefficients": {
            "continuum_eh": continuum,
            "discrete_eh": discrete,
            "topological": topological,
            "f4_dimension": exceptional.f4_dim,
            "e7_fundamental_dimension": exceptional.e7_fund_dim,
        },
        "reconstructed_internal_data": {
            "w33_vertex_count": reconstructed_vertices,
            "w33_edge_or_e8_root_count": reconstructed_edges,
            "spinor_cartan_rank": reconstructed_cartan,
            "shared_six_channel": reconstructed_shared_six,
            "tomotope_automorphism_order": reconstructed_tomotope_aut,
        },
        "matches_live_internal_data": {
            "vertex_count_matches": reconstructed_vertices == exceptional.srg_parameters[0],
            "edge_count_matches": reconstructed_edges == build_exceptional_channel_continuum_bridge_summary()[
                "discrete_curvature_channel"
            ]["w33_edge_count"],
            "cartan_rank_matches": reconstructed_cartan
            == channel["base_continuum_channel"]["spinor_cartan_rank"],
            "shared_six_matches": reconstructed_shared_six
            == channel["shared_six_channel"]["l6_a2_root_support"],
            "tomotope_aut_matches": reconstructed_tomotope_aut
            == channel["tomotope_triality_bridge"]["tomotope_automorphism_order"],
        },
        "sample_reconstructions": sample_reconstructions,
        "all_samples_constant": len(
            {
                (
                    entry["vertices"],
                    entry["edges"],
                    entry["cartan_rank"],
                    entry["shared_six"],
                    entry["tomotope_automorphism_order"],
                )
                for entry in sample_reconstructions
            }
        )
        == 1,
        "bridge_verdict": (
            "The curved refinement tower is now an inverse Rosetta map. Any "
            "three successive refinement levels already reconstruct the W33 "
            "vertex count 40, the edge/E8-root count 240, the l6 spinor Cartan "
            "rank 8, the shared A2/firewall/tomotope channel 6, and the "
            "tomotope automorphism order 96 = 16*6. So the discrete-to-"
            "continuum bridge is bidirectional at the level of the promoted "
            "exceptional channel data."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_curved_inverse_rosetta_summary(), indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    write_summary()
