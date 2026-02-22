#!/usr/bin/env python3
"""
Classify neighbour graphs in the W(3,3) point graph.

In the point graph of the generalised quadrangle W(3,3), each vertex has 12
neighbours.  The subgraph induced on those 12 neighbours can take several
forms: a 12‑cycle, a 9‑cycle plus a triangle, two 6‑cycles, a 6‑cycle plus two
triangles, or four disjoint triangles.  In his classification of the 28
strongly regular graphs with parameters (40,12,2,4), Spence identified one
graph where every neighbour graph is triangle‑free; all others contain
triangles.  This script builds W(3,3) and determines the type of each
neighbour graph.

Usage:

    python3 w33_neighbor_graph_classification.py

It prints a dictionary of neighbour‑graph types and how many vertices have
each type.
"""

from __future__ import annotations

import collections
import itertools
from typing import List, Tuple


def omega(x: Tuple[int, int, int, int], y: Tuple[int, int, int, int]) -> int:
    return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3


def construct_points() -> List[Tuple[int, int, int, int]]:
    """Construct the 40 projective points of F3^4."""
    F3 = [0, 1, 2]
    points = []
    seen = set()
    for vec in itertools.product(F3, repeat=4):
        if not any(vec):
            continue
        v = list(vec)
        for i in range(4):
            if v[i] != 0:
                inv = 1 if v[i] == 1 else 2
                v = [(x * inv) % 3 for x in v]
                break
        t = tuple(v)
        if t not in seen:
            seen.add(t)
            points.append(t)
    return points


def build_adjacency(points: List[Tuple[int, int, int, int]]) -> List[List[int]]:
    """Return the adjacency matrix (as list of lists) for the W(3,3) point graph."""
    n = len(points)
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if omega(points[i], points[j]) == 0:
                adj[i][j] = adj[j][i] = 1
    return adj


def classify_component(size: int, edges: int) -> str:
    """Classify a connected component by its size and edge count."""
    # For neighbour graphs in W33, components can only be cycles or triangles.
    if size == 3 and edges == 3:
        return "triangle"
    if edges == size:
        return "cycle"
    return "other"


def classify_neighbour_graph(neigh_adj: List[List[int]]) -> str:
    """Classify the induced subgraph on 12 neighbours of a vertex."""
    m = len(neigh_adj)
    visited = [False] * m
    component_sizes = []
    component_types = []
    for i in range(m):
        if not visited[i]:
            stack = [i]
            visited[i] = True
            comp = []
            while stack:
                v = stack.pop()
                comp.append(v)
                for u in neigh_adj[v]:
                    if not visited[u]:
                        visited[u] = True
                        stack.append(u)
            size = len(comp)
            # count edges inside this component
            edges = 0
            for v in comp:
                for u in neigh_adj[v]:
                    if u > v and u in comp:
                        edges += 1
            component_sizes.append(size)
            component_types.append(classify_component(size, edges))
    component_sizes.sort()
    # Determine global pattern
    if component_sizes == [12] and component_types == ["cycle"]:
        return "12-cycle"
    if component_sizes == [3, 9] and component_types.count("triangle") == 1:
        return "9+3"
    if component_sizes == [6, 6] and component_types == ["cycle", "cycle"]:
        return "6+6"
    if component_sizes == [3, 3, 6] and component_types.count("triangle") == 2:
        return "6+3+3"
    if component_sizes == [3, 3, 3, 3] and component_types == ["triangle"] * 4:
        return "3+3+3+3"
    return "other"


def main() -> None:
    points = construct_points()
    adj = build_adjacency(points)
    n = len(points)
    type_counts = collections.Counter()
    for v in range(n):
        # list of neighbours of v
        neighbours = [i for i, val in enumerate(adj[v]) if val == 1]
        # build adjacency list for the induced neighbour graph
        index_map = {p: idx for idx, p in enumerate(neighbours)}
        neigh_adj = [[] for _ in range(len(neighbours))]
        for a in neighbours:
            for b in neighbours:
                if adj[a][b]:
                    neigh_adj[index_map[a]].append(index_map[b])
        gtype = classify_neighbour_graph(neigh_adj)
        type_counts[gtype] += 1
    print("Neighbour graph types in W(3,3):")
    for t, count in type_counts.items():
        print(f"  {t}: {count}")


if __name__ == "__main__":
    main()
