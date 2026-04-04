from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_row_entry_witness_bridge import (
    build_k3_mixed_plane_row_entry_witness_summary,
)


def test_mixed_plane_row_entry_witness_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_row_entry_witness_summary()
    witness = summary["row_entry_witness"]

    assert witness["supported_row_count"] == 4046
    assert witness["row_support_size_distribution"] == {1: 4046}
    assert witness["entry_value_distribution"] == {1: 2029, 2: 2017}
    assert witness["row_component_distribution"] == {"invariant_row": 2018, "sign_row": 2028}


def test_mixed_plane_row_entry_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_row_entry_witness_summary()[
        "k3_mixed_plane_row_entry_witness_theorem"
    ]
    assert all(theorem.values())
