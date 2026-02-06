#!/usr/bin/env python3
"""Attempt to find a permutation P on 27 labels mapping triangles_in_h_set -> all_e6_tris.
If found, write mapping to artifacts/triad_label_permutation.json
"""
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

data = json.loads((ART / "tritangent_vs_e6.json").read_text(encoding="utf-8"))
triangles_h = [tuple(t) for t in data["triangles_in_h_sorted"]]
e6_tris = [tuple(t) for t in data["e6_triads_sorted"]]

tri_h_set = set(triangles_h)
e6_set = set(e6_tris)

n = 27
# compute triangle counts per vertex
tri_count_h = [0] * n
tri_count_e6 = [0] * n
for t in triangles_h:
    for v in t:
        tri_count_h[v] += 1
for t in e6_tris:
    for v in t:
        tri_count_e6[v] += 1

# candidate mapping: vertices in h can only map to e6 vertices with same tri count
candidates = {
    i: [j for j in range(n) if tri_count_e6[j] == tri_count_h[i]] for i in range(n)
}

# order vertices by fewest candidates
order = sorted(range(n), key=lambda x: len(candidates[x]))

# helper sets for fast membership
E6_tris_set = set(tuple(sorted(t)) for t in e6_tris)

mapping = {}
used = [False] * n

# backtracking
found = None


def consistent_partial(u, v, mapping):
    # check that for any triangle in h involving u and with other vertices mapped,
    # its mapped image is present in E6_tris_set
    for tri in triangles_h:
        if u in tri:
            other = [x for x in tri if x != u]
            # if both others are mapped, check
            if other[0] in mapping and other[1] in mapping:
                mapped_tri = tuple(sorted((v, mapping[other[0]], mapping[other[1]])))
                if mapped_tri not in E6_tris_set:
                    return False
    return True


def dfs(idx=0):
    global found
    if idx == n:
        found = dict(mapping)
        return True
    u = order[idx]
    for v in candidates[u]:
        if used[v]:
            continue
        if not consistent_partial(u, v, mapping):
            continue
        mapping[u] = v
        used[v] = True
        if dfs(idx + 1):
            return True
        used[v] = False
        del mapping[u]
    return False


ok = dfs()
if ok and found is not None:
    out = {"mapping": {str(k): int(v) for k, v in found.items()}}
    (ART / "triad_label_permutation.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Found mapping! Wrote artifacts/triad_label_permutation.json")
else:
    print("No mapping found under current constraints")

print("Tri counts h (unique counts):", sorted(set(tri_count_h)))
print("Tri counts e6 (unique counts):", sorted(set(tri_count_e6)))
