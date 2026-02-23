#!/usr/bin/env python3
"""Analyze a given cycle in W33 as a 1D cellular automaton tape.

This helper loads the W33 geometry, restricts the GF(2) projector to the
specified cycle of edge indices, and determines whether the resulting
submatrix is circulant.  If it is, the script reports the corresponding
elementary CA rule number (0..255).  You can use this to test specific
cycles for rule‑110, rule‑30, etc., without scanning the entire graph.

Usage examples:

    # test a manually specified 3-cycle
    python scripts/ca_on_cycle.py --cycle 0,1,2

    # test the first cycle stored in a JSON file produced by
    # scripts/w33_universal_search.py
    python scripts/ca_on_cycle.py --input data/test_ca_cycles.json --index 0

The script prints the detected rule or indicates that the cycle is not
circulant.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np

# import helpers from the universal search module
from w33_universal_search import (
    build_graph_and_l1,
    gf2_projector,
    is_circulant,
    rule_from_row,
)


def analyze_cycle(indices: list[int]) -> int | None:
    edges, L1, edge_idx = build_graph_and_l1()
    U2 = gf2_projector(L1)
    M = U2[np.ix_(indices, indices)]
    if not is_circulant(M):
        return None
    return rule_from_row(M[0])


def main():
    parser = argparse.ArgumentParser(description="Compute CA rule of a cycle")
    parser.add_argument(
        "--cycle",
        type=str,
        help="comma-separated list of edge indices forming the cycle",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON file containing cycle records (edge lists)",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="index into the JSON cycle array when --input is used",
    )
    args = parser.parse_args()

    if args.input:
        data = json.load(open(args.input))
        try:
            record = data[args.index]
        except Exception as e:
            print(f"failed to read record {args.index} from {args.input}: {e}")
            return
        indices = record[0]
    elif args.cycle:
        indices = [int(x) for x in args.cycle.split(",") if x.strip()]
    else:
        parser.error("must supply --cycle or --input")
        return

    print(f"testing cycle of length {len(indices)}: {indices}")
    rule = analyze_cycle(indices)
    if rule is None:
        print("cycle is not circulant; no elementary CA rule applies")
    else:
        print(f"circulant with rule {rule}")


if __name__ == "__main__":
    main()
