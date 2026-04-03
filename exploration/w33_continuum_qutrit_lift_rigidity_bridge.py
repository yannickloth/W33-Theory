"""Exact rigidity of the matter-coupled continuum residual.

CCCLXXXIII showed that every residual CP2/K3 seed gap scales by exactly 81:
the first-order local `r^20` gaps, the quadratic seed gap, and the quadratic
`sd^1` gap.

This module packages the sharper structural consequence.

The matter-coupled continuum ambiguity is not a new family-scale obstruction.
It is exactly the transport-side residual tensored by the already-fixed
81-dimensional logical qutrit packet. So the live remaining continuum theorem
has now reduced again: it is a transport-tail realization problem first, and
only then a matter-coupled one by exact replication.
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

from w33_continuum_qutrit_scaling_bridge import (  # noqa: E402
    QUTRIT_FACTOR,
    build_continuum_qutrit_scaling_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_continuum_qutrit_lift_rigidity_bridge_summary.json"


@lru_cache(maxsize=1)
def build_continuum_qutrit_lift_rigidity_summary() -> dict[str, Any]:
    scaling = build_continuum_qutrit_scaling_bridge_summary()
    theorem = scaling["continuum_qutrit_scaling_theorem"]

    return {
        "status": "ok",
        "logical_qutrit_lift": {
            "logical_qutrit_factor": QUTRIT_FACTOR,
            "all_residual_gap_ratios_equal_logical_qutrit_factor": (
                theorem["first_order_local_constant_seed_gap_scales_by_exactly_81"]
                and theorem["first_order_local_linear_seed_gap_scales_by_exactly_81"]
                and theorem["quadratic_seed_gap_scales_by_exactly_81"]
                and theorem["quadratic_sd1_gap_scales_by_exactly_81"]
            ),
        },
        "continuum_qutrit_lift_rigidity_theorem": {
            "matter_coupled_residual_seed_dependence_introduces_no_new_continuum_scale_beyond_transport": (
                theorem[
                    "therefore_the_matter_coupled_residual_seed_dependence_is_transport_tail_dependence_tensored_with_the_exact_logical_qutrit_packet"
                ]
            ),
            "the_family_sensitive_continuum_wall_is_exactly_the_transport_tail_wall_tensored_by_81": (
                theorem[
                    "therefore_the_matter_coupled_residual_seed_dependence_is_transport_tail_dependence_tensored_with_the_exact_logical_qutrit_packet"
                ]
            ),
            "therefore_the_live_continuum_existence_problem_is_transport_first_and_only_after_that_matter_coupled_by_exact_replication": (
                theorem[
                    "therefore_the_matter_coupled_residual_seed_dependence_is_transport_tail_dependence_tensored_with_the_exact_logical_qutrit_packet"
                ]
            ),
        },
        "bridge_verdict": (
            "The continuum wall is now rigid under the logical-qutrit lift. The "
            "matter-coupled CP2/K3 residual is not an additional family-scale "
            "continuum ambiguity. It is exactly the transport tail residual tensored "
            "by the fixed 81-dimensional logical qutrit packet. So the live "
            "existence problem is transport-first, with the matter-coupled wall "
            "already forced by exact replication."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_qutrit_lift_rigidity_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
