#!/usr/bin/env python3
"""Run Opus-style H1 computation using existing W33 CSV/JSON artifacts (no Sage required).
Writes results to artifacts/opus_h1_summary.json
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
# Import lib modules by path (avoid Python package issues)
import importlib.util

spec = importlib.util.spec_from_file_location("w33_io", str(ROOT / "lib" / "w33_io.py"))
w33_io = importlib.util.module_from_spec(spec)
import sys

sys.modules["w33_io"] = w33_io
spec.loader.exec_module(w33_io)
W33DataPaths = w33_io.W33DataPaths
load_w33_lines = w33_io.load_w33_lines
simplices_from_lines = w33_io.simplices_from_lines
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# load lines (from repo data)
paths = W33DataPaths.from_this_file(
    str(ROOT / "claude_workspace" / "w33_sage_incidence_and_h1.py")
)
lines = load_w33_lines(paths)

# build simplicial complex
simplices = simplices_from_lines(lines)
vertices = simplices[0]
edges = simplices[1]
tris = simplices[2]

n0 = len(vertices)
n1 = len(edges)
n2 = len(tris)


# boundary matrices (as in w33_h1_fast)
def faces(s):
    # oriented faces of a k-simplex (sorted tuple)
    # returns list of (sign, face) pairs
    out = []
    for i in range(len(s)):
        face = tuple(sorted([s[j] for j in range(len(s)) if j != i]))
        sign = -1 if (i % 2) else 1
        out.append((sign, face))
    return out


idx_vert = {v[0]: i for i, v in enumerate(vertices)}
idx_edge = {e: i for i, e in enumerate(edges)}
idx_tri = {t: i for i, t in enumerate(tris)}


def boundary_matrix(k_simplices, km1_simplices, km1_idx):
    m = len(km1_simplices)
    n = len(k_simplices)
    M = np.zeros((m, n), dtype=float)
    for j, s in enumerate(k_simplices):
        for sign, f in faces(s):
            i = km1_idx.get(f)
            if i is not None:
                M[i, j] = sign
    return M


# build d1 (edges -> vertices) and d2 (tris -> edges)
d1 = boundary_matrix(edges, vertices, idx_vert)
d2 = boundary_matrix(tris, edges, idx_edge)

# compute Z1 (nullspace of d1) and B1 (columnspace of d2)
U, s, Vh = np.linalg.svd(d1)
rank_d1 = np.sum(s > 1e-10)
Z1_basis = Vh[rank_d1:].T if rank_d1 < Vh.shape[0] else np.zeros((n1, 0))
dim_Z1 = Z1_basis.shape[1] if Z1_basis.size else 0

U2, s2, Vh2 = np.linalg.svd(d2)
rank_d2 = np.sum(s2 > 1e-10)
dim_B1 = rank_d2

beta1 = dim_Z1 - dim_B1

# build H1 basis as in w33_h1_fast
if dim_B1 > 0 and dim_Z1 > 0:
    B1_in_Z1 = Z1_basis.T @ d2
    U_B, s_B, _ = np.linalg.svd(B1_in_Z1, full_matrices=False)
    rank_B1_in_Z1 = np.sum(s_B > 1e-10)
    # orthonormal basis
    B1_orthonormal = U_B[:, :rank_B1_in_Z1]
    full_basis = np.hstack(
        [B1_orthonormal, np.random.randn(dim_Z1, dim_Z1 - rank_B1_in_Z1)]
    )
    Q_full, _ = np.linalg.qr(full_basis)
    H1_basis_in_Z1 = Q_full[:, rank_B1_in_Z1 : rank_B1_in_Z1 + beta1]
else:
    H1_basis_in_Z1 = np.eye(dim_Z1)[:, :beta1]

H1_basis = Z1_basis @ H1_basis_in_Z1 if H1_basis_in_Z1.size else np.zeros((n1, 0))

# load generators from JSON
cw_json = ROOT / "claude_workspace" / "data" / "w33_sage_incidence_h1.json"
with open(cw_json, "r", encoding="utf-8") as f:
    j = json.load(f)

generators = j.get("incidence", {}).get("generators", [])

# helper functions to build edge action
edge_index = {e: i for i, e in enumerate(edges)}


def gen_point_perm(gen_points):
    # JSON generators use 0-based points but we expect 0..39
    return [int(x) for x in gen_points]


# build edge action matrix


def edge_action_matrix(point_perm):
    M = np.zeros((n1, n1), dtype=float)
    for i, (a, b) in enumerate(edges):
        ua = point_perm[a]
        ub = point_perm[b]
        if ua < ub:
            j = edge_index[(ua, ub)]
            M[j, i] = 1
        else:
            j = edge_index[(ub, ua)]
            M[j, i] = -1
    return M


# compute H1 action and traces
h1_gen_matrices = []
summary = {"generators": []}
for gi, g in enumerate(generators):
    pts = g["points"]
    perm = gen_point_perm(pts)
    E = edge_action_matrix(perm)
    if H1_basis.size:
        E_h1 = E @ H1_basis
        H1_coords = np.linalg.lstsq(H1_basis, E_h1, rcond=None)[0]
    else:
        H1_coords = np.zeros((0, 0))
    tr = float(np.trace(H1_coords)) if H1_coords.size else 0.0
    det = float(np.linalg.det(H1_coords)) if H1_coords.size else 1.0
    summary["generators"].append(
        {"index": gi, "order": g.get("order"), "trace": tr, "det": det}
    )

# write output
out = {
    "dim_Z1": int(dim_Z1),
    "dim_B1": int(dim_B1),
    "beta1": int(beta1),
    "generators_summary": summary["generators"],
}
(ART / "opus_h1_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("Wrote artifacts/opus_h1_summary.json")
print(json.dumps(out, indent=2))
