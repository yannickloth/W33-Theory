from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _fixture_payload() -> dict:
    fixture_lines = [
        ([[0, 0], [0, 1], [0, 2]], (-1, -1, 1)),
        ([[1, 0], [1, 1], [1, 2]], (-1, -1, 1)),
        ([[2, 0], [2, 1], [2, 2]], (1, -1, -1)),
        ([[0, 0], [1, 0], [2, 0]], (1, 1, -1)),
        ([[0, 1], [1, 1], [2, 1]], (1, -1, 1)),
        ([[0, 2], [1, 2], [2, 2]], (1, 1, 1)),
        ([[0, 0], [1, 1], [2, 2]], (1, -1, -1)),
        ([[0, 1], [1, 2], [2, 0]], (-1, -1, -1)),
        ([[0, 2], [1, 0], [2, 1]], (-1, 1, 1)),
        ([[0, 0], [1, 2], [2, 1]], (-1, 1, 1)),
        ([[0, 1], [1, 0], [2, 2]], (1, 1, 1)),
        ([[0, 2], [1, 1], [2, 0]], (1, 1, -1)),
    ]
    return {
        "affine_u_line_slices": [
            {
                "u_line": u_line,
                "entries": [
                    {"z_profile_over_u_line": [z, z, z], "sign_pm1": int(signs[z])}
                    for z in (0, 1, 2)
                ],
            }
            for u_line, signs in fixture_lines
        ]
    }


def test_exact_truncation_smoke(tmp_path: Path):
    in_json = tmp_path / "in.json"
    in_json.write_text(json.dumps(_fixture_payload()), encoding="utf-8")
    out_json = tmp_path / "out.json"

    cmd = [
        sys.executable,
        "tools/enumerate_minimal_certificates.py",
        "--in-json",
        str(in_json),
        "--candidate-space",
        "hessian",
        "--mode",
        "exact",
        "--max-exact-solutions",
        "1",
        "--time-limit-sec",
        "10",
        "--out-json",
        str(out_json),
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data.get("status") == "ok"
    assert data.get("mode") == "exact"
    assert data.get("k_min") == 7
    assert data.get("exact_solutions_count") == 1
    assert data.get("distinct_canonical_representatives_found", 0) >= 1
    assert data.get("truncated_by_max_solutions") is True
    assert data.get("search_nodes_explored", 0) > 0
