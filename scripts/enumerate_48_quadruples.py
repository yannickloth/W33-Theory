#!/usr/bin/env python3
"""Enumerate some 48-element involution quadruples satisfying the tomotope
commutation/face-size conditions, but WITHOUT any edge-projection
requirement.  The aim is to see what edge-groups occur and confirm the
obstruction.

Outputs a JSON list of found quadruples and the induced edge-group
orbit statistics.
"""

from __future__ import annotations
import json, sys
from itertools import combinations
from ortools.sat.python import cp_model

# published p_i used only later for comparison
p0 = {5:10,10:5,6:9,9:6,7:12,12:7,8:11,11:8}
p1 = {1:6,6:1,2:5,5:2,3:8,8:3,4:7,7:4}
p2 = {5:9,9:5,6:10,10:6,7:11,11:7,8:12,12:8}
p3 = {5:8,8:5,6:7,7:6,9:12,12:9,10:11,11:10}
for perm in (p0,p1,p2,p3):
    for e in range(1,13): perm.setdefault(e,e)

# build P closure
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
print("P closure size",len(allP))

# compute Reye lines as before
def compute_reye_orbits():
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
    return line_orbits

line_orbits=compute_reye_orbits()
print("line orbit sizes",[len(o) for o in line_orbits])
candidate_lines=[]
for orb in line_orbits:
    if len(orb)!=16: continue
    deg={e:0 for e in range(1,13)}
    for tri in orb:
        for e in tri: deg[e]+=1
    if all(d==4 for d in deg.values()): candidate_lines.append(orb)
print("candidate line orbits",len(candidate_lines))
if not candidate_lines:
    sys.exit(1)
face_triples=candidate_lines[0]

pairs=[]
for face_idx,triple in enumerate(face_triples):
    for e in triple: pairs.append((e,face_idx))
assert len(pairs)==48
edge_of=[pairs[i][0] for i in range(48)]

# search
model=cp_model.CpModel()
r=[[model.NewIntVar(0,47,f"r{i}_{f}") for f in range(48)] for i in range(4)]
# no projection constraint
for i in range(4):
    model.AddAllDifferent([r[i][f] for f in range(48)])
# involution
for i in range(4):
    for f in range(48):
        t=model.NewIntVar(0,47,f"t_{i}_{f}")
        model.AddElement(r[i][f],[r[i][j] for j in range(48)],t)
        model.Add(t==f)
# commutation
pairs_comm=[(0,2),(0,3),(1,3)]
for (i,j) in pairs_comm:
    for f in range(48):
        t=model.NewIntVar(0,47,f"t_{i}{j}_{f}")
        u=model.NewIntVar(0,47,f"u_{i}{j}_{f}")
        model.AddElement(r[j][f],[r[i][k] for k in range(48)],t)
        model.AddElement(r[i][f],[r[j][k] for k in range(48)],u)
        model.Add(t==u)
# orbit size constraints on 48 (same function from previous script)
from collections import deque

def orbit_sizes(rvals, exclude_idx):
    gens=[rvals[i] for i in range(4) if i!=exclude_idx]
    seen=set(); sizes=[]
    for v in range(48):
        if v in seen: continue
        q=deque([v]); orb=set()
        while q:
            x=q.popleft()
            if x in orb: continue
            orb.add(x); seen.add(x)
            for g in gens:
                img=g[x]
                if img not in orb: q.append(img)
        sizes.append(len(orb))
    return sorted(sizes)

def validate_orbit_sizes(rvals):
    ok=(orbit_sizes(rvals,0)==[1]*4)
    ok&=(orbit_sizes(rvals,1)==[3]*12)
    ok&=(orbit_sizes(rvals,2)==[4]*16)
    ok&=(orbit_sizes(rvals,3)==[2]*8)
    return ok

solver=cp_model.CpSolver()
solver.parameters.max_time_in_seconds=20
solver.parameters.num_search_workers=8

# quick solve mode if passed '-quick'
if len(sys.argv)>1 and sys.argv[1]=='-quick':
    res=solver.Solve(model)
    print("quick solve status",solver.StatusName(res))
    if res==cp_model.OPTIMAL or res==cp_model.FEASIBLE:
        sol=[[solver.Value(r[i][f]) for f in range(48)] for i in range(4)]
        print("example r0" ,sol[0][:10])
        print("orbit sizes" ,[orbit_sizes(sol,i) for i in range(4)])
    sys.exit(0)

solutions=[]
max_sols=500
class MyCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.count=0
    def on_solution_callback(self):
        self.count+=1
        if len(solutions) < max_sols:
            sol=[[self.Value(r[i][f]) for f in range(48)] for i in range(4)]
            solutions.append(sol)
        if self.count >= 5000:
            self.StopSearch()

print("starting unrestricted search...")
res=solver.SearchForAllSolutions(model, MyCollector())
print("status",solver.StatusName(res),"recorded",len(solutions))

# save raw solutions for further analysis
json.dump({"pairs":pairs,"solutions":solutions},
          open("unrestricted_solutions.json","w"), indent=2)

# compute induced edge-group orbit sizes
stats=[]
if solutions:
    for sol in solutions:
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
        stats.append(sorted(orbs))
    print("edge orbit stats samples", stats[:5])
else:
    print("no solutions found")

json.dump({"pairs":pairs,"solutions_count":len(solutions),"edge_stats":stats},
          open("unrestricted_search_results.json","w"), indent=2)
