"""Phase DX — QEC: [[40,1,d]] graph-state code, stabilizer weight=k+1=13."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_qec_graph_bridge import build_qec_graph_summary

def test_phase_dx_qec() -> None:
    t = build_qec_graph_summary()["qec_graph_theorem"]
    assert t["therefore_qec_consistent"] is True
