#!/usr/bin/env sage
"""
Sage cross-check: W33 lines form A2 subsystems under the E8 root↔edge bridge.

Verifies (independently of numpy code):
  - W33 has 40 “lines” (K4 cliques via common-neighbor completion), each with 6 edges.
  - Using artifacts/e8_root_metadata_table.json (root_orbit = E8 simple-root coeffs),
    each line’s 6 roots have pairwise inner products:
      {-2:3, -1:6, +1:6}.
  - For any two distinct lines, the 36 cross inner products are always either:
      (36,0,0) or (12,12,12) for counts of (ip=0, ip=-1, ip=+1).
  - The “commutation graph” on lines (edge iff all 36 cross ips are 0) is SRG(40,12,2,4).

Outputs:
  - artifacts/sage_verify_w33_lines_as_a2.json
  - artifacts/sage_verify_w33_lines_as_a2.md
"""

from sage.all import *
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations

ROOT_JSON = "artifacts/e8_root_metadata_table.json"
OUT_JSON = "artifacts/sage_verify_w33_lines_as_a2.json"
OUT_MD = "artifacts/sage_verify_w33_lines_as_a2.md"


def load_root_by_edge():
    obj = json.load(open(ROOT_JSON, "r"))
    root_by_edge = {}
    for row in obj["rows"]:
        u, v = row["edge"]
        e = (min(u, v), max(u, v))
        r = tuple(int(x) for x in row["root_orbit"])
        root_by_edge[e] = r
    if len(root_by_edge) != 240:
        raise RuntimeError("expected 240 edge->root entries")
    return root_by_edge


def main():
    root_by_edge = load_root_by_edge()

    # Build W33 in the SAME vertex labeling used by the repo artifacts:
    # projective points in F3^4, canonicalized by scaling so the first nonzero is 1,
    # discovered in lexicographic order without sorting (matches numpy scripts).
    pts = []
    seen = set()
    for a in [0, 1, 2]:
        for b in [0, 1, 2]:
            for c in [0, 1, 2]:
                for d in [0, 1, 2]:
                    if a == b == c == d == 0:
                        continue
                    v = [a, b, c, d]
                    # normalize
                    for i in range(4):
                        if v[i] != 0:
                            inv = 1 if v[i] == 1 else 2
                            v = [(inv * x) % 3 for x in v]
                            break
                    t = tuple(v)
                    if t not in seen:
                        seen.add(t)
                        pts.append(t)
    if len(pts) != 40:
        raise RuntimeError("expected 40 points")

    def omega(x, y):
        return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3

    adj = matrix(GF(2), 40, 40)
    edge_list = []
    for i in range(40):
        for j in range(i + 1, 40):
            if omega(pts[i], pts[j]) == 0:
                adj[i, j] = 1
                adj[j, i] = 1
                edge_list.append((i, j))
    if len(edge_list) != 240:
        raise RuntimeError(f"expected 240 edges; got {len(edge_list)}")

    # Lines via common-neighbor completion: for each edge, two common neighbors => K4
    lines = set()
    for u, v in edge_list:
        common = [k for k in range(40) if adj[u, k] and adj[v, k]]
        if len(common) != 2:
            raise RuntimeError("edge should have exactly 2 common neighbors in SRG(40,12,2,4)")
        L = tuple(sorted([u, v, common[0], common[1]]))
        lines.add(L)
    lines = sorted(lines)
    if len(lines) != 40:
        raise RuntimeError(f"expected 40 lines; got {len(lines)}")

    # Group edges by line
    edges_by_line = defaultdict(list)
    for u, v in edge_list:
        common = [k for k in range(40) if adj[u, k] and adj[v, k]]
        L = tuple(sorted([u, v, common[0], common[1]]))
        edges_by_line[L].append((u, v))
    if any(len(edges_by_line[L]) != 6 for L in lines):
        raise RuntimeError("expected 6 edges per line")

    # E8 Cartan matrix in Sage canonical order; inner product in simple-root coeff basis: v*C*w
    E8 = RootSystem(["E", 8])
    C = matrix(ZZ, E8.cartan_type().cartan_matrix())

    def ip(a, b):
        va = vector(ZZ, a)
        vb = vector(ZZ, b)
        return int(va * C * vb)

    # Per-line A2 check
    a2_ok = True
    a2_fail = []
    for L in lines:
        elist = edges_by_line[L]
        roots = [root_by_edge[e] for e in elist]
        norms = set(ip(r, r) for r in roots)
        ips = Counter()
        for i in range(6):
            for j in range(i + 1, 6):
                ips[ip(roots[i], roots[j])] += 1
        if norms != {2} or ips != Counter({-2: 3, -1: 6, 1: 6}):
            a2_ok = False
            a2_fail.append({"line": L, "norms": sorted(list(norms)), "ip_counts": dict(ips)})
            break

    # Line-pair patterns + commutation graph
    patterns = Counter()
    m = len(lines)
    comm_edges = []
    for i in range(m):
        for j in range(i + 1, m):
            L1, L2 = lines[i], lines[j]
            c = Counter()
            for e1 in edges_by_line[L1]:
                r1 = root_by_edge[e1]
                for e2 in edges_by_line[L2]:
                    r2 = root_by_edge[e2]
                    c[ip(r1, r2)] += 1
            patt = (c.get(0, 0), c.get(-1, 0), c.get(1, 0))
            patterns[patt] += 1
            if patt == (36, 0, 0):
                comm_edges.append((i, j))
            elif patt != (12, 12, 12):
                raise RuntimeError(f"unexpected cross-ip pattern {patt}")

    G = Graph(comm_edges)
    G.add_vertices(range(m))
    degs = G.degree_sequence()
    deg_set = sorted(set(degs))
    # SRG check: degrees, common neighbors
    if deg_set != [12]:
        raise RuntimeError(f"expected 12-regular; got {deg_set}")
    lambdas = set()
    mus = set()
    for i in range(m):
        for j in range(i + 1, m):
            cn = len(set(G.neighbors(i)) & set(G.neighbors(j)))
            if G.has_edge(i, j):
                lambdas.add(cn)
            else:
                mus.add(cn)
    srg = {"n": int(m), "k": 12, "lambda": int(list(lambdas)[0]), "mu": int(list(mus)[0])}

    status = "ok"
    if not a2_ok:
        status = "fail"
    if patterns != Counter({(12, 12, 12): 540, (36, 0, 0): 240}):
        status = "fail"
    if srg != {"n": 40, "k": 12, "lambda": 2, "mu": 4}:
        status = "fail"

    report = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "counts": {"lines": 40, "edges": 240},
        "per_line_a2": {"ok": a2_ok, "first_failure": a2_fail[0] if a2_fail else None},
        "line_pair_patterns": {str(k): int(v) for k, v in patterns.items()},
        "commutation_graph": {"srg": srg, "edge_count": int(G.size())},
    }

    def to_py(o):
        if isinstance(o, Integer):
            return int(o)
        if isinstance(o, (list, tuple)):
            return [to_py(x) for x in o]
        if isinstance(o, dict):
            return {str(k): to_py(v) for k, v in o.items()}
        return o

    os.makedirs("artifacts", exist_ok=True)
    json.dump(to_py(report), open(OUT_JSON, "w"), indent=2, sort_keys=True)

    md = []
    md.append("# Sage verify: W33 lines as A2 subsystems")
    md.append("")
    md.append(f"- status: `{status}`")
    md.append(f"- lines: `{report['counts']['lines']}`")
    md.append(f"- edges: `{report['counts']['edges']}`")
    md.append(f"- A2 per-line ok: `{a2_ok}`")
    md.append(f"- line-pair patterns: `{report['line_pair_patterns']}`")
    md.append(f"- commutation graph SRG: `{srg}`")
    md.append(f"- JSON: `{OUT_JSON}`")
    open(OUT_MD, "w").write("\n".join(md) + "\n")

    print(f"status={status}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
