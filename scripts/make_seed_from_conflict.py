#!/usr/bin/env python3
"""Write a temporary seed JSON from a merged conflict analysis entry.

Usage:
  python scripts/make_seed_from_conflict.py --conf checks/PART_CVII_infeasible_block_analysis_quick_merged_1770498926.json --index 0 --bij committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json --out checks/_tmp_seed_test_1.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', required=True)
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--bij', required=True)
    parser.add_argument('--out', default='checks/_tmp_seed_test_1.json')
    args = parser.parse_args()

    conf = json.loads(open(args.conf, encoding='utf-8').read())
    entries = conf.get('checked', [])
    if args.index >= len(entries):
        raise SystemExit('index out of range')
    entry = entries[args.index]
    if 'minimal_conflict' not in entry:
        raise SystemExit('entry has no minimal_conflict')

    bij = json.loads(open(args.bij, encoding='utf-8').read())['bijection']
    bij = {int(k): int(v) for k, v in bij.items()}
    S = entry['minimal_conflict']
    seed_edges = [{'edge_index': int(e), 'root_index': int(bij[e])} for e in S if int(e) in bij]
    seed = {'seed_edges': seed_edges, 'rotation': None}
    outpath = Path(args.out)
    outpath.write_text(json.dumps(seed, indent=2), encoding='utf-8')
    print('Wrote', outpath, 'with', len(seed_edges), 'entries')

if __name__ == '__main__':
    main()
