from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.nontrivial_core_rulebook import build_report


def test_rulebook_flags() -> None:
    payload = build_report()
    assert payload["status"] == "ok"
    flags = payload["theorem_flags"]
    assert flags["at_most_two_varying_coordinates_per_direction_rule"] is True
    assert flags["at_most_one_missing_cartesian_point_per_direction_rule"] is True
    assert flags["unique_non_cartesian_family_per_mode"] is True
    assert flags["the_non_cartesian_family_is_z11_x_direction"] is True

    ex = payload["matrix"]["all_agl"]["(1,1)"]["directions"]["x"]
    assert ex["triples"] == [[1, 1, 1], [1, 2, 1], [2, 1, 1]]
    assert ex["fixed_coordinates"] == {"z2": 1}
    assert ex["allowed_coordinates"] == {"z0": [1, 2], "z1": [1, 2]}
    assert ex["missing_cartesian_points"] == [[2, 2]]


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "rulebook.json"
    out_md = tmp_path / "rulebook.md"
    cmd = [
        sys.executable,
        "tools/nontrivial_core_rulebook.py",
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
