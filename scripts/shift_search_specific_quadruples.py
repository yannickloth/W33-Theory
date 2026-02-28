#!/usr/bin/env python3
"""For each of the rare intersection=12 quadruples (from unrestricted_solutions.json)
try to find a cell-shift assignment making the full 192-flag orbit sizes correct.
The underlying 48 pairs are the first Reye line orbit used in enumerate_48_quadruples.py.
"""

from ortools.sat.python import cp_model
import json, sys
from itertools import combinations

# reconstruct the pairs exactly as in enumerate_48_quadruples
p0 = {5:10,10:5,6:9,9:6,7:12,12:7,8:11,11:8}
p1 = {1:6,6:1,2:5,5:2,3:8,8:3,4:7,7:4}
p2 = {5:9,9:5,6:10,10:6,7:11,11:7,8:12,12:8}
p3 = {5:8,8:5,6:7,7:6,9:12,12:9,10:11,11:10}
for perm in (p0,p1,p2,p3):
    for e in range(1,13): perm.setdefault(e,e)
# compute closure P
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
# compute Reye line orbits
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
if not candidate_lines:
    sys.exit("no candidate lines")
face_triples=candidate_lines[0]
pairs=[]
for face_idx,triple in enumerate(face_triples):
    for e in triple: pairs.append((e,face_idx))
assert len(pairs)==48

# load quadruples
soldata=json.load(open('unrestricted_solutions.json'))['solutions']
# Indices identified earlier as rare
special=[170,224,239,296]

# orbit size utilities extended for shifts
from collections import deque

def orbit_sizes_192(r_pair, r_shift, exclude_idx):
    gens=[(r_pair[i], r_shift[i]) for i in range(4) if i!=exclude_idx]
    seen=set(); sizes=[]
    for v in range(192):
        if v in seen: continue
        q=deque([v]); orb=set()
        while q:
            x=q.popleft()
            if x in orb: continue
            orb.add(x); seen.add(x)
            p=x//4; k=x%4
            for (pairmap, shiftmap) in gens:
                qpair = pairmap[p]
                qk = (k + shiftmap[p])%4
                new = 4*qpair + qk
                if new not in orb: q.append(new)
        sizes.append(len(orb))
    return sorted(sizes)

def validate(r_pair, r_shift):
    return (
        orbit_sizes_192(r_pair,r_shift,0)==[1]*4 and
        orbit_sizes_192(r_pair,r_shift,1)==[3]*12 and
        orbit_sizes_192(r_pair,r_shift,2)==[4]*16 and
        orbit_sizes_192(r_pair,r_shift,3)==[2]*8
    )

solver=cp_model.CpSolver()
solver.parameters.max_time_in_seconds=30
solver.parameters.num_search_workers=8

for idx in special:
    print(f"testing quadruple index {idx}")
    base=soldata[idx]
    # create model only for shifts
    model=cp_model.CpModel()
    r_shift=[[model.NewIntVar(0,3,f"s{i}_{p}") for p in range(48)] for i in range(4)]
    # involution shift constraints s[p]+s[q]==0 mod4 with q=r_pair[p]
    for i in range(4):
        for p in range(48):
            q=base[i][p]
            sq=model.NewIntVar(0,3,f"sq{i}_{p}")
            model.AddElement(q,[r_shift[i][j] for j in range(48)],sq)
            # mod eq
            modlist=[[a,b] for a in range(4) for b in range(4) if (a+b)%4==0]
            model.AddAllowedAssignments([r_shift[i][p],sq],modlist)
    # commutation shifts with fixed pair
    pairs_comm=[(0,2),(0,3),(1,3)]
    for (i,j) in pairs_comm:
        for p in range(48):
            pi=base[j][p]
            pj=base[i][p]
            sj_pi=model.NewIntVar(0,3,f"sj{ i}{j }_pi{p}")
            si_pj=model.NewIntVar(0,3,f"si{ i}{j }_pj{p}")
            model.AddElement(pi,[r_shift[j][k] for k in range(48)],sj_pi)
            model.AddElement(pj,[r_shift[i][k] for k in range(48)],si_pj)
            # s_i(p)+s_j(pi) == s_j(p)+s_i(pj) mod4
            mod4=[(a,b,c,d) for a in range(4) for b in range(4) for c in range(4) for d in range(4) if (a+b-c-d)%4==0]
            model.AddAllowedAssignments([r_shift[i][p],sj_pi,r_shift[j][p],si_pj],mod4)
    # orbit size constraint to be checked in callback
    class Col(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.solution=None
        def on_solution_callback(self):
            rsol=[[self.Value(r_shift[i][p]) for p in range(48)] for i in range(4)]
            if validate(base,rsol):
                self.solution=rsol
                self.StopSearch()
    collector=Col()
    res=solver.SearchForAllSolutions(model,collector)
    print("status",solver.StatusName(res),"found",collector.solution is not None)
    if collector.solution is not None:
        print("shift solution",collector.solution)
    print()