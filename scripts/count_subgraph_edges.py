from e8_embedding_group_theoretic import build_w33
import numpy as np

n, verts, adj, edges = build_w33()
# union as before
basis = np.load('data/24_basis.npz')['arr_0']
union=set()
for i in range(basis.shape[1]):
    vec=basis[:,i]
    for k,v in enumerate(vec):
        if v!=0:
            union.add(edges[k])

# count edges with both endpoints in subset S
S=set(range(8))  # vertices 0-7
count=0
for e in union:
    if e[0] in S and e[1] in S:
        count+=1
print('edges inside 0-7', count)
# edges connecting 0-3 to 4-7
count2=0
for (i,j) in union:
    if i<4 and j<8 and j>=4 or j<4 and i<8 and i>=4:
        count2+=1
print('edges 0-3 <-> 4-7', count2)
# edges from 0-3 to [13,22,31]
T={13,22,31}
count3=0
for (i,j) in union:
    if (i<4 and j in T) or (j<4 and i in T):
        count3+=1
print('edges 0-3 <-> T', count3)
