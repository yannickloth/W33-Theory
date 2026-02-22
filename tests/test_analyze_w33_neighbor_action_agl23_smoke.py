from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_w33_neighbor_action_agl23_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "w33_neighbor_action.json"
    out_md = tmp_path / "w33_neighbor_action.md"
    cmd = [
        sys.executable,
        "tools/analyze_w33_neighbor_action_agl23.py",
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
    assert payload.get("status") == "ok"
    assert payload.get("claim_holds") is True

    group = payload["group"]
    assert group["point_count"] == 40
    assert group["aut_group_order"] == 51840
    assert group["vertex_stabilizer_order"] == 1296

    nb = payload["neighborhood"]
    assert nb["neighbor_count"] == 12
    assert nb["triangles_ok"] is True
    assert len(nb["triangle_components"]) == 4
    assert all(len(c) == 3 for c in nb["triangle_components"])

    act = payload["neighbor_action"]
    assert act["induced_group_order"] == 432
    assert act["kernel_order"] == 3
    assert act["triangle_action_order"] == 24
    assert act["triangle_action_is_S4"] is True
    assert act["triangle_kernel_order"] == 18
    assert act["translations"]["order"] == 9
    assert act["translations"]["is_subgroup"] is True
    assert act["translations"]["is_abelian"] is True
    assert act["translations"]["is_normal"] is True

    inv = payload["involutions"]
    assert inv["count"] == 45
    assert inv["reflection_count"] == 36
    assert inv["rotation_count"] == 9
    assert inv["centralizer_size_histogram_by_type"]["reflection"] == {"12": 36}
    assert inv["reflection_conjugacy_class_count"] == 1
    assert inv["reflection_conjugacy_class_size"] == 36
    assert inv["reflection_centralizer_matches_d12_fingerprint"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "W33 Neighbor Action Realizes AGL(2,3)" in text
