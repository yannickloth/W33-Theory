"""
Phase CDXXIII — current K3 mixed-plane nilpotent holonomy increment failure.

CDXXII made the smallest positive matrix datum explicit. This phase applies
that criterion to the current host and shows the remaining failure is now
exactly absence of the first genuine nonzero nilpotent holonomy increment on
the same fixed mixed-plane host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_nilpotent_holonomy_increment_failure_bridge import (
    build_current_k3_mixed_plane_nilpotent_holonomy_increment_failure_summary,
)


def test_phase_cdxxiii_current_host_fails_only_by_missing_nonzero_nilpotent_increment() -> None:
    theorem = build_current_k3_mixed_plane_nilpotent_holonomy_increment_failure_summary()[
        "current_k3_mixed_plane_nilpotent_holonomy_increment_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_nilpotent_increment_test_for_one_reason_only_the_nonzero_increment_is_missing"
    ] is True


def test_phase_cdxxiii_live_wall_is_first_nonzero_nilpotent_holonomy_increment() -> None:
    theorem = build_current_k3_mixed_plane_nilpotent_holonomy_increment_failure_summary()[
        "current_k3_mixed_plane_nilpotent_holonomy_increment_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_nilpotent_holonomy_increment_on_the_same_fixed_host"
    ] is True
