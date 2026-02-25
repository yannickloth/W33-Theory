#!/usr/bin/env python3
"""Monster prime-ratio signatures as permutation indices r_p = [H:K].

Goal
----
Turn the emergent pattern

  r_p := n_{2X,3Y}^{pZ} / p  ∈  PermDegrees(H)  ⇔  r_p = [H:K]

into one cross-checked, repo-deterministic table across all supported
Ogg primes/classes.

Here:
  - pZ is a prime-order Monster class,
  - |C_M(pZ)| = p · H (ATLAS centralizer cofactor),
  - n_{2X,3Y}^{pZ} is the class-algebra structure constant-per-element for the
    (2X,3Y) pair into pZ (bundled CTblLib column data),
  - PermDegrees(H) is a committed/recognized transitive-permutation degree list
    for H, and
  - K is the stabilizer subgroup for the corresponding transitive action.

This is an *offline* script (no web/GAP). It only uses bundled ATLAS snapshots
and committed small degree lists.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_rp_index_table.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _fraction_from_payload(payload: object) -> Fraction:
    if not isinstance(payload, dict):
        return Fraction(0, 1)
    try:
        return Fraction(int(payload["numerator"]), int(payload["denominator"]))
    except Exception:
        return Fraction(0, 1)


def _iter_pairs(pair_keys: Iterable[str]) -> list[str]:
    out = []
    for k in pair_keys:
        if isinstance(k, str) and k:
            out.append(k)
    out.sort()
    return out


def _pair_to_ascii(pair: str) -> str:
    s = str(pair)
    # Tolerate either proper UTF-8 (×) or mojibake (Ã—) coming from older dumps.
    return s.replace("×", "x").replace("Ã—", "x")


def _pair_to_times(pair: str) -> str:
    s = str(pair)
    # Tolerate either ASCII (x) or mojibake (Ã—); normalize to × for display.
    return s.replace("x", "×").replace("Ã—", "×")


def _compute_mass_by_pair_for_prime(
    *,
    pairs: dict[str, Any],
    prime: int,
) -> dict[str, dict[str, object]]:
    mass_by_pair: dict[str, Fraction] = {}
    for pair_key, pdata in pairs.items():
        if not isinstance(pair_key, str) or not isinstance(pdata, dict):
            continue
        classes = pdata.get("classes", {})
        if not isinstance(classes, dict):
            continue
        mass = Fraction(0, 1)
        for cls_info in classes.values():
            if not isinstance(cls_info, dict):
                continue
            try:
                p = int(cls_info.get("prime", 0) or 0)
            except Exception:
                p = 0
            if p != int(prime):
                continue
            mass += _fraction_from_payload(cls_info.get("probability"))
        mass_by_pair[str(pair_key)] = mass

    out: dict[str, dict[str, object]] = {}
    for pair_key, mass in mass_by_pair.items():
        out[str(pair_key)] = {
            "numerator": int(mass.numerator),
            "denominator": int(mass.denominator),
            "value": str(mass),
            "float": float(mass),
        }
    return out


def _best_pair_by_mass(mass_by_pair: dict[str, dict[str, object]]) -> str | None:
    best_pair: str | None = None
    best_mass = -1.0
    for pair, info in mass_by_pair.items():
        if not isinstance(pair, str) or not isinstance(info, dict):
            continue
        try:
            mf = float(info.get("float", 0.0) or 0.0)
        except Exception:
            mf = 0.0
        if mf > best_mass:
            best_mass = float(mf)
            best_pair = str(pair)
    return best_pair


def analyze(*, include_mass_ranking: bool = True) -> dict[str, Any]:
    """Return a structured r_p index table report."""

    from scripts.w33_leech_monster import (
        analyze_monster_2x3_ogg_prime_triangle_support,
        load_monster_atlas_ccls,
    )
    from scripts.w33_monster_centralizer_cofactor_groups import (
        analyze as analyze_cofactors,
    )
    from scripts.w33_monster_prime_ratio_signatures import (
        analyze as analyze_ratio_signatures,
    )

    atlas = load_monster_atlas_ccls()
    if atlas is None:
        return {"available": False, "reason": "missing bundled monster_atlas_ccls.json"}
    atlas_classes = atlas.get("classes", {})
    if not isinstance(atlas_classes, dict) or not atlas_classes:
        return {"available": False, "reason": "invalid monster ATLAS payload"}

    tri = analyze_monster_2x3_ogg_prime_triangle_support()
    if tri.get("available") is not True:
        return {"available": False, "reason": "triangle support scan unavailable"}

    pairs = tri.get("pairs", {})
    ogg_primes = tri.get("ogg_primes", [])
    if not isinstance(pairs, dict) or not isinstance(ogg_primes, list):
        return {"available": False, "reason": "unexpected triangle-scan payload"}

    cofactor = analyze_cofactors()
    if cofactor.get("available") is not True:
        return {"available": False, "reason": "cofactor analysis unavailable"}
    classes = cofactor.get("classes", {})
    if not isinstance(classes, dict) or not classes:
        return {"available": False, "reason": "unexpected cofactor payload"}

    ratio = analyze_ratio_signatures()
    rungs = ratio.get("rungs", {}) if isinstance(ratio, dict) else {}
    if not isinstance(rungs, dict):
        rungs = {}

    pair_keys = _iter_pairs(pairs.keys())
    ogg_prime_list = sorted({int(p) for p in ogg_primes if isinstance(p, int) and p >= 5})

    # Partition classes by prime.
    classes_by_prime: dict[int, list[str]] = defaultdict(list)
    for cls_name, info in classes.items():
        if not isinstance(cls_name, str) or not isinstance(info, dict):
            continue
        p = int(info.get("order", 0) or 0)
        if p >= 5:
            classes_by_prime[int(p)].append(str(cls_name))
    for p, xs in classes_by_prime.items():
        xs.sort()

    # Per-class records (perm hits + optional irrep hits).
    per_class: dict[str, Any] = {}
    perm_hit_pair_counts: Counter[str] = Counter()
    irrep_hit_pair_counts: Counter[str] = Counter()
    n_perm_hit_classes = 0
    n_irrep_hit_classes = 0

    for cls_name, info in classes.items():
        if not isinstance(cls_name, str) or not isinstance(info, dict):
            continue

        order = int(info.get("order", 0) or 0)
        cent = int(info.get("centralizer_order", 0) or 0)
        cof = int(info.get("cofactor_order", 0) or 0)
        recognized = info.get("cofactor_group_recognized")

        # Cross-check: bundled ATLAS snapshot agrees with derived class metadata.
        atlas_meta = atlas_classes.get(str(cls_name), {})
        if isinstance(atlas_meta, dict) and atlas_meta:
            atlas_order = int(atlas_meta.get("order", 0) or 0)
            atlas_cent = int(atlas_meta.get("centralizer_order", 0) or 0)
            if atlas_order and atlas_order != order:
                raise AssertionError(
                    f"ATLAS order mismatch for {cls_name}: {order} vs {atlas_order}"
                )
            if atlas_cent and atlas_cent != cent:
                raise AssertionError(
                    f"ATLAS centralizer mismatch for {cls_name}: {cent} vs {atlas_cent}"
                )

        perm_hits = info.get("perm_hits", [])
        if not isinstance(perm_hits, list):
            perm_hits = []
        perm_hit_rows: list[dict[str, Any]] = []
        for h in perm_hits:
            if not isinstance(h, dict):
                continue
            pair = _pair_to_times(str(h.get("pair") or ""))
            r = int(h.get("r", 0) or 0)
            n = int(h.get("n", 0) or 0)
            stab = int(h.get("stabilizer_order", 0) or 0)
            if r <= 0 or stab <= 0:
                continue
            # Cross-check: r == [H:K] = |H|/|K|.
            if cof % r != 0 or cof // r != stab:
                raise AssertionError(
                    f"index mismatch for {cls_name} pair={pair}: cof={cof} r={r} stab={stab}"
                )
            # Cross-check: structure constant per element n == p*r (when present).
            if order > 0 and n > 0 and int(n) != int(order) * int(r):
                raise AssertionError(
                    f"structure constant mismatch for {cls_name} pair={pair}: n={n} p={order} r={r}"
                )
            perm_hit_rows.append(
                {
                    "pair": pair,
                    "r": int(r),
                    "n": int(n) if n else None,
                    "index_equals_r": True,
                    "cofactor_group": recognized,
                    "cofactor_order": int(cof),
                    "stabilizer_order": int(stab),
                    "stabilizer_group_recognized": h.get(
                        "stabilizer_group_recognized"
                    ),
                    "outer_stabilizer_order": h.get("outer_stabilizer_order"),
                    "outer_stabilizer_group_recognized": h.get(
                        "outer_stabilizer_group_recognized"
                    ),
                    "permrep_metadata": h.get("permrep_metadata"),
                }
            )
            perm_hit_pair_counts[pair] += 1

        if perm_hit_rows:
            n_perm_hit_classes += 1

        # Optional irrep-degree hits for sporadic rungs where we have committed spectra.
        irrep_hit_rows: list[dict[str, Any]] = []
        if cls_name in rungs:
            rin = rungs.get(cls_name, {})
            if isinstance(rin, dict):
                irrep_hits = rin.get("ratio_hits_in_irrep_degree_set", [])
                if isinstance(irrep_hits, list):
                    for h in irrep_hits:
                        if not isinstance(h, dict):
                            continue
                        pair = _pair_to_times(str(h.get("pair") or ""))
                        r = int(h.get("r", 0) or 0)
                        n = int(h.get("n", 0) or 0)
                        if order <= 0 or r <= 0:
                            continue
                        # Cross-check: n == p*r.
                        if int(n) != int(order) * int(r):
                            raise AssertionError(
                                f"r_p mismatch for {cls_name} pair={pair}: n={n} p={order} r={r}"
                            )
                        irrep_hit_rows.append(
                            {"pair": pair, "r": int(r), "n": int(n), "p": int(order)}
                        )
                        irrep_hit_pair_counts[pair] += 1

        if irrep_hit_rows:
            n_irrep_hit_classes += 1

        # Carry ratios_by_pair to show raw r-values even when no perm-hit occurs.
        ratios_by_pair = info.get("ratios_by_pair", {})
        if not isinstance(ratios_by_pair, dict):
            ratios_by_pair = {}

        per_class[cls_name] = {
            "class": cls_name,
            "p": int(order),
            "centralizer_order": int(cent),
            "cofactor_order": int(cof),
            "cofactor_group_recognized": recognized,
            "perm_degrees": info.get("perm_degrees", []),
            "perm_hits": perm_hit_rows,
            "irrep_hits": irrep_hit_rows,
            "ratios_by_pair": ratios_by_pair,
        }

    # Per-prime rollups: show mass-best vs index-best pair.
    per_prime: list[dict[str, Any]] = []
    best_by_perm_index_counts: Counter[str] = Counter()
    best_by_mass_counts: Counter[str] = Counter()
    n_perm_index_best_differs_from_mass_best = 0

    for p in ogg_prime_list:
        cls_list = classes_by_prime.get(int(p), [])
        if not cls_list:
            continue

        perm_index_hits: list[dict[str, Any]] = []
        # Determine best perm-index pair as the one achieving the largest r among all
        # perm hits across classes of this prime.
        best_pair_perm: str | None = None
        best_r_perm: int = 0
        for cls in cls_list:
            cinfo = per_class.get(cls, {})
            if not isinstance(cinfo, dict):
                continue
            for h in cinfo.get("perm_hits", []):
                if not isinstance(h, dict):
                    continue
                pair = str(h.get("pair") or "")
                r = int(h.get("r", 0) or 0)
                perm_index_hits.append({"class": cls, **h})
                if r > best_r_perm:
                    best_r_perm = int(r)
                    best_pair_perm = str(pair)

        if best_pair_perm is not None:
            best_by_perm_index_counts[best_pair_perm] += 1

        mass_by_pair = (
            _compute_mass_by_pair_for_prime(pairs=pairs, prime=int(p))
            if include_mass_ranking
            else {}
        )
        best_pair_mass = (
            _best_pair_by_mass(mass_by_pair) if include_mass_ranking else None
        )
        if isinstance(best_pair_mass, str):
            best_by_mass_counts[best_pair_mass] += 1

        if (
            isinstance(best_pair_mass, str)
            and isinstance(best_pair_perm, str)
            and best_pair_perm
            and best_pair_mass != best_pair_perm
        ):
            n_perm_index_best_differs_from_mass_best += 1

        per_prime.append(
            {
                "p": int(p),
                "classes": list(cls_list),
                "best_pair_by_mass": best_pair_mass,
                "mass_by_pair": mass_by_pair,
                "best_pair_by_perm_index": best_pair_perm,
                "best_perm_index_r": int(best_r_perm),
                "perm_index_hits": perm_index_hits,
            }
        )

    per_prime.sort(key=lambda rec: int(rec.get("p", 0) or 0))

    return {
        "available": True,
        "ogg_primes": ogg_prime_list,
        "pairs": pair_keys,
        "summary": {
            "n_classes": len(per_class),
            "n_classes_with_perm_hit": int(n_perm_hit_classes),
            "n_classes_with_irrep_hit": int(n_irrep_hit_classes),
            "perm_hit_pair_counts": dict(perm_hit_pair_counts),
            "irrep_hit_pair_counts": dict(irrep_hit_pair_counts),
            "n_primes": len(per_prime),
            "best_pair_by_perm_index_counts": dict(best_by_perm_index_counts),
            "best_pair_by_mass_counts": dict(best_by_mass_counts),
            "n_perm_index_best_differs_from_mass_best": int(
                n_perm_index_best_differs_from_mass_best
            ),
        },
        "per_prime": per_prime,
        "per_class": per_class,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(str(rep.get("reason") or "analysis unavailable"))

    print("=" * 78)
    print("MONSTER r_p INDEX TABLE: r_p = n/p as permutation index [H:K]")
    print("=" * 78)
    print(f"Ogg primes scanned: {rep.get('ogg_primes')}")
    print(f"Pairs: {rep.get('pairs')}")
    print()

    summary = rep.get("summary", {})
    if isinstance(summary, dict):
        print("Summary:")
        print(
            "  classes with perm-hit:",
            summary.get("n_classes_with_perm_hit"),
            "/",
            summary.get("n_classes"),
        )
        print("  classes with irrep-hit:", summary.get("n_classes_with_irrep_hit"))
        print("  best pair by perm-index counts:", summary.get("best_pair_by_perm_index_counts"))
        if summary.get("best_pair_by_mass_counts"):
            print("  best pair by mass counts:", summary.get("best_pair_by_mass_counts"))
            print(
                "  perm-index best differs from mass-best (primes):",
                summary.get("n_perm_index_best_differs_from_mass_best"),
                "/",
                summary.get("n_primes"),
            )
        print()

    per_prime = rep.get("per_prime", [])
    per_class = rep.get("per_class", {})
    assert isinstance(per_prime, list)
    assert isinstance(per_class, dict)

    for prec in per_prime:
        if not isinstance(prec, dict):
            continue
        p = int(prec.get("p", 0) or 0)
        best_mass = prec.get("best_pair_by_mass")
        best_perm = prec.get("best_pair_by_perm_index")
        best_r = int(prec.get("best_perm_index_r", 0) or 0)
        print(f"p={p:2d}: best perm-index pair = {best_perm} (r={best_r})")
        if isinstance(best_mass, str) and best_mass:
            if isinstance(best_perm, str) and best_perm and best_perm != best_mass:
                print(f"      mass-best differs: {best_mass}")
            else:
                print(f"      mass-best: {best_mass}")

        for cls in prec.get("classes", []):
            cinfo = per_class.get(cls, {})
            if not isinstance(cinfo, dict):
                continue
            recog = cinfo.get("cofactor_group_recognized")
            cof = cinfo.get("cofactor_order")
            hits = cinfo.get("perm_hits", [])
            if isinstance(hits, list) and hits:
                hit_str = ", ".join(
                    f"{h['pair']}→r={h['r']} (|K|={h['stabilizer_order']}, K≈{h.get('stabilizer_group_recognized')})"
                    for h in hits
                    if isinstance(h, dict)
                )
                print(f"      {cls}: H={recog} |H|={cof}  {hit_str}")
                continue

            # No perm-degree hit: still show the largest candidate r and whether it
            # defines an integral index |H|/r.
            ratios = cinfo.get("ratios_by_pair", {})
            if isinstance(ratios, dict) and ratios:
                best_pair = None
                best_r0 = -1
                best_n0 = None
                for pair0, payload0 in ratios.items():
                    if not isinstance(payload0, dict):
                        continue
                    r0 = payload0.get("r")
                    n0 = payload0.get("n")
                    if r0 is None:
                        continue
                    try:
                        r0i = int(r0)
                    except Exception:
                        continue
                    if r0i > best_r0:
                        best_r0 = r0i
                        best_pair = _pair_to_times(str(pair0))
                        best_n0 = int(n0) if n0 is not None else None

                if best_pair is not None and best_r0 > 0:
                    k_ord = None
                    if (
                        isinstance(cof, int)
                        and int(cof) > 0
                        and int(cof) % int(best_r0) == 0
                    ):
                        k_ord = int(int(cof) // int(best_r0))
                    k_desc = f"|K|={k_ord}" if k_ord is not None else "|K|=non-integer"
                    n_desc = f", n=p·r={best_n0}" if best_n0 is not None else ""
                    print(
                        f"      {cls}: H={recog} |H|={cof}  (no perm-hit) max r={best_r0} at {best_pair} ({k_desc}{n_desc})"
                    )
        print()

    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"Wrote {args.out_json}")


if __name__ == "__main__":
    main()
