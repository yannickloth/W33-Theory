"""Exact qutrit scaling of the residual continuum seed dependence.

CCCLXXXII isolated the remaining CP2/K3 seed dependence to the local `r^20`
tail channel and showed that the quadratic gap contracts at first refinement.
The next exact question is whether the matter-coupled residual is genuinely new
continuum data, or just the transport residual lifted through the already-fixed
81-dimensional logical qutrit packet.

This module promotes the exact answer:

1. the first-order local `r^20` seed gaps scale by exactly `81`;
2. the quadratic CP2/K3 seed gap and the sd^1 quadratic gap also scale by
   exactly `81`;
3. so the matter-coupled residual continuum ambiguity is not a new independent
   seed effect. It is the transport tail-channel ambiguity tensored by the
   exact logical-qutrit multiplicity.
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

from w33_continuum_seed_isolation_bridge import (  # noqa: E402
    build_continuum_seed_isolation_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_continuum_qutrit_scaling_bridge_summary.json"

QUTRIT_FACTOR = 81


def _fraction_from_gap(entry: dict[str, Any], key: str) -> Fraction:
    return Fraction(entry[key]["exact"])


def _fraction_payload(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_continuum_qutrit_scaling_bridge_summary() -> dict[str, Any]:
    seed = build_continuum_seed_isolation_bridge_summary()
    first_order = seed["first_order_seed_isolation"]
    quadratic = seed["quadratic_gap_contraction"]

    transport = first_order["transport"]
    matter = first_order["matter_coupled"]

    constant_r20_ratio = _fraction_from_gap(matter, "constant_corr20_gap") / _fraction_from_gap(
        transport, "constant_corr20_gap"
    )
    linear_r20_ratio = _fraction_from_gap(matter, "linear_corr20_gap") / _fraction_from_gap(
        transport, "linear_corr20_gap"
    )
    quadratic_seed_ratio = Fraction(quadratic["matter_seed_gap"]["exact"]) / Fraction(
        quadratic["transport_seed_gap"]["exact"]
    )
    quadratic_sd1_ratio = Fraction(quadratic["matter_sd1_gap"]["exact"]) / Fraction(
        quadratic["transport_sd1_gap"]["exact"]
    )

    return {
        "status": "ok",
        "residual_gap_scaling": {
            "logical_qutrit_factor": QUTRIT_FACTOR,
            "first_order_constant_r20_ratio": _fraction_payload(constant_r20_ratio),
            "first_order_linear_r20_ratio": _fraction_payload(linear_r20_ratio),
            "quadratic_seed_gap_ratio": _fraction_payload(quadratic_seed_ratio),
            "quadratic_sd1_gap_ratio": _fraction_payload(quadratic_sd1_ratio),
        },
        "continuum_qutrit_scaling_theorem": {
            "first_order_local_constant_seed_gap_scales_by_exactly_81": (
                constant_r20_ratio == QUTRIT_FACTOR
            ),
            "first_order_local_linear_seed_gap_scales_by_exactly_81": (
                linear_r20_ratio == QUTRIT_FACTOR
            ),
            "quadratic_seed_gap_scales_by_exactly_81": (
                quadratic_seed_ratio == QUTRIT_FACTOR
            ),
            "quadratic_sd1_gap_scales_by_exactly_81": (
                quadratic_sd1_ratio == QUTRIT_FACTOR
            ),
            "therefore_the_matter_coupled_residual_seed_dependence_is_transport_tail_dependence_tensored_with_the_exact_logical_qutrit_packet": (
                constant_r20_ratio == QUTRIT_FACTOR
                and linear_r20_ratio == QUTRIT_FACTOR
                and quadratic_seed_ratio == QUTRIT_FACTOR
                and quadratic_sd1_ratio == QUTRIT_FACTOR
            ),
        },
        "bridge_verdict": (
            "The residual continuum CP2/K3 ambiguity is now sharper again. The "
            "matter-coupled local r^20 seed gaps and the quadratic seed/sd^1 gaps "
            "are not independent continuum data: every one of them is exactly 81 "
            "times the corresponding transport gap. So the remaining family-sensitive "
            "continuum ambiguity is the transport tail-channel residual tensored by "
            "the exact logical-qutrit packet, not a separate new seed-scale effect."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_qutrit_scaling_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
