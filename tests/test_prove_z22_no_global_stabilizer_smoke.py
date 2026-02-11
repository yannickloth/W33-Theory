from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.prove_z22_no_global_stabilizer import analyze_no_global_stabilizer


def test_direct_api_no_global_stabilizer() -> None:
    payload_all = analyze_no_global_stabilizer("all_agl", (2, 2))
    payload_hessian = analyze_no_global_stabilizer("hessian216", (2, 2))
    payload_inv = analyze_no_global_stabilizer("involution_det2", (2, 2))

    assert payload_all["status"] == "ok"
    assert payload_all["checked_candidates"] == 864
    assert payload_all["match_count"] == 0
    assert payload_all["no_global_stabilizer"] is True

    assert payload_hessian["status"] == "ok"
    assert payload_hessian["checked_candidates"] == 432
    assert payload_hessian["match_count"] == 0
    assert payload_hessian["no_global_stabilizer"] is True

    assert payload_inv["status"] == "ok"
    assert payload_inv["checked_candidates"] == 216
    assert payload_inv["match_count"] == 0
    assert payload_inv["no_global_stabilizer"] is True


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "z22_global_exclusion.json"
    out_md = tmp_path / "z22_global_exclusion.md"

    cmd = [
        sys.executable,
        "tools/prove_z22_no_global_stabilizer.py",
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
    assert payload["z_map"] == [2, 2]
    assert payload["all_agl"]["match_count"] == 0
    assert payload["involution_det2"]["match_count"] == 0
