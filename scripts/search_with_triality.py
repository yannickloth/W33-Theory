#!/usr/bin/env python3
"""Search for 48-flag quadruples satisfying tomotope commutation plus a
triality condition: the product r0 r1 r2 r3 should have order exactly 3.

The script is a variation of enumerate_48_quadruples.py; it ignores
projection and orbit-size conditions, focusing on global structure.
"""

from __future__ import annotations
import json, sys, os
from itertools import combinations
from ortools.sat.python import cp_model

# compute possible involution quadruples as before
# p_i, P closure not needed for this search

# build 48 pairs from the first Reye candidate orbit (we only care about structure)
# reuse earlier JSON if available
if not os.path.exists("candidate_line_orbits.json"):
    # compute as in other scripts
    from itertools import combinations
    p0 = {5:10,10:5,6:9,9:6,7:12,12:7,8:11,11:8}
    p1 = {1:6,6:1,2:5,5:2,3:8,8:3,4:7,7:4}
    p2 = {5:9,9:5,6:10,10:6,7:11,11:7,8:12,12:8}
    p3 = {5:8,8:5,6:7,7:6,9:12,12:9,10:11,11:10}
    for perm in (p0,p1,p2,p3):
        for e in range(1,13): perm.setdefault(e,e)
    P=[]
    for perm in (p0,p1,p2,p3):
        arr=[0]+[perm[i] for i in range(1,13)]; P.append(arr)
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
        orbit=set(); stack=[s]
        while stack:
            cur=stack.pop()
            if cur in orbit: continue
            orbit.add(cur); seen.add(cur)
            for perm in allP:
                new=tuple(sorted(perm[i] for i in cur))
                if new not in orbit: stack.append(new)
        line_orbits.append(sorted(orbit))
    candidate_lines=[orb for orb in line_orbits if len(orb)==16 and all(sum(e in tri for tri in orb)==4 for e in range(1,13))]
    json.dump(candidate_lines, open("candidate_line_orbits.json","w"), indent=2)
else:
    candidate_lines=json.load(open("candidate_line_orbits.json"))

# pick first orbit just to generate pairs
face_triples=candidate_lines[0]
pairs=[]
for face_idx,triple in enumerate(face_triples):
    for e in triple:
        pairs.append((e,face_idx))

# solver setup
model=cp_model.CpModel()
r=[[model.NewIntVar(0,47,f"r{i}_{f}") for f in range(48)] for i in range(4)]
for i in range(4):
    model.AddAllDifferent([r[i][f] for f in range(48)])
# involution
for i in range(4):
    for f in range(48):
        t=model.NewIntVar(0,47,f"t_{i}_{f}")
        model.AddElement(r[i][f],[r[i][j] for j in range(48)],t)
        model.Add(t==f)
# commutation
for (i,j) in [(0,2),(0,3),(1,3)]:
    for f in range(48):
        t=model.NewIntVar(0,47,f"t_{i}{j}_{f}")
        u=model.NewIntVar(0,47,f"u_{i}{j}_{f}")
        model.AddElement(r[j][f],[r[i][k] for k in range(48)],t)
        model.AddElement(r[i][f],[r[j][k] for k in range(48)],u)
        model.Add(t==u)

# triality element: compose t = r3(r2(r1(r0(f))))
# require t^3 = identity but t != identity (order exactly 3)

tperm=[model.NewIntVar(0,47,f"t_{f}") for f in range(48)]
t2perm=[model.NewIntVar(0,47,f"t2_{f}") for f in range(48)]
for f in range(48):
    # compute a = r0[f]
    a = r[0][f]
    # b = r1[a]
    b = model.NewIntVar(0,47,f"b_{f}")
    model.AddElement(a,[r[1][k] for k in range(48)],b)
    # c = r2[b]
    c = model.NewIntVar(0,47,f"c_{f}")
    model.AddElement(b,[r[2][k] for k in range(48)],c)
    # tperm[f] = r3[c]
    model.AddElement(c,[r[3][k] for k in range(48)],tperm[f])
    # t2 = t(t(f))
    ivt = model.NewIntVar(0,47,f"ivt_{f}")
    model.AddElement(tperm[f],[tperm[k] for k in range(48)],ivt)
    model.AddElement(ivt,[tperm[k] for k in range(48)],t2perm[f])

# enforce t^3 = id
for f in range(48):
    t3 = model.NewIntVar(0,47,f"t3_{f}")
    model.AddElement(tperm[f],[tperm[k] for k in range(48)],t3)
    model.Add(t3 == f)

# ensure nonidentity
neqs=[]
for f in range(48):
    cvar=model.NewBoolVar(f"neqt_{f}")
    model.Add(tperm[f] != f).OnlyEnforceIf(cvar)
    neqs.append(cvar)
model.AddBoolOr(neqs)

solver=cp_model.CpSolver()
solver.parameters.max_time_in_seconds=30
solver.parameters.num_search_workers=8

class Col(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.count=0
        self.found=None
    def on_solution_callback(self):
        self.count+=1
        sol=[[self.Value(r[i][f]) for f in range(48)] for i in range(4)]
        # no further filtering
        self.found=sol
        self.StopSearch()

print("searching with triality condition")
collector=Col()
res=solver.SearchForAllSolutions(model,collector)
print("status",solver.StatusName(res),"solutions tried",collector.count)
if collector.found:
    json.dump({f"r{i}":collector.found[i] for i in range(4)},open("triality_solution.json","w"),indent=2)
    print("found example saved to triality_solution.json")
else:
    print("no quadruple satisfied triality condition")
