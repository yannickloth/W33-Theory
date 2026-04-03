"""Exact isolation of seed dependence in the transport continuum bridge.

After CCCLXXXI, the remaining continuum wall is already localized to the
curvature-sensitive tail channel on a fixed avatar package. The next exact
question is how much genuine seed dependence is still left on the curved 4D
side once the promoted coefficients are locked.

This module packages the strongest exact statement already justified by the
repo's promoted transport/refinement bridge:

1. at first order, the CP2/K3 transport bridge already shares the same
   universal limit term and the same `r^120` topological correction;
2. all first-order seed dependence is isolated to the `r^20` local correction;
3. at second order, the remaining CP2/K3 quadratic gap contracts at `sd^1`
   for both the transport and matter-coupled packages.

So the continuum wall is now sharper than "some external realization issue".
The universal and topological sectors are already locked, and the residual
seed dependence sits in the contracting local correction channel.
"""

from __future__ import annotations

from fractions import Fraction
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

from w33_transport_curved_dirac_quadratic_bridge import (  # noqa: E402
    build_transport_curved_dirac_quadratic_bridge_summary,
)
from w33_transport_curved_dirac_refinement_bridge import (  # noqa: E402
    build_transport_curved_dirac_refinement_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_continuum_seed_isolation_bridge_summary.json"


def _as_fraction(entry: dict[str, Any], key: str) -> Fraction:
    return Fraction(entry[key]["exact"])


def _fraction_payload(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_continuum_seed_isolation_bridge_summary() -> dict[str, Any]:
    refinement = build_transport_curved_dirac_refinement_summary()
    quadratic = build_transport_curved_dirac_quadratic_bridge_summary()

    first_order = {}
    for family in ("transport", "matter_coupled"):
        cp2, k3 = refinement["curved_refinement_first_order_bridge"][family]
        constant_limit_gap = abs(
            _as_fraction(cp2["constant_term_formula"], "limit")
            - _as_fraction(k3["constant_term_formula"], "limit")
        )
        constant_corr20_gap = abs(
            _as_fraction(cp2["constant_term_formula"], "corr_20_power_r")
            - _as_fraction(k3["constant_term_formula"], "corr_20_power_r")
        )
        constant_corr120_gap = abs(
            _as_fraction(cp2["constant_term_formula"], "corr_120_power_r")
            - _as_fraction(k3["constant_term_formula"], "corr_120_power_r")
        )

        linear_limit_gap = abs(
            _as_fraction(cp2["linear_term_formula"], "limit")
            - _as_fraction(k3["linear_term_formula"], "limit")
        )
        linear_corr20_gap = abs(
            _as_fraction(cp2["linear_term_formula"], "corr_20_power_r")
            - _as_fraction(k3["linear_term_formula"], "corr_20_power_r")
        )
        linear_corr120_gap = abs(
            _as_fraction(cp2["linear_term_formula"], "corr_120_power_r")
            - _as_fraction(k3["linear_term_formula"], "corr_120_power_r")
        )

        first_order[family] = {
            "constant_limit_gap": _fraction_payload(constant_limit_gap),
            "constant_corr20_gap": _fraction_payload(constant_corr20_gap),
            "constant_corr120_gap": _fraction_payload(constant_corr120_gap),
            "linear_limit_gap": _fraction_payload(linear_limit_gap),
            "linear_corr20_gap": _fraction_payload(linear_corr20_gap),
            "linear_corr120_gap": _fraction_payload(linear_corr120_gap),
            "seed_dependence_is_only_in_r20_channel": (
                constant_limit_gap == 0
                and constant_corr120_gap == 0
                and linear_limit_gap == 0
                and linear_corr120_gap == 0
                and constant_corr20_gap > 0
                and linear_corr20_gap > 0
            ),
        }

    q_gap = quadratic["quadratic_gap_theorem"]

    return {
        "status": "ok",
        "first_order_seed_isolation": first_order,
        "quadratic_gap_contraction": q_gap,
        "continuum_seed_isolation_theorem": {
            "transport_first_order_limit_and_topological_corrections_are_seed_universal": (
                first_order["transport"]["constant_limit_gap"]["exact"] == "0"
                and first_order["transport"]["constant_corr120_gap"]["exact"] == "0"
                and first_order["transport"]["linear_limit_gap"]["exact"] == "0"
                and first_order["transport"]["linear_corr120_gap"]["exact"] == "0"
            ),
            "matter_first_order_limit_and_topological_corrections_are_seed_universal": (
                first_order["matter_coupled"]["constant_limit_gap"]["exact"] == "0"
                and first_order["matter_coupled"]["constant_corr120_gap"]["exact"] == "0"
                and first_order["matter_coupled"]["linear_limit_gap"]["exact"] == "0"
                and first_order["matter_coupled"]["linear_corr120_gap"]["exact"] == "0"
            ),
            "all_first_order_seed_dependence_is_isolated_to_the_r20_local_channel": (
                first_order["transport"]["seed_dependence_is_only_in_r20_channel"]
                and first_order["matter_coupled"]["seed_dependence_is_only_in_r20_channel"]
            ),
            "transport_quadratic_gap_contracts_at_first_refinement": bool(
                q_gap["transport_first_refinement_contracts_gap"]
            ),
            "matter_quadratic_gap_contracts_at_first_refinement": bool(
                q_gap["matter_first_refinement_contracts_gap"]
            ),
            "therefore_the_remaining_continuum_seed_dependence_is_a_contracting_local_tail_channel_effect": (
                first_order["transport"]["seed_dependence_is_only_in_r20_channel"]
                and first_order["matter_coupled"]["seed_dependence_is_only_in_r20_channel"]
                and q_gap["transport_first_refinement_contracts_gap"]
                and q_gap["matter_first_refinement_contracts_gap"]
            ),
        },
        "bridge_verdict": (
            "The continuum bridge is now sharper than a generic CP2/K3 ambiguity. "
            "At first order, both the transport and matter-coupled bridges already "
            "share the same universal limit term and the same r^120 topological "
            "correction on CP2 and K3; all seed dependence is isolated to the r^20 "
            "local correction channel. At second order, the remaining CP2/K3 "
            "quadratic gap contracts at sd^1 for both packages. So the residual "
            "continuum wall is a contracting local tail-channel realization effect, "
            "not a free coefficient or topological-sector ambiguity."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_seed_isolation_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
