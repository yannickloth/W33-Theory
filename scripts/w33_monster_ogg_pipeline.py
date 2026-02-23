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
    structure_constant_per_element: int


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
        try:
            n = int(cls_info.get("structure_constant_per_element", 0) or 0)
        except Exception:
            n = 0
        hits.append(
            PrimeHit(
                prime=int(p),
                class_name=str(cls_name),
                prob=prob,
                structure_constant_per_element=int(n),
            )
        )
    return hits


def _pair_label(pair_info: dict[str, object]) -> str:
    a = pair_info.get("a_class", "?")
    b = pair_info.get("b_class", "?")
    return f"{a}x{b}"


def _pair_label_to_times(label: str) -> str:
    return str(label).replace("x", "×")


def _pair_label_to_x(label: str) -> str:
    return str(label).replace("×", "x")


def analyze(
    *,
    max_q_exp: int = 10,
    scan_primes: Iterable[int] | None = None,
    verify_rr_j: bool = False,
    include_ratio_signatures: bool = True,
) -> dict[str, Any]:
    """Run the Ogg-prime pipeline and return a structured report."""

    from w33_leech_monster import (
        analyze_monster_2x3_ogg_prime_triangle_support,
        analyze_rogers_ramanujan_j_invariant,
        verify_fricke_prime_replicability,
    )

    rr: dict[str, object] | None = None
    if verify_rr_j:
        rr = analyze_rogers_ramanujan_j_invariant(n_terms=8)

    rep = analyze_monster_2x3_ogg_prime_triangle_support()
    if rep.get("available") is not True:
        return {
            "available": False,
            "reason": "Monster 2x3 scan unavailable (missing bundled data).",
            "rr_j": rr,
        }

    pairs = rep.get("pairs", {})
    ogg_primes = rep.get("ogg_primes", [])
    if not isinstance(pairs, dict) or not isinstance(ogg_primes, list):
        return {"available": False, "reason": "Unexpected report format.", "rr_j": rr}

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
            pair_prime_mass[(label, int(p))] = sum((h.prob for h in hits), Fraction(0, 1))

    all_scan_primes = sorted({int(p) for p in ogg_primes if isinstance(p, int) and p >= 5})
    if scan_primes is None:
        scan_list = all_scan_primes
    else:
        allowed = {int(p) for p in scan_primes}
        scan_list = [p for p in all_scan_primes if p in allowed]

    results: list[dict[str, Any]] = []
    for p in scan_list:
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
        hit_payload = [
            {
                "class_name": str(h.class_name),
                "prob": {
                    "numerator": int(h.prob.numerator),
                    "denominator": int(h.prob.denominator),
                    "value": str(h.prob),
                    "float": float(h.prob),
                },
                "structure_constant_per_element": int(h.structure_constant_per_element),
                "r": (
                    int(h.structure_constant_per_element // int(p))
                    if int(p) > 0 and int(h.structure_constant_per_element) % int(p) == 0
                    else None
                ),
            }
            for h in hits
        ]

        cls_results: list[dict[str, Any]] = []
        for cls in classes:
            try:
                chk = verify_fricke_prime_replicability(cls, max_q_exp=int(max_q_exp))
                cls_results.append(chk)
            except Exception as e:
                cls_results.append(
                    {"class_name": str(cls), "p": int(p), "verified": False, "error": str(e)}
                )

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
                "hits": hit_payload,
                "classes": classes,
                "replicability": cls_results,
            }
        )

    ratio_sig: dict[str, Any] | None = None
    if include_ratio_signatures:
        try:
            from scripts.w33_monster_prime_ratio_signatures import (
                analyze as analyze_ratio_signatures,
            )

            ratio_sig = analyze_ratio_signatures()
            if ratio_sig.get("available") is not True:
                ratio_sig = None
        except Exception:
            ratio_sig = None

    if ratio_sig is not None:
        rungs = ratio_sig.get("rungs", {})
        if isinstance(rungs, dict):
            for rec in results:
                if not isinstance(rec, dict):
                    continue
                classes = rec.get("classes", [])
                if not isinstance(classes, list):
                    continue
                rung_info: dict[str, Any] = {}
                recommended_perm_pair: str | None = None
                recommended_irrep_pair: str | None = None
                for cls in classes:
                    if not isinstance(cls, str) or cls not in rungs:
                        continue
                    info = rungs.get(cls, {})
                    if not isinstance(info, dict):
                        continue
                    perm_hits = info.get("ratio_hits_in_perm_degree_set", [])
                    irrep_hits = info.get("ratio_hits_in_irrep_degree_set", [])
                    rung_info[cls] = {
                        "cofactor_group": info.get("cofactor_group"),
                        "ratio_hits_in_perm_degree_set": perm_hits,
                        "ratio_hits_in_irrep_degree_set": irrep_hits,
                    }

                    # Choose a canonical "recommended" pair for this rung.
                    if isinstance(perm_hits, list) and perm_hits:
                        # Prefer the largest nontrivial r.
                        best = max(
                            (
                                h
                                for h in perm_hits
                                if isinstance(h, dict) and int(h.get("r", 0) or 0) > 1
                            ),
                            key=lambda h: int(h.get("r", 0) or 0),
                            default=None,
                        )
                        if best is not None:
                            recommended_perm_pair = _pair_label_to_x(
                                str(best.get("pair") or "")
                            )
                    if isinstance(irrep_hits, list) and irrep_hits:
                        best = max(
                            (
                                h
                                for h in irrep_hits
                                if isinstance(h, dict) and int(h.get("r", 0) or 0) > 1
                            ),
                            key=lambda h: int(h.get("r", 0) or 0),
                            default=None,
                        )
                        if best is not None:
                            recommended_irrep_pair = _pair_label_to_x(
                                str(best.get("pair") or "")
                            )

                if rung_info:
                    rec["ratio_signature_rungs"] = rung_info
                    rec["recommended_pair_perm_hit"] = recommended_perm_pair
                    rec["recommended_pair_nontrivial_irrep_hit"] = recommended_irrep_pair

    return {
        "available": True,
        "scan_primes": scan_list,
        "replicability_max_q_exp": int(max_q_exp),
        "rr_j": rr,
        "results": results,
    }


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

    report = analyze(max_q_exp=int(args.max_q_exp), verify_rr_j=bool(args.verify_rr_j))
    if report.get("available") is not True:
        raise SystemExit(str(report.get("reason") or "analysis unavailable"))

    rr = report.get("rr_j")
    if isinstance(rr, dict):
        verdict = "PASS" if rr.get("verified") else "FAIL"
        print("=" * 78)
        print("ROGERS-RAMANUJAN CHECK: j(tau) as rational function of R(q)^5")
        print("=" * 78)
        print(f"Verdict: {verdict}")
        print()

    scan_primes = report.get("scan_primes", [])
    results = report.get("results", [])
    if not isinstance(results, list):
        raise SystemExit("Unexpected results payload.")

    print("=" * 78)
    print(
        "MONSTER OGG-PRIME PIPELINE: Delta(2,3,p) SUPPORT -> BEST PAIR -> REPLICABILITY"
    )
    print("=" * 78)
    print(f"Scan primes: {scan_primes}")
    print(f"Replicability max_q_exp: {int(args.max_q_exp)}")
    print()

    for item in results:
        if not isinstance(item, dict):
            continue
        p = int(item.get("p", 0) or 0)
        best_pair = str(item.get("best_pair") or "?")
        mass = item.get("mass", {})
        mass_str = mass.get("value") if isinstance(mass, dict) else None
        mass_f = mass.get("float") if isinstance(mass, dict) else None
        hits = item.get("hits", [])
        replicability = item.get("replicability", [])

        if isinstance(mass_str, str) and isinstance(mass_f, (int, float)):
            print(f"p={p:2d}: best={best_pair} mass={mass_str} (~{float(mass_f):.6g})")
        else:
            print(f"p={p:2d}: best={best_pair}")

        if isinstance(hits, list):
            for h in hits:
                if not isinstance(h, dict):
                    continue
                cls_name = str(h.get("class_name") or "?")
                prob = h.get("prob", {})
                prob_str = prob.get("value") if isinstance(prob, dict) else None
                prob_f = prob.get("float") if isinstance(prob, dict) else None
                if isinstance(prob_str, str) and isinstance(prob_f, (int, float)):
                    print(
                        f"      class {cls_name:4s} prob={prob_str} (~{float(prob_f):.6g})"
                    )
                else:
                    print(f"      class {cls_name:4s}")

        if isinstance(replicability, list):
            for chk in replicability:
                if not isinstance(chk, dict):
                    continue
                cls = str(chk.get("class_name") or "?")
                if "error" in chk:
                    print(
                        f"      replicability {cls:4s}: unavailable ({chk.get('error')})"
                    )
                    continue
                verdict = "PASS" if chk.get("verified") else "FAIL"
                nm = int(chk.get("n_mismatches", 0) or 0)
                print(f"      replicability {cls:4s}: {verdict} (mismatches={nm})")
        print()

    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Wrote {args.out_json}")


if __name__ == "__main__":
    main()
