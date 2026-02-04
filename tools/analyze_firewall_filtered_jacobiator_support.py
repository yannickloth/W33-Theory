#!/usr/bin/env python3
"""
Analyze the Jacobiator support of the "firewall-filtered" E8 bracket where we zero out
all g1×g1→g2 and g2×g2→g1 couplings whose underlying E6 i27-triad is firewall-forbidden.

This bracket is intentionally *not* a Lie algebra; the question is:
  - where does Jacobi fail?
  - which grades/basis indices does the Jacobiator live in?
  - how big is the span of observed Jacobiators?

Inputs:
  - artifacts/e8_structure_constants_w33_discrete.json
  - artifacts/e8_root_metadata_table.json
  - artifacts/firewall_bad_triads_mapping.json

Outputs:
  - artifacts/firewall_filtered_jacobiator_support.json
  - artifacts/firewall_filtered_jacobiator_support.md
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from random import Random
from typing import Dict, Iterable, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_SC = ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json"
IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
IN_FW = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
OUT_JSON = ROOT / "artifacts" / "firewall_filtered_jacobiator_support.json"
OUT_MD = ROOT / "artifacts" / "firewall_filtered_jacobiator_support.md"


Pair = Tuple[int, int]
Root = Tuple[int, ...]
Terms = List[Tuple[int, int]]


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=200_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--max_store",
        type=int,
        default=2000,
        help="store up to this many nonzero Jacobiators",
    )
    return ap.parse_args()


def _triad_key(a: int, b: int, c: int) -> Tuple[int, int, int]:
    return tuple(sorted((int(a), int(b), int(c))))


def _load_meta_by_root_orbit() -> Dict[Root, dict]:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    out: Dict[Root, dict] = {}
    for r in meta["rows"]:
        rt = tuple(int(x) for x in r["root_orbit"])
        out[rt] = r
    if len(out) != 240:
        raise RuntimeError("Expected 240 roots in metadata")
    return out


def _load_firewall_triads() -> set[Tuple[int, int, int]]:
    fw = json.loads(IN_FW.read_text(encoding="utf-8"))
    bad = {_triad_key(*t) for t in fw["bad_triangles_Schlafli_e6id"]}
    if len(bad) != 9:
        raise RuntimeError("Expected 9 firewall triads")
    return bad


def _parse_brackets(sc: dict) -> Dict[Pair, Terms]:
    table: Dict[Pair, Terms] = {}
    for key, terms in sc["brackets"].items():
        i_str, j_str = key.split(",")
        i, j = int(i_str), int(j_str)
        table[(i, j)] = [(int(k), int(c)) for k, c in terms]
    return table


def _random_triples(n: int, samples: int, seed: int) -> Iterable[Tuple[int, int, int]]:
    rng = Random(seed)
    for _ in range(samples):
        i = rng.randrange(n)
        j = rng.randrange(n - 1)
        if j >= i:
            j += 1
        a, b = (i, j) if i < j else (j, i)
        k0 = rng.randrange(n - 2)
        k = k0
        if k >= a:
            k += 1
        if k >= b:
            k += 1
        x, y, z = sorted((i, j, k))
        yield x, y, z


def _get_terms_filtered(
    i: int, j: int, table: Dict[Pair, Terms], forbidden: set[Pair]
) -> Tuple[int, Terms]:
    if i == j:
        return 1, []
    if i < j:
        if (i, j) in forbidden:
            return 1, []
        return 1, table.get((i, j), [])
    if (j, i) in forbidden:
        return -1, []
    return -1, table.get((j, i), [])


def _bracket_left_add(
    out: Dict[int, int],
    left: int,
    vec_terms: Terms,
    scalar: int,
    table: Dict[Pair, Terms],
    forbidden: set[Pair],
) -> None:
    if scalar == 0 or not vec_terms:
        return
    for b, c in vec_terms:
        coeff_b = scalar * c
        if coeff_b == 0 or b == left:
            continue
        s, terms = _get_terms_filtered(left, b, table, forbidden)
        if not terms:
            continue
        for k, ck in terms:
            v = out.get(k, 0) + coeff_b * s * ck
            if v:
                out[k] = v
            else:
                out.pop(k, None)


def _jacobi(
    i: int, j: int, k: int, table: Dict[Pair, Terms], forbidden: set[Pair]
) -> Dict[int, int]:
    out: Dict[int, int] = {}
    s_jk, t_jk = _get_terms_filtered(j, k, table, forbidden)
    _bracket_left_add(out, i, t_jk, s_jk, table, forbidden)
    s_ki, t_ki = _get_terms_filtered(k, i, table, forbidden)
    _bracket_left_add(out, j, t_ki, s_ki, table, forbidden)
    s_ij, t_ij = _get_terms_filtered(i, j, table, forbidden)
    _bracket_left_add(out, k, t_ij, s_ij, table, forbidden)
    return out


def main() -> None:
    args = _parse_args()
    sc = json.loads(IN_SC.read_text(encoding="utf-8"))
    basis = sc["basis"]
    n = int(basis["n"])
    cartan_dim = int(basis["cartan_dim"])
    roots: List[List[int]] = basis["roots"]
    if n != 248 or cartan_dim != 8 or len(roots) != 240:
        raise RuntimeError("Unexpected basis sizing")

    meta_by_root = _load_meta_by_root_orbit()
    bad_triads = _load_firewall_triads()
    table = _parse_brackets(sc)

    grade_by_idx: List[str] = ["g0"] * n
    for i in range(cartan_dim, n):
        rt = tuple(int(x) for x in roots[i - cartan_dim])
        grade_by_idx[i] = str(meta_by_root[rt]["grade"])

    def grade_of(idx: int) -> str:
        return "g0" if idx < cartan_dim else grade_by_idx[idx]

    # forbidden root-pairs (basis indices i<j) based on firewall triads.
    forbidden: set[Pair] = set()
    for (i, j), terms in table.items():
        if i < cartan_dim or j < cartan_dim:
            continue
        if not terms or len(terms) != 1:
            continue
        k, _c = terms[0]
        if k < cartan_dim:
            continue
        rt_i = tuple(int(x) for x in roots[i - cartan_dim])
        rt_j = tuple(int(x) for x in roots[j - cartan_dim])
        rt_k = tuple(int(x) for x in roots[k - cartan_dim])
        gi = meta_by_root[rt_i]["grade"]
        gj = meta_by_root[rt_j]["grade"]
        gk = meta_by_root[rt_k]["grade"]
        if (gi, gj, gk) not in (("g1", "g1", "g2"), ("g2", "g2", "g1")):
            continue
        a27 = meta_by_root[rt_i].get("i27")
        b27 = meta_by_root[rt_j].get("i27")
        c27 = meta_by_root[rt_k].get("i27")
        if a27 is None or b27 is None or c27 is None:
            continue
        if _triad_key(a27, b27, c27) in bad_triads:
            forbidden.add((i, j))

    t0 = time.time()
    failures = 0
    input_grade_hist = Counter()
    output_grade_hist = Counter()
    output_idx_hist = Counter()
    jacobi_size_hist = Counter()
    by_input_grade = defaultdict(Counter)  # input pattern -> output grade hist

    stored: List[Dict[str, object]] = []

    for_checked = 0
    for i, j, k in _random_triples(n, args.samples, args.seed):
        for_checked += 1
        gi, gj, gk = grade_of(i), grade_of(j), grade_of(k)
        pat = tuple(sorted((gi, gj, gk)))
        J = _jacobi(i, j, k, table, forbidden)
        if not J:
            continue
        failures += 1
        input_grade_hist[str(pat)] += 1
        jacobi_size_hist[len(J)] += 1

        for idx, coeff in J.items():
            go = grade_of(idx)
            output_grade_hist[go] += 1
            output_idx_hist[idx] += 1
            by_input_grade[str(pat)][go] += 1

        if len(stored) < args.max_store:
            stored.append(
                {
                    "triple": [int(i), int(j), int(k)],
                    "input_grades": [gi, gj, gk],
                    "jacobi": [[int(a), int(b)] for a, b in sorted(J.items())],
                }
            )

    dt = time.time() - t0

    # Estimate span ranks of observed Jacobiators in each grade, using real rank on stored ones.
    # (This is just a diagnostic, not a proof.)
    stored_vecs = stored
    idx_list = sorted({idx for rec in stored_vecs for idx, _c in rec["jacobi"]})
    idx_pos = {idx: p for p, idx in enumerate(idx_list)}
    M = np.zeros((len(stored_vecs), len(idx_list)), dtype=np.float64)
    for r, rec in enumerate(stored_vecs):
        for idx, c in rec["jacobi"]:
            M[r, idx_pos[idx]] = float(c)
    rank_all = int(np.linalg.matrix_rank(M, tol=1e-9)) if M.size else 0

    out = {
        "status": "ok",
        "samples": int(args.samples),
        "seed": int(args.seed),
        "counts": {
            "basis_n": n,
            "forbidden_pairs": int(len(forbidden)),
            "triples_checked": int(for_checked),
            "jacobi_failures": int(failures),
            "failure_rate": float(failures / max(1, for_checked)),
        },
        "histograms": {
            "input_grade_patterns": dict(input_grade_hist),
            "jacobi_term_counts": {str(k): int(v) for k, v in jacobi_size_hist.items()},
            "output_grade": dict(output_grade_hist),
            "top_output_indices": [
                {"idx": int(idx), "count": int(cnt), "grade": grade_of(int(idx))}
                for idx, cnt in output_idx_hist.most_common(20)
            ],
            "output_grade_by_input_pattern": {
                k: dict(v) for k, v in by_input_grade.items()
            },
        },
        "stored_examples": stored,
        "span_rank_diagnostic": {
            "stored_examples": int(len(stored_vecs)),
            "support_size": int(len(idx_list)),
            "rank_over_R": int(rank_all),
        },
        "elapsed_seconds": float(dt),
        "note": "This analyzes the Jacobiator of the firewall-filtered (non-Lie) bracket; ranks are heuristic diagnostics.",
    }

    OUT_JSON.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md: List[str] = []
    md.append("# Firewall-filtered bracket Jacobiator support\n")
    md.append(f"- samples: `{args.samples}` seed=`{args.seed}`")
    md.append(f"- failures: `{failures}` (rate `{out['counts']['failure_rate']:.6f}`)")
    md.append(f"- forbidden pairs: `{len(forbidden)}`")
    md.append(f"- elapsed: `{dt:.2f}s`\n")
    md.append("## Output grade histogram\n")
    for k, v in out["histograms"]["output_grade"].items():
        md.append(f"- {k}: `{v}`")
    md.append("\n## Input-grade patterns (failures only)\n")
    for k, v in out["histograms"]["input_grade_patterns"].items():
        md.append(f"- {k}: `{v}`")
    md.append("\n## Span diagnostic (stored examples)\n")
    sd = out["span_rank_diagnostic"]
    md.append(
        f"- stored: `{sd['stored_examples']}` support_size: `{sd['support_size']}` rank_R: `{sd['rank_over_R']}`\n"
    )
    md.append(f"- JSON: `{OUT_JSON}`")
    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print(
        f"samples={args.samples} failures={failures} rate={out['counts']['failure_rate']:.6f} wrote={OUT_JSON}"
    )


if __name__ == "__main__":
    main()
