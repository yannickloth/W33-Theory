#!/usr/bin/env python3
"""Quick diagnosis: run forced-seed on INFEASIBLE local blocks and do bounded greedy shrink.

Usage:
  python scripts/quick_infeasible_diagnosis.py --bij <bijection> --limit N --time-limit T --k K --seed S --shrink-max-checks M
"""
from __future__ import annotations

import argparse
import glob
import json
import time
from pathlib import Path
from typing import Any

# Make local scripts importable
import sys
sys.path.insert(0, str(Path(__file__).parent))
from analyze_infeasible_blocks import load_bijection, write_seed_for_edges, run_forced_seed, shrink_unsat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bij', required=True)
    parser.add_argument('--limit', type=int, default=8, help='Number of infeasible blocks to process')
    parser.add_argument('--time-limit', type=float, default=8.0)
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--seed', type=int, default=212)
    parser.add_argument('--shrink-max-checks', type=int, default=4)
    parser.add_argument('--auto-commit', action='store_true')
    args = parser.parse_args()

    bij = load_bijection(Path(args.bij))

    local_files = sorted(glob.glob('checks/PART_CVII_e8_bijection_local_seed_*.json'))
    ins = []
    for f in local_files:
        j = json.loads(open(f, encoding='utf-8').read())
        if j.get('status') == 'INFEASIBLE' and isinstance(j.get('block_edges'), list):
            ins.append((f, j))

    print('Found', len(ins), 'INFEASIBLE local seeds with block_edges')

    results: dict[str, Any] = {'checked': [], 'timestamp': int(time.time()), 'bij_source': str(args.bij)}

    for f, j in ins[: args.limit]:
        block_edges = j.get('block_edges')
        tmp_seed = Path.cwd() / 'checks' / f'_tmp_seed_block_quick_{Path(f).stem}.json'
        write_seed_for_edges(bij, block_edges, tmp_seed)

        res = run_forced_seed(tmp_seed, k=args.k, time_limit=args.time_limit, seed=args.seed)
        status = res.get('json', {}).get('status') if res.get('json') else None
        entry = {'file': f, 'start_vertex': j.get('start_vertex'), 'block_size': len(block_edges), 'forced_status': status}
        print('Processed', f, 'forced_status=', status)

        if status == 'INFEASIBLE':
            min_conflict = shrink_unsat(bij, block_edges, k=args.k, time_limit=args.time_limit, seed=args.seed, max_checks=args.shrink_max_checks)
            entry['minimal_conflict'] = min_conflict
            entry['minimal_conflict_size'] = len(min_conflict)
            print('  Minimal conflict size', len(min_conflict))

        results['checked'].append(entry)

        # Write partial results after each block to avoid losing progress
        stamp_now = int(time.time())
        outp_partial = Path.cwd() / 'checks' / f'PART_CVII_infeasible_block_analysis_quick_partial_{stamp_now}.json'
        outp_partial.write_text(json.dumps(results, indent=2), encoding='utf-8')
        print('  Wrote partial', outp_partial)

        # Optionally mirror into committed_artifacts and auto-commit
        if getattr(args, 'auto_commit', False):
            try:
                # import the local helper directly (script directory is on sys.path)
                from git_auto_keep import git_add_commit
                artifact = Path.cwd() / 'committed_artifacts' / outp_partial.name
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_text(outp_partial.read_text(encoding='utf-8'), encoding='utf-8')
                ok, msg = git_add_commit([str(artifact)], f'Quick infeasible analysis partial: {outp_partial.name}')
                print('  Auto-commit result:', ok, msg)
            except Exception as e:
                print('  Auto-commit failed:', e)

        try:
            tmp_seed.unlink()
        except Exception:
            pass

    stamp = int(time.time())
    outp = Path.cwd() / 'checks' / f'PART_CVII_infeasible_block_analysis_quick_{stamp}.json'
    outp.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print('Wrote', outp)


if __name__ == '__main__':
    main()
