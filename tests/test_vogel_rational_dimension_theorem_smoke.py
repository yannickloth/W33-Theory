from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.vogel_rational_dimension_theorem import (
    positive_nondeg_hit_dims,
    window_hit_dims,
)


def test_positive_hit_dims_exact() -> None:
    assert positive_nondeg_hit_dims() == [
        1,
        3,
        8,
        14,
        28,
        47,
        52,
        78,
        96,
        119,
        133,
        190,
        248,
        287,
        336,
        484,
        603,
        782,
        1081,
        1680,
        3479,
    ]


def test_window_hits_match_previous_sweep() -> None:
    assert window_hit_dims(200, 1000) == [248, 287, 336, 484, 603, 782]


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "theorem.json"
    out_md = tmp_path / "theorem.md"
    cmd = [
        sys.executable,
        "tools/vogel_rational_dimension_theorem.py",
        "--window-start",
        "200",
        "--window-end",
        "1000",
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
    assert payload["window"]["hit_dims"] == [248, 287, 336, 484, 603, 782]
    assert payload["targets"]["728"]["in_positive_hit_dims"] is False
    assert payload["targets"]["486"]["in_positive_hit_dims"] is False
    assert payload["targets"]["242"]["in_positive_hit_dims"] is False
    assert payload["verification"]["factorization_matches_bruteforce"] is True
