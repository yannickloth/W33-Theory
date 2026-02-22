from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import tools.s12_universal_algebra as s12_universal
import tools.vogel_universal_snapshot as vogel


def test_vogel_snapshot_core_smoke(tmp_path: Path):
    s12_report_path = tmp_path / "s12_universalization_report.json"
    s12_report = s12_universal.build_s12_universal_report(jordan_sample_limit=120)
    s12_report_path.write_text(json.dumps(s12_report, indent=2), encoding="utf-8")

    snapshot = vogel.build_snapshot(
        s12_report_path=s12_report_path,
        exceptional_line_denominator_cap=12,
    )
    assert snapshot["status"] == "ok"
    assert snapshot["exceptional_direct_table"]["all_match"] is True
    assert snapshot["exceptional_line_parametrization"]["all_match"] is True

    hits_728 = snapshot["target_dimension_hits"]["classical_families"]["728"]
    assert hits_728["A"] == [26]
    assert hits_728["B"] == []
    assert hits_728["C"] == []
    assert hits_728["D"] == []

    ex_hits_728 = snapshot["target_dimension_hits"]["exceptional_line_rational_search"][
        "728"
    ]
    assert ex_hits_728["hit_count"] == 0

    s12 = snapshot["s12_bridge"]
    assert s12 is not None
    assert s12["total_nonzero_dim"] == 728
    assert s12["jacobi_holds"] is False
    assert s12["ad3_holds"] is True


def test_vogel_snapshot_cli_smoke(tmp_path: Path):
    s12_report_path = tmp_path / "s12_universalization_report.json"
    s12_report = s12_universal.build_s12_universal_report(jordan_sample_limit=120)
    s12_report_path.write_text(json.dumps(s12_report, indent=2), encoding="utf-8")

    out_json = tmp_path / "vogel_snapshot.json"
    out_md = tmp_path / "vogel_snapshot.md"
    cmd = [
        sys.executable,
        "tools/vogel_universal_snapshot.py",
        "--s12-report-json",
        str(s12_report_path),
        "--exceptional-line-denominator-cap",
        "12",
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
    assert payload["exceptional_direct_table"]["all_match"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "# Vogel Universal Snapshot" in text
    assert "Target-Dimension Scan" in text
    assert "s12 Bridge" in text
