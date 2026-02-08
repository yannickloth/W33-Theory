#!/usr/bin/env python3
"""Auto post-sweep automation.

Monitors dd-shrink sweep activity and when quiet for a configured period runs:
  - scripts/minimize_forbids_greedy.py (attempt minimize and commit)
  - scripts/check_forbid_pairs_bruteforce.py (scan pairs for infeasible subset)
  - scripts/solve_e8_embedding_cpsat.py (long prove attempt)

Writes logs to checks/PART_CVII_auto_post_sweep_log.txt and reports to checks/PART_CVII_auto_post_report_<ts>.json
"""
from __future__ import annotations

import argparse
import json
import time
import glob
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path.cwd()
CHECKS = BASE / 'checks'
ART = BASE / 'committed_artifacts'
LOG = CHECKS / 'PART_CVII_auto_post_sweep_log.txt'
STATE = CHECKS / '_auto_post_state.json'

# default parameters
DEFAULT_POLL = 60
DEFAULT_QUIET_MIN = 10
DEFAULT_MIN_INTERVAL_MIN = 60

MINIMIZER = ['py', '-3', 'scripts/minimize_forbids_greedy.py']
PAIRS = ['py', '-3', 'scripts/check_forbid_pairs_bruteforce.py']
SOLVER = ['py', '-3', 'scripts/solve_e8_embedding_cpsat.py']


def log(msg: str):
    ts = time.time()
    line = f"{datetime.utcfromtimestamp(ts).isoformat()}Z: {msg}\n"
    print(line, end='')
    CHECKS.mkdir(exist_ok=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line)


def get_last_change_ts():
    # latest mtime among dd_shrink results, pair artifacts, forbids file
    ts = 0.0
    for p in glob.glob(str(CHECKS / 'PART_CVII_dd_shrink_result_*.json')):
        try:
            t = Path(p).stat().st_mtime
            ts = max(ts, t)
        except Exception:
            continue
    for p in glob.glob(str(CHECKS / 'PART_CVII_dd_pair_obstruction_*.json')):
        try:
            t = Path(p).stat().st_mtime
            ts = max(ts, t)
        except Exception:
            continue
    forb = CHECKS / 'PART_CVII_forbids.json'
    if forb.exists():
        try:
            ts = max(ts, forb.stat().st_mtime)
        except Exception:
            pass
    return ts


def run_cmd(cmd, timeout=None):
    log(f"Running: {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        log(f"Exit {proc.returncode} stdout(len)={len(proc.stdout)} stderr(len)={len(proc.stderr)}")
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        log(f"Timeout after {timeout}s: {' '.join(cmd)}")
        return -1, '', ''
    except Exception as e:
        log(f"Error running cmd: {e}")
        return -2, '', str(e)


def run_pipeline(k: int, prove_time: int, pair_time: int, global_time: int, commit: bool, seed: int):
    ts = int(time.time())
    report = {'ts': ts, 'k': k, 'prove_time': prove_time, 'pair_time': pair_time, 'global_time': global_time, 'seed': seed}
    # snapshot forbids
    forb_path = CHECKS / 'PART_CVII_forbids.json'
    if forb_path.exists():
        snap = CHECKS / f'_tmp_forbids_pre_{ts}.json'
        shutil.copy2(forb_path, snap)
        report['pre_forbids'] = str(snap)
    else:
        report['pre_forbids'] = None

    # run minimizer
    min_cmd = MINIMIZER + ['--forbid-file', str(forb_path), '--k', str(k), '--prove-time', str(prove_time), '--seed', str(seed)]
    if commit:
        min_cmd.append('--commit')
    rc, out, err = run_cmd(min_cmd, timeout=prove_time + 60)
    report['minimizer'] = {'rc': rc, 'stdout_len': len(out), 'stderr_len': len(err)}
    # copy minimizer output if exists
    minimized = CHECKS / 'PART_CVII_forbids_minimal_greedy.json'
    if minimized.exists():
        dst = CHECKS / f'PART_CVII_forbids_minimal_greedy_{ts}.json'
        shutil.copy2(minimized, dst)
        report['minimized_path'] = str(dst)

    # run pairs bruteforce
    pair_cmd = PAIRS + ['--k', str(k), '--time-limit', str(pair_time), '--seed', str(seed), '--stop-on-find']
    rc, out, err = run_cmd(pair_cmd, timeout=pair_time * 5)
    report['pairs'] = {'rc': rc, 'stdout_len': len(out), 'stderr_len': len(err)}
    pairs_out = CHECKS / 'PART_CVII_forbids_pairs_scan.json'
    if pairs_out.exists():
        try:
            j = json.loads(pairs_out.read_text(encoding='utf-8'))
            report['pairs_results'] = j
        except Exception as e:
            report['pairs_results'] = f'Error reading JSON: {e}'

    # run long global prove
    sol_cmd = SOLVER + ['--k', str(k), '--time-limit', str(global_time), '--forbid-json', str(forb_path), '--seed', str(seed), '--log']
    rc, out, err = run_cmd(sol_cmd, timeout=global_time + 120)
    report['global_prove'] = {'rc': rc, 'stdout_len': len(out), 'stderr_len': len(err)}
    sol_json = CHECKS / 'PART_CVII_e8_embedding_cpsat.json'
    if sol_json.exists():
        try:
            report['global_status'] = json.loads(sol_json.read_text(encoding='utf-8'))
        except Exception as e:
            report['global_status'] = f'Error reading solver JSON: {e}'

    # write report
    outp = CHECKS / f'PART_CVII_auto_post_report_{ts}.json'
    outp.write_text(json.dumps(report, indent=2), encoding='utf-8')
    # mirror report
    ART.mkdir(exist_ok=True)
    try:
        shutil.copy2(outp, ART / outp.name)
    except Exception as e:
        log(f"Failed to mirror report: {e}")
    log(f"Wrote auto-post report: {outp}")
    # update state
    STATE.write_text(json.dumps({'last_run': time.time(), 'report': str(outp)}), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet-minutes', type=int, default=DEFAULT_QUIET_MIN)
    parser.add_argument('--poll-interval', type=int, default=DEFAULT_POLL)
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--prove-time', type=int, default=300, help='seconds for minimizer prove step')
    parser.add_argument('--pair-time', type=int, default=60, help='seconds per pair test')
    parser.add_argument('--global-time', type=int, default=600, help='seconds for long global prove')
    parser.add_argument('--commit', action='store_true')
    parser.add_argument('--seed', type=int, default=212)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()

    quiet_s = args.quiet_minutes * 60
    min_interval_s = DEFAULT_MIN_INTERVAL_MIN * 60

    last_change = get_last_change_ts()
    last_seen = time.time()
    if last_change > 0:
        last_seen = time.time()

    last_run = 0.0
    if STATE.exists():
        try:
            st = json.loads(STATE.read_text(encoding='utf-8'))
            last_run = st.get('last_run', 0.0)
        except Exception:
            last_run = 0.0

    log(f"Auto-post-sweep started; quiet={args.quiet_minutes}m poll={args.poll_interval}s commit={args.commit}")
    try:
        while True:
            now = time.time()
            curr_change = get_last_change_ts()
            if curr_change != last_change:
                log(f"Detected activity: change_ts from {last_change} -> {curr_change}")
                last_change = curr_change
                last_seen = now
            else:
                idle = now - last_seen
                if idle >= quiet_s and (now - last_run) >= min_interval_s:
                    log(f"Idle for {idle}s >= quiet({quiet_s}s) and last_run {(now - last_run)}s ago; triggering pipeline")
                    report = run_pipeline(args.k, args.prove_time, args.pair_time, args.global_time, args.commit, args.seed)
                    last_run = time.time()
                    # If --once, break after running pipeline
                    if args.once:
                        log('--once provided; exiting after pipeline run')
                        break
                    # after run, update last_seen to avoid immediate re-run
                    last_seen = time.time()
            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        log('Auto-post-sweep interrupted by user')
    except Exception as e:
        log(f'Auto-post-sweep exception: {e}')


if __name__ == '__main__':
    main()
