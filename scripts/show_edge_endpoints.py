# Quick helper to show W33 edge endpoints and triangles for specific edge indices
import json

adj = []
with open("W33_adjacency_matrix.txt") as f:
    for line in f:
        row = [int(x) for x in line.strip().split()]
        adj.append(row)

n = len(adj)
edges = []
for i in range(n):
    for j in range(i + 1, n):
        if adj[i][j] == 1:
            edges.append((i, j))

print("Total edges:", len(edges))
print("Edge 37:", edges[37])
print("Edge 38:", edges[38])

# triangles
triangles = []
for i in range(n):
    for j in range(i + 1, n):
        for k in range(j + 1, n):
            if adj[i][j] and adj[j][k] and adj[i][k]:
                triangles.append((i, j, k))

print("Number of triangles:", len(triangles))
for t in triangles:
    if edges[37][0] in t and edges[37][1] in t:
        print("Triangle with edge 37:", t)
    if edges[38][0] in t and edges[38][1] in t:
        print("Triangle with edge 38:", t)

# Also show if edges 37 and 38 are adjacent
print("Edge 37 adjacent to edge 38?", len(set(edges[37]) & set(edges[38])) > 0)

# Show which vertices are shared if any
print("Common vertices:", set(edges[37]) & set(edges[38]))

# Print adjacencies of vertices
print(
    "Neighbors of vertex",
    edges[37][0],
    ":",
    [i for i in range(n) if adj[edges[37][0]][i]],
)
print(
    "Neighbors of vertex",
    edges[37][1],
    ":",
    [i for i in range(n) if adj[edges[37][1]][i]],
)
print(
    "Neighbors of vertex",
    edges[38][0],
    ":",
    [i for i in range(n) if adj[edges[38][0]][i]],
)
print(
    "Neighbors of vertex",
    edges[38][1],
    ":",
    [i for i in range(n) if adj[edges[38][1]][i]],
)
