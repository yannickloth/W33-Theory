"""Phase DLXIII — Regge: χ=-v, Gauss-Bonnet, tri/vertex=k, edge_val=λ."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_regge_gravity_bridge import build_regge_gravity_summary
def test_phase_dlxiii():
    assert build_regge_gravity_summary()["regge_gravity_theorem"]["therefore_regge_verified"]
