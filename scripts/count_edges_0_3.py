from e8_embedding_group_theoretic import build_w33

n, verts, adj, edges = build_w33()
edges0=[]
for (i,j) in edges:
    if (i<4 and j>=4) or (j<4 and i>=4):
        edges0.append((i,j))
print('edges with one endpoint in {0,1,2,3}:', len(edges0))
print(edges0)
