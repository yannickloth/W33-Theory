import json
adj = [list(map(int, l.split())) for l in open('W33_adjacency_matrix.txt').read().splitlines()]
edges = [(i,j) for i in range(len(adj)) for j in range(i+1,len(adj)) if adj[i][j]==1]
m = json.loads(open('artifacts/edge_to_e8_root.json').read())
absent = [e for e in edges if str(e) not in m and str(tuple(reversed(e))) not in m]
print('num_adj_edges', len(edges))
print('absent count', len(absent))
print('some absent', absent[:30])
print('some present keys', list(m.keys())[:10])
