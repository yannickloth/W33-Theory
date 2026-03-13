"""q=3 selection from the curved gravity/topology compression laws.

The recent bridges gave exact q=3 identities:

1. internal spectral ratio:
       a2 / a0 = 2 Phi_6(q) / q

2. curved 6-mode compression:
       12 a0 + 3 a2 = 2 Phi_3(q) a0

3. curved 1-mode / topology compression:
       a2 = (q + 1) Phi_6(q) |chi|,   with a0 = 6 |chi|.

For q = 3 all three hold exactly. This module proves the converse:
these curved compression laws select q = 3 uniquely among positive integers.

The gravity compression condition gives

    12 + 6 Phi_6(q) / q = 2 Phi_3(q)
    <=> q^3 - 2q^2 - 2q - 3 = 0
    <=> (q - 3)(q^2 + q + 1) = 0.

The topology compression condition gives

    12 / q = q + 1
    <=> q^2 + q - 12 = 0
    <=> (q - 3)(q + 4) = 0.

Both therefore have the unique positive integer solution q = 3.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_q3_curved_selection_bridge_summary.json"


def phi3(q: int) -> int:
    return q * q + q + 1


def phi6(q: int) -> int:
    return q * q - q + 1


def gravity_selection_polynomial(q: int) -> int:
    return q**3 - 2 * q**2 - 2 * q - 3


def topology_selection_polynomial(q: int) -> int:
    return q**2 + q - 12


@lru_cache(maxsize=1)
def build_q3_curved_selection_summary() -> dict[str, Any]:
    samples = []
    for q in (1, 2, 3, 4, 5, 7, 11):
        samples.append(
            {
                "q": q,
                "phi3": phi3(q),
                "phi6": phi6(q),
                "gravity_polynomial": gravity_selection_polynomial(q),
                "topology_polynomial": topology_selection_polynomial(q),
                "gravity_condition_holds": gravity_selection_polynomial(q) == 0,
                "topology_condition_holds": topology_selection_polynomial(q) == 0,
            }
        )

    return {
        "status": "ok",
        "curved_selection_equations": {
            "gravity_compression": {
                "equation": "12 + 6 Phi_6(q) / q = 2 Phi_3(q)",
                "polynomial": "q^3 - 2q^2 - 2q - 3",
                "factorization": "(q - 3)(q^2 + q + 1)",
                "unique_positive_integer_solution": 3,
            },
            "topology_compression": {
                "equation": "12 / q = q + 1",
                "polynomial": "q^2 + q - 12",
                "factorization": "(q - 3)(q + 4)",
                "unique_positive_integer_solution": 3,
            },
        },
        "sample_checks": samples,
        "bridge_verdict": (
            "The curved first-order bridge now supplies new q=3 selection "
            "principles. Demanding that the internal spectral ratio a2/a0 = "
            "2Phi_6(q)/q compress the barycentric 6-mode exactly to "
            "2Phi_3(q)a0 forces q = 3 uniquely. Demanding that the same ratio and "
            "the exact a0 = 6|chi| identity compress the 1-mode exactly to "
            "(q+1)Phi_6(q)|chi| also forces q = 3 uniquely. So the curved "
            "gravity/topology bridge is not merely compatible with q = 3; it "
            "selects q = 3."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_q3_curved_selection_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
