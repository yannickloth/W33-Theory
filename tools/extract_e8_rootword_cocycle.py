#!/usr/bin/env python3
"""Extract E8 root-word cocycle via projection to an A2 factor.

For each cycle (ordered list of vertices), compute the oriented E8 root on each
edge, pick an A2 simple-root pair from artifacts/a2_4_decomposition.json, and
compute S = sum_i ((r_i,alpha) - (r_i,beta)). If S is divisible by 3, then
s = (S/3) mod 3 is reported as the Z3 cocycle witness for the cycle.

Outputs:
 - analysis/minimal_commutator_cycles/e8_rootword_cocycle.json
 - analysis/minimal_commutator_cycles/e8_rootword_cocycle.csv

"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


def _dot_int(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return sum(int(a) * int(b) for a, b in zip(u, v, strict=True))


def load_cycles(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_edge_root_map(path: Path) -> Dict[Tuple[int, int], Tuple[int, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    m = {}
    # support two formats: dict mapping "(i, j)" -> coords, or list of entries with 'v_i','v_j','root_coords'
    if isinstance(data, dict):
        for k, coords in data.items():
            # parse key like "(i, j)"
            if isinstance(k, str) and k.startswith("(") and "," in k:
                s = k.strip()[1:-1]
                vi_s, vj_s = s.split(",")
                vi = int(vi_s.strip())
                vj = int(vj_s.strip())
            else:
                raise RuntimeError("Unsupported edge_to_root dict key format")
            coords_t = tuple(int(x) for x in coords)
            m[(vi, vj)] = coords_t
            m[(vj, vi)] = tuple(-x for x in coords_t)
    else:
        for ent in data:
            vi = int(ent["v_i"])
            vj = int(ent["v_j"])
            coords = tuple(int(x) for x in ent["root_coords"])
            m[(vi, vj)] = coords
            m[(vj, vi)] = tuple(-x for x in coords)
    return m


def load_a2_solution(path: Path, idx: int = 0) -> List[int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sol = data.get("a2_4_solution")
    if not sol or idx >= len(sol):
        raise RuntimeError("No A2 solution at index")
    return sol[idx]


def inner_prod_doubled(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    # undoubled inner product (u,v) = _dot_int(u,v) // 4
    return _dot_int(u, v) // 4


def find_simple_roots_in_a2(
    a2_indices: List[int], root_index_to_coords: Dict[int, Tuple[int, ...]]
):
    # pick two roots with (alpha,beta) == -1
    roots = {i: root_index_to_coords[i] for i in a2_indices}
    for i, a in roots.items():
        for j, b in roots.items():
            if i >= j:
                continue
            ip = inner_prod_doubled(a, b)
            if ip == -1:
                return a, b, i, j
    raise RuntimeError("No simple root pair found in A2 indices")


def canonical_cycle(cycle: List[int]) -> Tuple[int, ...]:
    # canonicalize up to rotation and reversal; return smallest lex tuple
    n = len(cycle)
    rots = [tuple(cycle[i:] + cycle[:i]) for i in range(n)]
    rev = list(reversed(cycle))
    rots += [tuple(rev[i:] + rev[:i]) for i in range(n)]
    return min(rots)


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--cycles-json",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
        ),
    )
    p.add_argument(
        "--edge-root-json",
        type=Path,
        default=Path("artifacts/edge_to_e8_root_combined.json"),
    )
    p.add_argument(
        "--a2-solution-json",
        type=Path,
        default=Path("artifacts/a2_4_decomposition.json"),
    )
    p.add_argument("--a2-index", type=int, default=0)
    p.add_argument(
        "--minimal-cycles-json",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
        ),
    )
    p.add_argument(
        "--out-dir", type=Path, default=Path("analysis/minimal_commutator_cycles")
    )
    args = p.parse_args()

    loaded_cycles = load_cycles(args.cycles_json)
    if isinstance(loaded_cycles, dict):
        if "canonical_cycles" in loaded_cycles:
            cycles = loaded_cycles["canonical_cycles"]
        elif "cycles" in loaded_cycles:
            cycles = loaded_cycles["cycles"]
        else:
            raise RuntimeError(
                "Unsupported cycles JSON structure; expected list or dict with canonical_cycles key"
            )
    else:
        cycles = loaded_cycles
    edge_root_map = load_edge_root_map(args.edge_root_json)
    a2_idxs = load_a2_solution(args.a2_solution_json, args.a2_index)

    # Build root_index -> coords map (prefer edge-bijection-format, else fallback to canonical bijection)
    root_index_map: Dict[int, Tuple[int, ...]] = {}
    try:
        er_data = json.loads(args.edge_root_json.read_text(encoding="utf-8"))
        if isinstance(er_data, list):
            for ent in er_data:
                idx = int(ent["root_index"])
                coords = tuple(int(x) for x in ent["root_coords"])
                if idx not in root_index_map:
                    root_index_map[idx] = coords
    except Exception:
        pass
    if not root_index_map:
        # fallback to canonical bijection file
        for ent in json.loads(
            Path("artifacts/edge_root_bijection_canonical.json").read_text(
                encoding="utf-8"
            )
        ):
            idx = int(ent["root_index"])
            coords = tuple(int(x) for x in ent["root_coords"])
            if idx not in root_index_map:
                root_index_map[idx] = coords

    # Find simple roots
    alpha, beta, ai_idx, bi_idx = find_simple_roots_in_a2(a2_idxs, root_index_map)
    print("Using A2 simple roots indices", ai_idx, bi_idx)

    # Try to load minimal cycles mapping to attach curvature k if missing
    minimal_k_map = {}
    minimal_path = args.minimal_cycles_json
    if minimal_path.exists():
        try:
            minimal_entries = json.loads(minimal_path.read_text(encoding="utf-8"))
            for ent in minimal_entries:
                if "cycle_vertices" in ent and isinstance(ent["cycle_vertices"], str):
                    cyc_list = [
                        int(x)
                        for x in ent["cycle_vertices"].split(",")
                        if x.strip() != ""
                    ]
                elif "cycle" in ent and isinstance(ent["cycle"], list):
                    cyc_list = [int(x) for x in ent["cycle"]]
                else:
                    continue
                canonical = canonical_cycle(cyc_list)
                minimal_k_map[canonical] = ent.get("k")
        except Exception:
            pass

    rows = []
    stats = Counter()

    for c in cycles:
        # support multiple cycle formats: {'cycle_vertices': "1,2,3"} or {'cycle': [1,2,3]} or bare list
        if isinstance(c, dict) and "cycle_vertices" in c:
            cyc = list(map(int, c["cycle_vertices"].split(",")))
        elif isinstance(c, dict) and "cycle" in c:
            cyc = list(map(int, c["cycle"]))
        elif isinstance(c, list):
            cyc = list(map(int, c))
        else:
            raise RuntimeError("Unsupported cycle format")

        # canonicalize and attempt to get k from minimal cycles mapping if absent
        canonical = canonical_cycle(cyc)
        k_val = c.get("k") if isinstance(c, dict) else None
        if k_val is None:
            k_val = minimal_k_map.get(canonical)

        # ensure closed cycle (vertices list should be unique canonical)
        edges = [(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))]
        # gather root coords for oriented edges
        rlist = []
        missing = False
        missing_edge = None
        for a, b in edges:
            key = (a, b)
            if key not in edge_root_map:
                missing = True
                missing_edge = (a, b)
                break
            rlist.append(edge_root_map[key])
        if missing:
            rows.append(
                {
                    "id": c.get("id") if isinstance(c, dict) else None,
                    "k": k_val,
                    "cycle_vertices": ",".join(str(x) for x in cyc),
                    "divisible": False,
                    "reason": "missing_edge_root",
                    "missing_edge": (
                        f"{missing_edge[0]},{missing_edge[1]}" if missing_edge else None
                    ),
                }
            )
            stats["missing_edge_root"] += 1
            continue

        # compute t_i = (r_i,alpha) - (r_i,beta)
        tvals = [
            inner_prod_doubled(r, alpha) - inner_prod_doubled(r, beta) for r in rlist
        ]
        S = sum(tvals)
        divisible = S % 3 == 0
        s_div3 = (S // 3) % 3 if divisible else None
        rows.append(
            {
                "id": c.get("id") if isinstance(c, dict) else None,
                "k": k_val,
                "cycle_vertices": ",".join(str(x) for x in cyc),
                "S": int(S),
                "divisible": bool(divisible),
                "s_mod3": int(s_div3) if s_div3 is not None else None,
            }
        )
        stats["total"] += 1
        if divisible:
            stats[f"mod_{s_div3}"] += 1

    # compute match statistics vs curvature k when available
    total_with_k = sum(1 for r in rows if r.get("k") is not None)
    divisible_with_k = sum(
        1 for r in rows if (r.get("k") is not None and r.get("divisible"))
    )
    match_divisible = sum(
        1
        for r in rows
        if (
            r.get("k") is not None
            and r.get("divisible")
            and r.get("s_mod3") == r.get("k")
        )
    )

    stats["k_total"] = total_with_k
    stats["divisible_with_k"] = divisible_with_k
    stats["k_match_divisible"] = match_divisible
    stats["match_rate_divisible"] = (
        (match_divisible / divisible_with_k) if divisible_with_k else None
    )

    out = {
        "a2_index": args.a2_index,
        "a2_indices": a2_idxs,
        "ai_idx": ai_idx,
        "bi_idx": bi_idx,
        "rows": rows,
        "stats": dict(stats),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "e8_rootword_cocycle.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    # CSV
    with (args.out_dir / "e8_rootword_cocycle.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["id", "k", "cycle_vertices", "S", "divisible", "s_mod3"])
        for r in rows:
            writer.writerow(
                [
                    r.get("id"),
                    r.get("k"),
                    r.get("cycle_vertices"),
                    r.get("S"),
                    r.get("divisible"),
                    r.get("s_mod3"),
                ]
            )

    print("Wrote outputs to", args.out_dir)


if __name__ == "__main__":
    main()
