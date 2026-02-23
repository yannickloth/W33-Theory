"""Compute stabilizer sizes of edges under Aut(W33).

The automorphism group of W33 (Sp(4,3)) has order 51840.  By transitivity the
stabilizer of any fixed edge has order 51840/240 = 216.  This script verifies the
claim and prints a frequency table.
"""

import json
from itertools import product
import networkx as nx


def build_W33():
    def omega(v, w):
        return (v[0] * w[1] - v[1] * w[0] + v[2] * w[3] - v[3] * w[2]) % 3

    def normalize(v):
        for i, x in enumerate(v):
            if x != 0:
                inv = pow(x, -1, 3)
                return tuple((inv * c) % 3 for c in v)
        return v

    points = [p for p in product(range(3), repeat=4) if p != (0, 0, 0, 0)]
    vertices = list({normalize(p) for p in points})
    edges = []
    for i, v in enumerate(vertices):
        for j, w in enumerate(vertices):
            if i < j and omega(v, w) == 0:
                edges.append((i, j))
    return vertices, edges


def edge_perm(perm, edge, edges):
    i, j = edge
    ni = perm[i]
    nj = perm[j]
    if ni > nj:
        ni, nj = nj, ni
    return edges.index((ni, nj))


def main():
    vertices, edges = build_W33()
    G = nx.Graph(); G.add_nodes_from(range(len(vertices))); G.add_edges_from(edges)
    matcher = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = list(matcher.isomorphisms_iter())
    print(f"total automorphisms: {len(autos)}")

    # compute stabilizer sizes
    counts = [0] * len(edges)
    for perm in autos:
        for e_idx, edge in enumerate(edges):
            if edge_perm(perm, edge, edges) == e_idx:
                counts[e_idx] += 1

    freq = {}
    for c in counts:
        freq[c] = freq.get(c, 0) + 1
    print("stabilizer size frequency:")
    for size, num in sorted(freq.items()):
        print(f"  {size}: {num} edges")

    # expected stabilizer size
    expected = len(autos) // len(edges)
    print(f"expected stabilizer size = {expected}")

if __name__ == '__main__':
    main()
