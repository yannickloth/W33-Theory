#!/usr/bin/env python3
import json
from itertools import combinations

data=json.load(open('unrestricted_solutions.json'))
solutions=data['solutions']
# compute pairs same as enumeration
p0 = {5:10,10:5,6:9,9:6,7:12,12:7,8:11,11:8}
p1 = {1:6,6:1,2:5,5:2,3:8,8:3,4:7,7:4}
p2 = {5:9,9:5,6:10,10:6,7:11,11:7,8:12,12:8}
p3 = {5:8,8:5,6:7,7:6,9:12,12:9,10:11,11:10}
for perm in (p0,p1,p2,p3):
    for e in range(1,13): perm.setdefault(e,e)
P=[]
for perm in (p0,p1,p2,p3): P.append([0]+[perm[i] for i in range(1,13)])
allP={tuple(arr) for arr in P}
changed=True
while changed:
    changed=False
    for a in list(allP):
        for b in P:
            comp=tuple(a[b[i]] for i in range(13))
            if comp not in allP:
                allP.add(comp); changed=True
subs=list(combinations(range(1,13),3))
line_orbits=[]
seen=set()
for s in subs:
    if s in seen: continue
    orb=set(); stack=[s]
    while stack:
        cur=stack.pop()
        if cur in orb: continue
        orb.add(cur); seen.add(cur)
        for perm in allP:
            new=tuple(sorted(perm[i] for i in cur))
            if new not in orb: stack.append(new)
    line_orbits.append(sorted(orb))
candidate_lines=[orb for orb in line_orbits if len(orb)==16 and all(sum(e in tri for tri in orb)==4 for e in range(1,13))]
face_triples=candidate_lines[0]
pairs=[(e,face_idx) for face_idx,triple in enumerate(face_triples) for e in triple]
edge_of=[pairs[i][0] for i in range(48)]

indices=[170,224,239,296]
for idx in indices:
    sol=solutions[idx]
    perm_e=[None]*12
    for e in range(1,13):
        f=[i for i,ee in enumerate(edge_of) if ee==e][0]
        perm_e[e-1]=edge_of[sol[0][f]]
    pairs_list=list(combinations(range(1,13),2))
    seen=set(); orbs=[]
    for p in pairs_list:
        if p in seen: continue
        orb=set(); stack=[p]
        while stack:
            q=stack.pop()
            if q in orb: continue
            orb.add(q); seen.add(q)
            a,b=q
            new=(perm_e[a-1],perm_e[b-1])
            if new not in orb: stack.append(new)
        orbs.append(len(orb))
    print(idx,'edge orbit pattern',sorted(orbs))
