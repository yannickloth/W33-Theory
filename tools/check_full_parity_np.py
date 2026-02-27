from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from w33_homology import build_w33
import networkx as nx

n, verts, adj, edges = build_w33()
G = nx.Graph(); G.add_nodes_from(range(n))
for i in range(n):
    for j in adj[i]:
        if i<j: G.add_edge(i,j)
from networkx.algorithms.isomorphism import GraphMatcher
print('building automorphisms...')
gm=GraphMatcher(G,G)
autos=[]
for iso in gm.isomorphisms_iter():
    autos.append(tuple(iso[i] for i in range(n)))
NP=[p for p in autos if p[0]==0]
print('NP size',len(NP))
counts={'even':0,'odd':0}
for p in NP:
    inv=0
    for i in range(n):
        for j in range(i+1,n):
            if p[i]>p[j]: inv+=1
    counts['even' if inv%2==0 else 'odd']+=1
print('parity full',counts)
