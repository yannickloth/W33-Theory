#!/usr/bin/env python3
"""Inspect a JSON dump produced by `explore_vogel_plane.py`.

Print summaries of integer dimensions, classical labels (sl_n), t/chi
statistics, and polynomial locus counts.  Useful when scanning the Vogel
plane and wanting quick diagnostics.

Usage:
    python scripts/analyze_vogel_grid.py artifacts/vogel_grid4.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def main():
    if len(sys.argv) != 2:
        print("Usage: analyze_vogel_grid.py <grid.json>")
        sys.exit(1)
    path = Path(sys.argv[1])
    data: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))

    print(f"loaded {len(data)} triples from {path}")

    # integer dims
    ints = [d for d in data if isinstance(d.get("dim"), int)]
    print(f"integer adjoint dims: {len(ints)} entries")
    dims = sorted({d['dim'] for d in ints})
    print("  dims sample:", dims[:20], "...")

    # SL classical labels
    sl = [d for d in data if d.get('classical')]
    print(f"classical labels: {len(sl)} triples")
    cls_count = Counter(d.get('classical') for d in sl)
    print("  counts by classical type:", cls_count)

    # polynomial vanishing
    poly_keys = ['P_sl','P_osp','P_exc','P_Lie','P_Lie_refined']
    poly_cnt = Counter()
    for d in data:
        for k in poly_keys:
            if d.get(k):
                poly_cnt[k] += 1
    print("polynomial zeros:", poly_cnt)

    # t and chi distributions
    tcnt = Counter(d.get('t') for d in data if 't' in d)
    chit = Counter(d.get('chi_x1') for d in data if 'chi_x1' in d)
    print("t values sample:", tcnt.most_common(10))
    print("chi_x1 values sample:", chit.most_common(10))

    # dims for special invariants
    chi60 = [d for d in data if d.get('chi_x1') in ('60','-60')]
    print(f"triples with |chi_x1|=60: {len(chi60)}; dims=", sorted({d['dim'] for d in chi60}))

    # show the 728 triple(s)
    p728 = [d for d in data if d.get('dim') == 728]
    print(f"found {len(p728)} triples with dim 728 (should be 2): {p728}")

if __name__ == "__main__":
    main()
