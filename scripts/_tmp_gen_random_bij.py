#!/usr/bin/env python3
"""Generate a deterministic "random" bijection file derived from the committed intermediate bijection.
Writes a file into checks/ with name PART_CVII_e8_bijection_random_<ts>.json
"""
import json, random, time
from pathlib import Path
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--seed', '-s', type=int, default=31337)
args = parser.parse_args()

SRC = Path('committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json')
if not SRC.exists():
    raise SystemExit(f'source bijection not found: {SRC}')
obj = json.loads(SRC.read_text(encoding='utf-8'))
bj = obj.get('bijection', {})
keys = sorted(bj.keys(), key=lambda x: int(x))
vals = [int(bj[k]) for k in keys]
random.Random(args.seed).shuffle(vals)
outbij = {k: int(v) for k, v in zip(keys, vals)}
stamp = int(time.time())
outfile = Path('checks') / f'PART_CVII_e8_bijection_random_{stamp}.json'
outfile.write_text(json.dumps({'bijection': outbij}, indent=2), encoding='utf-8')
print('Wrote', outfile)
