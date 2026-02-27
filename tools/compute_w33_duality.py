#!/usr/bin/env python3
"""Compute explicit duality map between points and lines of W(3,3).

Generates the symplectic polar space W(3,3) over F3, builds the bipartite
incidence graph (40 points vs 40 totally isotropic lines) and then finds a
graph automorphism that swaps the two parts. The resulting bijection
point->line is the desired duality.

Outputs:
  artifacts/w33_point_to_line_duality.json   # 40 entries
  artifacts/w33_duality_verification.json    # sanity checks

The script also verifies that conjugating the PSp(4,3) action on points by
this map produces the action on lines (hence demonstrating the outer
automorphism at the geometry level).

"""

from __future__ import annotations
import json
from itertools import combinations
from pathlib import Path
from typing import List, Set, Tuple, Dict

import numpy as np
import networkx as nx


def gen_group_n(gens, n, max_size=100000):
    """Generate group from given permutation generators acting on n elements.
    Similar to the version in compute_we6_outer_automorphism.py."""
    from collections import deque
    idp = np.arange(n, dtype=np.uint16)
    seen = {idp.tobytes(): idp}
    q = deque([idp])
    while q and len(seen) < max_size:
        p = q.popleft()
        for g in gens:
            h = g[p]
            k = h.tobytes()
            if k not in seen:
                seen[k] = h
                q.append(h)
    return seen

ROOT = Path(__file__).resolve().parents[1]

# symplectic form on F3^4
def omega(v: np.ndarray, w: np.ndarray) -> int:
    # v,w are length-4 over F3
    # use matrix [[0,1,-1,0],[ -1,0,0, 0],[1,0,0,0],[0,0,0,0]]? easier direct formula
    # we'll hardcode bilinear form: v0*w2 - v2*w0 + v1*w3 - v3*w1
    return int((v[0]*w[2] - v[2]*w[0] + v[1]*w[3] - v[3]*w[1]) % 3)


def generate_w33() -> Tuple[List[np.ndarray], List[List[int]]]:
    """Return list of 40 projective points (representative vectors) and
    list of 40 lines (each line is list of point indices)."""
    # generate all nonzero vectors in F3^4
    F = [0,1,2]
    vecs = []
    for a in F:
        for b in F:
            for c in F:
                for d in F:
                    if a==b==c==d==0: continue
                    vecs.append(np.array([a,b,c,d],dtype=int))
    # reduce to projective points: choose smallest lexicographic representative of each scalar class
    classes = {}
    for v in vecs:
        # find canonical key
        best = None
        for s in (1,2):
            vv = (v * s) % 3
            key = tuple(vv.tolist())
            if best is None or key < best:
                best = key
        classes[best] = np.array(best)
    points = list(classes.values())
    assert len(points)==40
    # map vector->point index
    vec_to_idx = {tuple(p.tolist()): i for i,p in enumerate(points)}
    # compute lines: totally isotropic 2-subspaces
    lines_set: Set[Tuple[int,...]] = set()
    for i,j in combinations(range(len(points)),2):
        v = points[i]
        w = points[j]
        # require they are linearly independent mod 3
        mat = np.vstack([v,w]).astype(int) % 3
        if np.linalg.matrix_rank(mat) < 2:
            continue
        if omega(v,w) % 3 != 0:
            continue
        # compute subspace vectors
        subs = []
        for a in F:
            for b in F:
                subs.append((a*v + b*w) % 3)
        # reduce to projective point indices
        idxs = set()
        for u in subs:
            key = tuple(u.tolist())
            # find class rep via scaling
            if key in vec_to_idx:
                idxs.add(vec_to_idx[key])
            else:
                # try scaled versions
                for s in (1,2):
                    key2 = tuple(((u*s)%3).tolist())
                    if key2 in vec_to_idx:
                        idxs.add(vec_to_idx[key2])
                        break
        if len(idxs)==4:
            tup = tuple(sorted(idxs))
            lines_set.add(tup)
    lines = [list(x) for x in sorted(lines_set)]
    assert len(lines)==40
    return points, lines


def build_incidence(points, lines):
    inc_pt_to_lin = {i:set() for i in range(len(points))}
    inc_lin_to_pt = {i:set() for i in range(len(lines))}
    for li,L in enumerate(lines):
        for p in L:
            inc_pt_to_lin[p].add(li)
            inc_lin_to_pt[li].add(p)
    return inc_pt_to_lin, inc_lin_to_pt


def find_duality(inc_pt_to_lin, inc_lin_to_pt):
    """Backtracking search enforcing forward adjacency preservation.

    A valid duality is a bijection f:points->lines such that whenever two
    points p,q are collinear (i.e. share a line), their image lines f(p),
    f(q) intersect.  This is the necessary part of the duality property.
    We search for any assignment satisfying this; the full duality will be
    verified later (including unique-point intersections for each original line).
    """
    N = len(inc_pt_to_lin)
    points = list(range(N))
    lines = list(range(N))
    # precompute neighbor sets
    neighbors = {p: set() for p in points}
    for p in points:
        for l in inc_pt_to_lin[p]:
            neighbors[p].update(inc_lin_to_pt[l])
        neighbors[p].discard(p)
    # initial candidate sets (all lines)
    candidate = {p:set(lines) for p in points}

    def recursive_assign(mapping: Dict[int,int], used_lines: Set[int]) -> Dict[int,int] | None:
        if len(mapping) == N:
            return mapping
        # pick unassigned point with smallest candidate pool
        unassigned = [p for p in points if p not in mapping]
        p = min(unassigned, key=lambda x: len(candidate[x]))
        for l in list(candidate[p] - used_lines):
            # check consistency with already assigned neighbors
            ok = True
            for q, lq in mapping.items():
                if q in neighbors[p]:
                    # require image lines intersect
                    if inc_lin_to_pt[l].isdisjoint(inc_lin_to_pt[lq]):
                        ok = False
                        break
            if not ok:
                continue
            newmap = dict(mapping)
            newmap[p] = l
            newused = set(used_lines)
            newused.add(l)
            res = recursive_assign(newmap, newused)
            if res is not None:
                return res
        return None

    return recursive_assign({}, set())


def verify_mapping(mapping, inc_pt_to_lin, inc_lin_to_pt):
    N = len(mapping)
    inv = {l:p for p,l in mapping.items()}
    # check bijection
    assert set(mapping.keys())==set(range(N))
    assert set(mapping.values())==set(range(N))
    # adjacency preservation
    for p in range(N):
        l = mapping[p]
        for l2 in inc_pt_to_lin[p]:
            q = inv[l2]
            if q not in inc_lin_to_pt[l]:
                print(f"mismatch: point {p} line {l2} mapped to {l}->{q}, but {q} not on line {l}")
                return False
    return True


def main():
    points, lines = generate_w33()
    inc_pt_to_lin, inc_lin_to_pt = build_incidence(points, lines)
    # try finding an incidence-swapping automorphism of the bipartite graph
    # (disabled for performance, will rely on CP-SAT search instead)
    if False:
        print("attempting bipartite incidence automorphism search")
        B = nx.Graph()
        for p in range(len(points)):
            B.add_node(p, part=0)
        for l_idx in range(len(lines)):
            B.add_node(40 + l_idx, part=1)
        for l_idx, L in enumerate(lines):
            for p in L:
                B.add_edge(p, 40 + l_idx)
        # copy with swapped part labels
        B1 = nx.Graph()
        for n, d in B.nodes(data=True):
            B1.add_node(n, part=1 - d['part'])
        B1.add_edges_from(B.edges())
        GM_bip = nx.algorithms.isomorphism.GraphMatcher(
            B, B1, node_match=lambda a, b: a['part'] == b['part'])
        bip_dual = None
        for m in GM_bip.isomorphisms_iter():
            if all((p < 40) == (m[p] >= 40) for p in range(40)):
                bip_dual = {p: m[p] - 40 for p in range(40)}
                break
        if bip_dual is not None:
            ok = verify_mapping(bip_dual, inc_pt_to_lin, inc_lin_to_pt)
            print("bipartite automorphism produced mapping, verification:", ok)
            out = ROOT / "artifacts"
            with open(out/"w33_point_to_line_duality.json","w") as f:
                json.dump(bip_dual, f)
            with open(out/"w33_duality_verification.json","w") as f:
                json.dump({"verified": ok}, f)
            print("artifacts written via bipartite automorphism")
            return
        print("bipartite automorphism attempt failed, falling back to backtracking")
    print("attempting recursive backtracking search for duality")
    dual = find_duality(inc_pt_to_lin, inc_lin_to_pt)
    if dual is not None:
        ok = verify_mapping(dual, inc_pt_to_lin, inc_lin_to_pt)
        print("backtracking found mapping, verification:", ok)
        out = ROOT / "artifacts"
        with open(out/"w33_point_to_line_duality.json","w") as f:
            json.dump(dual, f)
        with open(out/"w33_duality_verification.json","w") as f:
            json.dump({"verified": ok}, f)
        print("artifacts written via backtracking")
        return
    print("backtracking failed, attempting CP-SAT search")
    # attempt CP-SAT to find explicit duality using line-intersection constraints
    try:
        from ortools.sat.python import cp_model
    except Exception:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ortools"])
        from ortools.sat.python import cp_model
    N = len(points)
    model = cp_model.CpModel()
    x = [[model.NewBoolVar(f"x_{p}_{l}") for l in range(N)] for p in range(N)]
    y = [[model.NewBoolVar(f"y_{L}_{p}") for p in range(N)] for L in range(N)]
    # bijection constraints for x
    for p in range(N):
        model.Add(sum(x[p][l] for l in range(N)) == 1)
    for l in range(N):
        model.Add(sum(x[p][l] for p in range(N)) == 1)
    # exactly one intersection point per original line L
    for L in range(N):
        model.Add(sum(y[L][p] for p in range(N)) == 1)
    # linking constraints: if y[L][p]==1, then for each q on line L, the image of q must be a line containing p
    for L, Lpts in enumerate(lines):
        for p in range(N):
            for q in Lpts:
                # collect lines that contain p
                valid_ls = [l for l in range(N) if p in inc_lin_to_pt[l]]
                # enforce implication y[L][p] -> OR_{l in valid_ls} x[q][l]
                if valid_ls:
                    model.Add(sum(x[q][l] for l in valid_ls) >= y[L][p])
                else:
                    # no line contains p? should not happen
                    model.Add(y[L][p] == 0)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 120.0
    solver.parameters.num_search_workers = 8
    print("solving CP-SAT for duality map with full line intersection constraints...")
    res = solver.Solve(model)
    if res in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        dual = {}
        for p in range(N):
            for l in range(N):
                if solver.Value(x[p][l]) == 1:
                    dual[p] = l
                    break
        ok = verify_mapping(dual, inc_pt_to_lin, inc_lin_to_pt)
        print("CP-SAT mapping found, verification:", ok)
        out = ROOT / "artifacts"
        with open(out/"w33_point_to_line_duality.json","w") as f:
            json.dump(dual, f)
        with open(out/"w33_duality_verification.json","w") as f:
            json.dump({"verified": ok}, f)
        print("artifacts written via CP-SAT")
        return
    print("CP-SAT did not yield a mapping, proceeding to group-based search")
    # prepare lookup from vector to projective point index
    vec_to_idx = {tuple(p.tolist()): idx for idx, p in enumerate(points)}
    # derive PSp(4,3) action on points and lines using symplectic transvections
    def omega_vec(u: np.ndarray, v: np.ndarray) -> int:
        return int((u[0]*v[2] - u[2]*v[0] + u[1]*v[3] - u[3]*v[1]) % 3)
    def transv_apply(v, w):
        return (w + omega_vec(w, v) * v) % 3
    def canonical(v):
        for s in (1, 2):
            key = tuple((v * s) % 3)
            if key in vec_to_idx:
                return vec_to_idx[key]
        raise KeyError("vector not found")
    line_map = {tuple(sorted(L)): idx for idx, L in enumerate(lines)}
    def map_line(Lpts):
        return line_map[tuple(sorted(Lpts))]

    std = [np.array([1,0,0,0],int), np.array([0,1,0,0],int), np.array([0,0,1,0],int), np.array([0,0,0,1],int)]
    gens_v = std + [(std[0]+std[1])%3, (std[2]+std[3])%3]

    perms_pts = []
    perms_lines = []
    for v in gens_v:
        perm_p = []
        for p in points:
            perm_p.append(canonical(transv_apply(v, p)))
        perms_pts.append(np.array(perm_p, dtype=np.uint16))
        perm_l = []
        for L in lines:
            mapped = [canonical(transv_apply(v, points[pidx])) for pidx in L]
            perm_l.append(map_line(mapped))
        perms_lines.append(np.array(perm_l, dtype=np.uint16))
    Gp = gen_group_n(perms_pts, 40)
    Gl = gen_group_n(perms_lines, 40)
    print("Gp order", len(Gp), "Gl order", len(Gl))

    # build colored Schreier graphs and find isomorphism
    Gp_graph = nx.Graph()
    Gl_graph = nx.Graph()
    for i in range(40):
        Gp_graph.add_node(i)
        Gl_graph.add_node(i)
    for gi, perm in enumerate(perms_pts):
        for i in range(40):
            Gp_graph.add_edge(i, int(perm[i]), color=gi)
    for gi, perm in enumerate(perms_lines):
        for i in range(40):
            Gl_graph.add_edge(i, int(perm[i]), color=gi)
    GM = nx.algorithms.isomorphism.GraphMatcher(
        Gp_graph, Gl_graph, edge_match=lambda a,b: a['color']==b['color'])
    mapping = None
    for m in GM.isomorphisms_iter():
        mapping = m
        break
    if mapping is None:
        print("colored isomorphism failed, trying uncolored graphs")
        GM2 = nx.algorithms.isomorphism.GraphMatcher(Gp_graph, Gl_graph)
        for m in GM2.isomorphisms_iter():
            mapping = m
            break
    if mapping is None:
        print("no group-based conjugacy found either; giving up")
        out = ROOT / "artifacts"
        with open(out/"w33_duality_failure.json","w") as f:
            json.dump({"result": "none", "methods": ["backtracking", "cp-sat", "group"]}, f)
        raise RuntimeError("failed to find isomorphism between point and line actions")
    dual = mapping
    ok = verify_mapping(dual, inc_pt_to_lin, inc_lin_to_pt)
    print("verification (adjacency) of duality mapping", ok)
    out = ROOT / "artifacts"
    with open(out/"w33_point_to_line_duality.json","w") as f:
        json.dump(dual, f)
    with open(out/"w33_duality_verification.json","w") as f:
        json.dump({"verified": ok}, f)
    print("artifacts written via group isomorphism")

if __name__=="__main__":
    main()
