"""Coordinate-anchored extension equivalence on the fixed K3 tail package.

CDIV collapsed exact K3 tail realization on the fixed carrier-preserving
package to existence of any one exact affine increment witness:

- `ΔC = 14105`
- `ΔL = 143654`
- `ΔQ_seed = 3396050/3`
- `ΔQ_sd1 = 3904481/4`

Each of those increments already recovers the same exact scale `217/12`, so
they are not genuinely different external targets. The next exact reduction is
to package that fact as a local extension theorem:

- exact K3 tail realization is equivalent to a `ΔC`-anchored extension;
- equally, it is equivalent to a `ΔL`-anchored extension;
- equally, it is equivalent to a `ΔQ_seed`-anchored extension;
- equally, it is equivalent to a `ΔQ_sd1`-anchored extension.

So the live external wall is now one local coordinate-anchored extension
problem in any promoted witness chart on the same fixed package.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_coordinate_extension_equivalence_bridge_summary.json"
)

COORDINATE_CHARTS = ["dC", "dL", "dQ_seed", "dQ_sd1"]


@lru_cache(maxsize=1)
def build_k3_tail_coordinate_extension_equivalence_summary() -> dict[str, Any]:
    from w33_k3_tail_affine_increment_witness_bridge import (
        build_k3_tail_affine_increment_witness_summary,
    )
    from w33_k3_tail_increment_realization_equivalence_bridge import (
        build_k3_tail_increment_realization_equivalence_summary,
    )

    increment = build_k3_tail_affine_increment_witness_summary()
    realization = build_k3_tail_increment_realization_equivalence_summary()
    fixed = increment["fixed_k3_tail_exactness_channel"]

    chart_scales = {
        name: increment["affine_increment_witnesses"][name]["recovered_scale"]
        for name in COORDINATE_CHARTS
    }
    chart_extension_equivalences = {
        name: {
            "anchored_increment": increment["affine_increment_witnesses"][name][
                "exact_increment"
            ],
            "recovered_scale": chart_scales[name],
            "is_exact_extension_chart": chart_scales[name] == "217/12",
        }
        for name in COORDINATE_CHARTS
    }

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "coordinate_extension_charts": chart_extension_equivalences,
        "k3_tail_coordinate_extension_equivalence_theorem": {
            "each_promoted_coordinate_chart_recovers_the_same_exact_scale_217_over_12": (
                all(scale == "217/12" for scale in chart_scales.values())
            ),
            "exact_k3_tail_realization_is_already_equivalent_to_any_one_exact_affine_increment_witness": (
                realization["k3_tail_increment_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_any_one_exact_affine_increment_witness"
                ]
            ),
            "therefore_each_promoted_coordinate_chart_gives_an_equivalent_local_extension_problem": (
                all(scale == "217/12" for scale in chart_scales.values())
                and realization["k3_tail_increment_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_any_one_exact_affine_increment_witness"
                ]
            ),
            "the_live_external_wall_is_now_one_coordinate_anchored_extension_problem_in_any_promoted_chart": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and all(scale == "217/12" for scale in chart_scales.values())
                and realization["k3_tail_increment_realization_equivalence_theorem"][
                    "the_live_external_wall_is_now_exactly_one_affine_increment_witness_existence_problem"
                ]
            ),
        },
        "bridge_verdict": (
            "The sharpened K3 wall is now local in any promoted witness chart. "
            "Because each affine increment witness recovers the same exact "
            "scale 217/12, the four promoted coordinates define equivalent "
            "anchored extension problems on the same fixed carrier-preserving "
            "package. So the remaining external wall is no longer a coupled "
            "four-coordinate mystery; it is one coordinate-anchored K3 "
            "extension problem in any chosen promoted chart."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_k3_tail_coordinate_extension_equivalence_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
