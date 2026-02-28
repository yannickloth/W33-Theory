#!/usr/bin/env python3
"""Enumerate all 16-triple configurations on 12 points satisfying
Reye-degree condition (each point appears exactly 4 times) and test
each one for a tomotope involution assignment with the published edge
projections and commuting relations.

This is a brute-force backtracking; it will stop when a valid
configuration is found or after exploring a preset limit.
"""

from __future__ import annotations
import json, sys
from itertools import combinations
from ortools.sat.python import cp_model

# published edge permutations
p0 = {5:10,10:5,6:9,9:6,7:12,12:7,8:11,11:8}
p1 = {1:6,6:1,2:5,5:2,3:8,8:3,4:7,7:4}
p2 = {5:9,9:5,6:10,10:6,7:11,11:7,8:12,12:8}
p3 = {5:8,8:5,6:7,7:6,9:12,12:9,10:11,11:10}
for perm in (p0,p1,p2,p3):
    for e in range(1,13): perm.setdefault(e,e)

all_triples=list(combinations(range(1,13),3))

# backtracking to pick 16 triples with degree constraint
solutions_found=0
max_configs=1000

# helper to run CP-SAT search on a given set of triples

def test_config(triples):
    pairs=[]
    for face_idx,tri in enumerate(triples):
        for e in tri:
            pairs.append((e,face_idx))
    if len(pairs)!=48: return False
    # use same run_search from find_tomotope_flags_from_reye.py
    # we reimplement minimal version here
    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=10
    solver.parameters.num_search_workers=8
    # allowed projection
    allowed=[{} for _ in range(4)]
    for i,pmap in enumerate((p0,p1,p2,p3)):
        for f,(e,_) in enumerate(pairs):
            tgt=pmap[e]
            allowed[i].setdefault(f,[])
            for k,(ee,_) in enumerate(pairs):
                if ee==tgt: allowed[i][f].append(k)
            if not allowed[i][f]: return False
    model=cp_model.CpModel()
    r=[[model.NewIntVar(0,47,f"r{i}_{f}") for f in range(48)] for i in range(4)]
    for i in range(4):
        for f in range(48):
            model.AddAllowedAssignments([r[i][f]],[[k] for k in allowed[i][f]])
        model.AddAllDifferent([r[i][f] for f in range(48)])
    # involution & commutation
    for i in range(4):
        for f in range(48):
            t=model.NewIntVar(0,47,f"t_{i}_{f}")
            model.AddElement(r[i][f],[r[i][j] for j in range(48)],t)
            model.Add(t==f)
    pairs_comm=[(0,2),(0,3),(1,3)]
    for (i,j) in pairs_comm:
        for f in range(48):
            t=model.NewIntVar(0,47,f"t_{i}{j}_{f}")
            u=model.NewIntVar(0,47,f"u_{i}{j}_{f}")
            model.AddElement(r[j][f],[r[i][k] for k in range(48)],t)
            model.AddElement(r[i][f],[r[j][k] for k in range(48)],u)
            model.Add(t==u)
    # simple search for any solution
    res=solver.Solve(model)
    return res==cp_model.FEASIBLE or res==cp_model.OPTIMAL

# backtracking

def backtrack(start,chosen,deg):
    global solutions_found
    if solutions_found>=max_configs:
        return True
    if len(chosen)==16:
        # verify deg=4 each
        if all(deg[e]==4 for e in range(1,13)):
            solutions_found+=1
            print(f"testing config #{solutions_found}")
            if test_config(chosen):
                print("found valid configuration",chosen)
                json.dump({"triples":chosen},open("valid_config.json","w"),indent=2)
                return True
        return False
    for idx in range(start,len(all_triples)):
        tri=all_triples[idx]
        # quick degree prune
        ok=True
        for e in tri:
            if deg[e]>=4: ok=False; break
        if not ok: continue
        # choose
        chosen.append(tri)
        for e in tri: deg[e]+=1
        if backtrack(idx+1,chosen,deg): return True
        for e in tri: deg[e]-=1
        chosen.pop()
    return False

print("starting config search")
deg={e:0 for e in range(1,13)}
backtrack(0,[],deg)
if solutions_found==0:
    print("no config tested")
else:
    print(f"tested {solutions_found} configurations")
