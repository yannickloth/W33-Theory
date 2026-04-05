"""Phase CDXCIX — Anomaly cancellation: g=15 Weyl/gen, Tr(Y³)=0."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "exploration") not in sys.path:
    sys.path.insert(0, str(ROOT / "exploration"))
from w33_anomaly_cancellation_bridge import build_anomaly_cancellation_summary

def test_phase_cdxcix_anomaly() -> None:
    t = build_anomaly_cancellation_summary()["anomaly_cancellation_theorem"]
    assert t["therefore_anomaly_cancelled"] is True
