"""Search W33 graph for Fibonacci/Zeckendorf patterns in combinatorial counts.

The goal is to see whether the numbers 24, 72, 55, 13, etc. that appear in
RG and golden-structure analyses show up as natural combinatorial invariants
of the geometry.  The script computes a battery of counts and then expresses
the results in Fibonacci terms.
"""
from __future__ import annotations

import sys
from collections import deque

sys.path.append(".")
from e8_embedding_group_theoretic import build_w33


def fib_list(nmax: int) -> list[int]:
    a, b = 0, 1
    fibs = [0]
    while b <= nmax:
        fibs.append(b)
        a, b = b, a + b
    return fibs


def zeckendorf_rep(n: int, fibs: list[int]) -> list[int]:
    """Return indices of Fibonacci numbers summing to n (non-consecutive)."""
    if n == 0:
        return []
    rep = []
    # find largest fib <= n
    idx = max(i for i, f in enumerate(fibs) if f <= n)
    while n > 0:
        while fibs[idx] > n:
            idx -= 1
        rep.append(idx)
        n -= fibs[idx]
        idx -= 2
    return rep


def main():
    n, verts, adj, edges = build_w33()
    fibs = fib_list(1000)

    def is_fib(x):
        return x in fibs

    def fib_info(x):
        if is_fib(x):
            return f"F({fibs.index(x)})"
        return "+".join(f"F({i})" for i in zeckendorf_rep(x, fibs))

    stats = {}
    # basic
    stats['n_vertices'] = n
    stats['n_edges'] = len(edges)
    # degree
    stats['degree'] = len(adj[0]) if adj else 0
    # triangles per vertex
    tri_per_v = []
    for v in range(n):
        cnt = 0
        nbrs = set(adj[v])
        for i in nbrs:
            for j in nbrs:
                if j > i and j in adj[i]:
                    cnt += 1
        tri_per_v.append(cnt)
    stats['triangle_per_vertex'] = tri_per_v[0]
    # common neighbour counts (distance-2)
    dist2 = []
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
        dist2.append(sum(1 for d in dist if d == 2))
    stats['distance2'] = dist2[0]
    # edges among neighbours
    def edges_between(v):
        nbrs = set(adj[v])
        cnt = 0
        for i in nbrs:
            for j in adj[i]:
                if j in nbrs and j > i:
                    cnt += 1
        return cnt
    stats['edges_between_neighbours'] = edges_between(0)
    # total 4-cycles
    four = 0
    visited=set()
    for i,j in edges:
        for k in adj[j]:
            if k!=i and k in adj[i]:
                for l in adj[k]:
                    if l!=j and l in adj[i] and l!=i:
                        cycle = tuple(sorted([i,j,k,l]))
                        if cycle not in visited:
                            visited.add(cycle)
                            four += 1
    stats['4_cycles'] = four
    # print with fib info
    print("Computed statistics and Fibonacci/Zeckendorf patterns:")
    for k, v in stats.items():
        print(f"{k:>25}: {v:>5}   -> {fib_info(v)}")
    # check 72 decomposition
    print("\n72 Zeckendorf ->", fib_info(72))

if __name__ == '__main__':
    main()
