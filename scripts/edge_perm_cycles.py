import sys
sys.path.append('.')
from e8_embedding_group_theoretic import build_w33
from tools.cycle_space_analysis import compute_automorphisms

n, verts, adj, edges = build_w33()
autos = compute_automorphisms(n, adj, limit=1411)
perm = autos[1410]

# build edge permutation dict: key edge index -> new index (with orientation)
edge_dict = {e:i for i,e in enumerate(edges)}
perm_on_edges = {}
for k,(i,j) in enumerate(edges):
    ni = perm[i]
    nj = perm[j]
    sign=1
    if ni>nj:
        ni,nj=nj,ni
        sign=-1
    new_idx = edge_dict.get((ni,nj))
    perm_on_edges[k] = new_idx

# find cycles in this permutation
visited=set()
cycles=[]
for i in range(len(edges)):
    if i in visited: continue
    cycle=[]
    cur=i
    while cur not in visited:
        visited.add(cur)
        cycle.append(cur)
        cur = perm_on_edges[cur]
    if len(cycle)>1:
        cycles.append(cycle)

print('number of edge cycles', len(cycles))
print('cycle lengths distribution:')
from collections import Counter
cnt=Counter(len(c) for c in cycles)
print(cnt)
print('sample cycles lengths and first few elements:')
for c in cycles[:10]:
    print(len(c), c[:5])
