"""Exact transport/sl(27)/gauge realization of the first moonshine coefficient.

The previous bridge proved the local-to-global lift

    2160 -> 196560 -> 196884

through the exact identities

    196560 = 2160 * Phi_3 * Phi_6,
    196884 = 196560 + 4 * 81.

There is a sharper live realization inside the repo's current transport and
Lie data.

The exact current objects already provide:

    728 = dim sl(27)            (selector-completed traceless sector),
    729 = 728 + 1               (full completion by the unique selector),
    270 = directed transport edges,
     54 = 40 + 6 + 8            (full exceptional gauge-package rank).

Then the global moonshine numbers close exactly as

    196560 = 728 * 270,
    196884 = 729 * 270 + 54.

So the Leech kissing number is already the product of the live traceless
``sl(27)`` sector with the exact directed transport count, and the first
moonshine coefficient is the fully completed ``gl(27)`` transport block plus
the full exceptional gauge return.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "tools", ROOT / "pillars"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from THEORY_PART_CCXXIII_E8_THETA_SERIES import moonshine_decompositions
from w33_center_quad_transport_bridge import build_center_quad_transport_bridge_summary
from w33_exceptional_operator_projector_bridge import (
    build_exceptional_operator_projector_summary,
)
from w33_monster_selector_completion_bridge import build_monster_selector_completion_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_transport_moonshine_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_transport_moonshine_summary() -> dict[str, Any]:
    transport = build_center_quad_transport_bridge_summary()
    selector_completion = build_monster_selector_completion_summary()
    operator_projector = build_exceptional_operator_projector_summary()
    moonshine = moonshine_decompositions()

    sl27_traceless = int(selector_completion["selector_completion"]["sl27_traceless_dimension"])
    sl27_completed = int(selector_completion["selector_completion"]["full_golay_codewords"])
    directed_transport_edges = int(transport["transport_refinement"]["transport_edges_270"])
    gauge_package_rank = int(operator_projector["orthogonal_projectors"]["combined_gauge_package_rank"])

    leech_kissing_number = int(moonshine["196560"])
    first_moonshine_coefficient = int(moonshine["196884"])
    moonshine_gap = int(moonshine["324"])

    return {
        "status": "ok",
        "transport_moonshine_dictionary": {
            "sl27_traceless_dimension": sl27_traceless,
            "sl27_completed_dimension": sl27_completed,
            "directed_transport_edges": directed_transport_edges,
            "gauge_package_rank": gauge_package_rank,
            "leech_kissing_number": leech_kissing_number,
            "moonshine_gap": moonshine_gap,
            "first_moonshine_coefficient": first_moonshine_coefficient,
            "leech_equals_sl27_traceless_times_transport_edges": (
                leech_kissing_number == sl27_traceless * directed_transport_edges
            ),
            "first_moonshine_equals_completed_sl27_times_transport_plus_gauge_rank": (
                first_moonshine_coefficient
                == sl27_completed * directed_transport_edges + gauge_package_rank
            ),
            "moonshine_gap_equals_transport_plus_gauge_rank": (
                moonshine_gap == directed_transport_edges + gauge_package_rank
            ),
            "gauge_package_rank_equals_e6_plus_a2_plus_cartan": (
                gauge_package_rank == 40 + 6 + 8
            ),
        },
        "bridge_verdict": (
            "The first global moonshine coefficient now has a fully live "
            "transport/Lie realization. The Leech kissing number is exactly "
            "196560 = 728*270, i.e. the traceless sl(27) sector times the exact "
            "directed transport count. The first moonshine coefficient is then "
            "196884 = 729*270 + 54, i.e. the selector-completed sl(27) transport "
            "block plus the full exceptional gauge-package rank 40+6+8. So the "
            "global moonshine numbers are now written directly in the repo's "
            "current transport, selector, and exceptional operator data."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_transport_moonshine_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
