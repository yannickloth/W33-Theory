from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _fake_enumeration_payload(candidate_space: str) -> dict:
    rep_a = {
        "hit_count": 2,
        "canonical_repr": [
            {
                "line": [[0, 0], [0, 1], [0, 2]],
                "z": 0,
                "sign_pm1": -1,
                "line_type": "x",
            },
            {
                "line": [[0, 0], [0, 1], [0, 2]],
                "z": 1,
                "sign_pm1": -1,
                "line_type": "x",
            },
            {
                "line": [[0, 0], [1, 0], [2, 0]],
                "z": 0,
                "sign_pm1": 1,
                "line_type": "y",
            },
            {
                "line": [[0, 0], [1, 1], [2, 2]],
                "z": 2,
                "sign_pm1": 1,
                "line_type": "y=1x",
            },
        ],
    }
    rep_b = {
        "hit_count": 1,
        "canonical_repr": [
            {
                "line": [[0, 0], [1, 0], [2, 0]],
                "z": 2,
                "sign_pm1": -1,
                "line_type": "y",
            },
            {
                "line": [[0, 0], [1, 0], [2, 0]],
                "z": 1,
                "sign_pm1": 1,
                "line_type": "y",
            },
            {
                "line": [[0, 0], [1, 1], [2, 2]],
                "z": 0,
                "sign_pm1": -1,
                "line_type": "y=1x",
            },
        ],
    }
    return {
        "status": "ok",
        "mode": "exact",
        "candidate_space": candidate_space,
        "k_min": 7,
        "exact_solutions_count": 3,
        "distinct_canonical_representatives_found": 2,
        "representatives": [rep_a, rep_b],
    }


def test_classify_canonical_reps_smoke(tmp_path: Path):
    in_json = tmp_path / "enum.json"
    out_json = tmp_path / "classified.json"
    in_json.write_text(
        json.dumps(_fake_enumeration_payload("hessian")), encoding="utf-8"
    )

    cmd = [
        sys.executable,
        "tools/classify_canonical_reps.py",
        "--in-json",
        str(in_json),
        "--out-json",
        str(out_json),
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(out_json.read_text(encoding="utf-8"))

    assert data.get("status") == "ok"
    assert data.get("total_representatives") == 2
    assert data.get("total_weight") == 3
    aggregate = data.get("aggregate", {})
    assert aggregate.get("unique_lines_count_hist", {}).get("2") == 1
    assert aggregate.get("unique_lines_count_hist", {}).get("3") == 1
    assert aggregate.get("striation_family_count_hist", {}).get("2") == 1
    assert aggregate.get("striation_family_count_hist", {}).get("3") == 1
