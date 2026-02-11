#!/usr/bin/env python3
"""Simulated-annealing search for generator correspondence mapping (sigma).

This runs a time-limited SA across candidate base roots (top scans) and returns the
best sigma found. Optionally runs local repair on the best seed.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def invert_perm(perm: List[int]) -> List[int]:
    n = len(perm)
    inv = [0] * n
    for i, v in enumerate(perm):
        inv[v] = i
    return inv


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


def count_tri_satisfied(predicted: dict, roots, edge_entries) -> (int, int):
    edge_to_pair = {}
    for eidx in edge_entries:
        ent = edge_entries[eidx]
        if ent.get("edge"):
            pair = tuple(map(int, ent["edge"]))
        else:
            pair = (int(ent.get("v_i", 0)), int(ent.get("v_j", 0)))
        edge_to_pair[int(eidx)] = pair
    pair_to_edge = {tuple(sorted(v)): k for k, v in edge_to_pair.items()}
    nverts = 40
    adj = {i: set() for i in range(nverts)}
    for i, j in edge_to_pair.values():
        adj[i].add(j)
        adj[j].add(i)
    triangles = []
    for a in range(nverts):
        for b in sorted(adj[a]):
            if b <= a:
                continue
            for c in sorted(adj[b]):
                if c <= b:
                    continue
                if a in adj[c]:
                    e_ab = pair_to_edge[(a, b)]
                    e_bc = pair_to_edge[(b, c)]
                    e_ac = pair_to_edge[(a, c)]
                    triangles.append((e_ab, e_bc, e_ac))
    tri_ok = 0
    for e1, e2, e3 in triangles:
        r1 = roots[predicted[e1]]
        r2 = roots[predicted[e2]]
        r3 = roots[predicted[e3]]
        ok = all(int(r1[i] + r2[i]) == int(r3[i]) for i in range(8))
        if ok:
            tri_ok += 1
    return tri_ok, len(triangles)


def score_pred(predicted, roots, edge_entries):
    vals = list(predicted.values())
    from collections import Counter

    cnt = Counter(vals)
    duplicates = sum(v - 1 for v in cnt.values() if v > 1)
    bij = 1 if duplicates == 0 else 0
    tri_ok, tri_total = count_tri_satisfied(predicted, roots, edge_entries)
    score = bij * 1_000_000 + tri_ok * 1000 - duplicates
    return score, bij, tri_ok, duplicates


def run_sa_for_base(edge_entries, gens, inv_gens, roots, base_root, budget_sec=60):
    # determine n_src
    max_tok = -1
    for ent in edge_entries.values():
        for tok in ent.get("word", []) or []:
            if tok >= 0:
                max_tok = max(max_tok, tok)
            else:
                idx = -tok - 1
                max_tok = max(max_tok, idx)
    n_src = max_tok + 1
    n_target = len(gens)

    # initial sigma: map 0..n_src-1 to 0..n_src-1 (if available)
    sigma = list(range(n_src))
    if n_src > n_target:
        sigma = [i % n_target for i in range(n_src)]
    # allow unused target indices
    unused = [i for i in range(n_target) if i not in sigma]

    # compute initial
    best_pred = apply_sigma_to_words(edge_entries, gens, inv_gens, sigma, base_root)
    best_score, best_bij, best_tri_ok, best_dup = score_pred(
        best_pred, roots, edge_entries
    )
    best_sigma = list(sigma)

    # current score corresponding to current sigma
    score_curr = best_score

    start = time.time()
    iters = 0
    T0 = 0.5
    while time.time() - start < budget_sec:
        iters += 1
        # propose move
        move = random.random()
        sigma_new = list(sigma)
        if move < 0.8:
            # swap two source indices
            i = random.randrange(0, n_src)
            j = random.randrange(0, n_src)
            sigma_new[i], sigma_new[j] = sigma_new[j], sigma_new[i]
        else:
            # replace one mapping from unused if available
            if unused:
                i = random.randrange(0, n_src)
                newt = random.choice(unused)
                old = sigma_new[i]
                sigma_new[i] = newt
        pred_new = apply_sigma_to_words(
            edge_entries, gens, inv_gens, sigma_new, base_root
        )
        score_new, bij2, tri_ok2, dup2 = score_pred(pred_new, roots, edge_entries)
        # acceptance: compare to current sigma score; update best if improved
        if score_new > score_curr:
            sigma = sigma_new
            score_curr = score_new
            if score_new > best_score:
                best_score = score_new
                best_bij = bij2
                best_tri_ok = tri_ok2
                best_dup = dup2
                best_sigma = list(sigma_new)
                best_pred = pred_new
        else:
            # Metropolis acceptance based on score delta and temperature
            frac = (time.time() - start) / budget_sec
            T = T0 * (1 - frac) + 1e-6
            delta = score_new - score_curr
            exponent = delta / (T * 1e3) if T > 0 else -float("inf")
            # clamp exponent to avoid overflow in math.exp
            if exponent > 700:
                p = 1.0
            elif exponent < -700:
                p = 0.0
            else:
                p = math.exp(exponent)
            if random.random() < p:
                sigma = sigma_new
                score_curr = score_new
    return {
        "base": base_root,
        "best_score": best_score,
        "best_bij": int(best_bij),
        "best_tri_ok": int(best_tri_ok),
        "best_dup": int(best_dup),
        "best_sigma": best_sigma,
        "best_pred": best_pred,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--time-limit", type=float, default=600.0, help="Total time budget in seconds"
    )
    parser.add_argument(
        "--per-base",
        type=float,
        default=None,
        help="Time budget per base (overrides automatic splitting)",
    )
    parser.add_argument(
        "--local-repair",
        action="store_true",
        help="Run local repair on best seed after search",
    )
    parser.add_argument(
        "--local-time",
        type=float,
        default=120.0,
        help="Local repair time limit in seconds",
    )
    args = parser.parse_args()

    canonical_path = ROOT / "artifacts" / "edge_root_bijection_canonical.json"
    canonical = load_json(canonical_path)
    edge_entries = {int(e["edge_index"]): e for e in canonical}

    gen_map_path = ROOT / "artifacts" / "sp43_we6_generator_map_full_we6.json"
    gen_data = load_json(gen_map_path)
    gens = gen_data.get("generators")
    inv_gens = [invert_perm(g) for g in gens]

    # roots
    import importlib.util as _importlib_util

    spec = _importlib_util.spec_from_file_location(
        "compute_double_sixes", str(ROOT / "tools" / "compute_double_sixes.py")
    )
    cds = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(cds)
    roots = cds.construct_e8_roots()

    # base candidates
    scan_path = ROOT / "checks" / "PART_CVII_coset_base_scan.json"
    bases = []
    if scan_path.exists():
        dd = load_json(scan_path)
        tops = dd.get("top", [])
        bases = [t["base_root"] for t in tops[:10]]
    # canonical base
    canonical_base = None
    for ent in edge_entries.values():
        if not ent.get("word"):
            canonical_base = int(ent["root_index"])
            break
    if canonical_base is not None:
        bases.insert(0, canonical_base)
    bases = sorted(list(dict.fromkeys(bases)))

    if args.per_base is None:
        per_base = max(args.time_limit / max(1, len(bases)), 30.0)
    else:
        per_base = args.per_base

    best_overall = None
    start_all = time.time()
    for base in bases:
        elapsed = time.time() - start_all
        if elapsed > args.time_limit:
            break
        remain = args.time_limit - elapsed
        budget = min(per_base, remain)
        print(f"Searching base {base} with budget {budget:.1f}s")
        res = run_sa_for_base(edge_entries, gens, inv_gens, roots, base, budget)
        print(
            f"base {base} -> bij {res['best_bij']} tri_ok {res['best_tri_ok']} dup {res['best_dup']}"
        )
        if best_overall is None or res["best_score"] > best_overall["best_score"]:
            best_overall = res

    # write results
    (ROOT / "checks" / "PART_CVII_generator_correspondence_sa.json").write_text(
        json.dumps(best_overall, indent=2)
    )
    # write mapping artifact
    preds = best_overall["best_pred"]
    map_list = []
    for eidx in sorted(preds.keys()):
        ent = edge_entries[eidx]
        r = int(preds[eidx])
        map_list.append(
            {
                "edge_index": int(eidx),
                "edge": ent.get(
                    "edge", [int(ent.get("v_i", 0)), int(ent.get("v_j", 0))]
                ),
                "root_index": r,
            }
        )
    (ROOT / "artifacts" / "edge_root_bijection_genmap_sa_best.json").write_text(
        json.dumps(map_list, indent=2)
    )
    print(
        "Wrote SA best mapping and summary to checks/PART_CVII_generator_correspondence_sa.json"
    )

    if args.local_repair:
        # create seed file and run local_repair
        seed = {
            "seed_edges": [
                {
                    "edge_index": int(it["edge_index"]),
                    "edge": it["edge"],
                    "root_index": int(it["root_index"]),
                }
                for it in map_list
            ]
        }
        seed_path = ROOT / "checks" / "PART_CVII_e8_embedding_genmap_sa_seed.json"
        seed_path.write_text(json.dumps(seed, indent=2))
        print("Wrote seed", seed_path)
        import subprocess

        cmd = [
            "py",
            "-3",
            "scripts/local_repair_matching.py",
            "--k",
            "30",
            "--time-limit",
            str(int(args.local_time)),
            "--seed-json",
            str(seed_path),
            "--tries",
            "500000",
        ]
        print("Running local repair:", " ".join(cmd))
        subprocess.run(" ".join(cmd), shell=True)


if __name__ == "__main__":
    main()
