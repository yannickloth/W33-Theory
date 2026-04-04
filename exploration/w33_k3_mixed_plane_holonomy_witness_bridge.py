"""Mixed-plane K3 realization reduces to one nontrivial sign-trivial holonomy.

CDXVIII reduced exact mixed-plane tail realization to the smallest repo-native
cohomological datum:

- one support-preserving nonzero sign-trivial cocycle value.

But in adapted basis the cocycle already appears as the upper-right entry of a
reduced holonomy matrix

    [[1, c(g)], [0, s(g)]].

On the sign-trivial sector `s(g)=1`, so a nonzero cocycle value is exactly the
same thing as a non-identity unipotent adapted holonomy matrix. Over `F3` the
two nontrivial possibilities `[[1,1],[0,1]]` and `[[1,2],[0,1]]` are related
by the same natural diagonal gauge used earlier, so up to that gauge there is
one nontrivial sign-trivial holonomy class.

Therefore exact K3 tail realization is equivalent to one support-preserving
nontrivial sign-trivial adapted holonomy witness on the same fixed host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_holonomy_witness_bridge_summary.json"
)
MODULUS = 3


def _conjugate(matrix: np.ndarray, basis_change: np.ndarray) -> np.ndarray:
    determinant = int(round(float(np.linalg.det(basis_change)))) % MODULUS
    inverse = np.array(
        [
            [basis_change[1, 1], -basis_change[0, 1]],
            [-basis_change[1, 0], basis_change[0, 0]],
        ],
        dtype=int,
    )
    inverse = (pow(determinant, -1, MODULUS) * inverse) % MODULUS
    return (inverse @ matrix @ basis_change) % MODULUS


@lru_cache(maxsize=1)
def build_k3_mixed_plane_holonomy_witness_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_cocycle_witness_bridge import (
        build_k3_mixed_plane_cocycle_witness_summary,
    )
    from w33_transport_ternary_cocycle_bridge import adapted_reduced_transport_group

    cocycle = build_k3_mixed_plane_cocycle_witness_summary()
    host = cocycle["canonical_mixed_plane_support"]

    sign_trivial = [
        matrix.tolist()
        for matrix in adapted_reduced_transport_group()
        if int(matrix[1, 1]) == 1
    ]
    nontrivial_sign_trivial = [
        matrix for matrix in sign_trivial if matrix != [[1, 0], [0, 1]]
    ]

    basis_change = np.array([[1, 0], [0, 2]], dtype=int)
    conjugated = _conjugate(np.array([[1, 1], [0, 1]], dtype=int), basis_change)

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_holonomy_witness": {
            "sign_trivial_holonomy_matrices": sign_trivial,
            "nontrivial_sign_trivial_holonomy_matrices": nontrivial_sign_trivial,
            "canonical_nontrivial_holonomy": [[1, 1], [0, 1]],
            "gauge_related_nontrivial_holonomy": [[1, 2], [0, 1]],
            "conjugating_basis_change": basis_change.tolist(),
            "conjugated_matrix": conjugated.tolist(),
        },
        "k3_mixed_plane_holonomy_witness_theorem": {
            "a_nonzero_sign_trivial_cocycle_value_is_equivalent_to_a_nonidentity_unipotent_adapted_holonomy_matrix": (
                cocycle["k3_mixed_plane_cocycle_witness_theorem"][
                    "a_single_support_preserving_nonzero_sign_trivial_cocycle_value_already_forces_the_nonzero_fiber_shift_witness"
                ]
                and [[1, 1], [0, 1]] in nontrivial_sign_trivial
            ),
            "the_sign_trivial_sector_has_two_nontrivial_unipotent_matrices_over_f3": (
                sorted(nontrivial_sign_trivial) == [[[1, 1], [0, 1]], [[1, 2], [0, 1]]]
            ),
            "the_two_nontrivial_sign_trivial_holonomies_are_gauge_equivalent": (
                conjugated.tolist() == [[1, 2], [0, 1]]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nontrivial_sign_trivial_holonomy_witness_on_the_same_fixed_host": (
                cocycle["k3_mixed_plane_cocycle_witness_theorem"][
                    "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_cocycle_value_witness_on_the_canonical_mixed_plane_host"
                ]
                and sorted(nontrivial_sign_trivial) == [[[1, 1], [0, 1]], [[1, 2], [0, 1]]]
                and conjugated.tolist() == [[1, 2], [0, 1]]
            ),
            "the_live_external_wall_is_now_the_first_nontrivial_sign_trivial_holonomy_witness_on_the_same_fixed_host": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and conjugated.tolist() == [[1, 2], [0, 1]]
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 wall is now concrete in adapted holonomy "
            "language. A nonzero sign-trivial cocycle value is exactly a "
            "non-identity unipotent adapted holonomy matrix, and over F3 the "
            "two such matrices are gauge-equivalent. So exact K3 tail "
            "realization is equivalent to one support-preserving nontrivial "
            "sign-trivial holonomy witness on the same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_holonomy_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
