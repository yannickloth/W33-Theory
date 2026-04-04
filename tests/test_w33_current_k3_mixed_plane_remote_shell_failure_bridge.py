from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_remote_shell_failure_bridge import (
    build_current_k3_mixed_plane_remote_shell_failure_summary,
)


def test_current_mixed_plane_remote_shell_failure_has_expected_zero_state() -> None:
    summary = build_current_k3_mixed_plane_remote_shell_failure_summary()
    current = summary["current_mixed_plane_remote_shell_state"]
    exact = summary["exact_mixed_plane_remote_shell"]

    assert current["current_supported_entry_count_on_remote_shell"] == 0
    assert exact["remote_column_rank"] == 12


def test_current_mixed_plane_remote_shell_failure_theorem_holds() -> None:
    theorem = build_current_k3_mixed_plane_remote_shell_failure_summary()[
        "current_k3_mixed_plane_remote_shell_failure_theorem"
    ]
    assert all(theorem.values())
