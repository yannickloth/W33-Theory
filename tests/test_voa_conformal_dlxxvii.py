"""Phase DLXXVII — VOA: q=3 modules, c=6=rank, h(27)=2/3, Σh=4/3=C₂."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_voa_conformal_bridge import build_voa_conformal_summary
def test_phase_dlxxvii():
    assert build_voa_conformal_summary()["voa_conformal_theorem"]["therefore_voa_verified"]
