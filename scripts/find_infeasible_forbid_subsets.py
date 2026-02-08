#!/usr/bin/env python3
"""Search small subsets of forbids (pairs/triples) to find subsets that prove INFEASIBLE.

Writes checks/PART_CVII_forbids_subsets_results.json with found infeasible subsets.
"""
from __future__ import annotations

import json
import argparse
import subprocess
import time
from pathlib import Path
from itertools import combinations

CHECKS = Path('checks')
FORB = CHECKS / 'PART_CVII_forbids.json'
OUT = CHECKS / 'PART_CVII_forbids_subsets_results.json'
TMP = CHECKS / '_tmp_forbids_subset.json'
SOLVER_CMD = ['py', '-3', 'scripts/solve_e8_embedding_cpsat.py']


def run_solver_for_forbids(forb_path: Path, k: int, time_limit: int, seed: int):
    cmd = SOLVER_CMD + ['--k', str(k), '--time-limit', str(time_limit), '--forbid-json', str(forb_path), '--seed', str(seed)]
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    solf = CHECKS / 'PART_CVII_e8_embedding_cpsat.json'
    if solf.exists():
        try:
            j = json.loads(open(solf, encoding='utf-8').read())
            return j.get('status')
        except Exception as e:
            return None
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--time-limit', type=int, default=30)
    parser.add_argument('--seed', type=int, default=212)
    parser.add_argument('--max-size', type=int, default=2, help='Max subset size to test')
    args = parser.parse_args()

    if not FORB.exists():
        print('No forbids file found')
        raise SystemExit(0)
    forb = json.loads(open(FORB, encoding='utf-8').read())
    entries = forb.get('obstruction_sets', [])
    print('Found entries:', len(entries))
    if not entries:
        print('No entries in forbids')
        raise SystemExit(0)

    n = len(entries)
    results = {'found': [], 'tested': 0, 'time': time.time()}
    for s in range(1, min(args.max_size, n) + 1):
        for comb in combinations(range(n), s):
            subset = [entries[i] for i in comb]
            json.dump({'obstruction_sets': subset}, open(TMP, 'w', encoding='utf-8'), indent=2)
            status = run_solver_for_forbids(TMP, args.k, args.time_limit, args.seed)
            results['tested'] += 1
            if status == 'INFEASIBLE':
                results['found'].append({'indices': list(comb), 'subset': subset, 'status': status})
                # note: continue to find more, or break to find minimal
    results['time_end'] = time.time()
    open(OUT, 'w', encoding='utf-8').write(json.dumps(results, indent=2))
    print('Wrote results to', OUT)


if __name__ == '__main__':
    main()
