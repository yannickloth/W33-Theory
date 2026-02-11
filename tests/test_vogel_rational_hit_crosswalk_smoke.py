from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.vogel_rational_hit_crosswalk import build_crosswalk


def test_crosswalk_summary_sets() -> None:
    payload = build_crosswalk([728, 486, 242])
    summary = payload["summary"]
    assert summary["total_positive_hits"] == 21
    assert summary["classical_hit_dims"] == [3, 8, 28, 78, 190, 1081, 1680]
    assert summary["direct_table_hit_dims"] == [8, 14, 28, 52, 78, 133, 248]
    assert summary["classical_direct_overlap_dims"] == [8, 28, 78]
    assert summary["arithmetic_only_hit_dims"] == [
        1,
        47,
        96,
        119,
        287,
        336,
        484,
        603,
        782,
        3479,
    ]


def test_crosswalk_target_nearest_hits() -> None:
    payload = build_crosswalk([728, 486, 242])
    targets = payload["targets"]
    assert targets["728"]["in_positive_hit_set"] is False
    assert targets["728"]["nearest_hit"]["nearest_dims"] == [782]
    assert targets["728"]["nearest_hit"]["distance"] == 54
    assert targets["486"]["nearest_hit"]["nearest_dims"] == [484]
    assert targets["486"]["nearest_hit"]["distance"] == 2
    assert targets["242"]["nearest_hit"]["nearest_dims"] == [248]
    assert targets["242"]["nearest_hit"]["distance"] == 6


def test_crosswalk_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "crosswalk.json"
    out_md = tmp_path / "crosswalk.md"
    cmd = [
        sys.executable,
        "tools/vogel_rational_hit_crosswalk.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    assert out_json.exists()
    assert out_md.exists()
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["summary"]["total_positive_hits"] == 21
