import numpy as np
lines=[l.strip() for l in open('W33_adjacency_matrix.txt') if l.strip()]
adj=np.array([[int(x) for x in line.split()] for line in lines])
print('neighbors of 0', [i for i,v in enumerate(adj[0]) if v==1])
