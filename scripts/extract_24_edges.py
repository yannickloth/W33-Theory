"""Extract candidate 24-edge subgraph from automorphism #1410.

We choose the first six 4-cycles of the edge permutation (these were the
cycles touching vertices 0..3) which yield exactly 24 edges.  The script
prints the list and a few graph invariants so we can study the geometry.
"""
import sys
sys.path.append('.')
from e8_embedding_group_theoretic import build_w33
from tools.cycle_space_analysis import compute_automorphisms

n, verts, adj, edges = build_w33()
autos = compute_automorphisms(n, adj, limit=1411)
perm = autos[1410]

edge_dict = {e:i for i,e in enumerate(edges)}
perm_on_edges = {}
for k,(i,j) in enumerate(edges):
    ni=perm[i]; nj=perm[j]
    if ni>nj: ni,nj=nj,ni
    perm_on_edges[k] = edge_dict[(ni,nj)]

# compute cycles
visited=set(); cycles=[]
for i in range(len(edges)):
    if i in visited: continue
    cycle=[]; cur=i
    while cur not in visited:
        visited.add(cur)
        cycle.append(cur)
        cur = perm_on_edges[cur]
    if len(cycle)==4:
        cycles.append(cycle)

# choose first 6 cycles (arbitrary but they are the ones touching 0..3)
sel = cycles[:6]
sub_edges = []
for cyc in sel:
    for idx in cyc:
        sub_edges.append(edges[idx])

print('selected 6 cycles -> 24 edges:')
for e in sub_edges:
    print(e)

# compute vertex set and degree sequence
from collections import Counter
verts_used = [v for e in sub_edges for v in e]
vc = Counter(verts_used)
print('\nvertex degrees in subgraph:')
for v,c in sorted(vc.items()):
    print(v, c)

# adjacency representation
adj24 = {v:set() for v in set(verts_used)}
for i,j in sub_edges:
    adj24[i].add(j)
    adj24[j].add(i)
print('\nconnected components sizes:')
seen=set(); comps=[]
for v in adj24:
    if v in seen: continue
    stack=[v]; comp=[]
    while stack:
        x=stack.pop()
        if x in seen: continue
        seen.add(x); comp.append(x)
        for nb in adj24[x]:
            if nb not in seen: stack.append(nb)
    comps.append(comp)
print([len(c) for c in comps])

print('Done.')
