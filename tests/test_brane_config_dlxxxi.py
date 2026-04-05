"""Phase DLXXXI — Brane: N=q=3 D3, SU(3)=8, T=q/(q²+1), transverse=6."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_brane_config_bridge import build_brane_config_summary
def test_phase_dlxxxi():
    assert build_brane_config_summary()["brane_config_theorem"]["therefore_brane_verified"]
