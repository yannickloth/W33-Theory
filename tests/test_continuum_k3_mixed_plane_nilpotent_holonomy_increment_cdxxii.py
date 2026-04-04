"""
Phase CDXXII — K3 mixed-plane nilpotent holonomy increment.

CDXX made the smallest positive datum concrete in holonomy language. This
phase makes the adapted matrix increment itself explicit: exact K3 tail
realization is equivalent to one support-preserving nonzero nilpotent
holonomy increment on the same fixed host.
"""

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


def test_phase_cdxxii_realization_is_nonzero_nilpotent_holonomy_increment() -> None:
    theorem = build_k3_mixed_plane_nilpotent_holonomy_increment_summary()[
        "k3_mixed_plane_nilpotent_holonomy_increment_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_nilpotent_holonomy_increment_on_the_same_fixed_host"
    ] is True


def test_phase_cdxxii_live_wall_is_first_nonzero_nilpotent_holonomy_increment() -> None:
    theorem = build_k3_mixed_plane_nilpotent_holonomy_increment_summary()[
        "k3_mixed_plane_nilpotent_holonomy_increment_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_nilpotent_holonomy_increment_on_the_same_fixed_host"
    ] is True
