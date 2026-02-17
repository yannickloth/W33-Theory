#!/usr/bin/env python3
"""Scan Monster (2X,3Y) products for Ogg-prime triangle-group support.

This is a lightweight companion to `scripts/w33_leech_monster.py` that focuses on
the observable:

    Pr[(ab) ∈ pA/pB]  for a∈2A/2B and b∈3A/3B/3C.

Any nonzero probability certifies a Δ(2,3,p) triangle-group map into the Monster
with (x,y,xy) landing in those conjugacy classes.
"""

from __future__ import annotations


def main() -> None:
    from w33_leech_monster import analyze_monster_2x3_ogg_prime_triangle_support

    rep = analyze_monster_2x3_ogg_prime_triangle_support()
    if rep.get("available") is not True:
        raise SystemExit("Monster 2×3 triangle scan unavailable (missing data).")

    pairs = rep.get("pairs", {})
    ogg = rep.get("ogg_primes", [])
    if not isinstance(pairs, dict) or not isinstance(ogg, list):
        raise SystemExit("Unexpected report format.")

    print("=" * 78)
    print("MONSTER Δ(2,3,p) SUPPORT SCAN (Ogg primes)")
    print("=" * 78)

    missing_focus = [5, 7, 47, 59]
    print("Ogg primes:", ogg)
    print("Focus (often-missing in 2A×3B):", missing_focus)
    print()

    # Per pair summary.
    print("Per (2X×3Y) pair: primes supported")
    for key in sorted(pairs.keys()):
        info = pairs.get(key, {})
        primes = info.get("support_primes", [])
        if not isinstance(primes, list):
            primes = []
        flags = {p: ("✓" if p in primes else "·") for p in missing_focus}
        print(
            f"  {key:6s}  primes={primes}  "
            f"[5:{flags[5]} 7:{flags[7]} 47:{flags[47]} 59:{flags[59]}]"
        )
    print()

    # Per prime: which pairs support it.
    prime_to_pairs: dict[int, list[str]] = {
        int(p): [] for p in ogg if isinstance(p, int)
    }
    for key, info in pairs.items():
        primes = info.get("support_primes", [])
        if not isinstance(primes, list):
            continue
        for p in primes:
            if isinstance(p, int) and p in prime_to_pairs:
                prime_to_pairs[p].append(str(key))

    print("Per prime: which pairs light it up")
    for p in sorted(prime_to_pairs.keys()):
        hits = sorted(prime_to_pairs[p])
        print(f"  p={p:2d}: {hits}")


if __name__ == "__main__":
    main()
