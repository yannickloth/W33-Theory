#!/usr/bin/env python3
import json

# load pocket geometry to build overlap statistics
geo = json.load(open('pocket_geometry.json'))
pockets = [tuple(p) for p in geo['pockets']]

edges4=[]
edges6=[]
from itertools import combinations
for i,j in combinations(range(len(pockets)),2):
    inter = set(pockets[i]) & set(pockets[j])
    if len(inter)==4:
        edges4.append((i,j))
    elif len(inter)==6:
        edges6.append((i,j))

graph={}
for u,v in edges4+edges6:
    graph.setdefault(u,[]).append(v)
    graph.setdefault(v,[]).append(u)

comp=0
seen=set()
for u in range(len(pockets)):
    if u in seen: continue
    comp+=1
    stack=[u]
    while stack:
        x=stack.pop()
        if x in seen: continue
        seen.add(x)
        for y in graph.get(x,[]):
            if y not in seen: stack.append(y)

solutions = 2**comp
pocket_glue = {
    'total_pockets': len(pockets),
    'edges_size4': len(edges4),
    'edges_size6': len(edges6),
    'components': comp,
    'glue_solutions': solutions,
}
with open('pocket_glue_summary.json','w') as f: json.dump(pocket_glue,f,indent=2)
print('wrote pocket_glue_summary.json', pocket_glue)

# orbit 480 summary from octonion stats
try:
    stats = json.load(open('octonion_rep_stats.json'))
    orbit = {
        'group_order': 645120,
        'stabilizer_size': stats.get('stabilizer_size'),
        'orbit_size': stats.get('orbit_size')
    }
    with open('orbit_480_summary.json','w') as f: json.dump(orbit,f,indent=2)
    print('wrote orbit_480_summary.json', orbit)
except FileNotFoundError:
    print('octonion_rep_stats.json not found, skipping orbit summary')
