from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from w33_homology import build_w33

n, verts, adj, edges = build_w33()
print('n', n)
print('type adj', type(adj))
print('adj[0]', adj[0])
print('len adj[0]', len(adj[0]))
print('edges[0]', edges[0])
