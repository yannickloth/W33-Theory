"""Exact Heawood shell ladder tying Fano, AG21, G2, and D4.

The promoted torus/Fano route already had the key exact packets separately:

    7   = one Heawood bipartition half = Phi_6
    14  = Heawood vertices = dim(G2)
    21  = Heawood edges = Klein AG(2,1) code length
    24  = |Hurwitz units| = |Aut(Q8)| = D4 root shell
    42  = AGL(1,7)
    168 = Heawood bipartition-preserving automorphisms
    336 = full Heawood automorphisms

This module promotes the shell itself:

    14  = 2*7
    21  = 3*7
    42  = 2*21
    168 = 24*7 = 21*8
    336 = 24*14 = 21*16 = 42*8

So the Szilassi/Heawood dual is already carrying the same D4/G2/Klein-code
ladder as the harmonic-cube and tomotope packages.
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

from w33_d4_f4_tomotope_reye_bridge import build_d4_f4_tomotope_reye_summary
from w33_heawood_klein_symmetry_bridge import build_heawood_klein_symmetry_summary
from w33_klein_harmonic_vogel_bridge import build_klein_harmonic_vogel_summary
from w33_klein_quartic_ag21_bridge import build_klein_quartic_ag21_summary
from w33_mod7_fano_duality_bridge import build_mod7_fano_duality_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_heawood_shell_ladder_bridge_summary.json"


@lru_cache(maxsize=1)
def build_heawood_shell_ladder_summary() -> dict[str, Any]:
    heawood = build_heawood_klein_symmetry_summary()
    mod7 = build_mod7_fano_duality_summary()
    ag21 = build_klein_quartic_ag21_summary()
    klein = build_klein_harmonic_vogel_summary()
    d4 = build_d4_f4_tomotope_reye_summary()

    heptad_size = int(heawood["heawood_graph"]["bipartition_sizes"][0])
    heawood_vertices = int(heawood["heawood_graph"]["vertex_count"])
    heawood_edges = int(heawood["heawood_graph"]["edge_count"])
    phi6 = int(klein["harmonic_quartic_dictionary"]["harmonic_cubes"])
    g2_dimension = int(klein["harmonic_quartic_dictionary"]["g2_dimension"])
    ag21_length = int(ag21["ag21_coding_shadow"]["klein_quartic_ag_code_length"])
    hurwitz_unit_order = 24
    d4_seed_order = int(d4["q8_to_24cell_bridge"]["aut_q8_order"])
    affine_order = int(mod7["affine_group"]["full_affine_group_order"])
    affine_preserver_order = int(mod7["affine_group"]["heptad_preserver_subgroup_order"])
    preserving_order = int(
        heawood["bipartition_preserving_symmetry"]["heawood_bipartition_preserving_order"]
    )
    full_order = int(heawood["full_symmetry"]["full_heawood_automorphism_order"])
    preserving_edge_stabilizer = int(
        heawood["bipartition_preserving_symmetry"]["flag_edge_stabilizer_order"]
    )
    full_edge_stabilizer = int(heawood["full_symmetry"]["edge_stabilizer_order"])

    return {
        "status": "ok",
        "heawood_shell_dictionary": {
            "heptad_size": heptad_size,
            "phi6": phi6,
            "heawood_vertices": heawood_vertices,
            "g2_dimension": g2_dimension,
            "heawood_edges": heawood_edges,
            "ag21_length": ag21_length,
            "hurwitz_unit_order": hurwitz_unit_order,
            "d4_seed_order": d4_seed_order,
            "affine_order": affine_order,
            "affine_preserver_order": affine_preserver_order,
            "preserving_order": preserving_order,
            "full_order": full_order,
            "preserving_edge_stabilizer": preserving_edge_stabilizer,
            "full_edge_stabilizer": full_edge_stabilizer,
        },
        "exact_factorizations": {
            "heptad_size_equals_phi6": heptad_size == phi6,
            "vertices_equal_2_times_phi6": heawood_vertices == 2 * phi6,
            "vertices_equal_g2_dimension": heawood_vertices == g2_dimension,
            "edges_equal_3_times_phi6": heawood_edges == 3 * phi6,
            "edges_equal_ag21_length": heawood_edges == ag21_length,
            "affine_order_equals_2_times_ag21": affine_order == 2 * ag21_length,
            "affine_preserver_equals_ag21": affine_preserver_order == ag21_length,
            "hurwitz_units_equal_d4_seed": hurwitz_unit_order == d4_seed_order,
            "preserving_order_equals_hurwitz_units_times_phi6": (
                preserving_order == hurwitz_unit_order * phi6
            ),
            "preserving_order_equals_d4_seed_times_phi6": preserving_order == d4_seed_order * phi6,
            "preserving_order_equals_ag21_times_preserving_edge_stabilizer": (
                preserving_order == ag21_length * preserving_edge_stabilizer
            ),
            "full_order_equals_2_times_preserving": full_order == 2 * preserving_order,
            "full_order_equals_hurwitz_units_times_g2_dimension": (
                full_order == hurwitz_unit_order * g2_dimension
            ),
            "full_order_equals_d4_seed_times_g2_dimension": (
                full_order == d4_seed_order * g2_dimension
            ),
            "full_order_equals_ag21_times_full_edge_stabilizer": (
                full_order == ag21_length * full_edge_stabilizer
            ),
            "full_order_equals_affine_order_times_preserving_edge_stabilizer": (
                full_order == affine_order * preserving_edge_stabilizer
            ),
        },
        "bridge_verdict": (
            "The Szilassi/Heawood dual is now part of the same promoted shell "
            "ladder as the harmonic-cube, AG21, and D4 packages. One Heawood "
            "half is exactly Phi_6 = 7, the full vertex packet is exactly "
            "14 = dim(G2), the edge packet is exactly 21 = AG(2,1), the mod-7 "
            "affine shell is 42, the preserving symmetry shell is "
            "168 = |Hurwitz units|*Phi_6 = 24*7 = 21*8, and the full Heawood "
            "shell is 336 = |Hurwitz units|*dim(G2) = 24*14 = 21*16 = 42*8. "
            "So the torus/Fano route is already carrying the same Hurwitz/D4 "
            "seed, G2 harmonic packet, Klein coding length, and mod-7 affine "
            "shell in one exact object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_shell_ladder_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
