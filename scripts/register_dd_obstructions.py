#!/usr/bin/env python3
"""Collect unique dd_shrink results, verify via global CP-SAT, and record obstruction artifacts.

Usage:
  python scripts/register_dd_obstructions.py --k 40 --time-limit 30 --seed 212 --commit

"""
from __future__ import annotations

import json
import glob
import time
import subprocess
from pathlib import Path
from collections import defaultdict

BASE = Path.cwd()
CHECKS = BASE / 'checks'
ART = BASE / 'committed_artifacts'

# helpers
def load_json(p):
    return json.loads(open(p, encoding='utf-8').read())

# collect dd_shrink outputs
outs = glob.glob(str(CHECKS / 'PART_CVII_dd_shrink_result_*.json'))
by_result = defaultdict(list)
for p in outs:
    j = load_json(p)
    res = tuple(sorted(j.get('result', [])))
    by_result[res].append({'path': p, 'json': j})

print('Found', len(by_result), 'unique dd_shrink results')

# load bij
bij = load_json(str(ART / 'PART_CVII_e8_bijection_intermediate_1770491863.json'))['bijection']
bij = {int(k): int(v) for k, v in bij.items()}

# helper to write seed
def write_seed_for_edges(edges, outpath):
    seed_edges = []
    for e in edges:
        if e in bij:
            seed_edges.append({'edge_index': int(e), 'root_index': int(bij[e])})
    out = {'seed_edges': seed_edges, 'rotation': None}
    open(outpath, 'w', encoding='utf-8').write(json.dumps(out, indent=2))
    return outpath

# helper to get edge endpoints from adjacency
def edge_endpoints(edge_idx):
    adj = []
    with open(CHECKS.parent / 'W33_adjacency_matrix.txt', encoding='utf-8') as f:
        for line in f:
            row = [int(x) for x in line.strip().split()]
            adj.append(row)
    n = len(adj)
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if adj[i][j] == 1:
                edges.append((i, j))
    if edge_idx < 0 or edge_idx >= len(edges):
        return None
    return edges[edge_idx]

# load e8 roots
from e8_embedding_group_theoretic import generate_e8_roots, vec_dot, vec_add, vec_sub, vec_neg
roots = generate_e8_roots()

# Result artifacts will be written to checks/PART_CVII_dd_pair_obstruction_<ts>.json
for res, entries in by_result.items():
    if not res:
        continue
    ts = int(time.time())
    print('\nProcessing result', res, 'from', len(entries), 'dd outputs')
    seed_path = CHECKS / f'_tmp_seed_dd_verify_{ts}.json'
    write_seed_for_edges(res, seed_path)
    # run global CP-SAT check
    cmd = ['py', '-3', 'scripts/solve_e8_embedding_cpsat.py', '--seed-json', str(seed_path), '--k', '40', '--time-limit', '30', '--seed', '212', '--force-seed']
    print('Running solver:', ' '.join(cmd))
    proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # read solver JSON output
    sol_json_path = CHECKS / 'PART_CVII_e8_embedding_cpsat.json'
    sol_json = None
    if sol_json_path.exists():
        sol_json = load_json(sol_json_path)

    # build artifact
    art = {
        'dd_shrink_results': [e['path'] for e in entries],
        'set': list(res),
        'edges': list(res),
        'vertices': [list(edge_endpoints(e)) for e in res],
        'roots': [bij[e] for e in res],
        'root_vectors': {str(bij[e]): roots[bij[e]] for e in res},
        'dot_products': None,
        'sum_is_root': None,
        'diff_is_root': None,
        'solver_check': str(sol_json_path) if sol_json_path.exists() else None,
        'solver_status': sol_json.get('status') if sol_json else None,
        'notes': 'Auto-verified by register_dd_obstructions.py'
    }
    if len(res) == 2:
        a,b = res
        ra = roots[bij[a]]
        rb = roots[bij[b]]
        art['dot_products'] = vec_dot(ra, rb)
        # Use vec_neg to check negations properly
        art['sum_is_root'] = (vec_add(ra, rb) in roots) or (vec_neg(vec_add(ra, rb)) in roots)
        art['diff_is_root'] = (vec_sub(ra, rb) in roots) or (vec_neg(vec_sub(ra, rb)) in roots)
    stamp = int(time.time())
    outp = CHECKS / f'PART_CVII_dd_pair_obstruction_{stamp}.json'
    open(outp, 'w', encoding='utf-8').write(json.dumps(art, indent=2))
    print('Wrote', outp)
    # mirror to committed_artifacts
    art_out = ART / outp.name
    art_out.write_text(open(outp, encoding='utf-8').read(), encoding='utf-8')
    print('Mirrored to', art_out)

    # append to forbids list if solver returned INFEASIBLE
    if sol_json and sol_json.get('status') == 'INFEASIBLE':
        forb_path = CHECKS / 'PART_CVII_forbids.json'
        forb = {'obstruction_sets': []}
        if forb_path.exists():
            forb = load_json(forb_path)
        entry = {'set': list(res), 'roots': [bij[e] for e in res], 'timestamp': int(time.time()), 'source_dd': [e['path'] for e in entries]}
        forb.setdefault('obstruction_sets', []).append(entry)
        open(forb_path, 'w', encoding='utf-8').write(json.dumps(forb, indent=2))
        print('Appended to forbids:', forb_path)
        # mirror forbids too
        (ART / forb_path.name).write_text(open(forb_path, encoding='utf-8').read(), encoding='utf-8')
        print('Mirrored forbids to committed_artifacts')

print('\nDone')
