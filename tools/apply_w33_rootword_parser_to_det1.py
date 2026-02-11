#!/usr/bin/env python3
"""Apply W33RootwordParser to all cycles in det1_orbit_cycles.json and summarize."""
from __future__ import annotations

import csv
import json

# ensure repo root is on sys.path so `tools` can be imported when run as a script
import sys
from collections import Counter
from pathlib import Path
from pathlib import Path as _Path
from typing import List

sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

from tools.w33_rootword_uv_parser import W33RootwordParser


def oriented_root_for_edge(edge_to_root_map, a: int, b: int):
    # try exact orientation first
    if (a, b) in edge_to_root_map:
        return tuple(edge_to_root_map[(a, b)])
    if (b, a) in edge_to_root_map:
        return tuple(-x for x in edge_to_root_map[(b, a)])
    return None


def main():
    p = W33RootwordParser()
    # report current edge->root mapping coverage
    try:
        edges_present = set(tuple(sorted(e)) for e in p.edge_to_root.keys())
        print("Edge->root canonical entries (unique):", len(edges_present))
    except Exception:
        pass

    cycles_json = Path("analysis/minimal_commutator_cycles/det1_orbit_cycles.json")
    out_dir = Path("analysis/minimal_commutator_cycles")
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(cycles_json.read_text(encoding="utf-8"))
    cycles = data.get("canonical_cycles", [])

    rows = []
    stats = Counter()
    missing_edge_counter = Counter()
    for idx, c in enumerate(cycles):
        cyc = c.get("cycle")
        if not cyc or len(cyc) < 2:
            stats["invalid_cycle"] += 1
            continue
        n = len(cyc)
        rootword = []
        missing_edge = False
        missing_edge_pair = None
        for i in range(n):
            a = int(cyc[i])
            b = int(cyc[(i + 1) % n])
            r = oriented_root_for_edge(p.edge_to_root, a, b)
            if r is None:
                missing_edge = True
                missing_edge_pair = (a, b)
                break
            rootword.append(list(r))
        if missing_edge:
            stats["missing_edge_root"] += 1
            if missing_edge_pair is not None:
                missing_edge_counter[missing_edge_pair] += 1
            rows.append(
                {
                    "idx": idx,
                    "cycle": cyc,
                    "status": "missing_edge_root",
                    "missing_edge": missing_edge_pair,
                }
            )
            continue
        try:
            out = p.parse(rootword)
            k = out["k_canonical"]
            rows.append(
                {
                    "idx": idx,
                    "cycle": cyc,
                    "status": "ok",
                    "k_canonical": int(k),
                    "n12_pair": out["n12_pair"],
                    "u_canonical": out["u_canonical"],
                    "v_canonical": out["v_canonical"],
                }
            )
            stats["ok"] += 1
            stats[f"k_{k}"] += 1
        except Exception as e:
            stats["parse_error"] += 1
            rows.append(
                {"idx": idx, "cycle": cyc, "status": "parse_error", "error": str(e)}
            )

    out_json = out_dir / "w33_uv_parser_det1_results.json"
    out_csv = out_dir / "w33_uv_parser_det1_results.csv"

    out_json.write_text(
        json.dumps({"rows": rows, "stats": dict(stats)}, indent=2), encoding="utf-8"
    )

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "idx",
                "status",
                "k_canonical",
                "n12_pair",
                "u_canonical",
                "v_canonical",
                "cycle",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.get("idx"),
                    r.get("status"),
                    r.get("k_canonical"),
                    r.get("n12_pair"),
                    r.get("u_canonical"),
                    r.get("v_canonical"),
                    ",".join(str(x) for x in r.get("cycle")),
                ]
            )

    # write missing edges summary
    if missing_edge_counter:
        miss_json = out_dir / "w33_uv_parser_det1_missing_edges.json"
        miss_csv = out_dir / "w33_uv_parser_det1_missing_edges.csv"
        miss_data = [
            {"edge": f"{a},{b}", "count": c}
            for (a, b), c in missing_edge_counter.items()
        ]
        miss_json.write_text(
            json.dumps({"missing_edges": miss_data}, indent=2), encoding="utf-8"
        )
        with miss_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["edge_a", "edge_b", "count"])
            for (a, b), c in missing_edge_counter.most_common():
                w.writerow([a, b, c])
        print("Wrote", miss_json, miss_csv)

    print("Summary stats:", dict(stats))
    print("Wrote", out_json, out_csv)


if __name__ == "__main__":
    main()
