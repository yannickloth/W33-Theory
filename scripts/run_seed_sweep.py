#!/usr/bin/env python3
"""Run solver on multiple seed JSON files and archive results."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
import time


def run_one(seed_path: Path, k: int, time_limit: float, seed: int, seed_reward: float, force: bool, log: bool):
    cmd = ["py", "-3", "scripts/solve_e8_embedding_cpsat.py", "--seed-json", str(seed_path), "--k", str(k), "--time-limit", str(time_limit), "--seed", str(int(seed))]
    if force:
        cmd.append("--force-seed")
    else:
        cmd += ["--seed-reward", str(seed_reward)]
    if log:
        cmd += ["--log"]
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out_text = proc.stdout
    err_text = proc.stderr
    # read solver output JSON if exists
    cpsat_json_path = Path.cwd() / "checks" / "PART_CVII_e8_embedding_cpsat.json"
    cpsat = None
    if cpsat_json_path.exists():
        try:
            cpsat = json.loads(open(cpsat_json_path, encoding='utf-8').read())
        except Exception as e:
            cpsat = {'error': str(e)}
    res = {
        'seed_file': str(seed_path),
        'cmd': cmd,
        'stdout': out_text,
        'stderr': err_text,
        'cpsat': cpsat,
        'timestamp': int(time.time())
    }
    # write archive
    out_name = Path('checks') / f"PART_CVII_e8_embedding_cpsat_{seed_path.stem}.json"
    with open(out_name, 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2)
    print('Wrote archive:', out_name)
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument('seeds', nargs='+')
    p.add_argument('--k', type=int, default=40)
    p.add_argument('--time-limit', type=float, default=300.0)
    p.add_argument('--seed', type=int, default=212)
    p.add_argument('--seed-reward', type=float, default=10000.0)
    p.add_argument('--force', action='store_true')
    p.add_argument('--log', action='store_true')
    args = p.parse_args()

    for s in args.seeds:
        seed_path = Path(s)
        if not seed_path.exists():
            print('Seed not found:', s)
            continue
        run_one(seed_path, args.k, args.time_limit, args.seed, args.seed_reward, args.force, args.log)

if __name__ == '__main__':
    main()
