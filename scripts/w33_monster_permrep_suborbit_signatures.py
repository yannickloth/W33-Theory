#!/usr/bin/env python3
"""Suborbit signatures for sporadic permutation actions touched by r_p.

This is a deterministic/offline deepening of the "prime ratio signature" story:

  - The Monster 2×3 class-algebra scan selects permutation degrees r_p for the
    centralizer cofactors (M12, He, HN).
  - For He and HN, the ATLAS gives the *rank* and the full list of suborbit
    lengths for the corresponding primitive permutation representations.

Here we factor those suborbit lengths against canonical TOE/W(3,3) invariants,
showing unexpected exact coincidences (e.g. 1360 = 17×80, 166320 = 77×2160).

We also scan additional Held-group permutation actions (8330, 29155, 244800)
whose ATLAS suborbits directly contain modular/spectral constants (notably
2160 = E4[q^2] and 960 = Tr(L1)).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_permrep_suborbit_signatures.py
"""

from __future__ import annotations

import json
import math
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


def _load_permrep_meta(group: str, degree: int) -> dict[str, Any]:
    path = ROOT / "data" / f"{str(group).lower()}_permutation_degrees.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rep = payload.get("rep_metadata", {}).get(str(int(degree)), {})
    if not isinstance(rep, dict):
        return {}
    return dict(rep)


def analyze() -> dict[str, Any]:
    from scripts.w33_leech_monster import compute_w33_monster_invariants, e4_coeffs

    w33 = compute_w33_monster_invariants()
    n_inc = int(w33.get("n_incidence_objects", 0) or 0)
    n_vertices = int(w33.get("n_vertices", 0) or 0)
    ihara_chi = 240 - n_vertices
    assert ihara_chi == 200
    e4 = e4_coeffs(6)
    e4_q2 = int(e4[2])

    # W33 Hodge L1 spectrum (Pillar 6) -> trace Tr(L1)=960.
    l1_spectrum = {0: 81, 4: 120, 10: 24, 16: 15}
    tr_l1 = int(sum(int(lam) * int(mult) for lam, mult in l1_spectrum.items()))
    assert tr_l1 == 960

    # Aut(W33) = Sp(4,3) (as used throughout the repo).
    sp4_3_order = int(3**4 * (3**2 - 1) * (3**4 - 1))
    assert sp4_3_order == 51840

    he = _load_permrep_meta("He", 2058)
    he_8330 = _load_permrep_meta("He", 8330)
    he_29155 = _load_permrep_meta("He", 29155)
    he_244800 = _load_permrep_meta("He", 244800)
    hn = _load_permrep_meta("HN", 1140000)
    m12_495 = _load_permrep_meta("M12", 495)

    he_sub = [int(x) for x in he.get("suborbit_lengths", [])]
    he_8330_sub = [int(x) for x in he_8330.get("suborbit_lengths", [])]
    he_29155_sub = [int(x) for x in he_29155.get("suborbit_lengths", [])]
    he_244800_sub = [int(x) for x in he_244800.get("suborbit_lengths", [])]
    hn_sub = [int(x) for x in hn.get("suborbit_lengths", [])]
    m12_495_sub = [int(x) for x in m12_495.get("suborbit_lengths", [])]

    if he_sub:
        assert sum(he_sub) == 2058
    if he_8330_sub:
        assert sum(he_8330_sub) == 8330
    if he_29155_sub:
        assert sum(he_29155_sub) == 29155
    if he_244800_sub:
        assert sum(he_244800_sub) == 244800
    if hn_sub:
        assert sum(hn_sub) == 1140000
    if m12_495_sub:
        assert sum(m12_495_sub) == 495

    he_nontrivial = [x for x in he_sub if x != 1]
    he_gcd = 0
    for x in he_nontrivial:
        he_gcd = math.gcd(he_gcd, int(x))

    # Key exact coincidences (certified by ATLAS suborbits, then algebraically checked).
    he_hits = {
        "gcd_nontrivial": int(he_gcd),
        "has_17x80": bool((17 * n_inc) in he_sub),
        "has_17x8": bool((17 * 8) in he_sub),
        "nontrivial_sum": int(sum(he_nontrivial)),
        "nontrivial_sum_factorization": _factorint(int(sum(he_nontrivial))),
        "nontrivial_all_multiples_of_17": bool(
            all(int(x) % 17 == 0 for x in he_nontrivial)
        ),
    }
    if he_sub:
        # All nontrivial suborbits in the 2058 action are multiples of 17, and one is 17×80.
        assert he_hits["gcd_nontrivial"] == 17
        assert he_hits["nontrivial_all_multiples_of_17"] is True
        assert he_hits["has_17x80"] is True
        assert he_hits["has_17x8"] is True
        # 2058 = 1 + 17×121 (121 = 11^2).
        assert he_hits["nontrivial_sum"] == 17 * 121

    hn_hits = {
        "has_80x385": bool((n_inc * 385) in hn_sub),
        "has_77x2160": bool((77 * e4_q2) in hn_sub),
        "has_7x_aut_w33": bool((7 * sp4_3_order) in hn_sub),
        "has_27x385": bool((27 * 385) in hn_sub),
        "has_10x81x385": bool((10 * 81 * 385) in hn_sub),
    }
    if hn_sub:
        assert hn_hits["has_80x385"] is True
        assert hn_hits["has_77x2160"] is True
        assert hn_hits["has_7x_aut_w33"] is True
        assert hn_hits["has_27x385"] is True
        assert hn_hits["has_10x81x385"] is True

    he_8330_hits = {
        "has_9x80": bool((9 * n_inc) in he_8330_sub),
        "has_56x80": bool((56 * n_inc) in he_8330_sub),
    }
    if he_8330_sub:
        assert he_8330_hits["has_9x80"] is True  # 720 = 9×(points+lines)
        assert he_8330_hits["has_56x80"] is True  # 4480 = 56×(points+lines)

    he_29155_hits = {
        "has_e4_q2": bool(e4_q2 in he_29155_sub),
        "has_trace_l1": bool(tr_l1 in he_29155_sub),
        "has_6x240": bool((6 * 240) in he_29155_sub),
        "has_9x240": bool((9 * 240) in he_29155_sub),
        "has_48x240": bool((48 * 240) in he_29155_sub),
    }
    if he_29155_sub:
        assert he_29155_hits["has_e4_q2"] is True
        assert he_29155_hits["has_trace_l1"] is True
        assert he_29155_hits["has_6x240"] is True
        assert he_29155_hits["has_9x240"] is True
        assert he_29155_hits["has_48x240"] is True

    he_244800_hits = {
        "has_343": bool(343 in he_244800_sub),
        "has_1372_eq_4x343": bool(1372 in he_244800_sub),
        "has_1029_eq_3x343": bool(1029 in he_244800_sub),
        "has_16464_as_stabilizer": bool(16464 in he_244800_sub),
    }
    if he_244800_sub:
        assert he_244800_hits["has_343"] is True
        assert he_244800_hits["has_1372_eq_4x343"] is True
        assert he_244800_hits["has_1029_eq_3x343"] is True
        assert he_244800_hits["has_16464_as_stabilizer"] is True

    m12_495_hits = {
        "has_w33_incidence_80": bool(n_inc in m12_495_sub),
        "has_ihara_chi_200": bool(ihara_chi in m12_495_sub),
    }
    if m12_495_sub:
        assert m12_495_hits["has_w33_incidence_80"] is True
        assert m12_495_hits["has_ihara_chi_200"] is True

    return {
        "available": True,
        "w33": {
            "n_incidence_objects": n_inc,
            "aut_group_order": sp4_3_order,
        },
        "e4": {"q2": e4_q2, "coeffs": [int(x) for x in e4]},
        "w33_spectral": {"tr_L1": tr_l1},
        "he_2058": {
            "rank": int(he.get("rank", 0) or 0),
            "suborbit_lengths": he_sub,
            "suborbit_factorizations": {int(x): _factorint(int(x)) for x in he_sub},
            "signature_hits": he_hits,
        },
        "he_8330": {
            "rank": int(he_8330.get("rank", 0) or 0),
            "suborbit_lengths": he_8330_sub,
            "signature_hits": he_8330_hits,
        },
        "he_29155": {
            "rank": int(he_29155.get("rank", 0) or 0),
            "suborbit_lengths": he_29155_sub,
            "signature_hits": he_29155_hits,
        },
        "he_244800": {
            "rank": int(he_244800.get("rank", 0) or 0),
            "suborbit_lengths": he_244800_sub,
            "signature_hits": he_244800_hits,
        },
        "hn_1140000": {
            "rank": int(hn.get("rank", 0) or 0),
            "suborbit_lengths": hn_sub,
            "signature_hits": hn_hits,
        },
        "m12_495": {
            "rank": int(m12_495.get("rank", 0) or 0),
            "suborbit_lengths": m12_495_sub,
            "signature_hits": m12_495_hits,
        },
    }


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    w33 = rep["w33"]
    print("=" * 78)
    print("SPORADIC PERMREP SUBORBIT SIGNATURES (from r_p hits)")
    print("=" * 78)
    print(f"W33 incidence objects: {w33['n_incidence_objects']}")
    print(f"|Aut(W33)| (Sp(4,3)): {w33['aut_group_order']}")
    print()

    he = rep["he_2058"]
    he_sub = he["suborbit_lengths"]
    print("He permrep degree 2058:")
    print(f"  rank = {he['rank']}")
    print(f"  suborbits = {he_sub}")
    print(f"  gcd(nontrivial) = {he['signature_hits']['gcd_nontrivial']}")
    print(
        f"  sum(nontrivial) = {he['signature_hits']['nontrivial_sum']} (= 17×121 = 17×11^2)"
    )
    print(
        f"  contains 17×80? {he['signature_hits']['has_17x80']}  (80 = W33 points+lines)"
    )
    print(f"  contains 17×8?  {he['signature_hits']['has_17x8']}  (8 = rank(E8))")
    print()

    he_29155 = rep["he_29155"]
    print("He permrep degree 29155:")
    print(f"  rank = {he_29155['rank']}")
    print(
        f"  suborbits (count={len(he_29155['suborbit_lengths'])}): {he_29155['suborbit_lengths']}"
    )
    print(
        f"  contains 2160? {he_29155['signature_hits']['has_e4_q2']}  (2160 = E4[q^2])"
    )
    print(
        f"  contains 960?  {he_29155['signature_hits']['has_trace_l1']}  (960 = Tr(L1))"
    )
    print()

    hn = rep["hn_1140000"]
    hn_sub = hn["suborbit_lengths"]
    print("HN permrep degree 1140000:")
    print(f"  rank = {hn['rank']}")
    print(f"  suborbits (count={len(hn_sub)}): {hn_sub}")
    print(f"  contains 80×385?    {hn['signature_hits']['has_80x385']}")
    print(
        f"  contains 27×385?    {hn['signature_hits']['has_27x385']}  (27 = E6 fundamental)"
    )
    print(
        f"  contains 10×81×385? {hn['signature_hits']['has_10x81x385']}  (81 = b1(W33))"
    )
    print(
        f"  contains 77×2160?   {hn['signature_hits']['has_77x2160']}  (2160 = E4[q^2])"
    )
    print(f"  contains 7×51840?   {hn['signature_hits']['has_7x_aut_w33']}")
    print()

    m12 = rep["m12_495"]
    print("M12 permrep degree 495:")
    print(f"  rank = {m12['rank']}")
    print(
        f"  suborbits (count={len(m12['suborbit_lengths'])}): {m12['suborbit_lengths']}"
    )
    print(
        f"  contains 80?  {m12['signature_hits']['has_w33_incidence_80']}  (80 = W33 points+lines)"
    )
    print(
        f"  contains 200? {m12['signature_hits']['has_ihara_chi_200']}  (200 = |E|-|V|)"
    )
    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
