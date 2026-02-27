from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from w33_homology import build_w33
import networkx as nx

n, verts, adj, edges = build_w33()
# compute automorphisms
G = nx.Graph(); G.add_nodes_from(range(n))
for i in range(n):
    for j in adj[i]:
        if i<j: G.add_edge(i,j)
from networkx.algorithms.isomorphism import GraphMatcher

print('computing autos')
gm = GraphMatcher(G,G)
autos = []
for iso in gm.isomorphisms_iter():
    autos.append(tuple(iso[i] for i in range(n)))
NP=[p for p in autos if p[0]==0]
print('NP size',len(NP))
neighbors0 = adj[0]
print('neighbors of 0',neighbors0)
from collections import Counter
counts = Counter()
for p in NP:
    perm = [p[i] for i in neighbors0]
    # compute parity
    inv = 0
    for i in range(len(perm)):
        for j in range(i+1,len(perm)):
            if perm[i] > perm[j]: inv += 1
    counts[inv%2]+=1
print('parity counts on neighbor set',counts)
