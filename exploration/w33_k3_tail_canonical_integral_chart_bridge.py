"""Canonical integral chart criterion on the fixed K3 tail package.

CDV localized the live wall to any promoted witness chart:

- `ΔC = 14105`
- `ΔL = 143654`
- `ΔQ_seed = 3396050/3`
- `ΔQ_sd1 = 3904481/4`

Each chart recovers the same exact scale `217/12`, so exact K3 tail
realization is already equivalent to solving any one of those anchored
extension problems.

The next exact reduction is to choose the least-complexity local chart:

- among the four promoted increments, `ΔC` and `ΔL` are integral;
- among those integral charts, `ΔC = 14105` has the smaller absolute value;
- so `ΔC` is the canonical least-complexity exact chart.

Therefore the live external wall is now one canonical integral extension
problem: realizing `ΔC = 14105` on the fixed carrier-preserving K3 package.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_canonical_integral_chart_bridge_summary.json"
)

PROMOTED_CHARTS = {
    "dC": Fraction(14105, 1),
    "dL": Fraction(143654, 1),
    "dQ_seed": Fraction(3396050, 3),
    "dQ_sd1": Fraction(3904481, 4),
}


@lru_cache(maxsize=1)
def build_k3_tail_canonical_integral_chart_summary() -> dict[str, Any]:
    from w33_k3_tail_coordinate_extension_equivalence_bridge import (
        build_k3_tail_coordinate_extension_equivalence_summary,
    )

    base = build_k3_tail_coordinate_extension_equivalence_summary()
    fixed = base["fixed_k3_tail_exactness_channel"]

    chart_complexity = {
        name: {
            "exact_increment": str(value),
            "denominator": value.denominator,
            "abs_numerator": abs(value.numerator),
            "is_integral": value.denominator == 1,
        }
        for name, value in PROMOTED_CHARTS.items()
    }

    integral_charts = {
        name: info for name, info in chart_complexity.items() if info["is_integral"]
    }
    canonical_chart_name = min(
        integral_charts,
        key=lambda name: (
            integral_charts[name]["denominator"],
            integral_charts[name]["abs_numerator"],
            name,
        ),
    )

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "chart_complexity": chart_complexity,
        "canonical_integral_chart": {
            "name": canonical_chart_name,
            **integral_charts[canonical_chart_name],
        },
        "k3_tail_canonical_integral_chart_theorem": {
            "all_promoted_coordinate_charts_are_already_equivalent_local_extension_problems": (
                base["k3_tail_coordinate_extension_equivalence_theorem"][
                    "therefore_each_promoted_coordinate_chart_gives_an_equivalent_local_extension_problem"
                ]
            ),
            "the_promoted_integral_charts_are_exactly_dC_and_dL": (
                set(integral_charts) == {"dC", "dL"}
            ),
            "among_integral_charts_dC_is_the_least_complexity_chart_by_absolute_size": (
                canonical_chart_name == "dC"
                and integral_charts["dC"]["abs_numerator"]
                < integral_charts["dL"]["abs_numerator"]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_the_canonical_integral_chart_equation_deltaC_equals_14105": (
                base["k3_tail_coordinate_extension_equivalence_theorem"][
                    "therefore_each_promoted_coordinate_chart_gives_an_equivalent_local_extension_problem"
                ]
                and canonical_chart_name == "dC"
                and integral_charts["dC"]["exact_increment"] == "14105"
            ),
            "the_live_external_wall_is_now_one_canonical_integral_coordinate_extension_problem": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and canonical_chart_name == "dC"
                and integral_charts["dC"]["exact_increment"] == "14105"
                and base["k3_tail_coordinate_extension_equivalence_theorem"][
                    "the_live_external_wall_is_now_one_coordinate_anchored_extension_problem_in_any_promoted_chart"
                ]
            ),
        },
        "bridge_verdict": (
            "The K3 tail wall has now reduced to one least-complexity local "
            "equation. All four promoted witness charts are equivalent, but "
            "the integral charts are exactly dC and dL, and dC=14105 is the "
            "smaller one. So the remaining external wall is now one canonical "
            "integral extension problem: realize ΔC=14105 on the fixed "
            "carrier-preserving K3 package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_tail_canonical_integral_chart_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
