#!/usr/bin/env python3
"""Scan all start vertices with local CP-SAT to find infeasible blocks.

Writes out checks/PART_CVII_local_infeasible_summary_{stamp}.json
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


def run_local(seed_json, start_vertex, edge_limit, k, time_limit, seed, seed_reward):
    cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        "-u",
        "scripts/solve_e8_embedding_cpsat_local.py",
        "--seed-json",
        seed_json,
        "--start-vertex",
        str(start_vertex),
        "--edge-limit",
        str(edge_limit),
        "--k",
        str(k),
        "--time-limit",
        str(time_limit),
        "--seed",
        str(seed),
        "--seed-reward",
        str(seed_reward),
    ]
    print('Running:', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def main():
    seed_json = 'checks/PART_CVII_e8_bijection_seed_campaign_1770489801.json'
    out = {'seed_json': seed_json, 'scanned': [], 'timestamp': int(time.time())}
    for sv in range(40):
        try:
            run_local(seed_json, sv, 24, 40, 60, 211, 10000)
        except subprocess.CalledProcessError:
            print('Local run failed for', sv)
            continue
        # read latest local file
        from glob import glob
        latest = sorted(glob('checks/PART_CVII_e8_bijection_local_seed_*.json'), key=lambda p: Path(p).stat().st_mtime)[-1]
        j = json.load(open(latest, encoding='utf-8'))
        entry = {'start_vertex': j.get('start_vertex'), 'status': j.get('status'), 'block_edges': j.get('block_edges'), 'block_exact': j.get('block_exact')}
        out['scanned'].append(entry)
    outp = Path('checks') / f'PART_CVII_local_infeasible_summary_{int(time.time())}.json'
    outp.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print('Wrote', outp)

if __name__ == '__main__':
    main()
