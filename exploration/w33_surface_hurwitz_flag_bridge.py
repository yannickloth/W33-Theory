"""Exact surface/Hurwitz flag shell on the toroidal Csaszar/Szilassi route.

The promoted surface selector already fixes two key integers on the torus side:

    q(q+1) = 12    (the complete-graph / complete-face genus denominator at q=3)
    Phi_6(q) = 7   (the first positive toroidal dual value)

Each of the two dual toroidal seeds then carries exactly

    84 = 12 * 7 = q(q+1) Phi_6(q)

flags. This same shell closes simultaneously as

    84 = 14 * 6 = 21 * 4,

where 14 is the promoted Heawood/G2 packet, 21 is the Fano-flag / Heawood-edge
packet, 6 is the shared exceptional transport channel, and 4 is the
tetrahedral self-dual fixed-point value.

Doubling this gives

    168 = 2 * 84

for the toroidal dual pair, which is also the orientation-preserving Klein
quartic / Fano collineation order, and doubling once more gives the full
Heawood automorphism order

    336 = 4 * 84.

So the torus/Fano/Klein route already carries a rigid flag shell rather than a
mere collection of matching counts.
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

from w33_exceptional_channel_continuum_bridge import (
    build_exceptional_channel_continuum_bridge_summary,
)
from w33_heawood_klein_symmetry_bridge import build_heawood_klein_symmetry_summary
from w33_heawood_shell_ladder_bridge import build_heawood_shell_ladder_summary
from w33_surface_congruence_selector_bridge import (
    build_surface_congruence_selector_summary,
)
from w33_surface_neighborly_bridge import build_surface_neighborly_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_surface_hurwitz_flag_bridge_summary.json"


def _phi6(q: int) -> int:
    return q * q - q + 1


def _surface_flag_shell(q: int) -> int:
    return q * (q + 1) * _phi6(q)


def _positive_integer_solutions_to_surface_shell(target: int, upper_q: int = 20) -> list[int]:
    return [q for q in range(1, upper_q + 1) if _surface_flag_shell(q) == target]


@lru_cache(maxsize=1)
def build_surface_hurwitz_flag_summary() -> dict[str, Any]:
    surface_selector = build_surface_congruence_selector_summary()
    surface_neighborly = build_surface_neighborly_summary()
    heawood = build_heawood_shell_ladder_summary()
    heawood_symmetry = build_heawood_klein_symmetry_summary()
    exceptional = build_exceptional_channel_continuum_bridge_summary()

    q = 3
    q_plus_one = q + 1
    genus_denominator = q * q_plus_one
    phi6 = _phi6(q)
    tetra_fixed_point = int(
        surface_selector["fixed_and_first_torus_values"]["tetrahedron_fixed_point_value"]
    )
    nonzero_surface_residues = tuple(
        residue
        for residue in surface_selector["surface_selector"]["vertex_integral_residues_mod_12"]
        if residue != 0
    )
    single_surface_flags = int(surface_neighborly["fano_bridge"]["csaszar_flag_count"])
    dual_pair_flags = int(surface_neighborly["fano_bridge"]["dual_pair_total_flags"])
    heawood_preserving_order = int(
        heawood_symmetry["bipartition_preserving_symmetry"]["heawood_bipartition_preserving_order"]
    )
    heawood_full_order = int(
        heawood_symmetry["full_symmetry"]["full_heawood_automorphism_order"]
    )
    heawood_vertices = int(heawood["heawood_shell_dictionary"]["heawood_vertices"])
    heawood_edges = int(heawood["heawood_shell_dictionary"]["heawood_edges"])
    shared_six = int(exceptional["shared_six_channel"]["l6_a2_root_support"])
    q_solutions = _positive_integer_solutions_to_surface_shell(single_surface_flags)

    return {
        "status": "ok",
        "surface_hurwitz_dictionary": {
            "q": q,
            "q_plus_one": q_plus_one,
            "phi6": phi6,
            "genus_denominator": genus_denominator,
            "tetrahedron_fixed_point": tetra_fixed_point,
            "nonzero_surface_residues_mod_12": list(nonzero_surface_residues),
            "single_surface_flags": single_surface_flags,
            "dual_pair_flags": dual_pair_flags,
            "heawood_preserving_order": heawood_preserving_order,
            "heawood_full_order": heawood_full_order,
            "heawood_vertices": heawood_vertices,
            "heawood_edges": heawood_edges,
            "shared_six_channel": shared_six,
        },
        "exact_factorizations": {
            "genus_denominator_equals_q_times_q_plus_one": genus_denominator == q * q_plus_one,
            "first_toroidal_value_equals_phi6": (
                int(surface_selector["fixed_and_first_torus_values"]["first_toroidal_dual_value"]) == phi6
            ),
            "nonzero_surface_residues_are_q_q_plus_one_phi6": (
                nonzero_surface_residues == (q, q_plus_one, phi6)
            ),
            "nonzero_surface_residues_add_to_phi6": (
                nonzero_surface_residues[0] + nonzero_surface_residues[1] == nonzero_surface_residues[2]
            ),
            "single_surface_flags_equals_product_of_nonzero_surface_residues": (
                single_surface_flags
                == nonzero_surface_residues[0]
                * nonzero_surface_residues[1]
                * nonzero_surface_residues[2]
            ),
            "single_surface_flags_equals_genus_denominator_times_phi6": (
                single_surface_flags == genus_denominator * phi6
            ),
            "single_surface_flags_equals_heawood_vertices_times_shared_six": (
                single_surface_flags == heawood_vertices * shared_six
            ),
            "single_surface_flags_equals_heawood_edges_times_tetrahedron_fixed_point": (
                single_surface_flags == heawood_edges * tetra_fixed_point
            ),
            "dual_pair_flags_equals_two_single_surface_flag_packets": (
                dual_pair_flags == 2 * single_surface_flags
            ),
            "dual_pair_flags_equals_heawood_preserving_order": (
                dual_pair_flags == heawood_preserving_order
            ),
            "full_heawood_order_equals_four_single_surface_flag_packets": (
                heawood_full_order == 4 * single_surface_flags
            ),
            "full_heawood_order_equals_two_dual_pair_flag_packets": (
                heawood_full_order == 2 * dual_pair_flags
            ),
        },
        "q3_selection": {
            "surface_flag_shell_formula": "q(q+1)Phi_6(q)",
            "phi6_formula": "q^2 - q + 1",
            "target_single_surface_flag_packet": single_surface_flags,
            "positive_integer_solutions": q_solutions,
            "q3_is_unique_positive_solution": q_solutions == [3],
        },
        "bridge_verdict": (
            "The toroidal Csaszar/Szilassi route already carries a rigid flag shell. "
            "At q=3 the genus denominator is q(q+1)=12 and the first toroidal dual "
            "value is Phi_6(q)=7, so the nonzero admissible surface residues are "
            "exactly 3,4,7. They already close as 3+4=7 and 3*4*7=84, so each "
            "toroidal seed has exactly 84 flags. That same 84 is simultaneously 12*7, "
            "14*6, and 21*4, tying the torus route to "
            "the promoted G2 packet, the shared six-channel exceptional core, the "
            "Fano-flag/Heawood-edge packet, and the tetrahedral fixed point. Doubling "
            "gives 168, the exact toroidal dual-pair and Klein preserving shell, and "
            "doubling once more gives the full Heawood shell 336. More sharply, the "
            "surface-shell equation q(q+1)Phi_6(q)=84 has the unique positive integer "
            "solution q=3, so the torus/Hurwitz route supplies another exact q=3 "
            "selector rather than only another count coincidence."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_surface_hurwitz_flag_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
