"""Utility to search for natural 24/72 counts in W33 geometry.

Runs through a variety of combinatorial statistics on the W33 graph and
reports any numbers equal to 24, 72 or other key values.  This can help
identify the geometric origin of the surprising RG requirement that
m_t/m_b ≈ 72 at the GUT scale.
"""
from __future__ import annotations

import sys
from collections import defaultdict, deque

# ensure scripts directory on path so we can import build_w33
sys.path.append(".")
from e8_embedding_group_theoretic import build_w33


def main():
    n, verts, adj, edges = build_w33()
    stats = defaultdict(list)

    # basic counts
    stats['n_vertices'].append(n)
    stats['n_edges'].append(len(edges))

    # degree distribution
    deg = [len(adj[i]) for i in range(n)]
    stats['degrees'] = deg

    # triangles per vertex
    for v in range(n):
        nbrs = set(adj[v])
        count = 0
        for i in nbrs:
            for j in nbrs:
                if j > i and j in adj[i]:
                    count += 1
        stats['triangles_per_vertex'].append(count)

    # distance-2 counts
    for v in range(n):
        dist = [-1] * n
        dist[v] = 0
        dq = deque([v])
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                if dist[w] == -1:
                    dist[w] = dist[u] + 1
                    dq.append(w)
        stats['distance2_count'].append(sum(1 for x in dist if x == 2))

    # edges among neighbours
    for v in range(n):
        nbrs = set(adj[v])
        cnt = 0
        for i in nbrs:
            for j in adj[i]:
                if j in nbrs and j > i:
                    cnt += 1
        stats['edges_between_neighbours'].append(cnt)

    # report any stats equal to 24 or 72
    print("Looking for 24/72 in various counts")
    for key, vals in stats.items():
        unique = set(vals)
        if 24 in unique or 72 in unique:
            print(f"{key}: contains {unique & {24,72}} (values {sorted(unique)})")

    print("full stats (some keys truncated):")
    for key, vals in stats.items():
        if isinstance(vals, list) and len(vals) > 1:
            print(f"{key}: [{', '.join(str(x) for x in vals[:5])}...] (len {len(vals)})")
        else:
            print(f"{key}: {vals}")


if __name__ == '__main__':
    main()
