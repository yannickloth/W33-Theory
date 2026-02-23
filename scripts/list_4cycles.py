from e8_embedding_group_theoretic import build_w33
import sys
sys.path.append('.')
from tools.cycle_space_analysis import compute_automorphisms

n, verts, adj, edges = build_w33()
autos = compute_automorphisms(n, adj, limit=1411)
perm = autos[1410]
# build edge permutation
edge_dict={e:i for i,e in enumerate(edges)}
perm_on_edges={}
for k,(i,j) in enumerate(edges):
    ni=perm[i]; nj=perm[j]
    if ni>nj: ni,nj=nj,ni
    perm_on_edges[k]=edge_dict[(ni,nj)]

cycles=[]
visited=set()
for i in range(len(edges)):
    if i in visited: continue
    cycle=[]
    cur=i
    while cur not in visited:
        visited.add(cur)
        cycle.append(cur)
        cur=perm_on_edges[cur]
    if len(cycle)==4:
        cycles.append(cycle)

# now filter cycles that touch vertex<4
selected=[]
for cyc in cycles:
    vs=set()
    for idx in cyc:
        vs.update(edges[idx])
    if any(v<4 for v in vs):
        selected.append(cyc)

print('number of 4-cycles touching vertex<4', len(selected))
print('first few cycles with their edges', [(cyc, [edges[i] for i in cyc]) for cyc in selected[:10]])
