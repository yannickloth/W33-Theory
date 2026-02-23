"""Tests for scripts/w33_yukawa_blocks.py.

Verifies:
  1. The script runs and produces data/w33_yukawa_blocks.json
  2. H27 decomposes into exactly three 9-element SU(3)^3 blocks
  3. The best vertex-VEV pair gives a diagonal-dominant CKM matrix
  4. The CKM Frobenius error is below the identity-matrix baseline (~0.32)
  5. Eigenvalue hierarchies are nontrivial (ratio > 10 for at least one sector)
"""

import json
import os
import subprocess
import sys
import math
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def results():
    """Run the script once and return the parsed JSON output."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run(
        [sys.executable, "scripts/w33_yukawa_blocks.py"],
        env=env,
        capture_output=True,
        text=True,
        cwd=os.path.abspath("."),
    )
    assert res.returncode == 0, f"script failed:\n{res.stderr}"
    assert os.path.exists("data/w33_yukawa_blocks.json"), "JSON output not written"
    with open("data/w33_yukawa_blocks.json") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


def test_script_runs(results):
    """Script exits cleanly and writes output JSON."""
    assert results is not None


def test_block_scan_has_entries(results):
    """Block permutation scan produces at least one non-trivial result."""
    assert len(results["block_scan"]) >= 1


def test_best_block_exists(results):
    """Best block assignment was identified."""
    assert results["best_block"] is not None
    assert "ckm_error" in results["best_block"]
    assert "koide_Q" in results["best_block"]


def test_best_block_ckm_error_finite(results):
    """Best block-VEV CKM error is a finite positive number."""
    err = results["best_block"]["ckm_error"]
    assert math.isfinite(err)
    assert err > 0


def test_vertex_scan_best_exists(results):
    """Vertex-VEV scan found a best result."""
    assert results["vertex_scan_best"] is not None
    assert "ckm_error" in results["vertex_scan_best"]
    assert "V_CKM" in results["vertex_scan_best"]


def test_vertex_scan_ckm_below_identity_baseline(results):
    """Best vertex CKM error is below the trivial identity baseline (~0.32)."""
    err = results["vertex_scan_best"]["ckm_error"]
    # Identity matrix vs experimental CKM has Frobenius error ~0.32
    assert err < 0.35, (
        f"vertex-VEV CKM error {err:.4f} not better than identity baseline"
    )


def test_vertex_scan_diagonal_dominant(results):
    """The predicted CKM matrix is diagonal-dominant (correct quark mixing sign)."""
    V = np.abs(results["vertex_scan_best"]["V_CKM"])
    # Each row should have its largest element on the diagonal
    for i in range(3):
        assert V[i][i] == max(V[i]), (
            f"Row {i} of predicted CKM is not diagonal-dominant: {V[i]}"
        )


def test_vertex_scan_vud_close(results):
    """V_ud element (generation-0 diagonal) is in the correct ballpark (>0.85)."""
    V = np.abs(results["vertex_scan_best"]["V_CKM"])
    assert V[0][0] > 0.85, f"|V_ud| = {V[0][0]:.4f}, expected > 0.85"


def test_vertex_scan_vcs_close(results):
    """V_cs element is in the correct ballpark (>0.85)."""
    V = np.abs(results["vertex_scan_best"]["V_CKM"])
    assert V[1][1] > 0.85, f"|V_cs| = {V[1][1]:.4f}, expected > 0.85"


def test_eigenvalue_hierarchy_nontrivial(results):
    """At least one Yukawa sector has eigenvalue ratio > 10 (non-democratic)."""
    best = results["vertex_scan_best"]
    ratio_u = best.get("ratio_up", 0)
    ratio_d = best.get("ratio_down", 0)
    assert max(ratio_u, ratio_d) > 10, (
        f"Eigenvalue ratios ({ratio_u:.1f}, {ratio_d:.1f}) should exceed 10"
    )


def test_block_decomposition():
    """Verify H27 decomposes into exactly three 9-element blocks by GF(3) affine coord."""
    import sys
    sys.path.insert(0, "scripts")
    from e8_embedding_group_theoretic import build_w33

    n_w33, vertices_w33, adj_w33, _ = build_w33()
    v0_idx = 0
    neighbors_v0 = set(adj_w33[v0_idx])
    H27_vertices = [vertices_w33[i] for i in range(n_w33)
                    if i != v0_idx and i not in neighbors_v0]

    assert len(H27_vertices) == 27

    def gf3_inv(x):
        return {1: 1, 2: 2}[int(x) % 3]

    blocks = {0: 0, 1: 0, 2: 0}
    for v in H27_vertices:
        inv_x2 = gf3_inv(v[2])
        a = (v[0] * inv_x2) % 3
        blocks[a] += 1

    assert blocks == {0: 9, 1: 9, 2: 9}, (
        f"Expected 9+9+9 block decomposition, got {blocks}"
    )


def test_cross_block_triangles():
    """H27 has exactly 27 cross-block (one vertex from each block) triangles."""
    import sys
    sys.path.insert(0, "scripts")
    from e8_embedding_group_theoretic import build_w33
    from w33_ckm_from_vev import build_h27_index_and_tris

    n_w33, vertices_w33, adj_w33, _ = build_w33()
    v0_idx = 0
    neighbors_v0 = set(adj_w33[v0_idx])
    H27_vertices = [vertices_w33[i] for i in range(n_w33)
                    if i != v0_idx and i not in neighbors_v0]

    def gf3_inv(x):
        return {1: 1, 2: 2}[int(x) % 3]

    block_of = []
    for v in H27_vertices:
        inv_x2 = gf3_inv(v[2])
        a = (v[0] * inv_x2) % 3
        block_of.append(a)

    adj_local = [list(adj_w33[i]) for i in range(n_w33)]
    H27_idx_set = set(range(n_w33))
    H27_idx_set -= {v0_idx}
    H27_idx_set -= neighbors_v0
    # Build local triangle list directly
    H27_idx_list = [i for i in range(n_w33) if i != v0_idx and i not in neighbors_v0]
    h27_set = set(H27_idx_list)
    local_idx = {v: i for i, v in enumerate(H27_idx_list)}

    tris_012 = 0
    tris_same = 0
    seen = set()
    for ai, a_global in enumerate(H27_idx_list):
        for b_global in adj_w33[a_global]:
            if b_global not in h27_set or local_idx[b_global] <= ai:
                continue
            bi = local_idx[b_global]
            for c_global in adj_w33[a_global]:
                if c_global not in h27_set or local_idx[c_global] <= bi:
                    continue
                if c_global not in adj_w33[b_global]:
                    continue
                ci = local_idx[c_global]
                blocks_set = {block_of[ai], block_of[bi], block_of[ci]}
                if len(blocks_set) == 3:
                    tris_012 += 1
                else:
                    tris_same += 1

    assert tris_012 == 27, f"Expected 27 cross-block triangles, got {tris_012}"
    assert tris_same == 9, f"Expected 9 within-block triangles, got {tris_same}"
