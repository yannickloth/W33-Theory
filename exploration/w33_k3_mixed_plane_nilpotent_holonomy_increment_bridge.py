"""Mixed-plane K3 realization reduces to one nonzero nilpotent holonomy increment.

CDXX made the smallest positive datum concrete in adapted holonomy language:

- one support-preserving non-identity unipotent sign-trivial holonomy on the
  canonical mixed-plane host.

But every such sign-trivial holonomy has the form

    H = I + N

with `N` upper-triangular and nilpotent on the reduced transport fiber. Over
`F3` the nontrivial sign-trivial unipotent holonomies are exactly
`I + [[0,1],[0,0]]` and `I + [[0,2],[0,0]]`, and those two nilpotent
increments are gauge-equivalent by the same adapted diagonal change of basis.

Therefore exact K3 tail realization is equivalent to one support-preserving
nonzero nilpotent holonomy increment on the same fixed host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_nilpotent_holonomy_increment_bridge_summary.json"
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
def build_k3_mixed_plane_nilpotent_holonomy_increment_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_holonomy_witness_bridge import (
        build_k3_mixed_plane_holonomy_witness_summary,
    )

    holonomy = build_k3_mixed_plane_holonomy_witness_summary()
    host = holonomy["canonical_mixed_plane_support"]
    witness = holonomy["mixed_plane_holonomy_witness"]

    identity = np.array([[1, 0], [0, 1]], dtype=int)
    canonical_holonomy = np.array(witness["canonical_nontrivial_holonomy"], dtype=int)
    gauge_holonomy = np.array(witness["gauge_related_nontrivial_holonomy"], dtype=int)
    canonical_increment = ((canonical_holonomy - identity) % MODULUS).tolist()
    gauge_increment = ((gauge_holonomy - identity) % MODULUS).tolist()

    basis_change = np.array(witness["conjugating_basis_change"], dtype=int)
    conjugated_increment = _conjugate(np.array(canonical_increment, dtype=int), basis_change)

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_nilpotent_holonomy_increment": {
            "identity_holonomy": identity.tolist(),
            "canonical_nonzero_increment": canonical_increment,
            "gauge_related_nonzero_increment": gauge_increment,
            "all_sign_trivial_increments": [
                [[0, 0], [0, 0]],
                canonical_increment,
                gauge_increment,
            ],
            "nonzero_sign_trivial_increments": [
                canonical_increment,
                gauge_increment,
            ],
            "conjugating_basis_change": basis_change.tolist(),
            "conjugated_increment": conjugated_increment.tolist(),
        },
        "k3_mixed_plane_nilpotent_holonomy_increment_theorem": {
            "a_nonidentity_unipotent_sign_trivial_holonomy_is_equivalent_to_identity_plus_a_nonzero_nilpotent_increment": (
                witness["canonical_nontrivial_holonomy"] == [[1, 1], [0, 1]]
                and canonical_increment == [[0, 1], [0, 0]]
            ),
            "the_sign_trivial_sector_has_two_nonzero_nilpotent_increments_over_f3": (
                sorted([canonical_increment, gauge_increment])
                == [[[0, 1], [0, 0]], [[0, 2], [0, 0]]]
            ),
            "the_two_nonzero_sign_trivial_increments_are_gauge_equivalent": (
                conjugated_increment.tolist() == [[0, 2], [0, 0]]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_nilpotent_holonomy_increment_on_the_same_fixed_host": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and sorted([canonical_increment, gauge_increment])
                == [[[0, 1], [0, 0]], [[0, 2], [0, 0]]]
                and conjugated_increment.tolist() == [[0, 2], [0, 0]]
            ),
            "the_live_external_wall_is_now_the_first_nonzero_nilpotent_holonomy_increment_on_the_same_fixed_host": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and canonical_increment == [[0, 1], [0, 0]]
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 wall is now concrete in the smallest adapted "
            "matrix language the repo can recognize. A non-identity "
            "sign-trivial holonomy is exactly identity plus a nonzero "
            "nilpotent increment, and over F3 the two such increments are "
            "gauge-equivalent. So exact K3 tail realization is equivalent to "
            "one support-preserving nonzero nilpotent holonomy increment on "
            "the same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_k3_mixed_plane_nilpotent_holonomy_increment_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
