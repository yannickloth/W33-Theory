from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.core_motif_anchor_channels import build_report


def test_build_report_anchor_properties() -> None:
    payload = build_report()
    assert payload["status"] == "ok"

    full_anchors = payload["full_anchors"]
    reduced_anchors = payload["reduced_anchors"]
    assert "x:1-1-0" in full_anchors
    assert "x:2-2-1" in reduced_anchors

    combined = payload["anchor_evaluation"]["hessian_combined"]
    assert combined["representative_count"] == 335
    assert combined["fired_count"] == 38
    assert combined["conflict_count"] == 0
    assert abs(float(combined["precision_when_fired"]) - (36.0 / 38.0)) < 1e-12

    flags = payload["theorem_flags"]
    assert flags["full_anchor_contains_x110"] is True
    assert flags["reduced_anchor_contains_x221"] is True
    assert flags["combined_precision_when_fired_ge_0p90"] is True
    assert flags["combined_conflict_count_zero"] is True


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "core_motif_anchor_channels.json"
    out_md = tmp_path / "core_motif_anchor_channels.md"
    cmd = [
        sys.executable,
        "tools/core_motif_anchor_channels.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert out_md.exists()
