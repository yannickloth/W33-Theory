from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.vogel_integer_m_locus import build_payload, dim_from_m


def test_integer_m_locus_core() -> None:
    payload = build_payload(m_min=-200, m_max=200, target_dims=[728, 486, 242])
    assert payload["status"] == "ok"
    assert payload["verification"]["mismatch_count"] == 0
    assert payload["positive_integer_m_dims"] == [
        8,
        28,
        52,
        78,
        133,
        190,
        248,
        336,
        484,
        603,
        782,
        1081,
        1680,
        3479,
    ]
    assert payload["targets"]["728"]["is_integer_m_hit"] is False
    assert payload["targets"]["486"]["is_integer_m_hit"] is False
    assert payload["targets"]["242"]["is_integer_m_hit"] is False


def test_dim_from_m_examples() -> None:
    assert dim_from_m(8) == 248
    assert dim_from_m(26) == 782
    assert dim_from_m(-1) == 8


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "locus.json"
    out_md = tmp_path / "locus.md"
    cmd = [
        sys.executable,
        "tools/vogel_integer_m_locus.py",
        "--m-min",
        "-200",
        "--m-max",
        "200",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["verification"]["mismatch_count"] == 0
    assert out_md.exists()
