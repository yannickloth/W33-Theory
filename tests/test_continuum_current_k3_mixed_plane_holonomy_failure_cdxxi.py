"""
Phase CDXXI — current K3 mixed-plane holonomy failure.

CDXX made the smallest positive datum concrete in adapted holonomy language.
This phase applies that criterion to the current host and shows the remaining
failure is now exactly absence of the first non-identity unipotent
sign-trivial holonomy witness on the same fixed mixed-plane host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_holonomy_failure_bridge import (
    build_current_k3_mixed_plane_holonomy_failure_summary,
)


def test_phase_cdxxi_current_host_fails_only_by_missing_nontrivial_sign_trivial_holonomy() -> None:
    theorem = build_current_k3_mixed_plane_holonomy_failure_summary()[
        "current_k3_mixed_plane_holonomy_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_holonomy_witness_test_for_one_reason_only_the_nontrivial_sign_trivial_holonomy_is_missing"
    ] is True


def test_phase_cdxxi_live_wall_is_first_nonidentity_unipotent_sign_trivial_holonomy_witness() -> None:
    theorem = build_current_k3_mixed_plane_holonomy_failure_summary()[
        "current_k3_mixed_plane_holonomy_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonidentity_unipotent_sign_trivial_holonomy_witness_on_the_same_fixed_host"
    ] is True
