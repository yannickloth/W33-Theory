#!/usr/bin/env python3
"""Aggregate per-A2 e8 det1 results: compute union/diversity of divisible matches.

Writes a small report to stdout and an aggregated per-cycle CSV.

By default this aggregates the pre-apply `e8_det1_combined_a2_*` results. Use
`--a2-prefix e8_det1_postapply_a2_` to aggregate the current post-apply state.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

ROOT = Path("analysis/minimal_commutator_cycles")


def build_default_out_path(a2_prefix: str) -> Path:
    # Common pattern: e8_det1_<kind>_a2_  -> e8_det1_<kind>_aggregated_summary.csv
    base = a2_prefix
    if base.endswith("a2_"):
        base = base[:-3]
    base = base.rstrip("_")
    return ROOT / f"{base}_aggregated_summary.csv"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--a2-prefix",
        default="e8_det1_combined_a2_",
        help="Directory prefix under analysis/minimal_commutator_cycles (default: e8_det1_combined_a2_)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output CSV path (default derived from --a2-prefix)",
    )
    args = ap.parse_args()

    a2_prefix = str(args.a2_prefix)
    a2_files = [ROOT / f"{a2_prefix}{i}" / "e8_rootword_cocycle.json" for i in range(4)]

    all_rows: List[List[Dict]] = []
    for p in a2_files:
        if not p.exists():
            raise FileNotFoundError(f"Missing per-A2 file: {p}")
        j = json.loads(p.read_text(encoding="utf-8"))
        all_rows.append(j["rows"])

    n = len(all_rows[0])
    assert all(len(r) == n for r in all_rows), "mismatched lengths across A2s"

    k_total = 0
    any_divisible = 0
    any_match = 0
    all_divisible = 0
    match_counts_by_cycle = [0] * n
    divisible_counts_by_cycle = [0] * n

    for i in range(n):
        # pick k from first A2 (they all should have same k if present)
        k = all_rows[0][i].get("k")
        if k is not None:
            k_total += 1
        found_divisible = False
        found_match = False
        all_div = True
        for a in range(4):
            r = all_rows[a][i]
            if r.get("divisible"):
                divisible_counts_by_cycle[i] += 1
                found_divisible = True
                if r.get("k") is not None and r.get("s_mod3") == r.get("k"):
                    found_match = True
                    match_counts_by_cycle[i] += 1
            else:
                all_div = False
        if found_divisible:
            any_divisible += 1
        if found_match:
            any_match += 1
        if all_div:
            all_divisible += 1

    print("Total cycles:", n)
    print("Cycles with k present (from parser):", k_total)
    print(
        "Cycles with at least one A2 divisible by 3 (S%3==0):",
        any_divisible,
        f"({any_divisible/n:.3%})",
    )
    print(
        "Cycles with at least one A2 where s_mod3 == k:",
        any_match,
        f"({any_match/n:.3%})",
    )
    print(
        "Cycles where all 4 A2s are divisible:",
        all_divisible,
        f"({all_divisible/n:.3%})",
    )

    # For cycles with k present, compute fraction where at least one A2 matches
    if k_total:
        # count cycles with k present and at least one match
        k_present_and_any_match = 0
        k_present_and_any_div = 0
        for i in range(n):
            k = all_rows[0][i].get("k")
            if k is None:
                continue
            if match_counts_by_cycle[i] > 0:
                k_present_and_any_match += 1
            if divisible_counts_by_cycle[i] > 0:
                k_present_and_any_div += 1
        print("Among cycles with k present (", k_total, "):", sep="")
        print(
            " - cycles where at least one A2 is divisible:",
            k_present_and_any_div,
            f"({k_present_and_any_div/k_total:.3%})",
        )
        print(
            " - cycles where at least one A2 matches s_mod3 == k:",
            k_present_and_any_match,
            f"({k_present_and_any_match/k_total:.3%})",
        )

    # also compute distribution of matches (how many A2s match per cycle)
    match_dist = Counter(match_counts_by_cycle)
    div_dist = Counter(divisible_counts_by_cycle)
    print("\nMatch count distribution (number of A2s matching per cycle):")
    for k in range(5):
        print(k, match_dist.get(k, 0))
    print("\nDivisible count distribution (number of A2s divisible per cycle):")
    for k in range(5):
        print(k, div_dist.get(k, 0))

    # Save a CSV of per-cycle summary
    out = args.out if args.out is not None else build_default_out_path(a2_prefix)
    with out.open("w", encoding="utf-8") as f:
        f.write("idx,cycle,k,any_divisible,any_match,divisible_count,match_count\n")
        for i in range(n):
            cyc = (
                all_rows[0][i]["cycle_vertices"]
                if "cycle_vertices" in all_rows[0][i]
                else ",".join(str(x) for x in all_rows[0][i].get("cycle"))
            )
            k = all_rows[0][i].get("k")
            f.write(
                f"{i},{cyc},{k},{divisible_counts_by_cycle[i] > 0},{match_counts_by_cycle[i] > 0},{divisible_counts_by_cycle[i]},{match_counts_by_cycle[i]}\n"
            )
    print("Wrote", out)


if __name__ == "__main__":
    main()
