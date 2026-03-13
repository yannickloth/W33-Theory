"""q=3 selection from the internal spectral-action and Higgs ratios.

The recent cyclotomic bridge proved that for the full finite W33 package

    a2 / a0         = 2 Phi_6(q) / q,
    a4 / a0         = 2 (4 Phi_3(q) + q) / q,
    m_H^2 / v^2     = 2 Phi_6(q) / (4 Phi_3(q) + q),
    c_6 / a0        = 2 Phi_3(q),

with exact q=3 values

    a2 / a0     = 14/3,
    a4 / a0     = 110/3,
    m_H^2 / v^2 = 14/55,
    c_6 / a0    = 26.

This module proves the converse: these exact internal spectral-action quantities
already select q = 3 uniquely.

The striking part is that the three internal matter/Higgs equations all collapse
to the same quadratic:

    2 Phi_6(q) / q = 14/3
    2 (4 Phi_3(q) + q) / q = 110/3
    2 Phi_6(q) / (4 Phi_3(q) + q) = 14/55

all <=> 3 q^2 - 10 q + 3 = 0 = (q - 3)(3q - 1).

The curved 6-mode normalization gives a second exact selector:

    2 Phi_3(q) = 26
    <=> q^2 + q - 12 = 0
    <=> (q - 3)(q + 4) = 0.

So the matter/Higgs side and the gravity side now select the same q = 3.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_spectral_action_q3_selection_bridge_summary.json"


def phi3(q: int) -> int:
    return q * q + q + 1


def phi6(q: int) -> int:
    return q * q - q + 1


def internal_selection_polynomial(q: int) -> int:
    return 3 * q * q - 10 * q + 3


def gravity_normalization_polynomial(q: int) -> int:
    return q * q + q - 12


@lru_cache(maxsize=1)
def build_spectral_action_q3_selection_summary() -> dict[str, Any]:
    samples = []
    for q in (1, 2, 3, 4, 5, 7, 11):
        samples.append(
            {
                "q": q,
                "phi3": phi3(q),
                "phi6": phi6(q),
                "internal_polynomial": internal_selection_polynomial(q),
                "gravity_polynomial": gravity_normalization_polynomial(q),
                "internal_condition_holds": internal_selection_polynomial(q) == 0,
                "gravity_condition_holds": gravity_normalization_polynomial(q) == 0,
            }
        )

    return {
        "status": "ok",
        "selection_equations": {
            "internal_a2_ratio": {
                "equation": "2 Phi_6(q) / q = 14/3",
                "polynomial": "3q^2 - 10q + 3",
                "factorization": "(q - 3)(3q - 1)",
                "unique_positive_integer_solution": 3,
            },
            "internal_a4_ratio": {
                "equation": "2 (4 Phi_3(q) + q) / q = 110/3",
                "polynomial": "3q^2 - 10q + 3",
                "factorization": "(q - 3)(3q - 1)",
                "unique_positive_integer_solution": 3,
            },
            "higgs_ratio": {
                "equation": "2 Phi_6(q) / (4 Phi_3(q) + q) = 14/55",
                "polynomial": "3q^2 - 10q + 3",
                "factorization": "(q - 3)(3q - 1)",
                "unique_positive_integer_solution": 3,
            },
            "gravity_normalization": {
                "equation": "2 Phi_3(q) = 26",
                "polynomial": "q^2 + q - 12",
                "factorization": "(q - 3)(q + 4)",
                "unique_positive_integer_solution": 3,
            },
        },
        "sample_checks": samples,
        "bridge_verdict": (
            "The internal spectral-action side now selects q = 3 on its own. "
            "The exact ratios a2/a0 = 14/3, a4/a0 = 110/3, and m_H^2/v^2 = 14/55 "
            "all collapse to the same polynomial 3q^2 - 10q + 3, whose unique "
            "positive integer solution is q = 3. The curved gravity normalization "
            "c6/a0 = 26 gives the companion selector q^2 + q - 12, again with "
            "unique positive integer solution q = 3. So the matter/Higgs and "
            "gravity sectors are now independently and compatibly q = 3."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_spectral_action_q3_selection_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
