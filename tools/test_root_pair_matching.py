import json, pathlib
from itertools import combinations

ROOT=pathlib.Path()
bundle=ROOT/"TOE_duad_algebra_v06_20260227_bundle"/"TOE_duad_algebra_v05_20260227"
lines=json.loads((bundle/"W33_lines_40.json").read_text())["lines"]
pgpts=json.loads((bundle/"psp43_generators_on_points_40.json").read_text())["generators"]
pgpt_gens=[[int(x) for x in perm] for perm in pgpts]
edges=set()
for L in lines:
    for i in range(len(L)):
        for j in range(i+1,len(L)):
            a,b=L[i],L[j]
            edges.add((a,b) if a<b else (b,a))
edges=sorted(edges)

def point_to_edge(gens, edges):
    edge_index={e:i for i,e in enumerate(edges)}
    res=[]
    for pg in gens:
        perm=[]
        for a,b in edges:
            a2=pg[a]; b2=pg[b]
            if a2<b2:
                perm.append(edge_index[(a2,b2)])
            else:
                perm.append(edge_index[(b2,a2)])
        res.append(perm)
    return res


duad_edge_gens=point_to_edge(pgpt_gens, edges)

root_gens=json.loads((ROOT/"SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25"/"sp43_root_perms_fixed.json").read_text())
root_gens=[[int(x) for x in perm] for perm in root_gens]

from collections import deque

def closure_size(g1, g2):
    n1=len(g1[0]); n2=len(g2[0])
    seen={(tuple(range(n1)),tuple(range(n2))):True}
    q=deque([(list(range(n1)),list(range(n2)))])
    while q:
        p1,p2=q.popleft()
        for h1,h2 in zip(g1, g2):
            q1=[p1[h1[i]] for i in range(n1)]
            q2=[p2[h2[i]] for i in range(n2)]
            key=(tuple(q1),tuple(q2))
            if key not in seen:
                seen[key]=True
                q.append((q1,q2))
    return len(seen)

for comb in combinations(range(len(root_gens)), 2):
    sz=closure_size(duad_edge_gens, [root_gens[comb[0]], root_gens[comb[1]]])
    print(comb, sz)
