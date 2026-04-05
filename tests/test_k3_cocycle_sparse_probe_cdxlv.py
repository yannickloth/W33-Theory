"""
Phase CDXLV — K3 cocycle sparse probe: first nonzero witness localization.

The outer shell of the fan-adjacent sector (rank 20) is the first location
where a single F₃*-valued cocycle entry can appear without breaking d² = 0.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_cocycle_sparse_probe_bridge import (
    build_k3_cocycle_sparse_probe_summary,
)


def test_phase_cdxlv_first_nonzero_witness_lives_in_outer_shell() -> None:
    theorem = build_k3_cocycle_sparse_probe_summary()[
        "k3_cocycle_sparse_probe_theorem"
    ]
    assert theorem[
        "therefore_the_first_nonzero_witness_lives_in_the_outer_shell_at_minimum_weight_1"
    ] is True


def test_phase_cdxlv_spoke_columns_blocked_by_smith() -> None:
    theorem = build_k3_cocycle_sparse_probe_summary()[
        "k3_cocycle_sparse_probe_theorem"
    ]
    assert theorem[
        "the_outer_shell_admits_all_20_columns_as_valid_single_entry_cocycle_slots"
    ] is True


def test_phase_cdxlv_srg_consistency() -> None:
    summary = build_k3_cocycle_sparse_probe_summary()
    srg = summary["srg_consistency"]
    assert srg["edges"] == 240
    assert srg["triangles"] == 160
    assert srg["k3_euler_char"] == 24
