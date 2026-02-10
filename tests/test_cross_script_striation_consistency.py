from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_cross_script_striation_consistency():
    root = Path.cwd()
    in_json = root / "artifacts" / "e6_f3_trilinear_map.json"
    if not in_json.exists():
        pytest.skip("Missing artifacts/e6_f3_trilinear_map.json")

    out_json = root / "artifacts" / "e6_f3_trilinear_symmetry_breaking.json"
    out_md = root / "artifacts" / "e6_f3_trilinear_symmetry_breaking.md"

    # Ensure analysis output exists (run analyzer if needed)
    if not out_json.exists():
        cmd = [
            sys.executable,
            "tools/analyze_e6_f3_trilinear_symmetry_breaking.py",
            "--in-json",
            str(in_json),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ]
        r = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        assert r.returncode == 0, r.stderr
        assert out_json.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))

    # Extract the trilinear analysis reported direction & missing point
    direction = data["cross_checks"]["line_product_flag_geometry"][
        "distinguished_direction_all_positive"
    ]
    missing_point = tuple(
        data["cross_checks"]["line_product_flag_geometry"][
            "unique_missing_point_from_negative_lines"
        ]
    )

    # Build W33 local Heisenberg fibers and detect missing fibers
    from w33_homology import build_w33

    from scripts.w33_heisenberg_qutrit import build_f3_cube, compute_local_structure

    n, vertices, adj, edges = build_w33()
    adj_s = [set(adj[i]) for i in range(n)]
    N12, H27, triangles, h27_neighbors = compute_local_structure(0, n, adj_s)
    fibers, vertex_to_xyz = build_f3_cube(N12, H27, triangles, adj_s)

    missing_fibers = []
    for (x, y), verts in fibers.items():
        a, b, c = verts
        is_tri = b in adj_s[a] and c in adj_s[b] and c in adj_s[a]
        if not is_tri:
            missing_fibers.append((x, y))

    assert (
        missing_point in missing_fibers
    ), f"Missing point {missing_point} not found among local missing fibers {missing_fibers}"

    # Verify the missing point lies on a line from the reported distinguished direction family
    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    lines = analyze._all_affine_lines()
    family = [L for L in lines if analyze._line_equation_type(L)[0] == direction]
    assert any(
        tuple(missing_point) in L for L in family
    ), f"Missing point {missing_point} is not on any line in distinguished family {direction}"
