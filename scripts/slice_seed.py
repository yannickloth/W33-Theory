#!/usr/bin/env python3
"""Slice a seed JSON file to top-N seed_edges entries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--top", type=int, required=True)
    p.add_argument("--out", default=None)
    args=p.parse_args()

    inp=Path(args.infile)
    if not inp.exists():
        raise FileNotFoundError(inp)
    s=json.load(open(inp, encoding='utf-8'))
    out=Path(args.out) if args.out else inp.parent / f"{inp.stem}_top{args.top}{inp.suffix}"
    s2={'seed_edges': s.get('seed_edges', [])[:args.top], 'rotation': s.get('rotation')}
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(s2, f, indent=2)
    print('Wrote', out, 'seed_edges=', len(s2['seed_edges']))

if __name__=='__main__':
    main()
