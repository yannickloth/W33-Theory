"""Phase DLXVII — MSSM: g=15/gen, q=3 gens, 45=SO(10), gauge=k=12."""
from __future__ import annotations
import sys; from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path: sys.path.insert(0, str(ROOT / "exploration"))
from w33_mssm_spectrum_bridge import build_mssm_spectrum_summary
def test_phase_dlxvii():
    assert build_mssm_spectrum_summary()["mssm_spectrum_theorem"]["therefore_mssm_verified"]
