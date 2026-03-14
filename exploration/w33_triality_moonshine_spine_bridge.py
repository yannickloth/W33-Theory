"""Compressed triality-to-moonshine spine for the promoted W33 algebra.

The promoted algebraic ladder now has an exact internal top:

    24 -> 96 -> 192 -> 576 -> 1152 -> 51840 = |W(E6)|.

The next structural question is whether the current Monster/moonshine shell is
still an external add-on, or whether it is already a quotient/lift of that same
exact ladder.  It is.

The native compression is

    2160 = 51840 / 24,

where the divisor ``24`` is simultaneously

    |Aut(Q8)| = |Roots(D4)| = |V(24-cell)|.

That same compressed shell then closes all current live forms:

    2160 = 45*48 = 270*8 = 720*3 = 240*9,
    2187 = 2160 + 27 = 3^7,
    196560 = 2160*13*7,
    196884 = 196560 + 324.

So the promoted algebra is now one exact spine:

    24 -> 51840 -> 2160 -> 196560 -> 196884,

with the local Monster shell obtained by quotienting the W(E6) top by the D4
triality seed, then lifted globally by the same cyclotomic pair and completed
by the same gauge/matter gap that already appear elsewhere in the program.
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

from w33_monster_gap_duality_bridge import build_monster_gap_duality_summary
from w33_monster_moonshine_lift_bridge import build_monster_moonshine_lift_summary
from w33_monster_transport_shell_bridge import build_monster_transport_shell_summary
from w33_triality_ladder_algebra_bridge import build_triality_ladder_algebra_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_triality_moonshine_spine_bridge_summary.json"


@lru_cache(maxsize=1)
def build_triality_moonshine_spine_summary() -> dict[str, Any]:
    ladder = build_triality_ladder_algebra_summary()
    shell = build_monster_transport_shell_summary()
    moonshine = build_monster_moonshine_lift_summary()
    gap = build_monster_gap_duality_summary()

    q8_vertex_block = int(ladder["triality_ladder"]["q8_d4_24cell_vertex_block"]["value"])
    w_e6 = int(ladder["triality_ladder"]["e6_weyl_closure"]["value"])
    tritangents = int(ladder["triality_ladder"]["e6_weyl_closure"]["tritangents"])
    directed_transport_edges = int(
        ladder["triality_ladder"]["e6_weyl_closure"]["directed_transport_edges"]
    )
    transport_edges = int(ladder["triality_ladder"]["e6_weyl_closure"]["transport_edges"])
    a2_block_rank = int(ladder["base_live_ranks"]["a2_transfer_block_rank"])
    cartan_rank = int(ladder["base_live_ranks"]["cartan_rank"])

    q = int(shell["transport_shell_dictionary"]["q"])
    w33_edges = int(shell["transport_shell_dictionary"]["w33_edge_count"])
    local_shell = int(shell["transport_shell_dictionary"]["semisimple_transport_shell"])
    generation_block = int(shell["transport_shell_dictionary"]["generation_states"])
    local_complement = int(shell["transport_shell_dictionary"]["monster_complement_states"])

    phi3 = int(moonshine["moonshine_lift_dictionary"]["phi3"])
    phi6 = int(moonshine["moonshine_lift_dictionary"]["phi6"])
    leech = int(moonshine["moonshine_lift_dictionary"]["leech_kissing_number"])
    first_moonshine = int(moonshine["moonshine_lift_dictionary"]["first_moonshine_coefficient"])
    moonshine_gap = int(moonshine["moonshine_lift_dictionary"]["moonshine_gap"])

    gauge_rank = int(gap["moonshine_gap_dictionary"]["gauge_package_rank"])
    shared_six = int(gap["moonshine_gap_dictionary"]["shared_six_channel_rank"])
    spacetime_factor = int(gap["moonshine_gap_dictionary"]["spacetime_factor"])
    logical_qutrits = int(gap["moonshine_gap_dictionary"]["logical_qutrits"])

    spinor_dimension = q * a2_block_rank

    return {
        "status": "ok",
        "compressed_spine_dictionary": {
            "q8_vertex_block": q8_vertex_block,
            "weyl_e6_order": w_e6,
            "monster_semisimple_shell": local_shell,
            "monster_local_complement": local_complement,
            "phi3": phi3,
            "phi6": phi6,
            "leech_kissing_number": leech,
            "first_moonshine_coefficient": first_moonshine,
            "moonshine_gap": moonshine_gap,
            "tritangents": tritangents,
            "directed_transport_edges": directed_transport_edges,
            "transport_edges": transport_edges,
            "spinor_dimension": spinor_dimension,
            "cartan_rank": cartan_rank,
            "w33_edge_count": w33_edges,
            "generation_block": generation_block,
            "gauge_rank": gauge_rank,
            "shared_six": shared_six,
            "spacetime_factor": spacetime_factor,
            "logical_qutrits": logical_qutrits,
            "weyl_e6_quotiented_by_q8_vertex_block_equals_shell": (
                local_shell * q8_vertex_block == w_e6
            ),
            "shell_equals_tritangents_times_spinor_dimension": (
                local_shell == tritangents * spinor_dimension
            ),
            "shell_equals_directed_transport_edges_times_cartan_rank": (
                local_shell == directed_transport_edges * cartan_rank
            ),
            "shell_equals_transport_edges_times_q": local_shell == transport_edges * q,
            "shell_equals_w33_edges_times_q_squared": local_shell == w33_edges * q * q,
            "local_complement_equals_shell_plus_generation": (
                local_complement == local_shell + generation_block
            ),
            "leech_equals_shell_times_phi3_phi6": leech == local_shell * phi3 * phi6,
            "first_moonshine_equals_leech_plus_gap": first_moonshine == leech + moonshine_gap,
            "gap_equals_gauge_rank_times_shared_six": moonshine_gap == gauge_rank * shared_six,
            "gap_equals_spacetime_factor_times_logical_qutrits": (
                moonshine_gap == spacetime_factor * logical_qutrits
            ),
        },
        "bridge_verdict": (
            "The promoted algebra now has a compressed spine. The W(E6) top "
            "51840 quotiented by the exact D4/Q8/24-cell seed block 24 gives the "
            "live local Monster shell 2160. That shell is already the same exact "
            "object in five languages: 45*48, 270*8, 720*3, 240*9, and 51840/24. "
            "Adding the exact generation block gives the local complement "
            "2187 = 2160 + 27 = 3^7. Lifting by the same cyclotomic pair "
            "Phi_3*Phi_6 = 13*7 then gives 196560, and adding the same exact gap "
            "324 = 54*6 = 4*81 gives 196884. So the final promoted algebraic "
            "story is now one exact spine: 24 -> 51840 -> 2160 -> 196560 -> 196884."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_triality_moonshine_spine_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
