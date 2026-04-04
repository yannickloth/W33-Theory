from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_active_basis_failure_bridge import (
    build_current_k3_mixed_plane_active_basis_failure_summary,
)


def test_current_mixed_plane_active_basis_failure_has_expected_counts() -> None:
    summary = build_current_k3_mixed_plane_active_basis_failure_summary()
    current = summary["current_mixed_plane_active_basis_state"]
    exact = summary["exact_mixed_plane_active_basis"]

    assert current["current_active_column_supported_entry_count"] == 0
    assert current["current_inactive_column_supported_entry_count"] == 0
    assert exact["active_column_count"] == 36
    assert exact["active_column_restricted_rank"] == 36


def test_current_mixed_plane_active_basis_failure_theorem_holds() -> None:
    theorem = build_current_k3_mixed_plane_active_basis_failure_summary()[
        "current_k3_mixed_plane_active_basis_failure_theorem"
    ]
    assert all(theorem.values())
