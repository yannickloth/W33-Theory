#!/usr/bin/env python3
import networkx as nx
import sys
from pathlib import Path

# ensure scripts dir on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from w33_homology import build_w33

n, verts, adj, edges = build_w33()
G = nx.Graph()
G.add_nodes_from(range(n))
for i in range(n):
    for j in adj[i]:
        if i < j:
            G.add_edge(i, j)

print('computing automorphisms...')
gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
autos = []
for iso in gm.isomorphisms_iter():
    autos.append(tuple(iso[i] for i in range(n)))
print('total auts:', len(autos))
P = [p for p in autos if p[0] == 0]
print('stabilizer size:', len(P))
parities = [(sum(1 for i in range(n) if p[i] < i) % 2) for p in P]
even = sum(1 for par in parities if par == 0)
odd = len(P) - even
print('even/odd in stabilizer:', even, odd)
