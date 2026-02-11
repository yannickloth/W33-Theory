from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.vogel_rational_hit_catalog import nondeg_rational_roots_for_dim


def test_nondeg_roots_for_s12_dims_are_empty() -> None:
    assert nondeg_rational_roots_for_dim(728)["hits"] == []
    assert nondeg_rational_roots_for_dim(486)["hits"] == []
    assert nondeg_rational_roots_for_dim(242)["hits"] == []


def test_catalog_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "catalog.json"
    out_md = tmp_path / "catalog.md"
    cmd = [
        sys.executable,
        "tools/vogel_rational_hit_catalog.py",
        "--start",
        "200",
        "--end",
        "1000",
        "--step",
        "1",
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
    assert payload["hit_dims"] == [248, 287, 336, 484, 603, 782]
    assert payload["targets"]["728"]["hits"] == []
    assert payload["targets"]["486"]["hits"] == []
    assert payload["targets"]["242"]["hits"] == []
