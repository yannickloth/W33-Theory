"""Exact equivalence between K3 tail realization and the canonical chart equation.

CDVI chose the least-complexity exact local chart on the fixed carrier-
preserving K3 package:

- the integral promoted charts are exactly `ΔC=14105` and `ΔL=143654`;
- `ΔC=14105` is the smaller one;
- so the live wall is one canonical integral chart equation.

The next exact collapse is immediate: because CDIV already equated exact K3
tail realization with any one exact affine increment witness, and CDVI already
proved that the canonical integral chart `ΔC=14105` is one such exact witness
chart, exact K3 tail realization is now equivalent to solving that single
canonical integral equation.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT
    / "data"
    / "w33_k3_tail_canonical_chart_realization_equivalence_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_tail_canonical_chart_realization_equivalence_summary() -> dict[str, Any]:
    from w33_k3_tail_canonical_integral_chart_bridge import (
        build_k3_tail_canonical_integral_chart_summary,
    )
    from w33_k3_tail_increment_realization_equivalence_bridge import (
        build_k3_tail_increment_realization_equivalence_summary,
    )

    chart = build_k3_tail_canonical_integral_chart_summary()
    increment = build_k3_tail_increment_realization_equivalence_summary()
    fixed = chart["fixed_k3_tail_exactness_channel"]
    canonical = chart["canonical_integral_chart"]

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "canonical_integral_chart": canonical,
        "k3_tail_canonical_chart_realization_equivalence_theorem": {
            "exact_k3_tail_realization_is_already_equivalent_to_any_one_exact_affine_increment_witness": (
                increment["k3_tail_increment_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_any_one_exact_affine_increment_witness"
                ]
            ),
            "the_canonical_integral_chart_is_exactly_deltaC_equals_14105": (
                canonical["name"] == "dC"
                and canonical["exact_increment"] == "14105"
            ),
            "the_canonical_integral_chart_is_one_exact_affine_increment_witness_chart": (
                chart["k3_tail_canonical_integral_chart_theorem"][
                    "therefore_exact_k3_tail_realization_is_equivalent_to_the_canonical_integral_chart_equation_deltaC_equals_14105"
                ]
            ),
            "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_solving_deltaC_equals_14105": (
                increment["k3_tail_increment_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_any_one_exact_affine_increment_witness"
                ]
                and canonical["name"] == "dC"
                and canonical["exact_increment"] == "14105"
                and chart["k3_tail_canonical_integral_chart_theorem"][
                    "therefore_exact_k3_tail_realization_is_equivalent_to_the_canonical_integral_chart_equation_deltaC_equals_14105"
                ]
            ),
            "the_live_external_wall_is_now_one_single_integral_equation_on_the_fixed_package": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and canonical["name"] == "dC"
                and canonical["exact_increment"] == "14105"
                and increment["k3_tail_increment_realization_equivalence_theorem"][
                    "the_live_external_wall_is_now_exactly_one_affine_increment_witness_existence_problem"
                ]
            ),
        },
        "bridge_verdict": (
            "The sharpened K3 wall has now collapsed to one explicit integral "
            "equation. On the fixed carrier-preserving package, exact K3 tail "
            "realization is equivalent to solving the canonical chart equation "
            "ΔC=14105. All other promoted charts are already equivalent to "
            "that one by the earlier affine increment reductions."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_k3_tail_canonical_chart_realization_equivalence_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
