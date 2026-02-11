#!/usr/bin/env python3
"""Search all A2 subsystems for one that yields a divisible S for a given cycle."""
from __future__ import annotations

import json
from pathlib import Path


def _dot_int(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return sum(int(a) * int(b) for a, b in zip(u, v, strict=True))


def inner_prod_doubled(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return _dot_int(u, v) // 4


def load_edge_root_map(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    m = {}
    for ent in data:
        vi = int(ent["v_i"])
        vj = int(ent["v_j"])
        coords = tuple(int(x) for x in ent["root_coords"])
        m[(vi, vj)] = coords
        m[(vj, vi)] = tuple(-x for x in coords)
    return m


def find_simple_roots_in_a2(a2_indices, root_index_to_coords):
    roots = {
        i: root_index_to_coords[i] for i in a2_indices if i in root_index_to_coords
    }
    for i, a in roots.items():
        for j, b in roots.items():
            if i >= j:
                continue
            ip = inner_prod_doubled(a, b)
            if ip == -1:
                return a, b, i, j
    raise RuntimeError("No simple root pair found in A2 indices")


def main():
    cycles = json.loads(
        Path(
            "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
        ).read_text(encoding="utf-8")
    )
    cycle = cycles[0]
    cyc = list(map(int, cycle["cycle_vertices"].split(",")))
    edges = [(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))]

    edge_map = load_edge_root_map(Path("artifacts/edge_root_bijection_canonical.json"))
    root_index_map = {}
    for ent in json.loads(
        Path("artifacts/edge_root_bijection_canonical.json").read_text(encoding="utf-8")
    ):
        idx = int(ent["root_index"])
        coords = tuple(int(x) for x in ent["root_coords"])
        if idx not in root_index_map:
            root_index_map[idx] = coords

    a2_data = json.loads(
        Path("artifacts/a2_4_decomposition.json").read_text(encoding="utf-8")
    )
    a2_list = a2_data.get("a2_4_solution") or []
    all_a2 = a2_list

    print("a2 candidates", len(all_a2))
    good = []
    for idx, a2 in enumerate(all_a2):
        try:
            alpha, beta, ai, bi = find_simple_roots_in_a2(a2, root_index_map)
        except Exception:
            continue
        rlist = []
        ok = True
        for a, b in edges:
            key = (a, b)
            if key not in edge_map:
                ok = False
                break
            rlist.append(edge_map[key])
        if not ok:
            continue
        tvals = [
            inner_prod_doubled(r, alpha) - inner_prod_doubled(r, beta) for r in rlist
        ]
        S = sum(tvals)
        if S % 3 == 0:
            good.append((idx, a2, ai, bi, S, (S // 3) % 3))
    print("good count", len(good))
    for g in good[:20]:
        print(g)


if __name__ == "__main__":
    main()
