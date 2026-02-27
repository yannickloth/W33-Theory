from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from w33_homology import build_w33

n, verts, adj, edges = build_w33()
neighbor_map = {}
for i in range(n):
    if 13 <= i < 40:
        neighbor_map[i] = [j for j in adj[i] if j < 13]
from collections import Counter
print('neighbor sizes', Counter(len(v) for v in neighbor_map.values()))
int_counts = Counter()
for i, j in edges:
    if i >= 13 and j >= 13:
        inter = set(neighbor_map[i]).intersection(neighbor_map[j])
        int_counts[len(inter)] += 1
print('edge intersections among affines', int_counts)
print('total edges', len(edges))
print('affine-infty edges', sum(1 for i,j in edges if (i>=13 and j<13) or (j>=13 and i<13)))
