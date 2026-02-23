from e8_embedding_group_theoretic import build_w33
import sys
sys.path.append('.')
from tools.cycle_space_analysis import compute_automorphisms

n, verts, adj, edges = build_w33()
autos = compute_automorphisms(n, adj, limit=1411)
perm = autos[1410]
edge_dict={e:i for i,e in enumerate(edges)}
perm_on_edges={}
for k,(i,j) in enumerate(edges):
    ni=perm[i]; nj=perm[j]
    if ni>nj: ni,nj=nj,ni
    perm_on_edges[k]=edge_dict[(ni,nj)]

# gather cycles list
visited=set(); cycles=[]
for i in range(len(edges)):
    if i in visited: continue
    cycle=[]; cur=i
    while cur not in visited:
        visited.add(cur); cycle.append(cur); cur=perm_on_edges[cur]
    if len(cycle)==4: cycles.append(cycle)
# select first six cycles (from earlier output we know those indices?)
sel=cycles[:6]
union=set()
for cyc in sel:
    for idx in cyc:
        union.add(edges[idx])
print('selected edges count',len(union))
print(union)
print('vertices covered',sorted({v for e in union for v in e}))
