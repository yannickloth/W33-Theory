from e8_embedding_group_theoretic import build_w33
import numpy as np

n, verts, adj, edges = build_w33()
# load basis and compute union of edges
basis = np.load('data/24_basis.npz')['arr_0']
union=set()
for i in range(basis.shape[1]):
    vec=basis[:,i]
    for k,v in enumerate(vec):
        if v!=0:
            union.add(edges[k])
counts={i:0 for i in range(n)}
for (i,j) in union:
    counts[i]+=1
    counts[j]+=1
print('total union edges', len(union))
print('vertex frequencies in union (top 12):')
for v,c in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:12]:
    print(v, c)
print('vertices with >4 occurrences:', [v for v,c in counts.items() if c>4])
