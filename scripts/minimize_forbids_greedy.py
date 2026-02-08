#!/usr/bin/env python3
"""Greedy minimization of forbids: find a minimal subset of forbids that still causes INFEASIBLE in global CP-SAT.

Writes:
 - checks/PART_CVII_forbids_minimal_greedy.json
 - checks/PART_CVII_forbids_minimize_log.txt

Usage: py -3 scripts/minimize_forbids_greedy.py --k 40 --prove-time 60 --seed 212
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import shutil
from pathlib import Path

BASE = Path.cwd()
CHECKS = BASE / 'checks'
FORB = CHECKS / 'PART_CVII_forbids.json'
OUT = CHECKS / 'PART_CVII_forbids_minimal_greedy.json'
LOG = CHECKS / 'PART_CVII_forbids_minimize_log.txt'
TMP = CHECKS / '_tmp_forbids_trial.json'
SOLVER_CMD = ['py', '-3', 'scripts/solve_e8_embedding_cpsat.py']


def log(msg: str):
    ts = time.time()
    line = f"{ts}: {msg}\n"
    print(line, end='')
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line)


def run_solver_with_forbids(forb_path: Path, k: int, time_limit: int, seed: int):
    cmd = SOLVER_CMD + ['--k', str(k), '--time-limit', str(time_limit), '--forbid-json', str(forb_path), '--seed', str(seed)]
    log(f"Running solver: {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    log(f"Solver exit {proc.returncode} stdout(len)={len(proc.stdout)} stderr(len)={len(proc.stderr)}")
    # read solver JSON
    solf = CHECKS / 'PART_CVII_e8_embedding_cpsat.json'
    if solf.exists():
        try:
            j = json.loads(open(solf, encoding='utf-8').read())
            return j.get('status')
        except Exception as e:
            log(f"Failed to read solver JSON: {e}")
            return None
    else:
        log('Solver JSON not found after run')
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--prove-time', type=int, default=60)
    parser.add_argument('--seed', type=int, default=212)
    parser.add_argument('--commit', action='store_true', help='Commit minimized forbids to checks/PART_CVII_forbids.json')
    parser.add_argument('--forbid-file', type=str, default=str(FORB), help='Path to forbids JSON to minimize')
    args = parser.parse_args()

    forb_path = Path(args.forbid_file)
    if not forb_path.exists():
        print('No forbids file found at', forb_path)
        raise SystemExit(0)

    orig = json.loads(open(forb_path, encoding='utf-8').read())
    entries = orig.get('obstruction_sets', [])[:]
    if not entries:
        print('No obstruction_sets entries found in forbids file')
        raise SystemExit(0)

    # initial check: does full set cause INFEASIBLE?
    log('Starting minimization; verifying full forbids')
    status = run_solver_with_forbids(forb_path, args.k, args.prove_time, args.seed)
    if status != 'INFEASIBLE':
        log(f'Full forbids did not prove INFEASIBLE (status={status}). Aborting minimization.')
        raise SystemExit(0)

    # Greedy deletion
    changed = True
    current = entries[:]
    while changed:
        changed = False
        for i, entry in enumerate(list(current)):
            trial = [e for j, e in enumerate(current) if j != i]
            json.dump({'obstruction_sets': trial}, open(TMP, 'w', encoding='utf-8'), indent=2)
            st = run_solver_with_forbids(TMP, args.k, args.prove_time, args.seed)
            log(f'Trial removing index {i} returned status {st}')
            if st == 'INFEASIBLE':
                # removal successful -> entry is redundant
                log(f'Removing entry index {i} as redundant')
                current = trial
                changed = True
                break
            else:
                log(f'Keeping entry index {i} (status={st})')
        # loop until no single deletion preserves INFEASIBLE

    res = {'obstruction_sets': current}
    OUT.write_text(json.dumps(res, indent=2), encoding='utf-8')
    log(f'Wrote minimized forbids to {OUT} with {len(current)} entries')

    if args.commit:
        shutil.copy2(OUT, FORB)
        log(f'Committed minimized forbids to {FORB}')


if __name__ == '__main__':
    main()
