#!/usr/bin/env python3
"""Analyze dd_shrink_result JSONs and produce a reproducibility summary."""
import json, glob, time
from pathlib import Path
BASE = Path.cwd()
CHECKS = BASE / 'checks'
ART = BASE / 'committed_artifacts'

files = glob.glob(str(CHECKS / 'PART_CVII_dd_shrink_result_*.json')) + glob.glob(str(ART / 'PART_CVII_dd_shrink_result_*.json'))
summary = {
    'total_files': len(files),
    'by_status': {},
    'by_reproducible': {'true':0,'false':0},
    'seeds_present': 0,
    'seed_sources': {},
    'time_seconds': [],
    'entries': []
}

for p in sorted(files):
    try:
        j = json.loads(open(p,encoding='utf-8').read())
    except Exception as e:
        continue
    st = j.get('shrink_status')
    if st is None:
        st = 'unknown'
    summary['by_status'][st] = summary['by_status'].get(st,0) + 1
    ir = j.get('initial_reproducible')
    if ir:
        summary['by_reproducible']['true'] += 1
    else:
        summary['by_reproducible']['false'] += 1
    ss = j.get('seed_source')
    if ss:
        summary['seed_sources'][ss] = summary['seed_sources'].get(ss,0) + 1
        summary['seeds_present'] += 1
    ts = j.get('time_seconds')
    if ts:
        summary['time_seconds'].append(ts)
    summary['entries'].append({'path': p, 'shrink_status': st, 'initial_reproducible': ir, 'seed_source': ss, 'seed_artifact': j.get('seed_artifact'), 'result': j.get('result'), 'time_seconds': ts})

otfound = [e for e in files if 'not_reproducible' in open(e,encoding='utf-8').read()]

out = CHECKS / f'PART_CVII_dd_shrink_repro_summary_{int(time.time())}.json'
open(out,'w',encoding='utf-8').write(json.dumps(summary,indent=2))
print('Wrote', out)
