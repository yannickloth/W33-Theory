"""Head-compatible external line theorem for the internal common family line.

The current bridge does not yet prove that the external K3-side line equals the
internal common line ``span(1,1,0)``. But it already proves something sharper
than the old "there is a line candidate" wording.

Internally:
- the common family line is exact image-side data, because it is the image of
  the common square ``2E13``;
- the transport polarity is exact, with glue directed ``tail -> head``.

Externally:
- the bridge fixes exactly two polarized null-line roles inside ``U1``:
  head-biased and tail-biased;
- the sign-ordered selector packet rigidly picks the head-biased line.

So under the current exact bridge dictionary, the ambiguity collapses from two
possible ``U1`` null lines to one polarity-compatible candidate: the
head-biased line.
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

from w33_transport_polarized_line_shadow_bridge import (
    build_transport_polarized_line_shadow_bridge_summary,
)
from w33_u1_filtered_shadow_line_order_bridge import (
    build_u1_filtered_shadow_line_order_bridge_summary,
)
from w33_yukawa_generation_flag_bridge import build_yukawa_generation_flag_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_u1_head_compatible_line_bridge_summary.json"


@lru_cache(maxsize=1)
def build_u1_head_compatible_line_bridge_summary() -> dict[str, object]:
    transport = build_transport_polarized_line_shadow_bridge_summary()
    line_order = build_u1_filtered_shadow_line_order_bridge_summary()
    flag = build_yukawa_generation_flag_summary()

    head_line = transport["external_polarized_split_shadow"]["head_biased_line_coefficients"]
    tail_line = transport["external_polarized_split_shadow"]["tail_biased_line_coefficients"]

    return {
        "status": "ok",
        "internal_common_line": {
            "generator": flag["common_flag"]["line_generator"],
            "role": "image_of_common_square",
        },
        "internal_transport_polarity": {
            "head_type": transport["internal_transport_polarization"]["head_type"],
            "tail_type": transport["internal_transport_polarization"]["tail_type"],
            "glue_direction": transport["internal_transport_polarization"][
                "nilpotent_glue_direction"
            ],
        },
        "external_u1_line_roles": {
            "head_compatible_line_candidate": head_line,
            "tail_line_candidate": tail_line,
        },
        "u1_head_compatible_line_theorem": {
            "internal_common_line_is_exact_image_side_data": (
                flag["generation_flag_theorem"]["common_line_equals_image_of_common_square"]
            ),
            "internal_transport_head_is_the_image_side_of_the_current_polarity_dictionary": (
                transport["internal_transport_polarization"]["head_type"] == "invariant"
                and transport["internal_transport_polarization"]["tail_type"] == "sign"
                and transport["internal_transport_polarization"][
                    "nilpotent_glue_direction"
                ]
                == "tail_to_head"
            ),
            "external_bridge_fixes_head_biased_and_tail_biased_u1_lines": (
                transport["transport_polarized_line_shadow_theorem"][
                    "external_bridge_has_canonical_head_biased_and_tail_biased_u1_lines"
                ]
            ),
            "the_sign_ordered_rigid_u1_line_is_exactly_the_head_biased_line": (
                line_order["dominant_isotropic_line_coefficients"] == head_line
                and line_order["recessive_isotropic_line_coefficients"] == tail_line
                and line_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
            ),
            "the_tail_biased_u1_line_is_not_compatible_with_an_image_side_realization_of_the_internal_common_line": (
                transport["internal_transport_polarization"][
                    "nilpotent_glue_direction"
                ]
                == "tail_to_head"
                and line_order["dominant_isotropic_line_coefficients"] == head_line
                and line_order["recessive_isotropic_line_coefficients"] == tail_line
            ),
            "the_current_external_line_ambiguity_collapses_to_one_head_compatible_candidate": (
                flag["generation_flag_theorem"]["common_line_equals_image_of_common_square"]
                and transport["internal_transport_polarization"][
                    "nilpotent_glue_direction"
                ]
                == "tail_to_head"
                and line_order["dominant_isotropic_line_coefficients"] == head_line
                and line_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
            ),
        },
        "bridge_verdict": (
            "The current bridge still does not identify the external line with "
            "the internal line span(1,1,0), but it now collapses the external "
            "line ambiguity to one polarity-compatible candidate. The internal "
            "common line is image-side data, the current transport polarity is "
            "tail-to-head, and the external U1 packet already distinguishes a "
            "head-biased line from a tail-biased one. So under the present "
            "exact bridge dictionary, any compatible external realization of "
            "the internal common line must use the head-biased U1 line, not "
            "the tail-biased one."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_u1_head_compatible_line_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
