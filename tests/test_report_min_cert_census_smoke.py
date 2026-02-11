from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _enum_payload(candidate_space: str, include_fourth_family: bool) -> dict:
    rep = {
        "hit_count": 1,
        "canonical_repr": [
            {
                "line": [[0, 0], [0, 1], [0, 2]],
                "z": 0,
                "sign_pm1": -1,
                "line_type": "x",
            },
            {
                "line": [[0, 0], [1, 0], [2, 0]],
                "z": 1,
                "sign_pm1": 1,
                "line_type": "y",
            },
            {
                "line": [[0, 0], [1, 1], [2, 2]],
                "z": 2,
                "sign_pm1": -1,
                "line_type": "y=1x",
            },
        ],
    }
    if include_fourth_family:
        rep["canonical_repr"].append(
            {
                "line": [[0, 1], [1, 2], [2, 0]],
                "z": 0,
                "sign_pm1": 1,
                "line_type": "y=2x",
            }
        )

    return {
        "status": "ok",
        "mode": "exact",
        "candidate_space": candidate_space,
        "k_min": 7,
        "exact_solutions_count": 1,
        "distinct_canonical_representatives_found": 1,
        "representatives": [rep],
    }


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )


def test_report_min_cert_census_smoke(tmp_path: Path):
    h_enum = tmp_path / "h_enum.json"
    a_enum = tmp_path / "a_enum.json"
    h_class = tmp_path / "h_class.json"
    a_class = tmp_path / "a_class.json"
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"

    h_enum.write_text(json.dumps(_enum_payload("hessian", True)), encoding="utf-8")
    a_enum.write_text(json.dumps(_enum_payload("agl", False)), encoding="utf-8")

    r1 = _run(
        [
            sys.executable,
            "tools/classify_canonical_reps.py",
            "--in-json",
            str(h_enum),
            "--out-json",
            str(h_class),
        ]
    )
    assert r1.returncode == 0, r1.stderr

    r2 = _run(
        [
            sys.executable,
            "tools/classify_canonical_reps.py",
            "--in-json",
            str(a_enum),
            "--out-json",
            str(a_class),
        ]
    )
    assert r2.returncode == 0, r2.stderr

    r3 = _run(
        [
            sys.executable,
            "tools/report_min_cert_census.py",
            "--hessian-json",
            str(h_class),
            "--agl-json",
            str(a_class),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ]
    )
    assert r3.returncode == 0, r3.stderr
    assert out_json.exists()
    assert out_md.exists()

    report = json.loads(out_json.read_text(encoding="utf-8"))
    assert report.get("status") == "ok"
    comparison = report.get("comparison", {})
    assert comparison.get("hessian_representatives") == 1
    assert comparison.get("agl_representatives") == 1
    assert comparison.get("hessian_full_striation_reps") == 1
    assert comparison.get("agl_full_striation_reps") == 0
    assert comparison.get("action_orbit_ceiling", 0) > 0
    h_orbit = comparison.get("hessian_orbit_size_hist", {})
    a_orbit = comparison.get("agl_orbit_size_hist", {})
    assert sum(int(v) for v in h_orbit.values()) == 1
    assert sum(int(v) for v in a_orbit.values()) == 1
    assert isinstance(comparison.get("hessian_has_reduced_orbit_layer"), bool)
    assert isinstance(comparison.get("agl_all_full_orbit"), bool)

    markdown = out_md.read_text(encoding="utf-8")
    assert "# Minimal-Certificate Census Report" in markdown
    assert "## Orbit Stratification" in markdown
