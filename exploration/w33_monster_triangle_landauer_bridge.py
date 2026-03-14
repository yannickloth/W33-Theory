"""Native W33 triangle-stabilizer / moonshine-gap / Landauer bridge.

The recent Monster closures already identified the first moonshine gap

    324 = 196884 - 196560

in two live forms:

    324 = 54 * 6,
    324 = 4 * 81.

This module promotes the missing native W33 interpretation.  The same `324`
is already the local triangle stabilizer of the W(3,3) geometry:

    |Aut(W33)| / #triangles = 51840 / 160 = 324.

Equivalently, with q = 3 and the native SRG/GQ formulas,

    |Aut(W33)| = q^4 (q^2 - 1) (q^4 - 1),
    #triangles = ((q+1)(q^2+1)) * (q(q+1)) * (q-1) / 6,
    |Stab(Delta)| = 6 q^3 (q - 1).

At q = 3 this same local stabilizer closes all of the live promoted forms:

    324 = |Stab(Delta)| = 12 * 27 = 54 * 6 = 4 * 81.

Because Landauer acts on exact state counts, this also yields the exact local
entropy ledger

    E_gap / (kT) = ln 324 = ln 54 + ln 6 = ln 4 + ln 81.

So the first moonshine gap is not just an external correction term: it is
already a native local symmetry count of the W33 interaction triangles, and
its Landauer cost decomposes in the same exceptional/matter ways as the rest
of the promoted theory.
"""

from __future__ import annotations

from functools import lru_cache
import json
from math import log
from pathlib import Path
from typing import Any

from w33_monster_gap_duality_bridge import build_monster_gap_duality_summary
from w33_monster_transport_moonshine_bridge import build_monster_transport_moonshine_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_triangle_landauer_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_triangle_landauer_summary() -> dict[str, Any]:
    standard_model = build_standard_model_cyclotomic_summary()
    gap_duality = build_monster_gap_duality_summary()
    transport_moonshine = build_monster_transport_moonshine_summary()

    q = int(standard_model["cyclotomic_data"]["q"])
    gauge_rank = int(gap_duality["moonshine_gap_dictionary"]["gauge_package_rank"])
    shared_six = int(gap_duality["moonshine_gap_dictionary"]["shared_six_channel_rank"])
    spacetime_factor = int(gap_duality["moonshine_gap_dictionary"]["spacetime_factor"])
    logical_qutrits = int(gap_duality["moonshine_gap_dictionary"]["logical_qutrits"])
    moonshine_gap = int(gap_duality["moonshine_gap_dictionary"]["moonshine_gap"])
    transport_traceless = int(transport_moonshine["transport_moonshine_dictionary"]["sl27_traceless_dimension"])
    transport_edges = int(transport_moonshine["transport_moonshine_dictionary"]["directed_transport_edges"])
    first_moonshine = int(transport_moonshine["transport_moonshine_dictionary"]["first_moonshine_coefficient"])

    vertices = (q + 1) * (q * q + 1)
    degree = q * (q + 1)
    lambda_value = q - 1
    triangles = vertices * degree * lambda_value // 6
    automorphism_order = q**4 * (q * q - 1) * (q**4 - 1)
    triangle_stabilizer = automorphism_order // triangles
    general_formula_value = 6 * q**3 * (q - 1)
    generation_block = q**3

    exceptional_states = gauge_rank * shared_six
    matter_states = spacetime_factor * logical_qutrits
    degree_generation_states = degree * generation_block

    return {
        "status": "ok",
        "triangle_landauer_dictionary": {
            "q": q,
            "vertices": vertices,
            "degree": degree,
            "lambda": lambda_value,
            "triangle_count": triangles,
            "automorphism_order": automorphism_order,
            "triangle_stabilizer": triangle_stabilizer,
            "triangle_stabilizer_general_formula": "6*q^3*(q-1)",
            "triangle_stabilizer_matches_general_formula": triangle_stabilizer == general_formula_value,
            "moonshine_gap": moonshine_gap,
            "triangle_stabilizer_equals_moonshine_gap": triangle_stabilizer == moonshine_gap,
            "gauge_package_rank": gauge_rank,
            "shared_six_channel_rank": shared_six,
            "spacetime_factor": spacetime_factor,
            "logical_qutrits": logical_qutrits,
            "generation_block": generation_block,
            "triangle_stabilizer_equals_exceptional_times_shared_six": triangle_stabilizer == exceptional_states,
            "triangle_stabilizer_equals_spacetime_times_logical_qutrits": triangle_stabilizer == matter_states,
            "triangle_stabilizer_equals_degree_times_generation": triangle_stabilizer == degree_generation_states,
            "traceless_transport_block": transport_traceless * transport_edges,
            "first_moonshine_coefficient": first_moonshine,
            "first_moonshine_equals_transport_traceless_plus_triangle_stabilizer": (
                first_moonshine == transport_traceless * transport_edges + triangle_stabilizer
            ),
            "landauer_gap_over_kT": {
                "exact": "ln(324)",
                "float": log(triangle_stabilizer),
            },
            "landauer_exceptional_split": "ln(54) + ln(6)",
            "landauer_matter_split": "ln(4) + ln(81)",
            "landauer_exceptional_split_matches": abs(log(triangle_stabilizer) - (log(gauge_rank) + log(shared_six))) < 1e-12,
            "landauer_matter_split_matches": abs(log(triangle_stabilizer) - (log(spacetime_factor) + log(logical_qutrits))) < 1e-12,
        },
        "bridge_verdict": (
            "The first moonshine gap is now a native local symmetry of W(3,3). "
            "The graph has 160 interaction triangles and automorphism group "
            "order 51840, so orbit-stabilizer gives the exact local triangle "
            "stabilizer |Stab(Delta)| = 51840/160 = 324. That same count is "
            "already the live moonshine gap, and it closes all promoted forms "
            "at once: 324 = 12*27 = 54*6 = 4*81. So 196884 = 728*270 + "
            "|Stab(Delta)|, and in Landauer language the same local symmetry "
            "cost is E_gap/(kT) = ln 324 = ln 54 + ln 6 = ln 4 + ln 81. The "
            "first moonshine gap is therefore not an external correction term; "
            "it is already the native local W33 triangle symmetry written in "
            "exceptional, matter, and thermodynamic language."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_triangle_landauer_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
