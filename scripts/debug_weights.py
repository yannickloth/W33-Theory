import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.w33_algebra_qca import compute_chevalley_invariants, compute_simple_root_weights, build_w33_geometry

inv = compute_chevalley_invariants()
simples = inv['simple_edges']
pts, edges, adj, triangles, J = build_w33_geometry()
print('simple edges list:')
for s in simples:
    e = tuple(s['edge'])
    in_map = e in {ed for ed in edges}
    print(s['i'], e, s.get('grade'), 'in_map?', in_map)

# print edges that involve any simple-edge vertices
def find_edges_with(v):
    return [e for e in edges if v in e]
print('\nChecking membership by raw lookup:')
for s in simples:
    e = tuple(s['edge'])
    print('simple', s['i'], 'edge', e, 'contains vertices:', [find_edges_with(v) for v in e])

weights = compute_simple_root_weights(pts, edges, simples)
print('weights returned:')
for w in weights:
    print(w)
