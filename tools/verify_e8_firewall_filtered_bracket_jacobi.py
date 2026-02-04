#!/usr/bin/env python3
"""
Experiment: treat the firewall-forbidden cubic triads as *interaction selection rules* on the
Z3-graded E8 bracket, by zeroing out the corresponding root-channel couplings:

  - If x,y are g1 roots and [x,y] is a g2 root whose (i27) triple is one of the 9 firewall triads,
    then set [x,y]_fw = 0.
  - Likewise for g2×g2→g1 couplings whose underlying i27 triad is firewall-forbidden.

All other brackets (including g0, Cartan-root, and g1×g2→g0) are left unchanged.

This is *not* expected to remain a Lie algebra; the purpose is to quantify how the firewall
acts as a non-Lie selection rule on top of the certified E8 algebra.

Inputs:
  - artifacts/e8_structure_constants_w33_discrete.json
  - artifacts/e8_root_metadata_table.json
  - artifacts/firewall_bad_triads_mapping.json

Outputs:
  - artifacts/verify_e8_firewall_filtered_bracket_jacobi.json
  - artifacts/verify_e8_firewall_filtered_bracket_jacobi.md
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from random import Random
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
IN_SC = ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json"
IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
IN_FW = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"

OUT_JSON = ROOT / "artifacts" / "verify_e8_firewall_filtered_bracket_jacobi.json"
OUT_MD = ROOT / "artifacts" / "verify_e8_firewall_filtered_bracket_jacobi.md"


Pair = Tuple[int, int]
Root = Tuple[int, ...]
Terms = List[Tuple[int, int]]


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=50_000)
    ap.add_argument("--seed", type=int, default=0)
    return ap.parse_args()


def _triad_key(a: int, b: int, c: int) -> Tuple[int, int, int]:
    return tuple(sorted((int(a), int(b), int(c))))


def _load_grade_map() -> Dict[Root, dict]:
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


def _describe_idx(
    idx: int, cartan_dim: int, roots: List[List[int]], meta_by_root: Dict[Root, dict]
) -> Dict[str, object]:
    if idx < cartan_dim:
        return {"kind": "h", "h_index_1based": idx + 1, "grade": "g0"}
    rt = tuple(int(x) for x in roots[idx - cartan_dim])
    row = meta_by_root[rt]
    return {
        "kind": "e",
        "grade": row["grade"],
        "root_orbit": list(rt),
        "i27": row.get("i27"),
        "i3": row.get("i3"),
        "phase_z6": row.get("phase_z6"),
        "edge": row.get("edge"),
    }


def _get_terms_filtered(
    i: int,
    j: int,
    table: Dict[Pair, Terms],
    forbidden_pairs: set[Pair],
) -> Tuple[int, Terms]:
    if i == j:
        return 1, []
    if i < j:
        if (i, j) in forbidden_pairs:
            return 1, []
        return 1, table.get((i, j), [])
    if (j, i) in forbidden_pairs:
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


def main() -> None:
    args = _parse_args()
    sc = json.loads(IN_SC.read_text(encoding="utf-8"))
    basis = sc["basis"]
    n = int(basis["n"])
    cartan_dim = int(basis["cartan_dim"])
    roots: List[List[int]] = basis["roots"]
    if n != 248 or cartan_dim != 8 or len(roots) != 240:
        raise RuntimeError("Unexpected basis sizing")

    meta_by_root = _load_grade_map()
    bad_triads = _load_firewall_triads()
    table = _parse_brackets(sc)

    # Precompute forbidden root-pairs (basis indices i<j) based on firewall triads.
    forbidden: set[Pair] = set()
    removed = 0
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
        tri = _triad_key(a27, b27, c27)
        if tri in bad_triads:
            forbidden.add((i, j))
            removed += 1

    t0 = time.time()
    fail = 0
    first_fail: Dict[str, object] | None = None
    for_checked = 0
    for i, j, k in _random_triples(n, args.samples, args.seed):
        J = _jacobi(i, j, k, table, forbidden)
        for_checked += 1
        if J:
            fail += 1
            if first_fail is None:
                first_fail = {
                    "triple": [i, j, k],
                    "basis": [
                        _describe_idx(i, cartan_dim, roots, meta_by_root),
                        _describe_idx(j, cartan_dim, roots, meta_by_root),
                        _describe_idx(k, cartan_dim, roots, meta_by_root),
                    ],
                    "jacobi": [[idx, int(coeff)] for idx, coeff in sorted(J.items())],
                }

    dt = time.time() - t0
    out = {
        "status": "ok",
        "samples": int(args.samples),
        "seed": int(args.seed),
        "counts": {
            "basis_n": n,
            "forbidden_pairs": int(len(forbidden)),
            "forbidden_pairs_removed_from_table": int(removed),
            "jacobi_failures_in_sample": int(fail),
        },
        "failure_rate": float(fail / max(1, for_checked)),
        "elapsed_seconds": float(dt),
        "first_failure": first_fail,
        "note": "This firewall-filtered bracket is expected to violate Jacobi; use this as a quantified selection-rule diagnostic.",
    }

    OUT_JSON.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md: List[str] = []
    md.append("# Firewall-filtered E8 bracket: Jacobi diagnostic\n")
    md.append(f"- samples: `{args.samples}` seed=`{args.seed}`")
    md.append(f"- forbidden pairs removed: `{len(forbidden)}`")
    md.append(
        f"- Jacobi failures (sample): `{fail}` (rate `{out['failure_rate']:.6f}`)"
    )
    md.append(f"- elapsed: `{dt:.2f}s`\n")
    if first_fail is not None:
        md.append("## First failure\n")
        md.append(f"- triple: `{first_fail['triple']}`")
        md.append(f"- jacobi: `{first_fail['jacobi']}`\n")
    md.append(f"- JSON: `{OUT_JSON}`")
    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print(
        f"samples={args.samples} forbidden={len(forbidden)} fails={fail} "
        f"rate={out['failure_rate']:.6f} wrote={OUT_JSON}"
    )


if __name__ == "__main__":
    main()
