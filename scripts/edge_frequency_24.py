from e8_embedding_group_theoretic import build_w33
import numpy as np

n, verts, adj, edges = build_w33()
basis = np.load('data/24_basis.npz')['arr_0']
freq = {e:0 for e in edges}
for i in range(basis.shape[1]):
    vec=basis[:,i]
    for k,v in enumerate(vec):
        if v!=0:
            freq[edges[k]] += 1
# sort edges by freq descending
sorted_edges = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
print('top 30 most frequent edges and counts:')
for e,c in sorted_edges[:30]:
    print(c, e)
