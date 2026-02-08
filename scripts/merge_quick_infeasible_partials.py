#!/usr/bin/env python3
"""Merge partial quick infeasible analysis JSONs into a single summary.

Usage:
  python scripts/merge_quick_infeasible_partials.py --out checks/PART_CVII_infeasible_block_analysis_quick_merged.json
"""
from __future__ import annotations
import glob, json, time
from pathlib import Path
from collections import defaultdict

partials = sorted(glob.glob('checks/PART_CVII_infeasible_block_analysis_quick_partial_*.json'))
merged = {'checked': [], 'timestamp': int(time.time()), 'sources': partials}
seen = {}

for p in partials:
    try:
        j = json.loads(open(p, encoding='utf-8').read())
        for entry in j.get('checked', []):
            key = entry.get('file')
            # prefer entries with minimal_conflict present
            if key not in seen or (entry.get('minimal_conflict_size') and (seen[key].get('minimal_conflict_size', 1e9) > entry.get('minimal_conflict_size'))):
                seen[key] = entry
    except Exception:
        pass

merged['checked'] = list(seen.values())
# basic stats
sizes = [e.get('minimal_conflict_size') for e in merged['checked'] if isinstance(e.get('minimal_conflict_size'), int)]
if sizes:
    sizes.sort()
    stats = {'count': len(sizes), 'min': sizes[0], 'median': sizes[len(sizes)//2], 'max': sizes[-1]}
else:
    stats = {'count': 0}
merged['summary'] = stats

outp = Path('checks') / f'PART_CVII_infeasible_block_analysis_quick_merged_{int(time.time())}.json'
outp.write_text(json.dumps(merged, indent=2), encoding='utf-8')
print('Wrote', outp)
