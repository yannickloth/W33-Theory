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
        5616: "PSL3(3)",  # SL3(3) is centerless (13A cofactor)
        168: "PSL2(7)",  # ≅ GL3(2) (17A cofactor)
        # 7B centralizer in the Monster has shape 7^{1+4}.2A7 (CTblLib),
        # so the cofactor magnitude |C_M(7B)|/7 = 7^4·|2A7| = 12,101,040.
        12_101_040: "7^4:2A7",
        # 13B centralizer in the Monster is 13^{1+2}:24, so after dividing
        # by p the cofactor is 13^2:2A4 = 4056.
        4056: "13^2:2A4",
        # 5B centralizer shape 5^{1+6}:2J2 (CTblLib/ATLAS).  Dividing by p gives
        # cofactor 5^6:2J2 = 18,900,000,000.
        18_900_000_000: "5^6:2J2",
        60: "A5",  # ≅ PSL2(5) (19A cofactor)
        24: "S4",
        6: "S3",
        3: "C3",
        2: "C2",
        1: "1",
    }
    return by_order.get(int(order))


def _recognize_subgroup_by_order(order: int) -> str | None:
    """Recognize a few stabilizer subgroups by order.

    This is meant to be a conservative, offline bridge:
      cofactor group H  --(perm degree r)-->  stabilizer subgroup K ≤ H

    For the key sporadic rungs we rely on order-uniqueness:
      - |PSL2(11)| = 660
      - |A12| = 12!/2 = 239,500,800
      - |Sp4(4):2| = 2·|Sp4(4)| = 1,958,400
    """
    by_order = {
        660: "PSL2(11)",
        1320: "PGL2(11)",
        239_500_800: "A12",
        479_001_600: "S12",
        1_958_400: "Sp4(4):2",
        3_916_800: "Sp4(4):4",
        # Natural stabilizers for small-group minimal permutation actions.
        432: "3^2:GL2(3)",  # point stabilizer in PSL3(3) on PG(2,3)
        36: "3^2:C4",  # stabilizer of an ordered pair of distinct points in PG(2,3)
        21: "7:3",  # Borel in PSL2(7) on P^1(F7)
        39: "13:3",  # stabilizer candidate in 13^2:2A4 index 104
        12: "A4",  # point stabilizer in A5 on 5 points
        6: "S3",  # point stabilizer in S4 on 4 points
        2: "C2",  # point stabilizer in S3 on 3 points
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
        # PSL3(3) has a natural action on PG(2,3) points (13), on flags
        # (13*4=52), and (at least) a transitive action on ordered pairs of
        # distinct points (13*12=156).
        "PSL3(3)": [13, 52, 156],
        # 13^2:2A4 arises from the 13B centralizer 13^{1+2}.2A4 in the Monster.
        # Natural transitive degrees include the affine action on 13^2=169 points,
        # and (in our scan) the signature r_13=104 corresponds to a subgroup of
        # order 39 (=13:3).
        "13^2:2A4": [104, 169],
        # 5^6:2J2 is the cofactor of the 5B centralizer 5^{1+6}:2.J2; it has an
        # affine action on 5^6 points.
        "5^6:2J2": [15625],
        # PSL2(7) has a natural action on P^1(F7) (8) and a transitive action
        # on cosets of A4 (index 14).
        "PSL2(7)": [8, 14],
        "A5": [5],
        "S4": [4],
        "S3": [3],
        "C3": [3],
        "C2": [2],
        "1": [1],
    }.get(g, [])


def _permrep_metadata_for_group(group: str) -> dict[int, dict[str, Any]]:
    g = str(group)
    if g not in {"HN", "He", "M12"}:
        return {}
    path = ROOT / "data" / f"{g.lower()}_permutation_degrees.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    meta = payload.get("rep_metadata", {})
    if not isinstance(meta, dict):
        return {}
    out: dict[int, dict[str, Any]] = {}
    for k, v in meta.items():
        try:
            deg = int(k)
        except Exception:
            continue
        if isinstance(v, dict):
            out[int(deg)] = dict(v)
    return out


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
        permrep_meta = _permrep_metadata_for_group(recognized) if recognized else {}

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
                assert r is not None and int(r) > 0
                assert cof % int(r) == 0
                stab = int(cof // int(r))
                outer_stab = (
                    int(2 * stab) if recognized in {"HN", "He", "M12"} else None
                )
                rec: dict[str, Any] = {
                    "pair": str(pair_key),
                    "r": int(r),
                    "n": int(n),
                    "stabilizer_order": int(stab),
                    "stabilizer_group_recognized": _recognize_subgroup_by_order(
                        int(stab)
                    ),
                    "outer_stabilizer_order": (
                        int(outer_stab) if outer_stab is not None else None
                    ),
                    "outer_stabilizer_group_recognized": (
                        _recognize_subgroup_by_order(int(outer_stab))
                        if outer_stab is not None
                        else None
                    ),
                }

                meta = permrep_meta.get(int(r), {})
                if isinstance(meta, dict) and meta:
                    rec["permrep_metadata"] = dict(meta)
                    for k in (
                        "atlas_permrep_url",
                        "rank",
                        "suborbit_lengths_compressed",
                        "suborbit_lengths",
                    ):
                        if k in meta:
                            rec[f"permrep_{k}"] = meta.get(k)

                    if "stabilizer_order" in meta:
                        assert int(meta.get("stabilizer_order") or 0) == int(stab)
                    if outer_stab is not None and "outer_stabilizer_order" in meta:
                        assert int(meta.get("outer_stabilizer_order") or 0) == int(
                            outer_stab
                        )

                perm_hits.append(rec)

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
    # 11A: cofactor M12 has perm-degree hit r_11(2A×3B)=144, stabilizer PSL2(11).
    assert any(
        h["pair"] == "2A×3B"
        and int(h["r"]) == 144
        and int(h.get("stabilizer_order", 0) or 0) == 660
        and h.get("stabilizer_group_recognized") == "PSL2(11)"
        and int(h.get("outer_stabilizer_order", 0) or 0) == 1320
        and h.get("outer_stabilizer_group_recognized") == "PGL2(11)"
        for h in out["11A"]["perm_hits"]
    )
    # 5A: cofactor HN has perm-degree hit r_5(2A×3A)=1140000, stabilizer A12.
    assert any(
        h["pair"] == "2A×3A"
        and int(h["r"]) == 1140000
        and int(h.get("stabilizer_order", 0) or 0) == 239_500_800
        and h.get("stabilizer_group_recognized") == "A12"
        and int(h.get("outer_stabilizer_order", 0) or 0) == 479_001_600
        and h.get("outer_stabilizer_group_recognized") == "S12"
        for h in out["5A"]["perm_hits"]
    )
    # 7A: cofactor He has perm-degree hit r_7(2A×3A)=2058, stabilizer Sp4(4):2.
    assert any(
        h["pair"] == "2A×3A"
        and int(h["r"]) == 2058
        and int(h.get("stabilizer_order", 0) or 0) == 1_958_400
        and h.get("stabilizer_group_recognized") == "Sp4(4):2"
        and int(h.get("outer_stabilizer_order", 0) or 0) == 3_916_800
        and h.get("outer_stabilizer_group_recognized") == "Sp4(4):4"
        for h in out["7A"]["perm_hits"]
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
            hit_strs = []
            for h in perm_hits:
                if not isinstance(h, dict):
                    continue
                srec = h.get("stabilizer_group_recognized")
                rank = h.get("permrep_rank")
                if isinstance(srec, str) and srec:
                    extra = []
                    if rank is not None:
                        try:
                            extra.append(f"rank={int(rank)}")
                        except Exception:
                            pass
                    suffix = (
                        f" ({', '.join(['stab=' + srec] + extra)})"
                        if extra
                        else f" (stab={srec})"
                    )
                    hit_strs.append(f"{h['pair']}→r={h['r']}{suffix}")
                else:
                    hit_strs.append(f"{h['pair']}→r={h['r']}")
            hit_str = ", ".join(hit_strs)
            print(f"  r_p perm hits: {hit_str}")
        else:
            print("  r_p perm hits: none")

    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
