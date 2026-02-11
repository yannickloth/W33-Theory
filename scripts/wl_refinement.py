"""Weisfeiler-Lehman color refinement on W33 adjacency to get vertex color classes.
This provides a partition that's coarser than automorphism orbits but often useful.
Writes checks/PART_CXI_wl_colors.json and prints summary.
"""

import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(__file__))
ADJ_PATH = os.path.join(ROOT, "checks", "W33_adjacency_matrix.txt")
OUT_PATH = os.path.join(ROOT, "checks", "PART_CXI_wl_colors.json")


def read_adj(path):
    mat = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = [int(x) for x in line.strip().split()]
            if row:
                mat.append(row)
    return mat


def wl_refine(adj):
    n = len(adj)
    # initial colors: degree
    colors = [sum(row) for row in adj]
    changed = True
    iteration = 0
    while changed and iteration < 20:
        iteration += 1
        new_colors = [None] * n
        buckets = {}
        for v in range(n):
            neighbor_colors = sorted(colors[i] for i in range(n) if adj[v][i])
            key = (colors[v], tuple(neighbor_colors))
            # canonicalize
            if key not in buckets:
                buckets[key] = len(buckets)
            new_colors[v] = buckets[key]
        changed = any(new_colors[i] != colors[i] for i in range(n))
        colors = new_colors
    # group vertices by color
    classes = defaultdict(list)
    for i, c in enumerate(colors):
        classes[c].append(i)
    return dict(classes)


def main():
    adj = read_adj(ADJ_PATH)
    classes = wl_refine(adj)
    out = {str(k): v for k, v in classes.items()}
    from utils.json_safe import dump_json

    dump_json(out, OUT_PATH, indent=2)
    print(f"WL refinement produced {len(classes)} color classes")
    for k, v in classes.items():
        print(f" - color {k}: size {len(v)} -> {v}")


if __name__ == "__main__":
    main()
