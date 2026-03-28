"""Canonical rigid split transport avatar on the current K3 bridge.

Two recent bridge reductions fit together tightly:

1. the external line ambiguity collapses to one head-compatible `U1` line;
2. the unique external tail-to-head glue slot is structurally zero.

So the current bridge does not merely see a vague shadow of the internal
transport packet. It fixes one exact split avatar of it:

- head line: the head-compatible `U1` line,
- middle object: the split external 162-packet,
- tail line: the tail-biased `U1` line,
- glue: zero.

This is still not the internal non-split transport object, but it is now a
canonical rigid split transport avatar of that object.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_external_glue_zero_forcing_bridge import (
    build_external_glue_zero_forcing_bridge_summary,
)
from w33_transport_polarized_line_shadow_bridge import (
    build_transport_polarized_line_shadow_bridge_summary,
)
from w33_u1_head_compatible_line_bridge import (
    build_u1_head_compatible_line_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_rigid_split_avatar_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_rigid_split_avatar_bridge_summary() -> dict[str, Any]:
    polarized = build_transport_polarized_line_shadow_bridge_summary()
    head_line = build_u1_head_compatible_line_bridge_summary()
    zero_glue = build_external_glue_zero_forcing_bridge_summary()

    return {
        "status": "ok",
        "canonical_external_transport_avatar": {
            "head_line": head_line["external_u1_line_roles"][
                "head_compatible_line_candidate"
            ],
            "tail_line": head_line["external_u1_line_roles"]["tail_line_candidate"],
            "ordered_filtration_dimensions": polarized["external_polarized_split_shadow"][
                "ordered_filtration_dimensions"
            ],
            "glue_direction": polarized["internal_transport_polarization"][
                "nilpotent_glue_direction"
            ],
            "external_glue_rank": zero_glue["external_glue_slot"]["current_external_rank"],
            "external_glue_state": zero_glue["external_glue_slot"]["current_external_state"],
        },
        "transport_rigid_split_avatar_theorem": {
            "current_bridge_fixes_a_head_compatible_external_head_line": (
                head_line["u1_head_compatible_line_theorem"][
                    "the_current_external_line_ambiguity_collapses_to_one_head_compatible_candidate"
                ]
            ),
            "current_bridge_fixes_a_canonical_external_tail_line": (
                polarized["transport_polarized_line_shadow_theorem"][
                    "external_bridge_has_canonical_head_biased_and_tail_biased_u1_lines"
                ]
            ),
            "current_bridge_fixes_the_ordered_81_in_162_out_81_split_avatar_dimensions": (
                polarized["external_polarized_split_shadow"][
                    "ordered_filtration_dimensions"
                ]
                == [81, 162, 81]
            ),
            "current_bridge_forces_the_external_glue_of_that_avatar_to_be_zero": (
                zero_glue["external_glue_zero_forcing_theorem"][
                    "the_unique_external_tail_to_head_glue_slot_is_structurally_zero_on_the_present_bridge_object"
                ]
            ),
            "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet": (
                head_line["u1_head_compatible_line_theorem"][
                    "the_current_external_line_ambiguity_collapses_to_one_head_compatible_candidate"
                ]
                and polarized["transport_polarized_line_shadow_theorem"][
                    "external_bridge_has_canonical_head_biased_and_tail_biased_u1_lines"
                ]
                and polarized["external_polarized_split_shadow"][
                    "ordered_filtration_dimensions"
                ]
                == [81, 162, 81]
                and zero_glue["external_glue_zero_forcing_theorem"][
                    "the_unique_external_tail_to_head_glue_slot_is_structurally_zero_on_the_present_bridge_object"
                ]
            ),
            "that_avatar_is_still_not_the_internal_nonsplit_transport_object": (
                zero_glue["external_glue_zero_forcing_theorem"][
                    "split_vs_nonsplit_obstruction_is_already_exact_at_the_current_bridge_level"
                ]
            ),
        },
        "bridge_verdict": (
            "The current bridge now fixes one canonical rigid split avatar of "
            "the internal transport packet: head-compatible U1 line, tail U1 "
            "line, ordered dimensions 81 -> 162 -> 81, and zero glue. This is "
            "still not the internal non-split object, but it is no longer just "
            "an undifferentiated shadow."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_rigid_split_avatar_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
