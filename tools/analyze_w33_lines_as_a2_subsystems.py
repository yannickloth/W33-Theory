#!/usr/bin/env python3
"""
Key structural bridge: W33 lines as A2 (=SU(3)) root subsystems inside E8.

Given the certified bijection (240 E8 roots ↔ 240 W33 edges), every W33 line
(a 4-point clique) has exactly 6 edges. Empirically (and provably, once the
bijection is fixed), those 6 edges correspond to the 6 roots of an A2 subsystem:

  - all roots have squared length 2
  - pairwise inner products among distinct roots are exactly {-2, -1, +1}
  - the inner-product(-1) graph on the 6 roots is two disjoint triangles

Even more: for any pair of W33 lines L,M, the 36 cross inner products between
their 6+6 roots are *always* one of two patterns:

  (A) all 36 are 0  -> the two A2 subsystems commute (no mixed brackets)
  (B) 12 each of -1, 0, +1 -> the two subsystems are “coupled”

The “commuting” relation on the 40 lines produces a graph on 40 vertices that
is itself SRG(40,12,2,4) — i.e. another W33.

This is the cleanest finite-geometry → Lie-algebra bridge we currently have:
W33 line geometry partitions the 240 root channels into 40 A2 blocks, and the
commuting graph of those A2 blocks reproduces W33 again.

Outputs:
  - artifacts/w33_lines_as_a2_subsystems.json
  - artifacts/w33_lines_as_a2_subsystems.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _cartan_unit_e8_sage_order() -> np.ndarray:
    # This is the Gram matrix (simple-root inner products) in the SAME canonical
    # ordering used by artifacts/e8_root_to_edge.json and the Sage closeout.
    return np.array(
        [
            [2, 0, -1, 0, 0, 0, 0, 0],
            [0, 2, 0, -1, 0, 0, 0, 0],
            [-1, 0, 2, -1, 0, 0, 0, 0],
            [0, -1, -1, 2, -1, 0, 0, 0],
            [0, 0, 0, -1, 2, -1, 0, 0],
            [0, 0, 0, 0, -1, 2, -1, 0],
            [0, 0, 0, 0, 0, -1, 2, -1],
            [0, 0, 0, 0, 0, 0, -1, 2],
        ],
        dtype=int,
    )


def _ip_simple_coeffs(c: Tuple[int, ...], d: Tuple[int, ...], C: np.ndarray) -> int:
    # integer exact inner product in simple-root coefficient basis: c^T C d
    return int(sum(c[i] * int(C[i, j]) * d[j] for i in range(8) for j in range(8)))


def _build_w33_adj_points() -> np.ndarray:
    # W33 points: projective points in F3^4; edge iff omega==0.
    F3 = [0, 1, 2]
    points = []
    seen = set()
    for vec in product(F3, repeat=4):
        if not any(vec):
            continue
        v = list(vec)
        for i in range(4):
            if v[i] != 0:
                inv = 1 if v[i] == 1 else 2
                v = [(x * inv) % 3 for x in v]
                break
        t = tuple(v)
        if t not in seen:
            seen.add(t)
            points.append(t)

    def omega(x, y) -> int:
        return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3

    n = len(points)
    if n != 40:
        raise RuntimeError(f"Expected 40 W33 points; got {n}")
    adj = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            if omega(points[i], points[j]) == 0:
                adj[i, j] = adj[j, i] = True
    return adj


def _edge_line(adj: np.ndarray, u: int, v: int) -> Tuple[int, int, int, int]:
    # In SRG(40,12,2,4), each edge has exactly two common neighbors -> its unique line.
    common = [k for k in range(adj.shape[0]) if adj[u, k] and adj[v, k]]
    if len(common) != 2:
        raise RuntimeError(
            f"Edge ({u},{v}) has {len(common)} common neighbors (expected 2)"
        )
    return tuple(sorted([u, v, common[0], common[1]]))


def _srg_params(adj: np.ndarray) -> Dict[str, int]:
    n = int(adj.shape[0])
    degs = adj.sum(axis=1).astype(int)
    if len(set(degs.tolist())) != 1:
        raise RuntimeError("Graph is not regular")
    k = int(degs[0])
    lambdas = set()
    mus = set()
    for i in range(n):
        for j in range(i + 1, n):
            cn = int(np.dot(adj[i].astype(int), adj[j].astype(int)))
            if adj[i, j]:
                lambdas.add(cn)
            else:
                mus.add(cn)
    if len(lambdas) != 1 or len(mus) != 1:
        raise RuntimeError(f"Not SRG-like: lambdas={sorted(lambdas)} mus={sorted(mus)}")
    return {
        "n": n,
        "k": k,
        "lambda": int(next(iter(lambdas))),
        "mu": int(next(iter(mus))),
    }


def main() -> None:
    # Load root↔edge mapping (root_orbit coords are canonical E8 simple coeffs).
    meta = json.loads(
        (ROOT / "artifacts" / "e8_root_metadata_table.json").read_text(encoding="utf-8")
    )
    rows = meta["rows"]
    root_by_edge: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    for row in rows:
        e = tuple(sorted((int(row["edge"][0]), int(row["edge"][1]))))
        r = tuple(int(x) for x in row["root_orbit"])
        root_by_edge[e] = r
    if len(root_by_edge) != 240:
        raise RuntimeError(f"Expected 240 edges in mapping; got {len(root_by_edge)}")

    C = _cartan_unit_e8_sage_order()

    # Build W33 and group the 240 edges into 40 lines (each line has 6 edges).
    adj_pts = _build_w33_adj_points()
    edges_by_line: Dict[Tuple[int, int, int, int], List[Tuple[int, int]]] = defaultdict(
        list
    )
    for u, v in root_by_edge:
        L = _edge_line(adj_pts, u, v)
        edges_by_line[L].append((u, v))
    if len(edges_by_line) != 40:
        raise RuntimeError(f"Expected 40 W33 lines; got {len(edges_by_line)}")
    if any(len(v) != 6 for v in edges_by_line.values()):
        bad = sorted((L, len(v)) for L, v in edges_by_line.items() if len(v) != 6)[:5]
        raise RuntimeError(f"Expected 6 edges per line; got mismatches: {bad}")

    # Verify each line is an A2 root system.
    a2_ok = True
    a2_failures: List[Dict[str, object]] = []
    for L, elist in edges_by_line.items():
        roots6 = [root_by_edge[e] for e in elist]
        norms = [(_ip_simple_coeffs(r, r, C)) for r in roots6]
        if set(norms) != {2}:
            a2_ok = False
            a2_failures.append({"line": list(L), "reason": "bad_norms", "norms": norms})
            continue
        ips = Counter()
        for i in range(6):
            for j in range(i + 1, 6):
                ips[_ip_simple_coeffs(roots6[i], roots6[j], C)] += 1
        # For an A2 root system (6 roots), the 15 pairwise inner products among distinct roots are:
        #   3 pairs at -2 (opposites), 6 pairs at -1, 6 pairs at +1
        if ips != Counter({-2: 3, -1: 6, 1: 6}):
            a2_ok = False
            a2_failures.append(
                {
                    "line": list(L),
                    "reason": "ip_multiset_mismatch",
                    "ip_counts": dict(ips),
                }
            )
            continue

    # Line-pair coupling patterns.
    lines = list(edges_by_line.keys())
    pair_patterns: Counter[Tuple[int, int, int]] = Counter()  # (zeros, neg1, pos1)
    inter_by_pattern: Counter[Tuple[int, int, int, int]] = (
        Counter()
    )  # (line_intersection, zeros, neg1, pos1)

    # Build commutation graph on the 40 lines: edge iff all 36 cross inner products are 0.
    m = len(lines)
    comm = np.zeros((m, m), dtype=bool)
    for i, L1 in enumerate(lines):
        for j in range(i + 1, m):
            L2 = lines[j]
            c = Counter()
            for e1 in edges_by_line[L1]:
                r1 = root_by_edge[e1]
                for e2 in edges_by_line[L2]:
                    r2 = root_by_edge[e2]
                    c[_ip_simple_coeffs(r1, r2, C)] += 1
            # Sanity: cross inner products should never be ±2 between distinct lines.
            if c.get(2, 0) or c.get(-2, 0):
                raise RuntimeError(
                    f"Unexpected ±2 cross ip between lines {L1} and {L2}: {dict(c)}"
                )

            zeros = int(c.get(0, 0))
            neg1 = int(c.get(-1, 0))
            pos1 = int(c.get(1, 0))
            pair_patterns[(zeros, neg1, pos1)] += 1
            inter_by_pattern[(len(set(L1) & set(L2)), zeros, neg1, pos1)] += 1

            if zeros == 36:
                comm[i, j] = comm[j, i] = True
            else:
                # Expected coupled pattern: 12 each of -1,0,+1.
                if (zeros, neg1, pos1) != (12, 12, 12):
                    raise RuntimeError(
                        f"Unexpected cross-ip pattern for lines {L1} and {L2}: {dict(c)}"
                    )

    srg = _srg_params(comm)
    status = (
        "ok" if a2_ok and srg == {"n": 40, "k": 12, "lambda": 2, "mu": 4} else "fail"
    )

    out = {
        "status": status,
        "counts": {
            "w33_lines": 40,
            "edges": 240,
            "edges_per_line": 6,
            "line_pairs": int(m * (m - 1) // 2),
        },
        "per_line_a2": {
            "ok": bool(a2_ok),
            "failures": a2_failures[:10],
            "expected_pairwise_ip_counts": {"-2": 3, "-1": 6, "1": 6},
        },
        "line_pair_patterns": {
            "(zeros,neg1,pos1) counts": {
                str(k): int(v) for k, v in pair_patterns.items()
            },
            "(intersection,zeros,neg1,pos1) counts": {
                str(k): int(v) for k, v in inter_by_pattern.items()
            },
        },
        "commutation_graph": {
            "definition": "Lines adjacent iff all 36 cross inner-products are 0 (so all mixed brackets vanish).",
            "srg": srg,
            "edge_count": int(comm.sum() // 2),
            "degree_set": sorted(set(comm.sum(axis=1).astype(int).tolist())),
        },
        "sources": {
            "root_edge_table": "artifacts/e8_root_metadata_table.json",
        },
    }

    out_json = ROOT / "artifacts" / "w33_lines_as_a2_subsystems.json"
    out_md = ROOT / "artifacts" / "w33_lines_as_a2_subsystems.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# W33 lines as A2 subsystems (E8 root/edge bridge)\n")
    md.append(f"- status: `{status}`")
    md.append(f"- lines: `{out['counts']['w33_lines']}`")
    md.append(f"- edges: `{out['counts']['edges']}`")
    md.append(f"- edges_per_line: `{out['counts']['edges_per_line']}`\n")
    md.append("## Per-line A2 check\n")
    md.append(f"- ok: `{out['per_line_a2']['ok']}`")
    md.append(
        f"- expected pairwise ip counts: `{out['per_line_a2']['expected_pairwise_ip_counts']}`"
    )
    if a2_failures:
        md.append(f"- failures (first): `{a2_failures[0]}`")
    md.append("\n## Line-pair cross-ip patterns\n")
    md.append("- Only two patterns occur across the 780 line pairs:")
    md.append("  - `(zeros,neg1,pos1)=(36,0,0)` : fully commuting")
    md.append("  - `(zeros,neg1,pos1)=(12,12,12)` : coupled (balanced)")
    md.append(f"- counts: `{out['line_pair_patterns']['(zeros,neg1,pos1) counts']}`\n")
    md.append("## Line commutation graph\n")
    md.append(f"- SRG params: `{srg}`")
    md.append(f"- edge_count: `{out['commutation_graph']['edge_count']}`")
    md.append(f"- degree_set: `{out['commutation_graph']['degree_set']}`\n")
    md.append(f"- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"status={status} a2_ok={a2_ok} srg={srg} patterns={dict(pair_patterns)}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
