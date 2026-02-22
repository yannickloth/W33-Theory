from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import tools.s12_universal_algebra as s12


def test_analyze_s12_sl27_z3_bridge_cli_smoke(tmp_path: Path) -> None:
    s12_report_path = tmp_path / "s12_universalization_report.json"
    s12_report = s12.build_s12_universal_report(jordan_sample_limit=120)
    s12_report_path.write_text(json.dumps(s12_report, indent=2), encoding="utf-8")

    out_json = tmp_path / "bridge.json"
    out_md = tmp_path / "bridge.md"

    cmd = [
        sys.executable,
        "tools/analyze_s12_sl27_z3_bridge.py",
        "--s12-report-json",
        str(s12_report_path),
        "--max-block-size",
        "40",
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
    assert payload.get("status") == "ok"
    assert payload["search"]["match_count"] == 1
    assert payload["search"]["unique_sorted_solution"] is True

    rec = payload["search"]["matches"][0]
    assert rec["block_sizes"] == [9, 9, 9]
    assert rec["a_family_rank"] == 26
    assert rec["total_dim"] == 728

    assert payload["vogel_a_family_bridge"]["a_family_rank_from_total_dim"] == 26
    assert payload["bridge_claim_holds"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "sl_27" in text
    assert "(242, 243, 243)" in text
