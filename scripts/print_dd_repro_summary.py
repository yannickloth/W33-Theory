#!/usr/bin/env python3
import json, glob
from pathlib import Path
CHECKS = Path('checks')
js = list(CHECKS.glob('PART_CVII_dd_shrink_repro_summary_*.json'))
if not js:
    print('No summary file found')
    raise SystemExit(1)
# pick latest
j = sorted(js)[-1]
s = json.loads(open(j,encoding='utf-8').read())
print('Summary file:', j)
print('Total files:', s.get('total_files'))
print('by_status:', s.get('by_status'))
print('by_reproducible:', s.get('by_reproducible'))
print('\nEntries with initial_reproducible=True and shrink_status in [already_minimal, shrunk]:')
for e in s.get('entries',[]):
    if e.get('initial_reproducible') == True and e.get('shrink_status') in ('already_minimal','shrunk'):
        print('-', e['path'], e.get('shrink_status'), e.get('time_seconds'))
