#!/usr/bin/env python3
"""Summarize recent local CP-SAT seed results (block_exact, status, start vertex)."""
from __future__ import annotations

import glob
import json

files = sorted(glob.glob('checks/PART_CVII_e8_bijection_local_seed_*.json'))
print('Found', len(files), 'local seeds; showing last 30:')
best = (None, -1)
for f in files[-30:]:
    j = json.load(open(f, encoding='utf-8'))
    st = j.get('status')
    be = j.get('block_exact')
    sv = j.get('start_vertex')
    print(f'{f}: status={st} block_exact={be} start_vertex={sv}')
    if be is not None and be > best[1]:
        best = (f, be, sv)
print('\nBest local seed in last 30:', best)
