"""Polarized Jordan shadow of the transport 162-sector.

The current bridge stack already contains two exact ingredients:

1. internally, the transport ``162``-sector carries a canonical square-zero
   rank-81 glue operator;
2. externally, the current K3 bridge fixes a canonical head/tail polarized
   split shadow ``81 -> 162 -> 81``.

Those two facts combine into a stronger exact statement than either one alone.
Because the internal operator is square-zero on a 162-dimensional space with
rank = nullity = 81, its Jordan type is forced:

    2^81

There are exactly 81 size-2 Jordan blocks and no size-1 blocks. So the current
external bridge already matches the polarized associated graded of that
internal Jordan packet:

- invariant head of dimension 81;
- sign tail of dimension 81;
- canonical head-biased / tail-biased split shadow externally.

What it still does not realize is the nontrivial size-2 Jordan blocks
themselves, i.e. the internal nilpotent glue.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_transport_nilpotent_glue_obstruction_bridge import (
    build_transport_nilpotent_glue_obstruction_bridge_summary,
)
from w33_transport_polarized_line_shadow_bridge import (
    build_transport_polarized_line_shadow_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_jordan_shadow_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_jordan_shadow_bridge_summary() -> dict[str, object]:
    nilpotent = build_transport_nilpotent_glue_obstruction_bridge_summary()
    polarized = build_transport_polarized_line_shadow_bridge_summary()

    internal = nilpotent["internal_transport_nilpotent_glue"]
    internal_polarization = polarized["internal_transport_polarization"]
    external_shadow = polarized["external_polarized_split_shadow"]

    dimension = int(internal["dimension"])
    rank = int(internal["rank"])
    nullity = int(internal["nullity"])
    square_zero = bool(internal["square_zero"])

    two_block_count = rank if square_zero else 0
    one_block_count = dimension - 2 * two_block_count

    return {
        "status": "ok",
        "internal_transport_jordan_packet": {
            "dimension": dimension,
            "nilpotent_rank": rank,
            "nilpotent_nullity": nullity,
            "square_zero": square_zero,
            "jordan_block_size_2_count": two_block_count,
            "jordan_block_size_1_count": one_block_count,
            "exact_jordan_partition": f"2^{two_block_count}",
            "associated_graded_dimensions": [rank, nullity],
            "head_type": internal_polarization["head_type"],
            "tail_type": internal_polarization["tail_type"],
            "glue_direction": internal_polarization["nilpotent_glue_direction"],
        },
        "external_polarized_jordan_shadow": {
            "ordered_filtration_dimensions": external_shadow["ordered_filtration_dimensions"],
            "ordered_filtered_shadow_line_types": external_shadow[
                "ordered_filtered_shadow_line_types"
            ],
            "head_biased_line_coefficients": external_shadow[
                "head_biased_line_coefficients"
            ],
            "tail_biased_line_coefficients": external_shadow[
                "tail_biased_line_coefficients"
            ],
        },
        "transport_jordan_shadow_theorem": {
            "internal_transport_glue_has_exact_jordan_type_two_power_81": (
                dimension == 162
                and rank == 81
                and nullity == 81
                and square_zero is True
                and one_block_count == 0
            ),
            "internal_transport_associated_graded_is_exactly_81_head_plus_81_tail": (
                internal_polarization["ordered_filtration_dimensions"] == [81, 162, 81]
                and internal_polarization["head_type"] == "invariant"
                and internal_polarization["tail_type"] == "sign"
            ),
            "external_bridge_fixes_the_polarized_associated_graded_of_the_transport_jordan_packet": (
                external_shadow["ordered_filtration_dimensions"] == [81, 162, 81]
                and external_shadow["ordered_filtered_shadow_line_types"]
                == ["positive", "negative"]
                and polarized["transport_polarized_line_shadow_theorem"][
                    "current_bridge_reaches_a_canonical_head_tail_polarized_split_shadow"
                ]
            ),
            "current_bridge_does_not_yet_realize_the_internal_nontrivial_size_two_jordan_blocks": (
                nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"
                ]
            ),
            "current_bridge_reaches_the_polarized_jordan_shadow_but_not_the_internal_jordan_identity": (
                dimension == 162
                and rank == 81
                and nullity == 81
                and square_zero is True
                and one_block_count == 0
                and external_shadow["ordered_filtration_dimensions"] == [81, 162, 81]
                and external_shadow["ordered_filtered_shadow_line_types"]
                == ["positive", "negative"]
                and nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"
                ]
            ),
        },
        "bridge_verdict": (
            "The internal transport glue is now rigid enough to have an exact "
            "Jordan-theoretic reading: square-zero rank 81 on dimension 162 "
            "forces Jordan type 2^81. So the current K3 bridge already does "
            "more than match dimensions or even a filtered split shadow. It "
            "matches the polarized associated graded of that internal Jordan "
            "packet: invariant head 81, sign tail 81, and canonical head-"
            "biased/tail-biased split lines externally. What it still does not "
            "realize is the nontrivial size-2 Jordan blocks themselves, i.e. "
            "the internal nilpotent glue."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_jordan_shadow_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
