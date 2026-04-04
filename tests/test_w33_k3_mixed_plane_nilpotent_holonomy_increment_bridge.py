from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_nilpotent_holonomy_increment_bridge import (
    build_k3_mixed_plane_nilpotent_holonomy_increment_summary,
)


def test_mixed_plane_nilpotent_holonomy_increment_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_nilpotent_holonomy_increment_summary()
    witness = summary["mixed_plane_nilpotent_holonomy_increment"]

    assert witness["identity_holonomy"] == [[1, 0], [0, 1]]
    assert witness["canonical_nonzero_increment"] == [[0, 1], [0, 0]]
    assert witness["gauge_related_nonzero_increment"] == [[0, 2], [0, 0]]
    assert sorted(witness["nonzero_sign_trivial_increments"]) == [
        [[0, 1], [0, 0]],
        [[0, 2], [0, 0]],
    ]


def test_mixed_plane_nilpotent_holonomy_increment_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_nilpotent_holonomy_increment_summary()[
        "k3_mixed_plane_nilpotent_holonomy_increment_theorem"
    ]
    assert all(theorem.values())
