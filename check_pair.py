import numpy as np
lines=[l.strip() for l in open('W33_adjacency_matrix.txt') if l.strip()]
adj=np.array([[int(x) for x in line.split()] for line in lines])
print('adj 10,25',adj[10,25])
print('adj 12,22',adj[12,22])
