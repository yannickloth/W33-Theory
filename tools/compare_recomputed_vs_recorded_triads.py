#!/usr/bin/env python3
"""Compare recomputed ray-based triads to recorded triad table.

Usage:
  py -3 tools/compare_recomputed_vs_recorded_triads.py --recorded bundles/phase_aware_v3/W33_N12_58_phase_aware_loop_v3/w33_four_center_triads_with_ray_holonomy.csv --recomputed analysis/triad_recompute_20260209/w33_four_center_triads_with_ray_holonomy.csv --out analysis/triad_recompute_20260209/compare_recorded_vs_recomputed.json
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Tuple


def parse_recorded(path: Path):
    d = {}
    with path.open('r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            try:
                a = int(r['a'])
                b = int(r['b'])
                c = int(r['c'])
            except Exception:
                # skip malformed rows
                continue
            tri = tuple(sorted((a, b, c)))
            hol = int(r.get('hol_mod12') or 0)
            d[tri] = hol
    return d


def parse_recomputed(path: Path):
    d = {}
    with path.open('r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            tri_s = r.get('triad')
            if not tri_s:
                continue
            parts = [int(x) for x in tri_s.split()]
            tri = tuple(sorted(parts))
            hol = int(r.get('holonomy_z12') or 0)
            d[tri] = hol
    return d


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--recorded', required=True, type=Path)
    p.add_argument('--recomputed', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()

    rec = parse_recorded(args.recorded)
    rep = parse_recomputed(args.recomputed)

    common = set(rec.keys()) & set(rep.keys())
    matches = []
    mismatches = []
    for t in sorted(common):
        rhol = rec[t]
        phol = rep[t]
        if rhol == phol:
            matches.append({'triad': t, 'value': rhol})
        else:
            mismatches.append({'triad': t, 'recorded': rhol, 'recomputed': phol})

    out = {
        'recorded_count': len(rec),
        'recomputed_count': len(rep),
        'common_triads': len(common),
        'matches': len(matches),
        'match_fraction': len(matches)/len(common) if common else None,
        'mismatches_sample': mismatches[:40],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
