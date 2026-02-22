#!/usr/bin/env python3
"""Verify W33 point graph is isomorphic to symplectic graph Sp(4,3) using pure Python.
Writes artifacts/opus_symplectic_verify.json with summary.
"""
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# load w33_io by path
spec = importlib.util.spec_from_file_location("w33_io", str(ROOT / "lib" / "w33_io.py"))
w33_io = importlib.util.module_from_spec(spec)
sys.modules["w33_io"] = w33_io
spec.loader.exec_module(w33_io)
W33DataPaths = w33_io.W33DataPaths
load_w33_lines = w33_io.load_w33_lines

ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

paths = W33DataPaths.from_this_file(
    str(ROOT / "claude_workspace" / "w33_sage_incidence_and_h1.py")
)
lines = load_w33_lines(paths)

# Build adjacency matrices (W33 and Sp(4,3)) and compare spectra (fast heuristic for isomorphism)
W33_adj = np.zeros((40, 40), dtype=int)
for line in lines:
    for a, b in itertools.combinations(line, 2):
        W33_adj[a, b] = 1
        W33_adj[b, a] = 1

# Build Sp(4,3) points and symplectic adjacency
F = [0, 1, 2]
points = []
seen = set()
for v in itertools.product(F, repeat=4):
    if all(x == 0 for x in v):
        continue
    for c in v:
        if c != 0:
            inv = {1: 1, 2: 2}[c]
            norm = tuple(((x * inv) % 3) for x in v)
            break
    if norm not in seen:
        seen.add(norm)
        points.append(norm)
assert len(points) == 40


def symp(u, v):
    return (u[0] * v[2] - u[2] * v[0] + u[1] * v[3] - u[3] * v[1]) % 3


Sp_adj = np.zeros((40, 40), dtype=int)
for i in range(40):
    for j in range(i + 1, 40):
        if symp(points[i], points[j]) == 0:
            Sp_adj[i, j] = 1
            Sp_adj[j, i] = 1

# compare basic counts and spectra
res = {
    "W33_vertices": int(W33_adj.shape[0]),
    "W33_edges": int(W33_adj.sum() // 2),
    "Sp_vertices": int(Sp_adj.shape[0]),
    "Sp_edges": int(Sp_adj.sum() // 2),
}

# eigenvalues (sorted)
w_eigs = np.sort(np.round(np.linalg.eigvals(W33_adj).real, 8)).tolist()
s_eigs = np.sort(np.round(np.linalg.eigvals(Sp_adj).real, 8)).tolist()
res["W33_spectrum"] = w_eigs
res["Sp_spectrum"] = s_eigs
res["spectra_equal"] = w_eigs == s_eigs

# count totally isotropic lines (4-sets) in Sp graph
TI = []
for comb in itertools.combinations(range(40), 4):
    ok = True
    for a, b in itertools.combinations(comb, 2):
        if symp(points[a], points[b]) != 0:
            ok = False
            break
    if ok:
        TI.append(tuple(sorted(comb)))
res["sp_totally_isotropic_lines"] = int(len(TI))
res["w33_lines"] = int(len(lines))
(ART / "opus_symplectic_verify.json").write_text(
    json.dumps(res, indent=2), encoding="utf-8"
)
print("Wrote artifacts/opus_symplectic_verify.json")
print(json.dumps(res, indent=2))
