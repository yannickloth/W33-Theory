#!/usr/bin/env python3
import json, time, subprocess, glob, os
from pathlib import Path
BASE = Path.cwd()
CHECKS = BASE / 'checks'
ART = BASE / 'committed_artifacts'

def load_json(p):
    return json.loads(open(p, encoding='utf-8').read())

# find dd_shrink_result files mentioning result [50,51]
matches = []
for p in glob.glob(str(CHECKS / 'PART_CVII_dd_shrink_result_*.json')):
    try:
        j = load_json(p)
        if j.get('result') == [50, 51]:
            matches.append(p)
    except Exception:
        pass

if not matches:
    print('No dd_shrink_result files for [50,51] found in checks')
    raise SystemExit(1)

print('Found dd_shrink_result files:', matches)
# pick the first one to get seed info
j = load_json(matches[0])
seed_art = j.get('seed_artifact')
seed_map = j.get('seed_map')
seed_json_path = None
seed_source_used = None
if seed_art:
    sp = Path(seed_art)
    if not sp.exists():
        sp = Path.cwd() / sp if not sp.is_absolute() else sp
        if not sp.exists():
            sp = Path.cwd() / 'committed_artifacts' / Path(seed_art).name
    if sp.exists():
        seed_json_path = sp
        seed_source_used = f'td_shrink_seed_artifact:{sp}'

if seed_json_path is None and seed_map:
    # write tmp seed JSON from seed_map
    tmp_seed = CHECKS / f'_tmp_seed_dd_verify_manual_{int(time.time())}.json'
    se = [{'edge_index': int(k), 'root_index': int(v)} for k, v in seed_map.items()]
    open(tmp_seed, 'w', encoding='utf-8').write(json.dumps({'seed_edges': se, 'rotation': None}, indent=2))
    seed_json_path = tmp_seed
    seed_source_used = 'dd_shrink_result_seed_map'

if seed_json_path is None:
    # fallback to bijection map
    bij = load_json(str(ART / 'PART_CVII_e8_bijection_intermediate_1770491863.json'))['bijection']
    seed_edges = []
    for e in [50,51]:
        if str(e) in bij:
            seed_edges.append({'edge_index': int(e), 'root_index': int(bij[str(e)])})
    tmp_seed = CHECKS / f'_tmp_seed_dd_verify_manual_{int(time.time())}.json'
    open(tmp_seed, 'w', encoding='utf-8').write(json.dumps({'seed_edges': seed_edges, 'rotation': None}, indent=2))
    seed_json_path = tmp_seed
    seed_source_used = 'bijection_map'

print('Using seed JSON:', seed_json_path, 'source:', seed_source_used)
# run solver
cmd = ['py', '-3', 'scripts/solve_e8_embedding_cpsat.py', '--seed-json', str(seed_json_path), '--k', '40', '--time-limit', '30', '--seed', '212', '--force-seed']
print('Running solver:', ' '.join(cmd))
proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print('Solver stdout len', len(proc.stdout), 'stderr len', len(proc.stderr))
# read solver JSON
sol_json_path = CHECKS / 'PART_CVII_e8_embedding_cpsat.json'
sol_json = None
if sol_json_path.exists():
    sol_json = load_json(sol_json_path)

# Build artifact similar to register_dd_obstructions
from e8_embedding_group_theoretic import generate_e8_roots, vec_dot, vec_add, vec_sub, vec_neg
roots = generate_e8_roots()

art = {
    'dd_shrink_results': matches,
    'set': [50,51],
    'edges': [50,51],
    'vertices': [],
    'roots': None,
    'root_vectors': None,
    'dot_products': None,
    'sum_is_root': None,
    'diff_is_root': None,
    'solver_check': str(sol_json_path) if sol_json_path.exists() else None,
    'solver_status': sol_json.get('status') if sol_json else None,
    'seed_source_used': seed_source_used,
    'used_seed_json': str(seed_json_path),
    'verified_roots': [seed_map.get('50'), seed_map.get('51')] if seed_map else None,
    'notes': 'Manual registration by _tmp script'
}
# attempt to compute vertices from adjacency
adj = []
with open('W33_adjacency_matrix.txt', encoding='utf-8') as f:
    for line in f:
        adj.append([int(x) for x in line.strip().split()])
# build edge list
edges = []
n = len(adj)
for i in range(n):
    for j in range(i+1, n):
        if adj[i][j] == 1:
            edges.append((i,j))
for e in [50,51]:
    if e < len(edges):
        art['vertices'].append(list(edges[e]))
# decide roots to record
if art['verified_roots'] and all(r is not None for r in art['verified_roots']):
    art['roots'] = art['verified_roots']
else:
    bij = load_json(str(ART / 'PART_CVII_e8_bijection_intermediate_1770491863.json'))['bijection']
    art['roots'] = [int(bij[str(50)]), int(bij[str(51)])]
art['root_vectors'] = {str(r): roots[r] for r in art['roots'] if r is not None}
# compute dot_products if possible
if len(art['roots']) == 2 and art['roots'][0] is not None and art['roots'][1] is not None:
    ra = roots[art['roots'][0]]
    rb = roots[art['roots'][1]]
    art['dot_products'] = vec_dot(ra, rb)
    art['sum_is_root'] = (vec_add(ra, rb) in roots) or (vec_neg(vec_add(ra, rb)) in roots)
    art['diff_is_root'] = (vec_sub(ra, rb) in roots) or (vec_neg(vec_sub(ra, rb)) in roots)

stamp = int(time.time())
outp = CHECKS / f'PART_CVII_dd_pair_obstruction_{stamp}.json'
open(outp, 'w', encoding='utf-8').write(json.dumps(art, indent=2))
print('Wrote', outp)
# mirror
(ART / outp.name).write_text(open(outp, encoding='utf-8').read(), encoding='utf-8')
print('Mirrored to committed_artifacts')
# append to forbids if infeasible
if sol_json and sol_json.get('status') == 'INFEASIBLE':
    forb_path = CHECKS / 'PART_CVII_forbids.json'
    forb = {'obstruction_sets': []}
    if forb_path.exists():
        forb = load_json(forb_path)
    entry = {'set': [50,51], 'roots': art['roots'], 'timestamp': int(time.time()), 'source_dd': matches, 'seed_source_used': seed_source_used}
    forb.setdefault('obstruction_sets', []).append(entry)
    open(forb_path, 'w', encoding='utf-8').write(json.dumps(forb, indent=2))
    (ART / forb_path.name).write_text(open(forb_path, encoding='utf-8').read(), encoding='utf-8')
    print('Appended to forbids and mirrored')
print('Done')
