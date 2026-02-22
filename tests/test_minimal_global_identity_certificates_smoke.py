from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.minimal_global_identity_certificates import build_report


def test_identity_certificate_flags() -> None:
    payload = build_report(max_examples=2, top_k=4)
    assert payload["status"] == "ok"
    flags = payload["theorem_flags"]
    assert flags["all_agl_min_size_6"] is True
    assert flags["hessian216_min_size_5"] is True
    assert flags["hessian_strictly_smaller_than_agl"] is True
    assert flags["all_agl_count_688"] is True
    assert flags["hessian216_count_33"] is True
    assert flags["gap_robust_under_distinct_lines"] is True
    assert flags["gap_robust_under_striation_complete"] is True
    assert flags["gap_robust_under_both_constraints"] is True

    agl = payload["mode_results"]["all_agl"]
    hessian = payload["mode_results"]["hessian216"]
    assert agl["minimal_certificate_size"] == 6
    assert hessian["minimal_certificate_size"] == 5
    assert agl["target_candidate"]["A"] == [1, 0, 0, 1]
    assert agl["target_candidate"]["shift"] == [0, 0]
    assert agl["target_candidate"]["eps"] == 1
    assert agl["variant_profiles"]["distinct_lines"]["minimal_certificate_count"] == 167
    assert (
        agl["variant_profiles"]["striation_complete"]["minimal_certificate_count"]
        == 246
    )
    assert (
        agl["variant_profiles"]["distinct_lines_striation_complete"][
            "minimal_certificate_count"
        ]
        == 79
    )
    assert (
        hessian["variant_profiles"]["distinct_lines"]["minimal_certificate_count"] == 17
    )
    assert (
        hessian["variant_profiles"]["striation_complete"]["minimal_certificate_count"]
        == 4
    )
    assert (
        hessian["variant_profiles"]["distinct_lines_striation_complete"][
            "minimal_certificate_count"
        ]
        == 3
    )


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "identity_certs.json"
    out_md = tmp_path / "identity_certs.md"
    cmd = [
        sys.executable,
        "tools/minimal_global_identity_certificates.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
        "--max-examples",
        "2",
        "--top-k",
        "4",
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["mode_results"]["all_agl"]["minimal_certificate_size"] == 6
    assert payload["mode_results"]["hessian216"]["minimal_certificate_size"] == 5
    assert (
        payload["mode_results"]["all_agl"]["variant_profiles"]["distinct_lines"][
            "minimal_certificate_size"
        ]
        == 6
    )
    assert (
        payload["mode_results"]["hessian216"]["variant_profiles"][
            "distinct_lines_striation_complete"
        ]["minimal_certificate_size"]
        == 5
    )
    assert out_md.exists()
