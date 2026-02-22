#!/usr/bin/env python3
"""Monster Ogg-prime pipeline: Delta(2,3,p) support -> best (2X,3Y) -> replicability.

This script operationalizes the workflow:
  1) Use the class-algebra scan (CTblLib columns + ATLAS centralizers) to certify
     Delta(2,3,p) support in the Monster via nonzero Pr[(2X)(3Y) in class of order p].
  2) For each Ogg prime p, pick the (2X,3Y) pair with the largest probability
     mass into order-p classes.
  3) Run an offline McKay-Thompson "prime replicability" check for each
     supported candidate class (where an explicit q-series formula is bundled).

Usage:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_ogg_pipeline.py
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _fraction_from_payload(payload: object) -> Fraction:
    if not isinstance(payload, dict):
        return Fraction(0, 1)
    try:
        return Fraction(int(payload["numerator"]), int(payload["denominator"]))
    except Exception:
        return Fraction(0, 1)


def _leading_int(s: str) -> int | None:
    out = ""
    for ch in s:
        if "0" <= ch <= "9":
            out += ch
        else:
            break
    if not out:
        return None
    try:
        return int(out)
    except Exception:
        return None


@dataclass(frozen=True)
class PrimeHit:
    prime: int
    class_name: str
    prob: Fraction


def _iter_prime_hits(pair_info: dict[str, object]) -> Iterable[PrimeHit]:
    classes = pair_info.get("classes", {})
    if not isinstance(classes, dict):
        return []

    hits: list[PrimeHit] = []
    for cls_name, cls_info in classes.items():
        if not isinstance(cls_name, str) or not isinstance(cls_info, dict):
            continue
        p = None
        if "prime" in cls_info:
            try:
                p = int(cls_info["prime"])
            except Exception:
                p = None
        if p is None:
            p = _leading_int(cls_name)
        if p is None:
            continue
        prob = _fraction_from_payload(cls_info.get("probability"))
        if prob == 0:
            continue
        hits.append(PrimeHit(prime=int(p), class_name=str(cls_name), prob=prob))
    return hits


def _pair_label(pair_info: dict[str, object]) -> str:
    a = pair_info.get("a_class", "?")
    b = pair_info.get("b_class", "?")
    return f"{a}x{b}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-q-exp", type=int, default=10)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument(
        "--verify-rr-j",
        action="store_true",
        help="Also verify the Rogers-Ramanujan continued-fraction identity for j(tau).",
    )
    args = parser.parse_args()

    from w33_leech_monster import (
        analyze_monster_2x3_ogg_prime_triangle_support,
        analyze_rogers_ramanujan_j_invariant,
        verify_fricke_prime_replicability,
    )

    if args.verify_rr_j:
        rr = analyze_rogers_ramanujan_j_invariant(n_terms=8)
        verdict = "PASS" if rr.get("verified") else "FAIL"
        print("=" * 78)
        print("ROGERS-RAMANUJAN CHECK: j(tau) as rational function of R(q)^5")
        print("=" * 78)
        print(f"Verdict: {verdict}")
        print()

    rep = analyze_monster_2x3_ogg_prime_triangle_support()
    if rep.get("available") is not True:
        raise SystemExit("Monster 2x3 scan unavailable (missing bundled data).")

    pairs = rep.get("pairs", {})
    ogg_primes = rep.get("ogg_primes", [])
    if not isinstance(pairs, dict) or not isinstance(ogg_primes, list):
        raise SystemExit("Unexpected report format.")

    # Normalize pairs into a stable list.
    pair_list: list[dict[str, object]] = []
    for info in pairs.values():
        if isinstance(info, dict):
            pair_list.append(info)
    pair_list.sort(key=_pair_label)

    # Precompute per-pair per-prime hits and masses.
    pair_prime_hits: dict[tuple[str, int], list[PrimeHit]] = {}
    pair_prime_mass: dict[tuple[str, int], Fraction] = {}
    for info in pair_list:
        label = _pair_label(info)
        by_p: dict[int, list[PrimeHit]] = {}
        for hit in _iter_prime_hits(info):
            by_p.setdefault(int(hit.prime), []).append(hit)
        for p, hits in by_p.items():
            pair_prime_hits[(label, int(p))] = sorted(hits, key=lambda h: h.class_name)
            pair_prime_mass[(label, int(p))] = sum(
                (h.prob for h in hits), Fraction(0, 1)
            )

    scan_primes = sorted({int(p) for p in ogg_primes if isinstance(p, int) and p >= 5})

    results: list[dict[str, Any]] = []

    print("=" * 78)
    print(
        "MONSTER OGG-PRIME PIPELINE: Delta(2,3,p) SUPPORT -> BEST PAIR -> REPLICABILITY"
    )
    print("=" * 78)
    print(f"Scan primes: {scan_primes}")
    print(f"Replicability max_q_exp: {int(args.max_q_exp)}")
    print()

    for p in scan_primes:
        # Find best pair by mass.
        best_label: str | None = None
        best_mass = Fraction(-1, 1)
        for info in pair_list:
            label = _pair_label(info)
            mass = pair_prime_mass.get((label, int(p)), Fraction(0, 1))
            if mass > best_mass:
                best_mass = mass
                best_label = label

        hits = pair_prime_hits.get((best_label or "", int(p)), [])
        classes = [h.class_name for h in hits]

        print(f"p={p:2d}: best={best_label} mass={best_mass} (~{float(best_mass):.6g})")
        for h in hits:
            print(f"      class {h.class_name:4s} prob={h.prob} (~{float(h.prob):.6g})")

        cls_results: list[dict[str, Any]] = []
        for cls in classes:
            try:
                chk = verify_fricke_prime_replicability(
                    cls, max_q_exp=int(args.max_q_exp)
                )
                cls_results.append(chk)
                verdict = "PASS" if chk.get("verified") else "FAIL"
                nm = int(chk.get("n_mismatches", 0) or 0)
                print(f"      replicability {cls:4s}: {verdict} (mismatches={nm})")
            except Exception as e:
                cls_results.append(
                    {"class_name": cls, "p": int(p), "verified": False, "error": str(e)}
                )
                print(f"      replicability {cls:4s}: unavailable ({e})")

        results.append(
            {
                "p": int(p),
                "best_pair": best_label,
                "mass": {
                    "numerator": int(best_mass.numerator),
                    "denominator": int(best_mass.denominator),
                    "value": str(best_mass),
                    "float": float(best_mass),
                },
                "classes": classes,
                "replicability": cls_results,
            }
        )
        print()

    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Wrote {args.out_json}")


if __name__ == "__main__":
    main()
