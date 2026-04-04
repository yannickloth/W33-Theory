from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_inert_fan_geometry_bridge import (
    build_k3_mixed_plane_inert_fan_geometry_summary,
)


def test_mixed_plane_inert_fan_geometry_has_expected_structure() -> None:
    summary = build_k3_mixed_plane_inert_fan_geometry_summary()
    geometry = summary["mixed_plane_inert_fan_geometry"]

    assert geometry["anchor_point"] == 0
    assert geometry["anchor_lines"] == [0, 1, 2]
    assert geometry["active_spokes"] == [15, 16, 17]
    assert geometry["inactive_union"] == [36, 37, 38, 39, 40, 41, 42, 43, 44]


def test_mixed_plane_inert_fan_geometry_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_inert_fan_geometry_summary()[
        "k3_mixed_plane_inert_fan_geometry_theorem"
    ]
    assert all(theorem.values())
