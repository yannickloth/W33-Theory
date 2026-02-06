"""Compute automorphism orbits for W33 using networkx GraphMatcher.
This enumerates all automorphisms (may be many) and accumulates vertex images to form orbits.
Writes checks/PART_CXI_aut_orbits.json
"""

import json
import os
from collections import defaultdict

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

ROOT = os.path.dirname(os.path.dirname(__file__))
ADJ_PATH = os.path.join(ROOT, "checks", "W33_adjacency_matrix.txt")
OUT_PATH = os.path.join(ROOT, "checks", "PART_CXI_aut_orbits.json")


def read_adj(path):
    mat = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = [int(x) for x in line.strip().split()]
            if row:
                mat.append(row)
    return mat


def main(max_iso=None):
    adj = read_adj(ADJ_PATH)
    n = len(adj)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j]:
                G.add_edge(i, j)

    gm = GraphMatcher(G, G)
    orbits = [set() for _ in range(n)]
    count = 0
    for mapping in gm.isomorphisms_iter():
        count += 1
        for i in range(n):
            orbits[i].add(mapping[i])
        if max_iso and count >= max_iso:
            break
    orbits = [sorted(list(s)) for s in orbits]
    # compress into orbit classes
    seen = set()
    classes = []
    for i, s in enumerate(orbits):
        tup = tuple(s)
        if i in seen:
            continue
        # find all vertices whose orbit set equals s (they are in same orbit)
        members = [j for j, ss in enumerate(orbits) if ss == s]
        for m in members:
            seen.add(m)
        classes.append(sorted(members))

    out = {
        "count_auts_enumerated": count,
        "orbits_by_vertex": orbits,
        "orbit_classes": classes,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(
        f"Enumerated {count} automorphisms (early stopped if limited). Found {len(classes)} orbit classes."
    )
    for c in classes:
        print(c)


if __name__ == "__main__":
    main()
