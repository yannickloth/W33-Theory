#!/usr/bin/env python3
"""Extended reproducibility sweep for a single conflict entry (pair 50,51).
Runs dd_shrink_conflict.py for multiple bijections and seeds with extended time-limits
and collects a summary of results.
"""
import subprocess, time, json, shutil, os, glob
from pathlib import Path

BIJ = [
    'committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json',
    'checks/PART_CVII_e8_bijection_random_1770585565.json',
    'checks/PART_CVII_e8_bijection_random_1770585575.json',
]
SEEDS = list(range(212, 222))  # 10 seeds: 212..221
CONF = 'checks/PART_CVII_dd_shrink_input_pair_1770577580.json'
OUT_SUM = Path('checks') / f'dd_repro_sweep_summary_{int(time.time())}.json'
summary = []

for bij in BIJ:
    bij_label = Path(bij).stem
    for seed in SEEDS:
        stamp = int(time.time())
        cmd = [
            'py', '-3', '-X', 'utf8', 'scripts/dd_shrink_conflict.py',
            '--bij', bij,
            '--conf', CONF,
            '--index', '0',
            '--max-checks', '2000',
            '--k', '40',
            '--time-limit', '300',
            '--seed', str(seed),
        ]
        print('\n=== Running:', ' '.join(cmd))
        start = time.time()
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end = time.time()
        print(proc.stdout)
        if proc.stderr:
            print('STDERR:\n', proc.stderr)
        # find most recent dd_shrink_result created in checks (timestamp after start)
        results = sorted(glob.glob('checks/PART_CVII_dd_shrink_result_*.json'))
        latest = None
        for r in reversed(results):
            try:
                j = json.loads(open(r, encoding='utf-8').read())
            except Exception:
                continue
            if j.get('timestamp', 0) >= int(start - 2):
                latest = r
                break
        cpsat = Path('checks') / 'PART_CVII_e8_embedding_cpsat.json'
        cpsat_copy = None
        if cpsat.exists():
            cpsat_copy = Path('checks') / f'dd_repro_pair_1770577580_{bij_label}_seed{seed}_{stamp}_cpsat.json'
            shutil.copyfile(str(cpsat), str(cpsat_copy))
        rec = {
            'bij': bij,
            'bij_label': bij_label,
            'seed': seed,
            'dd_shrink_result': latest,
            'cpsat_json': str(cpsat_copy) if cpsat_copy else None,
            'stdout': proc.stdout[:4000],
            'stderr': proc.stderr[:4000],
            'elapsed_seconds': end - start,
            'timestamp': stamp,
        }
        # if we have a dd_shrink result, parse key fields
        if latest:
            try:
                rj = json.loads(open(latest, encoding='utf-8').read())
                rec['initial_reproducible'] = rj.get('initial_reproducible')
                rec['shrink_status'] = rj.get('shrink_status')
                rec['result_size'] = rj.get('result_size')
            except Exception:
                pass
        summary.append(rec)
        # small delay
        time.sleep(1)

OUT_SUM.write_text(json.dumps(summary, indent=2), encoding='utf-8')
print('Wrote summary to', OUT_SUM)
print('Done')
