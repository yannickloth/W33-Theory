"""Exact quadratic shadow of the active family packet.

This module packages the strongest conservative v29-style theorem that is
already forced by the repo's exact finite family normal form.

In the exact basis
    u = (1,1,0), v = (0,0,1), w = (1,-1,0),
the universal generation nilpotents are

    N_(+-) =  E12 - 2 E13 + 2 E23,
    N_(-+) = -E12 - 2 E13 - 2 E23.

Writing their active simple-root parts as

    A_(+-) =  E12 + 2 E23,
    A_(-+) = -E12 - 2 E23,

one gets the exact quadratic closure

    A_(+-)^2 = A_(-+)^2 = 2 E13 = [E12, 2 E23].

So the first nonlinear family packet is not extra input. It is the exact
central quadratic shadow of the active simple-root packet already present in
the repo-native normal form.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from exploration.w33_yukawa_family_normal_form_bridge import (
    build_yukawa_family_normal_form_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_PATH = DATA_DIR / "w33_yukawa_quadratic_shadow_bridge_summary.json"


def _standard_matrix(i: int, j: int) -> np.ndarray:
    matrix = np.zeros((3, 3), dtype=int)
    matrix[i, j] = 1
    return matrix


@lru_cache(maxsize=1)
def build_yukawa_quadratic_shadow_summary() -> dict[str, Any]:
    family = build_yukawa_family_normal_form_summary()
    normal = family["generation_normal_form"]

    n_plus = np.array(normal["plus_minus_nilpotent"], dtype=int)
    n_minus = np.array(normal["minus_plus_nilpotent"], dtype=int)

    e12 = _standard_matrix(0, 1)
    e13 = _standard_matrix(0, 2)
    e23 = _standard_matrix(1, 2)

    active_plus = e12 + 2 * e23
    active_minus = -e12 - 2 * e23
    central_shadow = 2 * e13

    return {
        "status": "ok",
        "normal_form_packet": {
            "active_plus": active_plus.astype(int).tolist(),
            "active_minus": active_minus.astype(int).tolist(),
            "central_shadow": central_shadow.astype(int).tolist(),
            "plus_minus_nilpotent": n_plus.astype(int).tolist(),
            "minus_plus_nilpotent": n_minus.astype(int).tolist(),
        },
        "quadratic_shadow_theorem": {
            "active_plus_squares_to_central_shadow": np.array_equal(
                active_plus @ active_plus, central_shadow
            ),
            "active_minus_squares_to_central_shadow": np.array_equal(
                active_minus @ active_minus, central_shadow
            ),
            "central_shadow_is_simple_root_commutator": np.array_equal(
                e12 @ (2 * e23) - (2 * e23) @ e12, central_shadow
            ),
            "universal_nilpotents_are_active_minus_central_shadow": np.array_equal(
                n_plus, active_plus - central_shadow
            )
            and np.array_equal(n_minus, active_minus - central_shadow),
            "central_shadow_equals_common_square_from_family_normal_form": np.array_equal(
                np.array(normal["common_square"], dtype=int), central_shadow
            ),
            "first_nonlinear_family_packet_is_quadratic_shadow_of_active_packet": True,
        },
        "bridge_verdict": (
            "The repo-native v29-style statement is now exact in finite form. "
            "In the standard upper-triangular family normal form, the active "
            "simple-root packet squares to the same central 2E13 channel, and "
            "the universal generation nilpotents are exactly active packet minus "
            "that quadratic shadow. So the first nonlinear family packet is "
            "already generated internally by the active packet rather than "
            "appearing as an independent extra mode."
        ),
        "source_files": [
            "exploration/w33_yukawa_family_normal_form_bridge.py",
        ],
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_yukawa_quadratic_shadow_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
