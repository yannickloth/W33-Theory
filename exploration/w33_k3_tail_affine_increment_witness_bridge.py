"""Affine single-increment witness criterion on the fixed K3 package.

CDII packaged the missing positive target exactly as one affine displacement
from the present zero witness point to the exact nonzero witness point on the
fixed carrier-preserving K3 package.

Because the current refined K3 point is exactly zero in all promoted witness
coordinates, the affine displacement coordinates are already the promoted
increments themselves. So the next exact reduction is:

- any one promoted affine increment
  `ΔC=14105`, `ΔL=143654`, `ΔQ_seed=3396050/3`, or `ΔQ_sd1=3904481/4`
  already recovers the same exact scale `217/12`;
- therefore any one such increment identifies the full affine witness target;
- so the remaining wall is existence of any one exact affine increment witness
  on the same fixed carrier-preserving K3 package.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_affine_increment_witness_bridge_summary.json"
)

AFFINE_INCREMENT_WITNESSES = {
    "dC": Fraction(14105, 1),
    "dL": Fraction(143654, 1),
    "dQ_seed": Fraction(3396050, 3),
    "dQ_sd1": Fraction(3904481, 4),
}
PRIMITIVE_INCREMENT_GENERATOR = {
    "dC": 780,
    "dL": 7944,
    "dQ_seed": 62600,
    "dQ_sd1": 53979,
}


@lru_cache(maxsize=1)
def build_k3_tail_affine_increment_witness_summary() -> dict[str, Any]:
    from w33_k3_tail_affine_witness_target_bridge import (
        build_k3_tail_affine_witness_target_summary,
    )

    base = build_k3_tail_affine_witness_target_summary()
    fixed = base["fixed_k3_tail_exactness_channel"]

    recovered_scales = {
        name: str(AFFINE_INCREMENT_WITNESSES[name] / PRIMITIVE_INCREMENT_GENERATOR[name])
        for name in AFFINE_INCREMENT_WITNESSES
    }

    increment_equalities = {
        name: {
            "primitive_increment": str(PRIMITIVE_INCREMENT_GENERATOR[name]),
            "exact_increment": str(AFFINE_INCREMENT_WITNESSES[name]),
            "recovered_scale": recovered_scales[name],
        }
        for name in AFFINE_INCREMENT_WITNESSES
    }

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "affine_increment_witnesses": increment_equalities,
        "k3_tail_affine_increment_witness_theorem": {
            "the_current_refined_k3_point_is_zero_so_affine_increments_equal_the_exact_witness_coordinates": (
                base["current_zero_witness_point"]
                == {"C": "0", "L": "0", "Q_seed": "0", "Q_sd1": "0"}
                and base["affine_witness_displacement"] == base["exact_witness_point"]
            ),
            "each_promoted_affine_increment_recovers_the_same_exact_scale_217_over_12": (
                all(scale == "217/12" for scale in recovered_scales.values())
            ),
            "therefore_any_one_promoted_affine_increment_identifies_the_full_affine_witness_target": (
                base["k3_tail_affine_witness_target_theorem"][
                    "that_affine_displacement_lies_on_the_fixed_tail_line_with_common_scale_217_over_12"
                ]
                and all(scale == "217/12" for scale in recovered_scales.values())
            ),
            "therefore_the_live_external_wall_is_existence_of_any_one_exact_affine_increment_witness_on_the_same_fixed_package": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and all(scale == "217/12" for scale in recovered_scales.values())
                and base["k3_tail_affine_witness_target_theorem"][
                    "therefore_the_live_external_wall_is_one_exact_affine_witness_target_on_the_same_fixed_package"
                ]
            ),
        },
        "bridge_verdict": (
            "The affine K3 wall has now reduced to one increment witness. "
            "Because the current refined K3 point is zero in every promoted "
            "coordinate, the affine displacement coordinates are already the "
            "exact increments ΔC=14105, ΔL=143654, ΔQ_seed=3396050/3, and "
            "ΔQ_sd1=3904481/4. Any one of those recovers the same exact scale "
            "217/12 and therefore identifies the full affine target. So the "
            "remaining external wall is existence of any one exact affine "
            "increment witness on the same fixed carrier-preserving K3 package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_tail_affine_increment_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
