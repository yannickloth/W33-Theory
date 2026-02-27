from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from w33_homology import build_w33

n, verts, adj, edges = build_w33()
inf = list(range(1,13))
triangles = []
for i in inf:
    for j in inf:
        if j<=i: continue
        if j not in adj[i]: continue
        for k in inf:
            if k<=j: continue
            if k in adj[i] and k in adj[j]:
                triangles.append((i,j,k))
print('triangles found', triangles)
