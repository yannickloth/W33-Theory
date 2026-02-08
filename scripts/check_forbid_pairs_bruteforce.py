#!/usr/bin/env python3
"""Brute-force check pairs of forbids to find subsets that cause INFEASIBLE.
Writes checks/PART_CVII_forbids_pairs_scan.json
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from itertools import combinations

CHECKS = Path('checks')
FORB = CHECKS / 'PART_CVII_forbids.json'
OUT = CHECKS / 'PART_CVII_forbids_pairs_scan.json'
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
        except Exception:
            return None
    return None


def main():
    parser = __import__('argparse').ArgumentParser()
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--time-limit', type=int, default=20)
    parser.add_argument('--seed', type=int, default=212)
    parser.add_argument('--stop-on-find', action='store_true')
    args = parser.parse_args()

    if not FORB.exists():
        print('No forbids file found')
        raise SystemExit(0)
    forb = json.loads(open(FORB, encoding='utf-8').read())
    entries = forb.get('obstruction_sets', [])
    n = len(entries)
    results = {'tested': 0, 'found': []}
    for (i, j) in combinations(range(n), 2):
        subset = [entries[i], entries[j]]
        json.dump({'obstruction_sets': subset}, open(TMP, 'w', encoding='utf-8'), indent=2)
        status = run_solver_for_forbids(TMP, args.k, args.time_limit, args.seed)
        results['tested'] += 1
        print(f'Tested pair {i},{j} -> status={status}')
        if status == 'INFEASIBLE':
            results['found'].append({'indices': [i, j], 'subset': subset})
            print('Found infeasible pair:', i, j)
            if args.stop_on_find:
                break
    results['time'] = time.time()
    open(OUT, 'w', encoding='utf-8').write(json.dumps(results, indent=2))
    print('Wrote results to', OUT)


if __name__ == '__main__':
    main()
