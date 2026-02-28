#!/usr/bin/env python3
"""Search for a tomotope-style 192-flag maniplex by lifting the Reye
12_4_16 incidence.  The search runs on 48 edge-face pairs and uses
OR-Tools CP-SAT to assign four involutions r0..r3 satisfying the
projection to the published p_i actions and the tomotope commuting
relations.  The discovered 48-model is then trivially lifted to 192 flags
by replicating each pair four times.

Produces JSON files on success:
  * tomotope_search_48.json    (r0..r3 on 48 indices)
  * tomotope_search_192.json   (lifted permutations on 192 flags)
  * reye_pairs.json            (the 48 pairs used)

Also prints diagnostics.
"""

from __future__ import annotations
import json, sys
from itertools import combinations
from ortools.sat.python import cp_model

# published p_i permutations on edges 1..12
p0 = {5:10,10:5,6:9,9:6,7:12,12:7,8:11,11:8}
p1 = {1:6,6:1,2:5,5:2,3:8,8:3,4:7,7:4}
p2 = {5:9,9:5,6:10,10:6,7:11,11:7,8:12,12:8}
p3 = {5:8,8:5,6:7,7:6,9:12,12:9,10:11,11:10}

# ensure identity on unspecified edges
for perm in (p0,p1,p2,p3):
    for e in range(1,13):
        perm.setdefault(e,e)

# build full group P closure (not strictly necessary for lines, but helpful)
P = []
for perm in (p0,p1,p2,p3):
    arr = [0] + [perm[i] for i in range(1,13)]
    P.append(arr)
# closure
allP = {tuple(arr) for arr in P}
changed = True
while changed:
    changed = False
    for a in list(allP):
        for b in P:
            comp = tuple(a[b[i]] for i in range(13))
            if comp not in allP:
                allP.add(comp)
                changed = True
print(f"P closure size = {len(allP)} (should be 96)")

# compute Reye lines: orbits of 3-subsets
subs = list(combinations(range(1,13), 3))
line_orbits = []
seen = set()
for s in subs:
    if s in seen:
        continue
    orbit = set()
    stack = [s]
    while stack:
        cur = stack.pop()
        if cur in orbit:
            continue
        orbit.add(cur)
        seen.add(cur)
        for perm in allP:
            new = tuple(sorted(perm[i] for i in cur))
            if new not in orbit:
                stack.append(new)
    line_orbits.append(sorted(orbit))
print("line orbit sizes", [len(o) for o in line_orbits])
# filter orbits of size 16 that satisfy Reye incidence (each edge appears exactly 4 times)
candidate_lines = []
for orb in line_orbits:
    if len(orb) != 16:
        continue
    deg = {e:0 for e in range(1,13)}
    for tri in orb:
        for e in tri:
            deg[e] += 1
    if all(d == 4 for d in deg.values()):
        candidate_lines.append(orb)
print("candidate line-orbits", len(candidate_lines))
# save candidate orbits for later analysis
with open("candidate_line_orbits.json","w") as f:
    json.dump(candidate_lines, f, indent=2)
if not candidate_lines:
    raise RuntimeError("no suitable Reye orbit found")

final_solution = None
final_pairs = None

# solver configuration and helper class
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0
solver.parameters.num_search_workers = 8

class SolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solution_count = 0
        self.best_solution = None
    def on_solution_callback(self):
        self.solution_count += 1
        sol = [[self.Value(r[i][f]) for f in range(48)] for i in range(4)]
        if validate_orbit_sizes(sol):
            self.best_solution = sol
            self.StopSearch()

# helper: run CP-SAT search on given 48 pairs

def run_search(pairs):
    # build edge_of
    edge_of = [pairs[i][0] for i in range(len(pairs))]
    # allowed targets for r_i
    allowed = [{} for _ in range(4)]
    for i, pmap in enumerate((p0,p1,p2,p3)):
        for f in range(48):
            e = edge_of[f]
            target_edge = pmap[e]
            allowed[i].setdefault(f, [])
            for k, (ee, _) in enumerate(pairs):
                if ee == target_edge:
                    allowed[i][f].append(k)
        for f in range(48):
            if not allowed[i][f]:
                return None
    # build CP-SAT model
    model = cp_model.CpModel()
    r = [[model.NewIntVar(0, 47, f"r{i}_{f}") for f in range(48)] for i in range(4)]
    for i in range(4):
        for f in range(48):
            model.AddAllowedAssignments([r[i][f]], [[k] for k in allowed[i][f]])
    for i in range(4):
        model.AddAllDifferent([r[i][f] for f in range(48)])
    # involution
    for i in range(4):
        for f in range(48):
            t = model.NewIntVar(0,47,f"t_{i}_{f}")
            model.AddElement(r[i][f], [r[i][j] for j in range(48)], t)
            model.Add(t == f)
    pairs_comm = [(0,2),(0,3),(1,3)]
    for (i,j) in pairs_comm:
        for f in range(48):
            t = model.NewIntVar(0,47,f"t_{i}{j}_{f}")
            u = model.NewIntVar(0,47,f"u_{i}{j}_{f}")
            model.AddElement(r[j][f], [r[i][k] for k in range(48)], t)
            model.AddElement(r[i][f], [r[j][k] for k in range(48)], u)
            model.Add(t == u)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 8
    collector = SolutionCollector()
    res = solver.SearchForAllSolutions(model, collector)
    print("sat status", solver.StatusName(res), "solutions tried", collector.solution_count)
    return collector.best_solution

# try each candidate orbit
for orbit_idx, face_triples in enumerate(candidate_lines):
    print(f"trying candidate orbit {orbit_idx}")
    pairs = []
    for face_idx, triple in enumerate(face_triples):
        for e in triple:
            pairs.append((e, face_idx))
    if len(pairs) != 48:
        print("orbit produced", len(pairs), "pairs, skipping")
        continue
    sol48 = run_search(pairs)
    if sol48 is not None:
        final_solution = sol48
        final_pairs = pairs
        break

if final_solution is None:
    print("no valid 48-solution found for any candidate orbit")
    sys.exit(1)

pairs = final_pairs
best_solution = final_solution
print("found valid 48-permutation set")
out = {f"r{i}": best_solution[i] for i in range(4)}
json.dump(out, open("tomotope_search_48.json","w"), indent=2)
# lift to 192
# each of 48 pairs produces 4 flags: index = 4*p + k

# backtracking search using CP-SAT
model = cp_model.CpModel()
# create integer vars r[i][f]
r = [[model.NewIntVar(0, 47, f"r{i}_{f}") for f in range(48)] for i in range(4)]
# enforce projection by domain restriction: we'll add table constraints
for i in range(4):
    for f in range(48):
        model.AddAllowedAssignments([r[i][f]], [[k] for k in allowed[i][f]])
# permutation constraints
for i in range(4):
    model.AddAllDifferent([r[i][f] for f in range(48)])
# involution constraints: r[i][r[i][f]] == f
for i in range(4):
    for f in range(48):
        t = model.NewIntVar(0,47,f"t_{i}_{f}")
        model.AddElement(r[i][f], [r[i][j] for j in range(48)], t)
        model.Add(t == f)
# commutation: r0 commutes with r2,r3; r1 with r3
pairs_comm = [(0,2),(0,3),(1,3)]
for (i,j) in pairs_comm:
    for f in range(48):
        t = model.NewIntVar(0,47,f"t_{i}{j}_{f}")
        u = model.NewIntVar(0,47,f"u_{i}{j}_{f}")
        # t = r_i[r_j[f]]
        model.AddElement(r[j][f], [r[i][k] for k in range(48)], t)
        # u = r_j[r_i[f]]
        model.AddElement(r[i][f], [r[j][k] for k in range(48)], u)
        model.Add(t == u)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0
solver.parameters.num_search_workers = 8

class SolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solution_count = 0
        self.best_solution = None
    def on_solution_callback(self):
        self.solution_count += 1
        # copy current r values
        sol = [[self.Value(r[i][f]) for f in range(48)] for i in range(4)]
        # check orbit sizes on 48; if good, save and stop
        if validate_orbit_sizes(sol):
            self.best_solution = sol
            self.StopSearch()

# note: SolutionCollector is now available to run_search

# orbit size calculator on 48
from collections import deque

def orbit_sizes(rvals, exclude_idx):
    # compute orbits under all generators except exclude_idx
    gens = [rvals[i] for i in range(4) if i != exclude_idx]
    seen = set()
    sizes = []
    for v in range(48):
        if v in seen: continue
        q = deque([v]); orb=set()
        while q:
            x=q.popleft()
            if x in orb: continue
            orb.add(x); seen.add(x)
            for g in gens:
                image = g[x]
                if image not in orb: q.append(image)
        sizes.append(len(orb))
    return sorted(sizes)

def validate_orbit_sizes(rvals):
    # i=0 -> vertices-> size1
    ok = (orbit_sizes(rvals,0) == [1]*4)
    ok &= (orbit_sizes(rvals,1) == [3]*12)
    ok &= (orbit_sizes(rvals,2) == [4]*16)
    ok &= (orbit_sizes(rvals,3) == [2]*8)
    return ok

collector = SolutionCollector()
print("starting CP-SAT search...")
res = solver.SearchForAllSolutions(model, collector)
print("sat status", solver.StatusName(res), "solutions tried", collector.solution_count)

if collector.best_solution is None:
    print("no valid 48-solution found")
    sys.exit(1)
else:
    print("found valid 48-permutation set")
    out = {f"r{i}": collector.best_solution[i] for i in range(4)}
    json.dump(out, open("tomotope_search_48.json","w"), indent=2)
    # lift to 192
    # each of 48 pairs produces 4 flags: index = 4*p + k
    def lift(rvals):
        perm192 = [None]*192
        for f in range(48):
            for k in range(4):
                src = 4*f + k
                tgt_f = rvals[f]
                # choose same k to preserve cell index
                perm192[src] = 4*tgt_f + k
        return perm192
    r192 = [lift(best_solution[i]) for i in range(4)]
    json.dump({f"r{i}": r192[i] for i in range(4)}, open("tomotope_search_192.json","w"), indent=2)
    json.dump({"pairs": pairs}, open("reye_pairs.json","w"), indent=2)
    print("results written")
