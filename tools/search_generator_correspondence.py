#!/usr/bin/env python3
"""Search for generator index correspondence (source -> target) that maximizes
triangle satisfaction and bijectivity when applying generator words to a base root.

Approach: for a set of candidate base roots (default: top from previous scan + canonical base root),
perform random-swapping local search on sigma mapping source gens -> target gens.

Writes best mapping artifact to checks/PART_CVII_generator_correspondence_search.json
and best predicted mapping to artifacts/edge_root_bijection_genmap_best.json
"""
from __future__ import annotations

import json
import random
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def invert_perm(perm: List[int]) -> List[int]:
    n = len(perm)
    inv = [0] * n
    for i, v in enumerate(perm):
        inv[v] = i
    return inv


def count_tri_satisfied(predicted: dict, roots: List[Tuple[int, ...]], edge_entries: dict) -> Tuple[int, int]:
    # build pair map
    edge_to_pair = {}
    for eidx, ent in edge_entries.items():
        if ent.get('edge'):
            pair = tuple(map(int, ent['edge']))
        else:
            pair = (int(ent.get('v_i', 0)), int(ent.get('v_j', 0)))
        edge_to_pair[int(eidx)] = pair
    pair_to_edge = {tuple(sorted(v)): k for k, v in edge_to_pair.items()}
    nverts = 40
    adj = {i: set() for i in range(nverts)}
    for (i, j) in edge_to_pair.values():
        adj[i].add(j); adj[j].add(i)
    triangles = []
    for a in range(nverts):
        for b in sorted(adj[a]):
            if b <= a: continue
            for c in sorted(adj[b]):
                if c <= b: continue
                if a in adj[c]:
                    e_ab = pair_to_edge[(a, b)]
                    e_bc = pair_to_edge[(b, c)]
                    e_ac = pair_to_edge[(a, c)]
                    triangles.append((e_ab, e_bc, e_ac))
    tri_ok = 0
    for (e1, e2, e3) in triangles:
        r1 = roots[predicted[e1]]
        r2 = roots[predicted[e2]]
        r3 = roots[predicted[e3]]
        ok = all(int(r1[i] + r2[i]) == int(r3[i]) for i in range(8))
        if ok: tri_ok += 1
    return tri_ok, len(triangles)


def score_mapping(predicted: dict, roots: List[Tuple[int, ...]], edge_entries: dict) -> Tuple[int, int, int]:
    # returns tuple (bijective_flag, tri_ok_count, -duplicates)
    values = list(predicted.values())
    cnt = Counter(values)
    duplicates = sum(v - 1 for v in cnt.values() if v > 1)
    bij = 1 if duplicates == 0 else 0
    tri_ok, tri_total = count_tri_satisfied(predicted, roots, edge_entries)
    return bij, tri_ok, -duplicates


def apply_sigma_to_words(edge_entries, gens, inv_gens, sigma, base_root):
    predicted = {}
    n_gens = len(gens)
    for eidx, ent in edge_entries.items():
        word = ent.get("word", []) or []
        p = base_root
        for tok in word:
            if tok >= 0:
                mapped = sigma[tok]
                if mapped >= n_gens:
                    # invalid mapping
                    p = None
                    break
                p = gens[mapped][p]
            else:
                idx = -tok - 1
                mapped = sigma[idx]
                p = inv_gens[mapped][p]
        if p is None:
            predicted[eidx] = -1
        else:
            predicted[eidx] = int(p)
    return predicted


def main():
    random.seed(42)
    canonical_path = ROOT / "artifacts" / "edge_root_bijection_canonical.json"
    if not canonical_path.exists():
        raise SystemExit("Run canonical bijection first")
    canonical = load_json(canonical_path)
    edge_entries = {int(e["edge_index"]): e for e in canonical}

    gen_map_path = ROOT / "artifacts" / "sp43_we6_generator_map_full_we6.json"
    gen_data = load_json(gen_map_path)
    gens = gen_data.get("generators")
    inv_gens = [invert_perm(g) for g in gens]

    # load roots
    import importlib.util as _importlib_util
    spec = _importlib_util.spec_from_file_location("compute_double_sixes", str(ROOT / "tools" / "compute_double_sixes.py"))
    cds = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(cds)
    roots = cds.construct_e8_roots()

    # determine source gens count from words
    max_tok = -1
    for ent in edge_entries.values():
        for tok in ent.get('word', []) or []:
            if tok >= 0:
                max_tok = max(max_tok, tok)
            else:
                idx = -tok - 1
                max_tok = max(max_tok, idx)
    n_src = max_tok + 1
    n_target = len(gens)
    print(f"n_src={n_src} n_target={n_target} base candidates...")

    # base root candidates: top from previous scan if exists
    scan_path = ROOT / "checks" / "PART_CVII_coset_base_scan.json"
    bases = []
    if scan_path.exists():
        dd = load_json(scan_path)
        tops = dd.get('top', [])
        bases = [t['base_root'] for t in tops[:10]]
    # always include canonical base root
    canonical_base = None
    for ent in edge_entries.values():
        if not ent.get('word'):
            canonical_base = int(ent['root_index'])
            break
    if canonical_base is not None:
        bases.insert(0, canonical_base)
    # dedup
    bases = sorted(list(dict.fromkeys(bases)))
    print('base candidates', bases)

    best_global = None
    # search parameters
    time_budget = 30.0  # seconds
    t0 = time.time()

    for base_root in bases:
        # initial sigma: identity mapping to first n_src target indices
        if n_src <= n_target:
            sigma = list(range(n_src))
        else:
            # should not happen, but pad
            sigma = [i % n_target for i in range(n_src)]
        # if n_src < n_target we may later swap in unused target indices
        unused = [i for i in range(n_target) if i not in sigma]

        # compute base score
        pred = apply_sigma_to_words(edge_entries, gens, inv_gens, sigma, base_root)
        bij, tri_ok, neg_dups = score_mapping(pred, roots, edge_entries)
        best = {'sigma': list(sigma), 'base': base_root, 'bij': bij, 'tri_ok': tri_ok, 'neg_dups': neg_dups, 'predicted': pred}
        print(f"base {base_root} initial bij {bij} tri_ok {tri_ok} dup {-neg_dups}")

        iters = 0
        # local search loop
        while time.time() - t0 < time_budget:
            iters += 1
            # propose swap: pick two source indices i,j and swap their mapped targets
            i = random.randrange(0, n_src)
            j = random.randrange(0, n_src)
            if i == j: continue
            sigma_new = list(sigma)
            sigma_new[i], sigma_new[j] = sigma_new[j], sigma_new[i]
            pred_new = apply_sigma_to_words(edge_entries, gens, inv_gens, sigma_new, base_root)
            bij2, tri_ok2, neg_dups2 = score_mapping(pred_new, roots, edge_entries)
            score_old = (best['bij']*10000 + best['tri_ok']*10 + -best['neg_dups'])
            score_new = (bij2*10000 + tri_ok2*10 + -neg_dups2)
            if score_new > score_old:
                sigma = sigma_new
                best = {'sigma': list(sigma), 'base': base_root, 'bij': bij2, 'tri_ok': tri_ok2, 'neg_dups': neg_dups2, 'predicted': pred_new}
            # occasionally try random reassignment to unused target index if available
            if random.random() < 0.01 and unused:
                i = random.randrange(0, n_src)
                j_target = random.choice(unused)
                sigma_new = list(sigma)
                # replace sigma_new[i] with j_target ensuring injectivity by putting old value to unused
                old = sigma_new[i]
                sigma_new[i] = j_target
                # update unused set temporarily
                pred_new = apply_sigma_to_words(edge_entries, gens, inv_gens, sigma_new, base_root)
                bij2, tri_ok2, neg_dups2 = score_mapping(pred_new, roots, edge_entries)
                score_new = (bij2*10000 + tri_ok2*10 + -neg_dups2)
                if score_new > score_old:
                    sigma = sigma_new
                    # recompute unused
                    unused = [i for i in range(n_target) if i not in sigma]
                    best = {'sigma': list(sigma), 'base': base_root, 'bij': bij2, 'tri_ok': tri_ok2, 'neg_dups': neg_dups2, 'predicted': pred_new}

        print(f"base {base_root} best bij {best['bij']} tri_ok {best['tri_ok']} dup {-best['neg_dups']}")
        if best_global is None or (best['bij']*10000 + best['tri_ok']*10 + -best['neg_dups']) > (best_global['bij']*10000 + best_global['tri_ok']*10 + -best_global['neg_dups']):
            best_global = best

    # write best_global to file
    out = {
        'best_base': int(best_global['base']),
        'best_sigma': best_global['sigma'],
        'best_bij': int(best_global['bij']),
        'best_tri_ok': int(best_global['tri_ok']),
        'best_dup': -int(best_global['neg_dups'])
    }
    (ROOT / 'checks' / 'PART_CVII_generator_correspondence_search.json').write_text(json.dumps(out, indent=2))
    # also write predicted mapping artifact
    map_list = []
    preds = best_global['predicted']
    for eidx in sorted(preds.keys()):
        ent = edge_entries[eidx]
        r = int(preds[eidx])
        map_list.append({
            'edge_index': int(eidx),
            'edge': ent.get('edge', [int(ent.get('v_i',0)), int(ent.get('v_j',0))]),
            'root_index': r
        })
    (ROOT / 'artifacts' / 'edge_root_bijection_genmap_best.json').write_text(json.dumps(map_list, indent=2))
    print('Wrote best results to checks/PART_CVII_generator_correspondence_search.json and artifact mapping')


if __name__ == '__main__':
    main()
