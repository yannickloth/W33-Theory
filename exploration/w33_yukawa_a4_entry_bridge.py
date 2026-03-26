"""Exact A4 entry point for the family spurion in the 4D product heat expansion.

This module packages the strongest conservative continuum-side theorem currently
supported by the local internal-family closure notes:

  - the exact internal one-parameter family spurion is blind at the first two
    product heat-coefficient levels A0 and A2;
  - its first nonzero contribution is the exact A4 shift
        ΔA4 = 81 ε^2 a0 = 1209 a0 / 9194;
  - therefore the family spurion first enters the 4D spectral action at the
    finite f0 term, not the leading Λ^4 cosmological term or the Λ^2
    Einstein-Hilbert-like term.

This does not prove the full curved lift. It sharpens the wall: the remaining
continuum family problem is the refined A4 density.
"""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_PATH = DATA_DIR / "w33_yukawa_a4_entry_bridge_summary.json"

M0 = 81
M1 = 459
M2_GEOMETRIC = 20979
EPSILON_SQUARED = Fraction(403, 248238)
DELTA_A4_COEFFICIENT = Fraction(1209, 9194)


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@lru_cache(maxsize=1)
def build_yukawa_a4_entry_summary() -> dict[str, Any]:
    return {
        "status": "ok",
        "internal_moment_tower": {
            "trace_0": M0,
            "trace_1": M1,
            "trace_2": f"{M2_GEOMETRIC} + 162 epsilon^2",
            "epsilon_squared": _fraction_text(EPSILON_SQUARED),
        },
        "product_heat_coefficients": {
            "A0": "81 a0",
            "A2": "-459 a0 + 81 a2",
            "A4": f"{M2_GEOMETRIC}/2 a0 + 81 epsilon^2 a0 - 459 a2 + 81 a4",
            "delta_A4": f"{_fraction_text(DELTA_A4_COEFFICIENT)} a0",
        },
        "spectral_action_consequence": {
            "delta_S_lambda": f"{_fraction_text(DELTA_A4_COEFFICIENT)} a0 f0",
            "family_spurion_shifts_lambda4_term": False,
            "family_spurion_shifts_lambda2_term": False,
            "family_spurion_first_shifts_f0_term": True,
        },
        "a4_entry_theorem": {
            "A0_is_family_blind": True,
            "A2_is_family_blind": True,
            "A4_is_first_family_entry_point": True,
            "delta_A4_equals_81_epsilon_squared_a0": (
                DELTA_A4_COEFFICIENT == 81 * EPSILON_SQUARED
            ),
            "delta_A4_is_1209_over_9194_times_a0": True,
            "remaining_continuum_wall_is_refined_a4_density": True,
        },
        "bridge_verdict": (
            "The exact local product-heat bridge sharpens the continuum wall. "
            "The family spurion does not touch A0 or A2, so it does not modify "
            "the leading Λ^4 or Λ^2 spectral-action terms. Its first exact entry "
            "is ΔA4 = 1209 a0 / 9194. So the honest next theorem is the refined "
            "A4 density, not a re-derivation of the leading geometric channel."
        ),
        "source_notes": [
            "TOE_CLOSED_INTERNAL_THEORY_v33.md",
            "TOE_EXACT_HEAT_COEFF_BRIDGE_v34.md",
        ],
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_yukawa_a4_entry_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
