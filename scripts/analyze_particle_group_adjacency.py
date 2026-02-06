"""Analyze adjacency between vertex groups defined in PART_CXI_particle_map.json
Reads:
 - checks/W33_adjacency_matrix.txt (40x40 whitespace-separated adjacency)
 - PART_CXI_particle_map.json (vertex ranges like "V1-V16")

Produces a JSON summary checks/PART_CXI_group_adjacency.json and prints a concise report.
"""

import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(__file__))
ADJ_PATH = os.path.join(ROOT, "checks", "W33_adjacency_matrix.txt")
PMAP_PATH = os.path.join(ROOT, "PART_CXI_particle_map.json")
OUT_PATH = os.path.join(ROOT, "checks", "PART_CXI_group_adjacency.json")


def parse_vertex_range(s):
    s = s.strip()
    # accept forms like 'V1-V16', 'V27' or just '1-16' etc.
    if s.startswith("V") and "-" not in s:
        s = s[1:]
    if "-" in s:
        a, b = s.split("-")
        if a.startswith("V"):
            a = a[1:]
        if b.startswith("V"):
            b = b[1:]
        return list(range(int(a) - 1, int(b)))
    else:
        if s.startswith("V"):
            s = s[1:]
        return [int(s) - 1]


def read_adj(path):
    mat = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = [int(x) for x in line.strip().split()]
            if row:
                mat.append(row)
    return mat


def main():
    pm = json.load(open(PMAP_PATH))
    vertex_map = pm.get("vertex_map", {})
    # Build ordered groups
    ordered_groups = ["fermions", "exotics", "e6_singlet", "gauge", "dark_matter"]
    groups = {}
    for g in ordered_groups:
        val = vertex_map.get(g)
        if val is None:
            groups[g] = []
        elif isinstance(val, str):
            # could be "V1-V16"
            if "," in val:
                parts = [p.strip() for p in val.split(",")]
                idxs = []
                for p in parts:
                    idxs.extend(parse_vertex_range(p))
            else:
                idxs = parse_vertex_range(val)
            groups[g] = idxs
        elif isinstance(val, list):
            idxs = []
            for p in val:
                if isinstance(p, str):
                    idxs.extend(parse_vertex_range(p))
                else:
                    idxs.append(int(p))
            groups[g] = idxs
        else:
            groups[g] = []

    adj = read_adj(ADJ_PATH)
    n = len(adj)
    assert n == 40

    # For each vertex compute number of neighbors in each group
    per_vertex = {}
    for v in range(n):
        neigh = adj[v]
        counts = {}
        for g, idxs in groups.items():
            counts[g] = sum(neigh[i] for i in idxs)
        per_vertex[f"V{v+1}"] = {k: int(vv) for k, vv in counts.items()}

    # Group summaries
    group_stats = {}
    for g, idxs in groups.items():
        rows = [per_vertex[f"V{i+1}"] for i in idxs]
        # For each target group, collect counts
        tgt_stats = {}
        for tgt in ordered_groups:
            vals = [r[tgt] for r in rows]
            if vals:
                import statistics

                tgt_stats[tgt] = {
                    "mean": statistics.mean(vals),
                    "stdev": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                    "min": min(vals),
                    "max": max(vals),
                    "counts": vals,
                }
            else:
                tgt_stats[tgt] = {
                    "mean": 0.0,
                    "stdev": 0.0,
                    "min": 0,
                    "max": 0,
                    "counts": [],
                }
        group_stats[g] = tgt_stats

    # Total edges between groups (undirected counted once)
    total_edges_between = defaultdict(int)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j]:
                # find groups
                gi = None
                gj = None
                for g, idxs in groups.items():
                    if i in idxs:
                        gi = g
                    if j in idxs:
                        gj = g
                if gi is None or gj is None:
                    continue
                key = tuple(sorted((gi, gj)))
                total_edges_between[key] += 1

    # compute normalized neighbor vectors (fraction of 12 neighbors by group)
    vecs = {}
    for v in range(n):
        p = per_vertex[f"V{v+1}"]
        vec = [p[g] / 12.0 for g in ordered_groups]
        vecs[f"V{v+1}"] = vec

    import math

    def dist(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    # within-group average pairwise distances
    within_group_dist = {}
    for g, idxs in groups.items():
        pairs = []
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                vi = f"V{idxs[i] + 1}"
                vj = f"V{idxs[j] + 1}"
                pairs.append(dist(vecs[vi], vecs[vj]))
        within_group_dist[g] = sum(pairs) / len(pairs) if pairs else 0.0

    between_group_dist = {}
    group_keys = list(groups.keys())
    for i in range(len(group_keys)):
        for j in range(i + 1, len(group_keys)):
            g1 = group_keys[i]
            g2 = group_keys[j]
            idxs1 = groups[g1]
            idxs2 = groups[g2]
            pairs = []
            for a in idxs1:
                for b in idxs2:
                    va = f"V{a + 1}"
                    vb = f"V{b + 1}"
                    pairs.append(dist(vecs[va], vecs[vb]))
            between_group_dist[f"{g1}-{g2}"] = sum(pairs) / len(pairs) if pairs else 0.0

    out = {
        "n_vertices": n,
        "groups": {g: [int(i) for i in idxs] for g, idxs in groups.items()},
        "per_vertex_neighbor_counts": per_vertex,
        "group_stats": group_stats,
        "total_edges_between_groups": {
            "-".join(k): int(v) for k, v in total_edges_between.items()
        },
        "within_group_distance": within_group_dist,
        "between_group_distance": between_group_dist,
    }

    # Write JSON
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    # Print a concise summary
    print("Group adjacency summary:")
    for g in ordered_groups:
        stats = group_stats[g]
        row = [f"{g}->{tgt}:{stats[tgt]['mean']:.2f}" for tgt in ordered_groups]
        print(" - ", ", ".join(row))
    print("Total edges between groups:")
    for k, v in out["total_edges_between_groups"].items():
        print(f" - {k}: {v}")
    print("\nWithin-group average normalized distances:")
    for k, v in within_group_dist.items():
        print(f" - {k}: {v:.4f}")
    print("\nSelected between-group distances (gauge vs others):")
    for other in ordered_groups:
        if other == "gauge":
            continue
        key = (
            f"gauge-{other}"
            if f"gauge-{other}" in between_group_dist
            else f"{other}-gauge"
        )
        val = between_group_dist.get(key)
        print(f" - gauge vs {other}: {val:.4f}")


if __name__ == "__main__":
    main()
