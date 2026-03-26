"""Semisimplification shadow of the transport 162-sector on the K3 side.

The current bridge already proves:

- the internal transport packet is a non-split
  ``0 -> 81 -> 162 -> 81`` extension;
- the external canonical mixed K3 packet is a split ``81 (+) ⊕ 81 (-)`` object.

This module packages the strongest exact relation available now. The two
objects agree at the semisimplified / graded shadow level:

    81 ⊕ 81.

What they do not share is the extension class: it is nonzero internally and
zero externally.
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

from w33_k3_transport_shadow_bridge import build_k3_transport_shadow_bridge_summary
from w33_transport_mixed_plane_obstruction_bridge import (
    build_transport_mixed_plane_obstruction_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_semisimplification_shadow_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_semisimplification_shadow_bridge_summary() -> dict[str, Any]:
    shadow = build_k3_transport_shadow_bridge_summary()
    obstruction = build_transport_mixed_plane_obstruction_summary()

    external_split = [
        shadow["canonical_mixed_plane"]["positive_qutrit_modes"],
        shadow["canonical_mixed_plane"]["negative_qutrit_modes"],
    ]
    internal_graded = [
        shadow["internal_transport_extension"]["short_exact_sequence_dimensions"][0],
        shadow["internal_transport_extension"]["short_exact_sequence_dimensions"][2],
    ]

    return {
        "status": "ok",
        "internal_transport_semisimplification": internal_graded,
        "external_split_shadow": external_split,
        "transport_semisimplification_shadow_theorem": {
            "internal_semisimplification_is_81_plus_81": internal_graded == [81, 81],
            "external_split_shadow_is_81_plus_81": external_split == [81, 81],
            "internal_and_external_objects_match_exactly_at_semisimplified_shadow_level": (
                internal_graded == external_split == [81, 81]
            ),
            "internal_extension_class_is_nonzero": shadow["comparison_theorem"][
                "exact_identification_as_extension_object_is_obstructed"
            ],
            "external_extension_class_is_zero": shadow["canonical_mixed_plane"][
                "is_split_two_line_package"
            ],
            "transport_k3_match_is_semisimplified_shadow_not_extension_identity": (
                internal_graded == external_split == [81, 81]
                and obstruction["comparison_theorem"][
                    "exact_split_vs_nonsplit_obstruction_is_present"
                ]
            ),
        },
        "bridge_verdict": (
            "The current transport/K3 comparison is now sharper than a raw size "
            "match. The internal non-split transport packet and the external "
            "split K3 packet agree exactly at the semisimplified shadow "
            "81 ⊕ 81, but not at the extension-class level. So the present "
            "bridge identifies the graded shadow, not the full extension object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_semisimplification_shadow_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
