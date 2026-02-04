#!/usr/bin/env python3
"""
Derive a W33-native “fusion law” for E8 root brackets using the edge↔root bridge.

Inputs:
  - artifacts/e8_root_metadata_table.json
    (contains root_orbit = canonical E8 simple-root coefficients, and edge=(u,v))

Core facts (proved by computation here):
  1) The 240 W33 edges partition into 40 W33 lines (K4's); each line has 6 edges.
  2) The 6 roots on a line form an A2 root system.
  3) For two distinct lines L,M, the 36 cross inner products are always either:
       - commuting:  (zeros,neg1,pos1) = (36,0,0)
       - coupled:    (zeros,neg1,pos1) = (12,12,12)
  4) For any coupled line-pair (L,M), the 12 pairs (α∈A2(L), β∈A2(M)) with α·β=-1
     produce 12 distinct roots α+β that split as exactly two full A2’s (two lines),
     6 roots each.

This gives a finite-geometry bracket skeleton:
  - [A2(L), A2(M)] = 0  iff L commutes with M
  - otherwise, [A2(L), A2(M)] lands in A2(N1) ⊕ A2(N2)
    where {N1,N2} is a deterministic unordered pair of lines.

Outputs:
  - artifacts/w33_line_fusion_law.json
  - artifacts/w33_line_fusion_law.md
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


def _ip(c: Tuple[int, ...], d: Tuple[int, ...], C: np.ndarray) -> int:
    return int(sum(c[i] * int(C[i, j]) * d[j] for i in range(8) for j in range(8)))


def _build_w33_adj_points() -> np.ndarray:
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
    common = [k for k in range(adj.shape[0]) if adj[u, k] and adj[v, k]]
    if len(common) != 2:
        raise RuntimeError(
            f"Edge ({u},{v}) has {len(common)} common neighbors (expected 2)"
        )
    return tuple(sorted([u, v, common[0], common[1]]))


def _find_special_vertex_for_line(
    line: Tuple[int, int, int, int],
    edges: List[Tuple[int, int]],
    root_by_edge: Dict[Tuple[int, int], Tuple[int, ...]],
    C: np.ndarray,
) -> int:
    verts = list(line)
    # In every line, exactly one vertex has the property that its 3 incident edges
    # are pairwise inner-product -1 (a triangle in the ip=-1 edge-edge graph).
    for v in verts:
        star = [e for e in edges if v in e]
        if len(star) != 3:
            raise RuntimeError("Line edge list inconsistent")
        ips = []
        for a, b in combinations(star, 2):
            ips.append(_ip(root_by_edge[a], root_by_edge[b], C))
        if ips == [-1, -1, -1]:
            return v
    raise RuntimeError(f"No special vertex found for line {line}")


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
    meta = json.loads(
        (ROOT / "artifacts" / "e8_root_metadata_table.json").read_text(encoding="utf-8")
    )
    rows = meta["rows"]

    root_by_edge: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    edge_by_root: Dict[Tuple[int, ...], Tuple[int, int]] = {}
    for row in rows:
        e = tuple(sorted((int(row["edge"][0]), int(row["edge"][1]))))
        r = tuple(int(x) for x in row["root_orbit"])
        root_by_edge[e] = r
        edge_by_root[r] = e
    if len(root_by_edge) != 240 or len(edge_by_root) != 240:
        raise RuntimeError("Expected 240 root↔edge rows")

    C = _cartan_unit_e8_sage_order()
    adj_pts = _build_w33_adj_points()

    # Partition edges into 40 lines.
    edges_by_line: Dict[Tuple[int, int, int, int], List[Tuple[int, int]]] = defaultdict(
        list
    )
    for u, v in root_by_edge:
        edges_by_line[_edge_line(adj_pts, u, v)].append((u, v))
    lines = sorted(edges_by_line.keys())
    if len(lines) != 40:
        raise RuntimeError(f"Expected 40 lines; got {len(lines)}")
    if any(len(edges_by_line[L]) != 6 for L in lines):
        raise RuntimeError("Expected 6 edges per line")

    line_index = {L: i for i, L in enumerate(lines)}

    # Per-line: identify special vertex and A2 check.
    per_line: List[Dict[str, object]] = []
    for L in lines:
        elist = sorted(tuple(sorted(e)) for e in edges_by_line[L])
        vstar = _find_special_vertex_for_line(L, elist, root_by_edge, C)

        roots6 = [root_by_edge[e] for e in elist]
        ips = Counter()
        norms = []
        for i in range(6):
            norms.append(_ip(roots6[i], roots6[i], C))
            for j in range(i + 1, 6):
                ips[_ip(roots6[i], roots6[j], C)] += 1
        if set(norms) != {2} or ips != Counter({-2: 3, -1: 6, 1: 6}):
            raise RuntimeError(f"Line {L} failed A2 check")

        per_line.append(
            {
                "i": int(line_index[L]),
                "line": list(L),
                "special_vertex": int(vstar),
                "edges": [list(e) for e in elist],
            }
        )

    # Build commutation graph on lines and fusion law on coupled pairs.
    comm = np.zeros((40, 40), dtype=bool)
    fusion: Dict[str, List[int]] = {}
    pattern_counts = Counter()
    coupled_outline_pattern = Counter()

    for i in range(40):
        for j in range(i + 1, 40):
            L1, L2 = lines[i], lines[j]
            c = Counter()
            for e1 in edges_by_line[L1]:
                r1 = root_by_edge[tuple(sorted(e1))]
                for e2 in edges_by_line[L2]:
                    r2 = root_by_edge[tuple(sorted(e2))]
                    c[_ip(r1, r2, C)] += 1
            patt = (int(c.get(0, 0)), int(c.get(-1, 0)), int(c.get(1, 0)))
            pattern_counts[patt] += 1

            if patt == (36, 0, 0):
                comm[i, j] = comm[j, i] = True
                continue
            if patt != (12, 12, 12):
                raise RuntimeError(
                    f"Unexpected line-pair cross-ip pattern: {patt} for {L1},{L2}"
                )

            # Coupled: compute output lines from the 12 ip=-1 pairs (unique outputs).
            out_lines = Counter()
            for e1 in edges_by_line[L1]:
                r1 = root_by_edge[tuple(sorted(e1))]
                for e2 in edges_by_line[L2]:
                    r2 = root_by_edge[tuple(sorted(e2))]
                    if _ip(r1, r2, C) != -1:
                        continue
                    r3 = tuple(r1[k] + r2[k] for k in range(8))
                    e3 = edge_by_root[r3]
                    L3 = _edge_line(adj_pts, e3[0], e3[1])
                    out_lines[L3] += 1

            if len(out_lines) != 2 or set(out_lines.values()) != {6}:
                raise RuntimeError(
                    f"Coupled pair {L1},{L2} did not yield 2×6 outputs: {out_lines}"
                )
            coupled_outline_pattern[
                (len(out_lines), tuple(sorted(out_lines.values())))
            ] += 1

            outs = sorted(line_index[L] for L in out_lines.keys())
            fusion[f"{i},{j}"] = outs

    # Sanity counts.
    srg = _srg_params(comm)
    if srg != {"n": 40, "k": 12, "lambda": 2, "mu": 4}:
        raise RuntimeError(f"Unexpected SRG params for line commutation graph: {srg}")

    # Per-line degrees in commutation graph.
    comm_degs = comm.sum(axis=1).astype(int).tolist()
    if set(comm_degs) != {12}:
        raise RuntimeError(
            f"Expected commutation degree 12; got {sorted(set(comm_degs))}"
        )

    status = "ok"
    out = {
        "status": status,
        "counts": {
            "lines": 40,
            "edges": 240,
            "commuting_line_pairs": int(pattern_counts[(36, 0, 0)]),
            "coupled_line_pairs": int(pattern_counts[(12, 12, 12)]),
        },
        "per_line": per_line,
        "line_pair_cross_ip_patterns": {
            str(k): int(v) for k, v in pattern_counts.items()
        },
        "coupled_output_line_pattern": {
            str(k): int(v) for k, v in coupled_outline_pattern.items()
        },
        "line_commutation_graph": {
            "definition": "Lines adjacent iff all 36 cross inner-products are 0.",
            "srg": srg,
            "edge_count": int(comm.sum() // 2),
        },
        "fusion_law": {
            "definition": (
                "For each coupled line-pair (i<j), record the two output line indices "
                "{k,l} such that all 12 roots (α+β) for α·β=-1 land in A2(k)⊕A2(l)."
            ),
            "pairs": fusion,
        },
        "sources": {"root_edge_table": "artifacts/e8_root_metadata_table.json"},
    }

    out_json = ROOT / "artifacts" / "w33_line_fusion_law.json"
    out_md = ROOT / "artifacts" / "w33_line_fusion_law.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# W33 line fusion law (E8 bracket skeleton)\n")
    md.append(f"- status: `{status}`")
    md.append(f"- lines: `{out['counts']['lines']}`")
    md.append(f"- edges: `{out['counts']['edges']}`")
    md.append(f"- commuting_line_pairs: `{out['counts']['commuting_line_pairs']}`")
    md.append(f"- coupled_line_pairs: `{out['counts']['coupled_line_pairs']}`\n")
    md.append("## Cross-ip patterns between lines\n")
    md.append(f"- patterns: `{out['line_pair_cross_ip_patterns']}`\n")
    md.append("## Coupled output structure\n")
    md.append(
        "- For every coupled pair, the 12 α·β=-1 pairs produce 12 distinct outputs split as 2×6 roots = two full lines."
    )
    md.append(f"- pattern counts: `{out['coupled_output_line_pattern']}`\n")
    md.append("## Line commutation graph\n")
    md.append(f"- SRG params: `{srg}`")
    md.append(f"- edge_count: `{out['line_commutation_graph']['edge_count']}`\n")
    md.append(f"- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(
        f"ok commuting_pairs={out['counts']['commuting_line_pairs']} coupled_pairs={out['counts']['coupled_line_pairs']}"
    )


if __name__ == "__main__":
    main()
