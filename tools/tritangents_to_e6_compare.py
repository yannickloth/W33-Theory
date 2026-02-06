#!/usr/bin/env python3
"""Compute tritangent triangles from Schläfli graph, map to H indices via embedding, and compare to E6 triads.
Writes artifacts/tritangent_vs_e6.json with results.
"""
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# helper: build 27-line Schläfli adjacency


def build_27_lines():
    lines = []
    for i in range(1, 7):
        lines.append(("E", i))
    for i in range(1, 7):
        lines.append(("C", i))
    for i in range(1, 7):
        for j in range(i + 1, 7):
            lines.append(("L", i, j))
    return lines


def lines_intersect(L1, L2):
    if L1 == L2:
        return False

    t1, t2 = L1[0], L2[0]

    if t1 == "E" and t2 == "E":
        return False
    if t1 == "C" and t2 == "C":
        return False

    if t1 == "E" and t2 == "C":
        return L1[1] != L2[1]
    if t1 == "C" and t2 == "E":
        return L1[1] != L2[1]

    if t1 == "E" and t2 == "L":
        return L1[1] in L2[1:]
    if t1 == "L" and t2 == "E":
        return L2[1] in L1[1:]

    if t1 == "C" and t2 == "L":
        return L1[1] in L2[1:]
    if t1 == "L" and t2 == "C":
        return L2[1] in L1[1:]

    if t1 == "L" and t2 == "L":
        s1 = set(L1[1:])
        s2 = set(L2[1:])
        return len(s1 & s2) == 0

    return False


lines = build_27_lines()
# build adjacency matrix
adj = [[0] * 27 for _ in range(27)]
for i, j in combinations(range(27), 2):
    if lines_intersect(lines[i], lines[j]):
        adj[i][j] = adj[j][i] = 1

# find triangles in Schläfli graph
triangles = []
for i, j, k in combinations(range(27), 3):
    if adj[i][j] and adj[i][k] and adj[j][k]:
        triangles.append(tuple(sorted((i, j, k))))

# load embedding mapping (H idx -> Schläfli idx)
emb = json.loads(
    (ART / "h27_in_schlafli_intersection.json").read_text(encoding="utf-8")
)
if not emb.get("found_embedding"):
    raise RuntimeError("No embedding found")
map_h_to_s = {int(k): int(v) for k, v in emb["mapping"].items()}
# inverse map
map_s_to_h = {v: k for k, v in map_h_to_s.items()}

# map triangles to H indices
triangles_in_h = [
    tuple(sorted((map_s_to_h[s1], map_s_to_h[s2], map_s_to_h[s3])))
    for (s1, s2, s3) in triangles
]
triangles_in_h_set = set(triangles_in_h)

# load E6 triads (affine + fiber)
e6 = json.loads(
    (ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json").read_text(
        encoding="utf-8"
    )
)
affine_tris = [
    tuple(sorted(tri)) for item in e6["affine_u_lines"] for tri in item["triads"]
]
fiber_tris = [tuple(sorted(tri)) for tri in e6["fiber_triads_e6id"]]
all_e6_tris = set(tuple(sorted(t)) for t in affine_tris + fiber_tris)

results = {
    "triangle_count_schlafli": len(triangles),
    "triangle_count_h": len(triangles_in_h),
    "distinct_triangles_h": len(triangles_in_h_set),
    "e6_triads_count": len(all_e6_tris),
    "triangles_equal_e6": sorted([tuple(t) for t in triangles_in_h_set])
    == sorted([tuple(t) for t in all_e6_tris]),
    "triangles_in_h_sorted": sorted([tuple(t) for t in triangles_in_h_set]),
    "e6_triads_sorted": sorted([tuple(t) for t in all_e6_tris]),
}

(ART / "tritangent_vs_e6.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("Wrote artifacts/tritangent_vs_e6.json")
print(json.dumps(results, indent=2))
