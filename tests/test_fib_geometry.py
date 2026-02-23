import os, sys

# make sure scripts folder (contains e8_embedding_group_theoretic.py) is importable
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, scripts_dir)
from e8_embedding_group_theoretic import build_w33


def fib_list(nmax: int) -> list[int]:
    a, b = 0, 1
    fibs = [0]
    while b <= nmax:
        fibs.append(b)
        a, b = b, a + b
    return fibs


def zeckendorf(n: int, fibs: list[int]) -> list[int]:
    if n == 0:
        return []
    rep = []
    idx = max(i for i, f in enumerate(fibs) if f <= n)
    while n > 0:
        while fibs[idx] > n:
            idx -= 1
        rep.append(idx)
        n -= fibs[idx]
        idx -= 2
    return rep


def test_basic_counts_fibonacci():
    n, verts, adj, edges = build_w33()
    fibs = fib_list(1000)

    # compute invariants
    degree = len(adj[0])
    def count_tri(v):
        nbrs = set(adj[v])
        c = 0
        for i in nbrs:
            for j in nbrs:
                if j > i and j in adj[i]:
                    c += 1
        return c
    tri = count_tri(0)
    # distance-2 count
    from collections import deque
    dist = [-1] * n
    dist[0] = 0
    dq = deque([0])
    while dq:
        u = dq.popleft()
        for w in adj[u]:
            if dist[w] == -1:
                dist[w] = dist[u] + 1
                dq.append(w)
    d2 = sum(1 for d in dist if d == 2)
    # four-cycles
    four = 0
    visited = set()
    for i, j in edges:
        for k in adj[j]:
            if k != i and k in adj[i]:
                for l in adj[k]:
                    if l != j and l in adj[i] and l != i:
                        cycle = tuple(sorted((i, j, k, l)))
                        if cycle not in visited:
                            visited.add(cycle)
                            four += 1

    # verify Zeckendorf representation of each is unique and not use consecutive fibs
    for val in [n, len(edges), degree, tri, d2, four]:
        rep = zeckendorf(val, fibs)
        # ensure sum matches
        assert sum(fibs[i] for i in rep) == val
        # ensure non-consecutive indices
        for a, b in zip(rep, rep[1:]):
            assert b <= a - 2

    # 72 itself decomposes as expected
    rep72 = zeckendorf(72, fibs)
    assert rep72 == [10, 7, 4, 2]
