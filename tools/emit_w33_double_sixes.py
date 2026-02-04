#!/usr/bin/env python3
"""Enumerate all unordered double-sixes (disjoint K6 pairs with perfect matching) and write to artifacts.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

from tools.find_k6_double_sixes_w33_fast import bron_kerbosch_bounded
from tools.find_schlafli_embedding_in_w33 import compute_w33_lines, construct_w33_points


def main():
    pts = construct_w33_points()
    lines = compute_w33_lines(pts)
    n = len(lines)

    # build line-line disjointness graph
    G = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if set(lines[i]).isdisjoint(set(lines[j])):
                G[i].add(j)
                G[j].add(i)

    cliques = []
    bron_kerbosch_bounded(G, set(), set(range(n)), set(), 6, cliques)
    print("K6 cliques found:", len(cliques))

    double_sixes = []
    for i in range(len(cliques)):
        a = cliques[i]
        for b in cliques[i + 1 :]:
            if a & b:
                continue
            # bipartite matching
            B = nx.Graph()
            A_nodes = [("A", x) for x in a]
            B_nodes = [("B", y) for y in b]
            B.add_nodes_from(A_nodes)
            B.add_nodes_from(B_nodes)
            for x in a:
                for y in b:
                    if y in G[x]:
                        B.add_edge(("A", x), ("B", y))
            matching = nx.algorithms.bipartite.matching.hopcroft_karp_matching(
                B, top_nodes=A_nodes
            )
            pairs = [(u, v) for u, v in matching.items() if u[0] == "A"]
            if len(pairs) == 6:
                double_sixes.append({"A": sorted(list(a)), "B": sorted(list(b))})

    print("Unordered double-sixes found:", len(double_sixes))
    (ART / "w33_double_sixes_full.json").write_text(
        json.dumps({"double_sixes": double_sixes}, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "w33_double_sixes_full.json")


if __name__ == "__main__":
    main()
