"""Phase CDLXIII — 240 edges ↔ 240 E₈ roots via D₈+S⁺ split."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))
from w33_edge_root_correspondence_bridge import build_edge_root_correspondence_summary

def test_phase_cdlxiii_edge_root_correspondence() -> None:
    t = build_edge_root_correspondence_summary()["edge_root_correspondence_theorem"]
    assert t["therefore_edge_root_correspondence"] is True

def test_phase_cdlxiii_e8_dim_edges_plus_cartan() -> None:
    t = build_edge_root_correspondence_summary()["edge_root_correspondence_theorem"]
    assert t["e8_dim_is_edges_plus_cartan"] is True
