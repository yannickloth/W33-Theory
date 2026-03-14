"""Exact dual realization of the first moonshine gap.

The recent Monster closures already give two exact live forms for the first
nontrivial moonshine coefficient:

    196560 = 728 * 270,
    196884 = 729 * 270 + 54.

What is still hidden in that presentation is the role of the *gap*

    324 = 196884 - 196560.

This module identifies that gap in two exact repo-native ways:

    324 = 54 * 6 = (40 + 6 + 8) * 6,
    324 = 4 * 81 = (q + 1) * q^4.

So the same moonshine gap is simultaneously

1. the full exceptional gauge-package rank times the shared six-channel core,
2. the spacetime factor times the exact logical-qutrit matter sector.

Equivalently, the first moonshine coefficient admits the dual exact closures

    196884 = 728 * 270 + 54 * 6,
    196884 = 729 * 270 + 54.

This is the cleanest current bridge between the transport/moonshine side and
the exceptional/generation side: the same `324` is both exceptional gauge
return and spacetime-times-matter.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_exceptional_operator_projector_bridge import (
    build_exceptional_operator_projector_summary,
)
from w33_monster_moonshine_lift_bridge import build_monster_moonshine_lift_summary
from w33_monster_transport_moonshine_bridge import build_monster_transport_moonshine_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_gap_duality_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_gap_duality_summary() -> dict[str, Any]:
    moonshine_lift = build_monster_moonshine_lift_summary()
    transport_moonshine = build_monster_transport_moonshine_summary()
    exceptional = build_exceptional_operator_projector_summary()

    moonshine_dict = moonshine_lift["moonshine_lift_dictionary"]
    transport_dict = transport_moonshine["transport_moonshine_dictionary"]
    exceptional_dict = exceptional["orthogonal_projectors"]
    channel_ranks = exceptional["operator_space"]["channel_ranks"]

    leech = int(transport_dict["leech_kissing_number"])
    first = int(transport_dict["first_moonshine_coefficient"])
    gap = int(transport_dict["moonshine_gap"])
    sl27_traceless = int(transport_dict["sl27_traceless_dimension"])
    sl27_completed = int(transport_dict["sl27_completed_dimension"])
    transport_edges = int(transport_dict["directed_transport_edges"])
    gauge_rank = int(transport_dict["gauge_package_rank"])
    shared_six = int(channel_ranks["a2"])
    spacetime_factor = int(moonshine_dict["spacetime_factor"])
    logical_qutrits = int(moonshine_dict["logical_qutrits"])

    return {
        "status": "ok",
        "moonshine_gap_dictionary": {
            "leech_kissing_number": leech,
            "first_moonshine_coefficient": first,
            "moonshine_gap": gap,
            "sl27_traceless_dimension": sl27_traceless,
            "sl27_completed_dimension": sl27_completed,
            "directed_transport_edges": transport_edges,
            "gauge_package_rank": gauge_rank,
            "shared_six_channel_rank": shared_six,
            "spacetime_factor": spacetime_factor,
            "logical_qutrits": logical_qutrits,
            "gap_equals_exceptional_gauge_rank_times_shared_six": gap == gauge_rank * shared_six,
            "gap_equals_spacetime_factor_times_logical_qutrits": gap == spacetime_factor * logical_qutrits,
            "exceptional_gap_matches_spacetime_matter_gap": (
                gauge_rank * shared_six == spacetime_factor * logical_qutrits
            ),
            "first_moonshine_equals_traceless_transport_plus_exceptional_gap": (
                first == sl27_traceless * transport_edges + gauge_rank * shared_six
            ),
            "first_moonshine_equals_completed_transport_plus_gauge_rank": (
                first == sl27_completed * transport_edges + gauge_rank
            ),
            "gauge_rank_equals_e6_plus_a2_plus_cartan": gauge_rank == 40 + 6 + 8,
            "shared_six_is_live_a2_rank": shared_six == 6,
        },
        "bridge_verdict": (
            "The first moonshine gap is now exact in two independent live forms. "
            "The gap 324 between 196884 and 196560 is simultaneously the full "
            "exceptional gauge-package rank times the shared six-channel core, "
            "324 = 54*6, and the spacetime factor times the exact logical-qutrit "
            "matter sector, 324 = 4*81. So the first moonshine coefficient has "
            "the dual exact closures 196884 = 728*270 + 54*6 and "
            "196884 = 729*270 + 54. This is the cleanest current bridge between "
            "the transport/moonshine side and the exceptional/generation side."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_gap_duality_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
