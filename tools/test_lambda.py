from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from w33_homology import build_w33
import json
import numpy as np

n, verts, adj, edges = build_w33()
# load PG coords
pts=json.loads((Path('PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01')/'PG33_points.json').read_text())
vecs=[np.array(p,dtype=int) for p in pts]
J = np.array([[0,0,0,1],[0,0,1,0],[0,2,0,0],[2,0,0,0]],dtype=int)

def compute_lambda(p):
    lamb=None
    for i in range(n):
        for j in range(i+1,n):
            lhs=int((vecs[p[i]]@J@vecs[p[j]])%3)
            rhs=int((vecs[i]@J@vecs[j])%3)
            if rhs==0:
                if lhs!=0: return None
                continue
            # want lhs == lambda*rhs mod3
            for lam in (1,2):
                if lhs==(lam*rhs)%3:
                    chosen=lam
                    break
            else:
                return None
            if lamb is None:
                lamb=chosen
            elif lamb!=chosen:
                return None
    return lamb

# compute automorphisms using networkx
import networkx as nx
G=nx.Graph(); G.add_nodes_from(range(n))
for i in range(n):
    for j in adj[i]:
        if i<j: G.add_edge(i,j)
gm=nx.algorithms.isomorphism.GraphMatcher(G,G)
autos=[]
for iso in gm.isomorphisms_iter():
    autos.append(tuple(iso[i] for i in range(n)))
NP=[p for p in autos if p[0]==0]
counts={1:0,2:0,None:0}
for p in NP[:20]:
    lam=compute_lambda(p)
    counts[lam]+=1
print('sample counts',counts)
# count all
counts_all={1:0,2:0,None:0}
for p in NP:
    lam=compute_lambda(p)
    counts_all[lam]+=1
print('all counts',counts_all)
