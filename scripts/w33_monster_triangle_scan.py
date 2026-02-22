#!/usr/bin/env python3
"""Scan Monster (2X,3Y) products for Ogg-prime triangle-group support.

This is a lightweight companion to `scripts/w33_leech_monster.py` that focuses on
the observable:

  Pr[(ab) in class of order p]

for:
  a in {2A, 2B}
  b in {3A, 3B, 3C}
  p in Ogg primes (genus-zero X0(p)^+ list).

Implementation notes:
- All probabilities are exact rationals computed from bundled CTblLib-derived
  Monster character columns plus ATLAS centralizers.
- Output is ASCII-only so it renders cleanly in Windows terminals.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

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
    m = re.match(r"^([0-9]+)", s)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


@dataclass(frozen=True)
class PrimeMass:
    prime: int
    mass: Fraction
    classes: tuple[str, ...]


def _iter_prime_masses_for_pair(pair_info: dict[str, object]) -> Iterable[PrimeMass]:
    classes = pair_info.get("classes", {})
    if not isinstance(classes, dict):
        return []

    by_p: dict[int, list[tuple[str, Fraction]]] = {}
    for cls_name, cls_info in classes.items():
        if not isinstance(cls_name, str):
            continue
        if not isinstance(cls_info, dict):
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
        by_p.setdefault(p, []).append((cls_name, prob))

    out: list[PrimeMass] = []
    for p, rows in by_p.items():
        mass = sum((r[1] for r in rows), Fraction(0, 1))
        out.append(
            PrimeMass(
                prime=int(p), mass=mass, classes=tuple(sorted(r[0] for r in rows))
            )
        )
    return sorted(out, key=lambda pm: pm.prime)


def _pair_label(pair_info: dict[str, object]) -> str:
    a = pair_info.get("a_class", "?")
    b = pair_info.get("b_class", "?")
    return f"{a}x{b}"


def main() -> None:
    from w33_leech_monster import analyze_monster_2x3_ogg_prime_triangle_support

    rep = analyze_monster_2x3_ogg_prime_triangle_support()
    if rep.get("available") is not True:
        raise SystemExit("Monster 2x3 triangle scan unavailable (missing data).")

    pairs = rep.get("pairs", {})
    ogg_primes = rep.get("ogg_primes", [])
    if not isinstance(pairs, dict) or not isinstance(ogg_primes, list):
        raise SystemExit("Unexpected report format.")

    ogg = [int(p) for p in ogg_primes if isinstance(p, int)]
    ogg_scan = [p for p in ogg if p >= 5]
    focus = [5, 7, 47, 59]

    # Normalize pairs into a stable list.
    pair_list: list[dict[str, object]] = []
    for info in pairs.values():
        if isinstance(info, dict):
            pair_list.append(info)
    pair_list.sort(key=_pair_label)

    # Build per-pair masses, and per-prime mass lookup.
    pair_prime_mass: dict[tuple[str, int], PrimeMass] = {}
    support_primes: dict[str, set[int]] = {}
    for info in pair_list:
        label = _pair_label(info)
        masses = list(_iter_prime_masses_for_pair(info))
        support_primes[label] = {pm.prime for pm in masses}
        for pm in masses:
            pair_prime_mass[(label, pm.prime)] = pm

    print("=" * 78)
    print("MONSTER Delta(2,3,p) SUPPORT SCAN (Ogg primes)")
    print("=" * 78)
    print("Ogg primes:", ogg)
    print("Scan primes:", ogg_scan)
    print("Focus primes:", focus)
    print("Note: p=2,3 are Ogg primes but are not target classes in this scan.")
    print()

    print("Per (2X x 3Y) pair: supported + missing primes")
    for info in pair_list:
        label = _pair_label(info)
        supp = sorted(support_primes.get(label, set()))
        missing = sorted(set(ogg_scan) - set(supp))
        flags = []
        for p in focus:
            ok = "Y" if p in supp else "-"
            pm = pair_prime_mass.get((label, p))
            if pm is None:
                flags.append(f"{p}:{ok}")
            else:
                flags.append(
                    f"{p}:{ok} (mass={float(pm.mass):.6g} from {list(pm.classes)})"
                )
        print(f"  {label:6s} support={supp} missing={missing}")
        print(f"         focus: {', '.join(flags)}")
    print()

    # Per prime: which pairs support it, and which has the largest mass.
    print(
        "Per prime p: which pairs light it up (and the best pair by probability mass)"
    )
    for p in ogg_scan:
        hits = [label for (label, pp) in pair_prime_mass.keys() if pp == p]
        hits = sorted(set(hits))
        if not hits:
            print(f"  p={p:2d}: hits=[]")
            continue
        best_label = None
        best_mass = Fraction(-1, 1)
        best_classes: tuple[str, ...] = ()
        for label in hits:
            pm = pair_prime_mass[(label, p)]
            if pm.mass > best_mass:
                best_mass = pm.mass
                best_label = label
                best_classes = pm.classes
        best_str = (
            f"{best_label} mass={best_mass} (~{float(best_mass):.6g}) classes={list(best_classes)}"
            if best_label is not None
            else "n/a"
        )
        print(f"  p={p:2d}: hits={hits}  best={best_str}")


if __name__ == "__main__":
    main()
