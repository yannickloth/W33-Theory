from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.classify_global_full_sign_stabilizers import build_census


def test_census_theorem_flags() -> None:
    payload = build_census()
    assert payload["status"] == "ok"
    flags = payload["theorem_flags"]
    assert flags["all_agl_trivial_only"] is True
    assert flags["hessian216_trivial_only"] is True
    assert flags["involution_subset_none"] is True

    nonzero = payload["nonzero_cells"]
    assert len(nonzero) == 2
    keys = {(row["mode"], tuple(row["z_map"]), row["match_count"]) for row in nonzero}
    assert keys == {("all_agl", (1, 0), 1), ("hessian216", (1, 0), 1)}


def test_census_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "census.json"
    out_md = tmp_path / "census.md"
    cmd = [
        sys.executable,
        "tools/classify_global_full_sign_stabilizers.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["matrix"]["all_agl"]["(2,2)"]["match_count"] == 0
    assert payload["matrix"]["hessian216"]["(2,2)"]["match_count"] == 0
    assert payload["matrix"]["involution_det2"]["(1,0)"]["match_count"] == 0
    assert out_md.exists()
