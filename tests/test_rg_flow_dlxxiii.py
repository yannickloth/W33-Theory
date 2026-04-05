"""Phase DLXXIII — RG flow: β₀=10, asymp free, k/|s|=q, γ=1/6."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_rg_flow_bridge import build_rg_flow_summary
def test_phase_dlxxiii():
    assert build_rg_flow_summary()["rg_flow_theorem"]["therefore_rg_verified"]
