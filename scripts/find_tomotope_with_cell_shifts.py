#!/usr/bin/env python3
"""Search for a tomotope-style 192-flag maniplex by adding a cell-index
shift (mod 4) to each of the 48 Reye edge-face pairs.

Each generator r_i is modelled by:
    r_i(p,k) = (q, (k + shift_i[p]) mod 4)
where p is a pair index 0..47 and k=0..3 is the cell coordinate.  The
base permutation q = r_i_pair[p] must reproduce the published p_i edge
action when p=(edge,face).

The CP-SAT model encodes:
  * r_i_pair is a permutation of 48 elements
  * shift_i[p] in {0,1,2,3}
  * involution constraints on pair and shift
  * commutation relations r0↔r2, r0↔r3, r1↔r3 including shift addition
  * orbit-size pattern on the full 192 flags

If a solution is found it will be written to JSON files analogous to
`find_tomotope_flags_from_reye.py`.  The script is experimental; failures
will indicate that even adding a 4-cycle index per pair is insufficient.
"""

from __future__ import annotations
import json, sys, os
from itertools import combinations
from ortools.sat.python import cp_model

# p_i permutations as before
p0 = {5:10,10:5,6:9,9:6,7:12,12:7,8:11,11:8}
p1 = {1:6,6:1,2:5,5:2,3:8,8:3,4:7,7:4}
p2 = {5:9,9:5,6:10,10:6,7:11,11:7,8:12,12:8}
p3 = {5:8,8:5,6:7,7:6,9:12,12:9,10:11,11:10}
for perm in (p0,p1,p2,p3):
    for e in range(1,13): perm.setdefault(e,e)

# build Reye pairs the same way as in find_tomotope_flags_from_reye
# we reuse the precomputed JSON if available to save time
if not os.path.exists("candidate_line_orbits.json"):
    # compute closure of P and line orbits as in previous script
    from itertools import combinations
    P = []
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

if not candidate_lines:
    raise RuntimeError("no suitable Reye orbit found")

# choose one candidate (there are 4) and try searching; iterate similarly
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0
solver.parameters.num_search_workers = 8

# orbit-size utilities from 48 script, extended to 192
from collections import deque

def orbit_sizes_192(r_pair, r_shift, exclude_idx):
    # r_pair, r_shift indexed by [i][p]
    # compute orbits on 192 flags except generator exclude_idx
    gens = [(r_pair[i], r_shift[i]) for i in range(4) if i!=exclude_idx]
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

def validate_orbit_sizes_192(r_pair, r_shift):
    ok = (orbit_sizes_192(r_pair,r_shift,0)==[1]*4)
    ok &= (orbit_sizes_192(r_pair,r_shift,1)==[3]*12)
    ok &= (orbit_sizes_192(r_pair,r_shift,2)==[4]*16)
    ok &= (orbit_sizes_192(r_pair,r_shift,3)==[2]*8)
    return ok

# helper to run search on one orbit (48 pairs)
def run_search_with_shifts(pairs):
    # prepare allowed targets for pair permutation from edge action
    allowed_pair=[{ } for _ in range(4)]
    for i,pmap in enumerate((p0,p1,p2,p3)):
        for idx,(e,f) in enumerate(pairs):
            target=e
            # possible pairs indices that have same target edge
            allowed_pair[i].setdefault(idx,[])
            for j,(ee,_) in enumerate(pairs):
                if ee==pmap[e]: allowed_pair[i][idx].append(j)
            if not allowed_pair[i][idx]:
                return None
    # build CP-SAT model
    model=cp_model.CpModel()
    r_pair=[[model.NewIntVar(0,47,f"r{i}_p{p}") for p in range(48)] for i in range(4)]
    r_shift=[[model.NewIntVar(0,3,f"s{i}_p{p}") for p in range(48)] for i in range(4)]
    # domain restrictions for pair permutations
    for i in range(4):
        for p in range(48):
            model.AddAllowedAssignments([r_pair[i][p]], [[k] for k in allowed_pair[i][p]])
        model.AddAllDifferent([r_pair[i][p] for p in range(48)])
    # involution and shift consistency
    for i in range(4):
        for p in range(48):
            t=model.NewIntVar(0,47,f"t{i}_{p}")
            model.AddElement(r_pair[i][p],[r_pair[i][j] for j in range(48)],t)
            model.Add(t==p)
            # shift condition: s[p]+s[q] mod4 == 0
            qvar = model.NewIntVar(0,47,f"q{i}_{p}")
            model.AddElement(r_pair[i][p],[r_shift[i][j] for j in range(48)],qvar)
            # qvar is actually shift_i[q]; enforce modulo sum
            # use linear constraint: s[p]+s[qvar] == 0 mod 4
            # implement with table of allowed pairs
            sp=r_shift[i][p]
            # create intermediary for s[q]
            sq=model.NewIntVar(0,3,f"sq{i}_{p}")
            model.AddElement(r_pair[i][p],[r_shift[i][j] for j in range(48)],sq)
            # enforce (sp + sq) % 4 == 0 using allowed assignments
            modlist=[[a,b] for a in range(4) for b in range(4) if (a+b)%4==0]
            model.AddAllowedAssignments([sp,sq],modlist)
    # commutation constraints including shifts
    pairs_comm=[(0,2),(0,3),(1,3)]
    for (i,j) in pairs_comm:
        for p in range(48):
            # compute r_i(r_j(p)) and r_j(r_i(p)) and equate both pair and shift
            # use element constraints chaining
            pi = r_pair[j][p]
            pj = r_pair[i][p]
            # pair after i then j: r_pair[j][ pi ]
            t1=model.NewIntVar(0,47,f"c{i}{j}_p{p}_1")
            model.AddElement(pi,[r_pair[j][k] for k in range(48)],t1)
            t2=model.NewIntVar(0,47,f"c{i}{j}_p{p}_2")
            model.AddElement(pj,[r_pair[i][k] for k in range(48)],t2)
            model.Add(t1==t2)
            # shift sums: s_i(p)+s_j(pi) == s_j(p)+s_i(pj) mod4
            si_p=r_shift[i][p]
            sj_pi=model.NewIntVar(0,3,f"sj_{i}_{j}_pi{p}")
            model.AddElement(pi,[r_shift[j][k] for k in range(48)],sj_pi)
            sj_p=r_shift[j][p]
            si_pj=model.NewIntVar(0,3,f"si_{i}_{j}_pj{p}")
            model.AddElement(pj,[r_shift[i][k] for k in range(48)],si_pj)
            # sum equality modulo 4
            # we again use AllowedAssignments on four vars
            mod4=[(a,b,c,d) for a in range(4) for b in range(4) for c in range(4) for d in range(4) if (a+b-c-d)%4==0]
            model.AddAllowedAssignments([si_p,sj_pi,sj_p,si_pj],mod4)
    # orbit size constraint on 192
    # we will collect solution via callback and then verify and stop when found
    class Col(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.found=None
        def on_solution_callback(self):
            rsol=[[self.Value(r_pair[i][p]) for p in range(48)] for i in range(4)]
            sshift=[[self.Value(r_shift[i][p]) for p in range(48)] for i in range(4)]
            if validate_orbit_sizes_192(rsol,sshift):
                self.found=(rsol,sshift)
                self.StopSearch()
    collector=Col()
    res=solver.SearchForAllSolutions(model,collector)
    print("sat status",solver.StatusName(res))
    return collector.found

# attempt each candidate line orbit
for idx,face_triples in enumerate(candidate_lines):
    print(f"trying orbit {idx}")
    pairs=[]
    for fidx,triple in enumerate(face_triples):
        for e in triple:
            pairs.append((e,fidx))
    sol=run_search_with_shifts(pairs)
    if sol:
        rsol,sshift=sol
        print("found solution for orbit",idx)
        json.dump({"pairs":pairs,"r_pair":rsol,"r_shift":sshift},open("tomotope_shift_solution.json","w"),indent=2)
        break
else:
    print("no solution with cell-shifts found for any orbit")

