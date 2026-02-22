from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.minimal_global_full_sign_cores import build_report


def test_core_matrix_flags() -> None:
    payload = build_report()
    assert payload["status"] == "ok"
    flags = payload["theorem_flags"]
    assert flags["all_agl_only_identity_at_z10"] is True
    assert flags["hessian_only_identity_at_z10"] is True
    assert flags["involution_subset_all_unsat"] is True
    assert flags["nontrivial_cells_need_four_striations_in_agl_hessian"] is True
    assert flags["involution_z10_needs_five_with_striation_complete"] is True

    agl_z22 = payload["matrix"]["all_agl"]["(2,2)"]
    assert agl_z22["status"] == "unsat"
    assert agl_z22["minimal_core_size"] == 3
    assert len(agl_z22["minimal_core"]) == 3
    assert agl_z22["variant_profiles"]["distinct_lines"]["minimal_core_size"] == 3
    assert agl_z22["variant_profiles"]["striation_complete"]["minimal_core_size"] == 4
    assert (
        agl_z22["variant_profiles"]["distinct_lines_striation_complete"][
            "minimal_core_size"
        ]
        == 4
    )

    agl_z10 = payload["matrix"]["all_agl"]["(1,0)"]
    assert agl_z10["status"] == "sat"
    assert agl_z10["match_count"] == 1
    assert agl_z10["variant_profiles"] == {}

    inv_z10 = payload["matrix"]["involution_det2"]["(1,0)"]
    assert inv_z10["status"] == "unsat"
    assert inv_z10["minimal_core_size"] == 4
    assert inv_z10["variant_profiles"]["distinct_lines"]["minimal_core_size"] == 4
    assert inv_z10["variant_profiles"]["striation_complete"]["minimal_core_size"] == 5


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "cores.json"
    out_md = tmp_path / "cores.md"
    cmd = [
        sys.executable,
        "tools/minimal_global_full_sign_cores.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["matrix"]["involution_det2"]["(2,2)"]["status"] == "unsat"
    assert payload["matrix"]["involution_det2"]["(2,2)"]["minimal_core_size"] == 3
    assert (
        payload["matrix"]["involution_det2"]["(2,2)"]["variant_profiles"][
            "striation_complete"
        ]["minimal_core_size"]
        == 4
    )
    assert out_md.exists()
