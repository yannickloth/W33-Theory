"""Exact harmonic-cube / Klein-quartic / Vogel shell bridge.

This module compresses the new promoted algebra into one ambient shell picture.

The exact local shell is now:

    27^2 = 729,
    728 = dim sl(27),
    364 = |PG(5,3)| = 728 / 2,
    364 = 40 + 324.

The harmonic-cube / Klein-quartic side supplies the same shell in a different
factorization:

    14 = 7 cubes + 7 anticubes = dim G2,
    56 = 14 * 4 = 2 * 28,
    84 = 14 * 6 = 4 * 21,
    168 = 2 * 84 = 8 * 21 = 24 * 7,
    364 = 14 * 26 = 28 * 13,
    728 = 56 * 13 = 28 * 26.

So the promoted algebra is best read as an A_26 ambient Klein shell dressed by
the G2 harmonic-cube packet, the W33 slice 40, and the exact moonshine gap 324.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_klein_quartic_ag21_bridge import build_klein_quartic_ag21_summary
from w33_monster_gap_duality_bridge import build_monster_gap_duality_summary
from w33_s12_klein_projective_bridge import build_s12_klein_projective_summary
from w33_s12_vogel_spine_bridge import build_s12_vogel_spine_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_klein_harmonic_vogel_bridge_summary.json"


@lru_cache(maxsize=1)
def build_klein_harmonic_vogel_summary() -> dict[str, Any]:
    s12 = build_s12_klein_projective_summary()
    vogel = build_s12_vogel_spine_summary()
    ag21 = build_klein_quartic_ag21_summary()
    gap = build_monster_gap_duality_summary()

    phi3 = int(
        s12["quartic_parallelism_guide_rail"]["clifford_parallelism_external_plane_points"]
    )
    bitangents = int(s12["quartic_parallelism_guide_rail"]["plane_quartic_bitangent_count"])
    ambient_pg53 = int(s12["harmonic_cube_square_dictionary"]["ambient_pg53_points"])
    w33_slice = int(s12["harmonic_cube_square_dictionary"]["w33_klein_slice_points"])
    moonshine_gap = int(s12["harmonic_cube_square_dictionary"]["moonshine_gap"])
    sl27_shell = int(s12["harmonic_cube_square_dictionary"]["sl27_shell_dimension"])
    a26_rank = int(vogel["vogel_a_line_dictionary"]["a_family_rank"])
    g2_dim = int(vogel["vogel_a_line_dictionary"]["g2_dimension"])
    shared_six = int(gap["moonshine_gap_dictionary"]["shared_six_channel_rank"])
    spacetime_factor = int(gap["moonshine_gap_dictionary"]["spacetime_factor"])
    logical_qutrits = int(gap["moonshine_gap_dictionary"]["logical_qutrits"])
    ag21_length = int(ag21["ag21_coding_shadow"]["klein_quartic_ag_code_length"])

    cubes = 7
    anticubes = 7
    packet_total = cubes + anticubes
    quartic_triangles = 56
    quartic_edges = 84
    quartic_automorphisms = 168
    quartic_vertices = 24
    gauge_closure = 12
    cartan_rank = 8

    return {
        "status": "ok",
        "harmonic_quartic_dictionary": {
            "harmonic_cubes": cubes,
            "harmonic_anticubes": anticubes,
            "harmonic_packet_total": packet_total,
            "klein_quartic_vertices": quartic_vertices,
            "klein_quartic_triangles": quartic_triangles,
            "klein_quartic_edges": quartic_edges,
            "klein_quartic_automorphism_order": quartic_automorphisms,
            "bitangent_count": bitangents,
            "ag21_length": ag21_length,
            "phi3": phi3,
            "shared_six_channel_rank": shared_six,
            "spacetime_factor": spacetime_factor,
            "logical_qutrits": logical_qutrits,
            "g2_dimension": g2_dim,
            "a26_rank": a26_rank,
            "ambient_pg53_points": ambient_pg53,
            "w33_klein_slice_points": w33_slice,
            "moonshine_gap": moonshine_gap,
            "sl27_shell_dimension": sl27_shell,
            "harmonic_packet_total_equals_g2_dimension": packet_total == g2_dim,
            "triangles_equals_packets_times_spacetime": (
                quartic_triangles == packet_total * spacetime_factor
            ),
            "triangles_equals_two_times_bitangents": quartic_triangles == 2 * bitangents,
            "triangles_equals_cartan_times_phi6": quartic_triangles == cartan_rank * cubes,
            "vertices_equal_d4_q8_seed": quartic_vertices == 24,
        },
        "promoted_factorizations": {
            "edges_equals_packets_times_shared_six": quartic_edges == packet_total * shared_six,
            "edges_equals_four_times_ag21": quartic_edges == 4 * ag21_length,
            "edges_equals_gauge_closure_times_phi6": quartic_edges == gauge_closure * cubes,
            "automorphisms_equals_two_times_edges": quartic_automorphisms == 2 * quartic_edges,
            "automorphisms_equals_eight_times_ag21": quartic_automorphisms == 8 * ag21_length,
            "automorphisms_equals_vertex_seed_times_phi6": quartic_automorphisms == quartic_vertices * cubes,
            "ambient_equals_g2_times_a26": ambient_pg53 == g2_dim * a26_rank,
            "ambient_equals_bitangents_times_phi3": ambient_pg53 == bitangents * phi3,
            "ambient_equals_w33_slice_plus_gap": ambient_pg53 == w33_slice + moonshine_gap,
            "sl27_equals_two_times_ambient": sl27_shell == 2 * ambient_pg53,
            "sl27_equals_bitangents_times_a26": sl27_shell == bitangents * a26_rank,
            "sl27_equals_triangles_times_phi3": sl27_shell == quartic_triangles * phi3,
            "gap_equals_spacetime_times_logical_qutrits": (
                moonshine_gap == spacetime_factor * logical_qutrits
            ),
        },
        "bridge_verdict": (
            "The harmonic-cube/Klein-quartic side is now part of the same promoted "
            "ambient shell as the s12/Golay/Vogel bridge. The 7 cubes and 7 "
            "anticubes give 14 = dim G2, the quartic triangles give "
            "56 = 14*4 = 2*28, the quartic edges give 84 = 14*6 = 4*21, and the "
            "quartic automorphism order gives 168 = 2*84 = 8*21 = 24*7. The same "
            "ambient shell then closes as 364 = 14*26 = 28*13 = 40 + 324, while "
            "the full sl(27) shell closes as 728 = 2*364 = 28*26 = 56*13. So the "
            "final promoted algebra is best read as an A_26 ambient Klein shell "
            "dressed by the G2 harmonic-cube packet, with the live W33 slice and "
            "the exact moonshine gap occupying the same projective ambient space."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_klein_harmonic_vogel_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
