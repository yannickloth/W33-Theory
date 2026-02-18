#!/usr/bin/env python3
"""Recognize Monster prime-order centralizer cofactors beyond the sporadic ladder.

For a prime-order Monster class pX, the ATLAS gives the centralizer order
|C_M(pX)|.  The quotient magnitude

  |C_M(pX)| / p

often matches a familiar group:
  - sporadic rungs (B, Fi24', Th, HN, He, M12) for a few primes, and
  - small Lie/symmetric/cyclic groups for several higher Ogg primes.

This script is deterministic/offline (uses bundled ATLAS snapshot and the
repo's existing 2×3 triangle-support scan) and focuses on:
  1) recognizing cofactor magnitudes by order,
  2) checking whether the prime-ratio signatures r_p := n/p (from the (2X,3Y)
     class-algebra scan) land in a natural permutation-degree list for that
     cofactor group.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_centralizer_cofactor_groups.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _factorint(n: int) -> dict[int, int]:
    nn = int(n)
    out: dict[int, int] = {}
    d = 2
    while d * d <= nn:
        while nn % d == 0:
            out[d] = out.get(d, 0) + 1
            nn //= d
        d = 3 if d == 2 else d + 2
    if nn > 1:
        out[nn] = out.get(nn, 0) + 1
    return out


def _recognize_small_group_by_order(order: int) -> str | None:
    by_order = {
        5616: "PSL3(3)",  # SL3(3) is centerless
        168: "PSL2(7)",  # ≅ GL3(2)
        60: "A5",  # ≅ PSL2(5)
        24: "S4",
        6: "S3",
        3: "C3",
        2: "C2",
        1: "1",
    }
    return by_order.get(int(order))


def _perm_degrees_for_group(group: str) -> list[int]:
    g = str(group)
    if g in {"HN", "He", "M12"}:
        path = ROOT / "data" / f"{g.lower()}_permutation_degrees.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            degs = payload.get("degrees", [])
            if isinstance(degs, list):
                return [int(x) for x in degs]
        return []
    # Natural minimal faithful permutation degrees for small groups.
    return {
        "PSL3(3)": [13],  # action on PG(2,3) points
        "PSL2(7)": [8],  # action on P^1(F7)
        "A5": [5],
        "S4": [4],
        "S3": [3],
        "C3": [3],
        "C2": [2],
        "1": [1],
    }.get(g, [])


def analyze() -> dict[str, Any]:
    from scripts.w33_leech_monster import (
        analyze_monster_2x3_ogg_prime_triangle_support,
        analyze_monster_prime_centralizer_sporadic_ladder,
        load_monster_atlas_ccls,
    )

    atlas = load_monster_atlas_ccls()
    if atlas is None:
        return {"available": False}
    classes = atlas.get("classes", {})
    if not isinstance(classes, dict) or not classes:
        return {"available": False}

    ladder = analyze_monster_prime_centralizer_sporadic_ladder()
    if ladder.get("available") is not True:
        return {"available": False}
    ladder_matches = ladder.get("matches", {})
    if not isinstance(ladder_matches, dict):
        return {"available": False}

    tri = analyze_monster_2x3_ogg_prime_triangle_support()
    if tri.get("available") is not True:
        return {"available": False}
    pairs = tri.get("pairs", {})
    if not isinstance(pairs, dict) or not pairs:
        return {"available": False}
    targets = tri.get("targets", {})
    if not isinstance(targets, dict):
        return {"available": False}
    target_classes = []
    for k in ("value", "trace"):
        xs = targets.get(k, [])
        if isinstance(xs, list):
            target_classes.extend([str(x) for x in xs])
    target_classes = sorted(set(target_classes))

    out: dict[str, Any] = {}
    for cls in target_classes:
        meta = classes.get(cls, {})
        if not isinstance(meta, dict):
            continue
        try:
            p = int(meta["order"])
            cent = int(meta["centralizer_order"])
        except Exception:
            continue
        if p <= 1 or cent % p != 0:
            continue
        cof = cent // p

        ladder_info = ladder_matches.get(cls, {})
        spor = None
        if isinstance(ladder_info, dict):
            if isinstance(ladder_info.get("exact_sporadic_match"), str):
                spor = ladder_info.get("exact_sporadic_match")
        recognized = spor or _recognize_small_group_by_order(cof)

        perm_degs = _perm_degrees_for_group(recognized) if recognized else []
        perm_deg_set = set(int(x) for x in perm_degs)

        ratios: dict[str, Any] = {}
        perm_hits: list[dict[str, Any]] = []
        for pair_key, pdata in pairs.items():
            if not isinstance(pdata, dict):
                continue
            cinfo = pdata.get("classes", {}).get(cls)
            if not isinstance(cinfo, dict):
                continue
            n = int(cinfo.get("structure_constant_per_element", 0) or 0)
            r = None if n % p != 0 else int(n // p)
            in_perm = (r is not None) and (r in perm_deg_set)
            ratios[str(pair_key)] = {
                "n": int(n),
                "r": r,
                "r_in_perm_degrees": bool(in_perm),
            }
            if in_perm:
                perm_hits.append({"pair": str(pair_key), "r": int(r), "n": int(n)})

        perm_hits = sorted(perm_hits, key=lambda x: (int(x["r"]), str(x["pair"])))

        out[cls] = {
            "order": int(p),
            "centralizer_order": int(cent),
            "cofactor_order": int(cof),
            "cofactor_factorization": _factorint(int(cof)),
            "cofactor_group_recognized": recognized,
            "perm_degrees": perm_degs,
            "perm_hits": perm_hits,
            "ratios_by_pair": ratios,
        }

    # A few exact, structure-only recognitions (order matches).
    assert out["13A"]["cofactor_order"] == 5616
    assert out["17A"]["cofactor_order"] == 168
    assert out["19A"]["cofactor_order"] == 60
    assert out["23A"]["cofactor_order"] == 24
    assert out["29A"]["cofactor_order"] == 3
    assert out["31A"]["cofactor_order"] == 6
    assert out["47A"]["cofactor_order"] == 2

    # Perm-degree hits that link cleanly to r_p signatures.
    # 23A: cofactor S4 has degree-4 action, and r_23(2A×3B)=4.
    assert any(
        h["pair"] == "2A×3B" and int(h["r"]) == 4 for h in out["23A"]["perm_hits"]
    )
    # 29A: cofactor C3 has degree-3 regular action, and r_29(2A×3B)=3.
    assert any(
        h["pair"] == "2A×3B" and int(h["r"]) == 3 for h in out["29A"]["perm_hits"]
    )

    return {"available": True, "classes": out, "pairs": sorted(pairs.keys())}


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")
    classes = rep.get("classes", {})
    assert isinstance(classes, dict)

    print("=" * 78)
    print(
        "MONSTER CENTRALIZER COFACTORS: sporadic ladder + small Lie/symmetric matches"
    )
    print("=" * 78)
    print("Cofactor is |C_M(pX)|/p. r_p signature is n/p from (2X,3Y) scan.")

    for cls in sorted(classes.keys()):
        info = classes[cls]
        if not isinstance(info, dict):
            continue
        p = int(info["order"])
        cof = int(info["cofactor_order"])
        rec = info.get("cofactor_group_recognized")
        perm_degs = info.get("perm_degrees", [])
        perm_hits = info.get("perm_hits", [])
        print()
        print(f"{cls}: p={p:>2d}  cofactor={cof:<16d}  recognized={rec}")
        if perm_degs:
            print(f"  perm degrees: {perm_degs}")
        if perm_hits:
            hit_str = ", ".join(f"{h['pair']}→r={h['r']}" for h in perm_hits)
            print(f"  r_p perm hits: {hit_str}")
        else:
            print("  r_p perm hits: none")

    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
