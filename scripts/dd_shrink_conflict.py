#!/usr/bin/env python3
"""Delta-debugging shrink (divide-and-conquer) for infeasible conflict sets.

Usage:
  python scripts/dd_shrink_conflict.py --bij committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json --conf checks/PART_CVII_infeasible_block_analysis_quick_merged_1770498926.json --index 0 --max-checks 500 --k 40 --time-limit 30 --seed 212

Writes: checks/PART_CVII_dd_shrink_result_<ts>.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import time
from pathlib import Path
from typing import Iterable, List

print('dd_shrink_conflict module loaded')


# create a simple run log so we can detect that the script started
Path('checks/PART_CVII_dd_shrink_run_log.txt').write_text('dd_shrink_conflict started at '+str(time.time())+'\n')

def run_forced_seed(seed_json: Path, k: int, time_limit: float, seed: int):
    cmd = [
        'py', '-3', '-X', 'utf8', 'scripts/solve_e8_embedding_cpsat.py',
        '--seed-json', str(seed_json),
        '--k', str(k),
        '--time-limit', str(time_limit),
        '--seed', str(seed),
        '--force-seed'
    ]
    try:
        timeout = max(10, int(time_limit) + 5)
        proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        out_json = None
        checks_path = Path.cwd() / 'checks' / 'PART_CVII_e8_embedding_cpsat.json'
        if checks_path.exists():
            out_json = json.loads(checks_path.read_text(encoding='utf-8'))
        return {'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr, 'json': out_json}
    except subprocess.TimeoutExpired as e:
        return {'timeout': True, 'error': f'Timeout after {timeout}s', 'stdout': getattr(e, 'stdout', ''), 'stderr': getattr(e, 'stderr', '')}
    except Exception as e:
        return {'error': str(e)}


def write_seed_for_edges(bij: dict, edges: Iterable[int], outpath: Path):
    seed_edges = []
    for e in edges:
        if e in bij:
            seed_edges.append({'edge_index': int(e), 'root_index': int(bij[e])})
    out = {'seed_edges': seed_edges, 'rotation': None}
    outpath.write_text(json.dumps(out, indent=2), encoding='utf-8')


def ddmin(bij: dict, S: List[int], k: int, time_limit: float, seed: int, max_checks: int):
    """Delta debugging to minimize failing set S.
    Returns a minimal failing subset (not guaranteed minimal w.r.t. checks bound).
    """
    n = 2
    checks = 0

    def test(subset: List[int]):
        nonlocal checks
        checks += 1
        tmp = Path.cwd() / 'checks' / f'_tmp_seed_dd_{int(time.time()*1000)}.json'
        write_seed_for_edges(bij, subset, tmp)
        res = run_forced_seed(tmp, k=k, time_limit=time_limit, seed=seed)
        try:
            tmp.unlink()
        except Exception:
            pass
        j = res.get('json')
        return j and j.get('status') == 'INFEASIBLE'

    S = list(S)
    if not test(S):
        return []

    while True:
        if max_checks is not None and checks >= max_checks:
            return S
        if len(S) == 1:
            return S
        subset_size = math.ceil(len(S) / n)
        some_progress = False
        for i in range(0, len(S), subset_size):
            part = S[i:i + subset_size]
            if not part:
                continue
            if test(part):
                S = part
                n = max(n - 1, 2)
                some_progress = True
                break
            others = [x for x in S if x not in part]
            if others and test(others):
                S = others
                n = max(n - 1, 2)
                some_progress = True
                break
            if max_checks is not None and checks >= max_checks:
                return S
        if not some_progress:
            if n >= len(S):
                return S
            n = min(len(S), n * 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bij', required=True)
    parser.add_argument('--conf', required=True, help='Conflict source JSON (e.g., quick merged)')
    parser.add_argument('--index', type=int, default=0, help='Which conflict entry index to shrink')
    parser.add_argument('--max-checks', type=int, default=1000)
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--time-limit', type=float, default=60.0)
    parser.add_argument('--seed', type=int, default=212)
    args = parser.parse_args()

    bij = json.loads(open(args.bij, encoding='utf-8').read())['bijection']
    bij = {int(k): int(v) for k, v in bij.items()}

    conf_json = json.loads(open(args.conf, encoding='utf-8').read())
    entries = conf_json.get('checked', [])
    if args.index >= len(entries):
        raise SystemExit('Index out of range')
    entry = entries[args.index]
    if 'minimal_conflict' not in entry:
        raise SystemExit('No minimal_conflict found in selected entry')

    S = entry['minimal_conflict']
    print(f'Starting ddmin on conflict of size {len(S)}')

    start = time.time()
    result = ddmin(bij, S, k=args.k, time_limit=args.time_limit, seed=args.seed, max_checks=args.max_checks)
    elapsed = time.time() - start

    out = {
        'source_conf_entry': entry,
        'initial_size': len(S),
        'result': result,
        'result_size': len(result),
        'checks_limit': int(args.max_checks),
        'time_seconds': elapsed,
        'timestamp': int(time.time())
    }

    stamp = int(time.time())
    outpath = Path.cwd() / 'checks' / f'PART_CVII_dd_shrink_result_{stamp}.json'
    outpath.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print('Wrote', outpath)

    # mirror to committed_artifacts
    art = Path.cwd() / 'committed_artifacts' / outpath.name
    art.write_text(outpath.read_text(encoding='utf-8'), encoding='utf-8')
    print('Also wrote', art)


if __name__ == '__main__':
    main()
