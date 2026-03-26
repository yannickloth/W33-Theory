"""Exact external exceptional quanta from the promoted residue dictionary.

This module packages the next conservative bridge step after the local A4
normalization theorem.

The promoted local/external data already on the live surface are:
  - internal exceptional ranks: (40, 6, 8)
  - continuum Einstein-Hilbert coefficient: c_EH = 320 = 40 * 8
  - curved 6-mode coefficient: c_6 = 12480 = 40 * 6 * 52
  - topological coefficient: a2 = 2240 = 40 * 56
  - curved Weinberg lock: 9 c_EH / c_6 = 3 / 13

So the external exceptional quanta are not floating:
  - Q_curv = c_6 / (40 * 6) = 52
  - Q_top  = a2 / 40 = 56

This does not yet count which primitive branches of the actual refinement
tower are activated. It fixes the external quanta that any such global counting
theorem must reproduce.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_PATH = DATA_DIR / "w33_external_exceptional_quanta_bridge_summary.json"

E6_RANK = 40
A2_RANK = 6
CARTAN_RANK = 8
CONTINUUM_EH = 320
CURVED_SIX_MODE = 12480
TOPOLOGICAL_A2 = 2240
WEINBERG_LOCK = Fraction(3, 13)
TOPOLOGICAL_TO_EH_RATIO = Fraction(7, 1)


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@lru_cache(maxsize=1)
def build_external_exceptional_quanta_summary() -> dict[str, Any]:
    q_curv = Fraction(CURVED_SIX_MODE, E6_RANK * A2_RANK)
    q_top = Fraction(TOPOLOGICAL_A2, E6_RANK)
    derived_weinberg = Fraction(9 * CONTINUUM_EH, CURVED_SIX_MODE)
    derived_top_ratio = Fraction(TOPOLOGICAL_A2, CONTINUUM_EH)

    return {
        "status": "ok",
        "promoted_residue_data": {
            "internal_exceptional_ranks": [E6_RANK, A2_RANK, CARTAN_RANK],
            "continuum_eh_coefficient": CONTINUUM_EH,
            "curved_six_mode_coefficient": CURVED_SIX_MODE,
            "topological_coefficient": TOPOLOGICAL_A2,
            "curved_weinberg_lock": _fraction_text(WEINBERG_LOCK),
            "topological_to_eh_ratio": _fraction_text(TOPOLOGICAL_TO_EH_RATIO),
        },
        "external_quanta": {
            "Q_curv": _fraction_text(q_curv),
            "Q_top": _fraction_text(q_top),
        },
        "external_quantum_theorem": {
            "continuum_eh_equals_40_times_8": CONTINUUM_EH == E6_RANK * CARTAN_RANK,
            "curved_six_mode_equals_40_times_6_times_Q_curv": (
                CURVED_SIX_MODE == E6_RANK * A2_RANK * q_curv
            ),
            "topological_coefficient_equals_40_times_Q_top": (
                TOPOLOGICAL_A2 == E6_RANK * q_top
            ),
            "weinberg_lock_reconstructs_Q_curv": derived_weinberg == WEINBERG_LOCK,
            "topological_ratio_reconstructs_Q_top": (
                derived_top_ratio == TOPOLOGICAL_TO_EH_RATIO
            ),
            "external_exceptional_quanta_are_fixed_as_52_and_56": (
                q_curv == 52 and q_top == 56
            ),
            "global_branch_activation_count_remains_open": True,
        },
        "bridge_verdict": (
            "The promoted residue dictionary already fixes the external "
            "exceptional quanta. Once c_EH = 40*8, c_6 = 12480, a2 = 2240, "
            "and 9 c_EH / c_6 = 3/13 are taken as exact, the external bridge "
            "quanta are forced to Q_curv = 52 and Q_top = 56. So the open "
            "global problem is no longer local normalization of those quanta. "
            "It is which primitive external branches are actually activated, "
            "with what sign and multiplicity, on the refined tower."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_external_exceptional_quanta_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
