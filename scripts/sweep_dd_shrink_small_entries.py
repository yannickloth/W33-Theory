#!/usr/bin/env python3
"""Sweep dd_shrink over all infeasible-block analysis files for entries with small minimal_conflict size (<= threshold)

Usage:
  python scripts/sweep_dd_shrink_small_entries.py --threshold 30 --k 40 --time-limit 30 --max-checks 2000
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import time
from pathlib import Path

CHECKS = Path('checks')

parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=int, default=30)
parser.add_argument('--k', type=int, default=40)
parser.add_argument('--time-limit', type=int, default=30)
parser.add_argument('--max-checks', type=int, default=2000)
parser.add_argument('--seed', type=int, default=212)
args = parser.parse_args()

# collect existing dd_shrink results mapping from source file to result files
existing = {}
for p in glob.glob(str(CHECKS / 'PART_CVII_dd_shrink_result_*.json')):
    j = json.loads(open(p, encoding='utf-8').read())
    src = j['source_conf_entry']['file']
    existing.setdefault(src, []).append(p)

candidates = []
for f in glob.glob(str(CHECKS / 'PART_CVII_infeasible_block_analysis*.json')):
    j = json.loads(open(f, encoding='utf-8').read())
    for idx, entry in enumerate(j.get('checked', [])):
        if 'minimal_conflict' not in entry:
            continue
        if len(entry['minimal_conflict']) <= args.threshold:
            src = entry['file'] if 'file' in entry else entry.get('file', f)
            # Use the actual file in the entry if present (it seems to be the local seed file)
            # but we will call dd_shrink with this conf file and the index
            # Avoid re-running if we already have dd_shrink result referring to this conf file
            if str(f) in existing and existing.get(str(f)):
                # there are dd_shrink results for this source conf file; skip only if there are results
                # (we accept re-running if needed)
                pass
            candidates.append((f, idx, len(entry['minimal_conflict'])))

print(f'Found {len(candidates)} small entries (<= {args.threshold}) to run dd_shrink on')
logp = CHECKS / 'PART_CVII_dd_shrink_sweep_log.txt'
logp.write_text('Started sweep at '+str(time.time())+'\n')

# run dd_shrink for each candidate sequentially
for f, idx, size in candidates:
    print('Running dd_shrink on', f, 'index', idx, 'size', size)
    logp.write_text(logp.read_text() + f'Run: {f} idx {idx} size {size} at {time.time()}\n')
    cmd = [
        'py', '-3', 'scripts/dd_shrink_conflict.py',
        '--bij', 'committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json',
        '--conf', str(f),
        '--index', str(idx),
        '--max-checks', str(args.max_checks),
        '--k', str(args.k),
        '--time-limit', str(args.time_limit),
        '--seed', str(args.seed)
    ]
    ret = subprocess.run(cmd, check=False)
    logp.write_text(logp.read_text() + f'Exit code: {ret.returncode} at {time.time()}\n')
    time.sleep(0.2)

print('Sweep done; now running register_dd_obstructions.py to verify and record artifacts')
subprocess.run(['py', '-3', 'scripts/register_dd_obstructions.py'])
print('Finished')
