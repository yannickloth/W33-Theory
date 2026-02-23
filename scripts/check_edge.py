import sys
from pathlib import Path
# allow importing from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))
# also include scripts directory itself
sys.path.insert(0, str(Path(__file__).parent))
from w33_algebra_qca import build_w33_geometry

pts, edges, adj, triangles, J = build_w33_geometry()
print('number of edges', len(edges))

# load e8_root_to_edge mapping and check how many map to actual edges
import json
root_to_edge = json.loads(Path('artifacts/e8_root_to_edge.json').read_text(encoding='utf-8'))
count_adj = 0
for k,v in root_to_edge.items():
    u,vv = int(v[0]), int(v[1])
    if (u,vv) in edges or (vv,u) in edges:
        count_adj += 1
print(f'adjacent root-edge pairs: {count_adj}/240')

for pair in [(13,15),(9,33),(5,39)]:
    print(pair, 'in edges?', pair in edges or (pair[1],pair[0]) in edges,
          'J=', J(pts[pair[0]], pts[pair[1]]))
