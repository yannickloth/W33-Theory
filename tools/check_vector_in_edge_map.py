import json
from pathlib import Path

m = json.loads(Path('artifacts/edge_to_e8_root.json').read_text(encoding='utf-8'))
# normalize keys and values
vec_to_edge = {}
for k, v in m.items():
    # parse key string like "(a, b)"
    s = k.strip()
    if s.startswith('(') and s.endswith(')'):
        s2 = s[1:-1]
    else:
        s2 = s
    a_s, b_s = [x.strip() for x in s2.split(',')]
    a, b = int(a_s), int(b_s)
    vec_to_edge[tuple(v)] = (a, b)

# sample roots from minimal_holonomy file
minf = json.loads(Path('analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json').read_text(encoding='utf-8'))
ent = next(e for e in minf if e.get('edge_roots_present'))
roots = [tuple(r) for r in ent['edge_roots']]

for r in roots:
    found = vec_to_edge.get(r)
    neg = tuple(-x for x in r)
    found_neg = vec_to_edge.get(neg)
    print('root', r, 'found->', found, 'neg->', found_neg)

print('done')
