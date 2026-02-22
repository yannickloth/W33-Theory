#!/usr/bin/env python3
"""
Sage cross-check: firewall-filtered closed sections are exactly affine graphs.

We work purely combinatorially from repo artifacts:
  - artifacts/canonical_su3_gauge_and_cubic.json  (45 unsigned cubic triads on the 27)
  - artifacts/firewall_bad_triads_mapping.json    (9 forbidden triads)
  - artifacts/e6_cubic_affine_heisenberg_model.json (Heisenberg coords e6id -> (u,z) with u∈F3^2, z∈F3)

Definitions:
  - A "section" is a choice of exactly one lift (u,z) per fiber {u}×F3, so there are 3^9 sections.
  - Let T be the 36 remaining triads after deleting the 9 forbidden ones.
  - A section S is "closed" iff no triad t∈T intersects S in exactly 2 points.

Claim (verified here in Sage):
  - Exactly 27 sections are closed.
  - They are precisely the graphs of affine maps z(x,y)=a x + b y + c on F3^2 (a,b,c∈F3).

Outputs:
  - artifacts/sage_firewall_affine_sections.json
  - artifacts/sage_firewall_affine_sections.md

Run:
  ./run_sage.sh tools/sage_verify_firewall_affine_sections.py
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

try:
    from sage.all import GF  # type: ignore
except Exception:  # pragma: no cover
    try:  # pragma: no cover
        from sageall import GF  # type: ignore
    except Exception:  # pragma: no cover
        GF = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]

IN_CUBIC = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
IN_FW = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
IN_HEIS = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"

OUT_JSON = ROOT / "artifacts" / "sage_firewall_affine_sections.json"
OUT_MD = ROOT / "artifacts" / "sage_firewall_affine_sections.md"


def _triad_key(t: Sequence[int]) -> Tuple[int, int, int]:
    a, b, c = sorted((int(t[0]), int(t[1]), int(t[2])))
    return (a, b, c)


def _is_closed_section(triads_fw: Sequence[Set[int]], section: Set[int]) -> bool:
    for tri in triads_fw:
        c = len(tri & section)
        if c == 2:
            return False
    return True


def _affine_params_fit(zmap: Dict[Tuple[int, int], int]) -> Tuple[int, int, int] | None:
    for a in range(3):
        for b in range(3):
            for c in range(3):
                ok = True
                for x in range(3):
                    for y in range(3):
                        if (a * x + b * y + c) % 3 != int(zmap[(x, y)]):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    return (a, b, c)
    return None


def main() -> None:
    cubic = json.loads(IN_CUBIC.read_text(encoding="utf-8"))
    triads_all = [_triad_key(t) for t in cubic["triads"]]
    if len(triads_all) != 45:
        raise RuntimeError(f"Expected 45 cubic triads, got {len(triads_all)}")

    fw = json.loads(IN_FW.read_text(encoding="utf-8"))
    bad9 = {_triad_key(t) for t in fw["bad_triangles_Schlafli_e6id"]}
    if len(bad9) != 9:
        raise RuntimeError(f"Expected 9 firewall triads, got {len(bad9)}")

    triads_fw = [set(t) for t in triads_all if t not in bad9]
    if len(triads_fw) != 36:
        raise RuntimeError(f"Expected 36 remaining triads, got {len(triads_fw)}")

    heis = json.loads(IN_HEIS.read_text(encoding="utf-8"))
    e6_to_hz = {
        int(k): (tuple(v["u"]), int(v["z"]))
        for k, v in heis["e6id_to_heisenberg"].items()
    }
    hz_to_e6 = {(u, z): e6id for e6id, (u, z) in e6_to_hz.items()}

    # fibers: u -> [e6id_z0, e6id_z1, e6id_z2]
    fibers: Dict[Tuple[int, int], List[int]] = {}
    for e6id, (u, _z) in e6_to_hz.items():
        fibers.setdefault(u, []).append(int(e6id))
    for u in fibers:
        fibers[u] = sorted(fibers[u])
    if len(fibers) != 9 or any(len(v) != 3 for v in fibers.values()):
        raise RuntimeError("Expected 9 fibers of size 3")

    fiber_keys = sorted(fibers.keys())
    fiber_list = [fibers[u] for u in fiber_keys]

    # enumerate all sections
    closed_sections: List[Tuple[int, ...]] = []
    for choice in itertools.product([0, 1, 2], repeat=9):
        sec = {int(fiber_list[i][choice[i]]) for i in range(9)}
        if _is_closed_section(triads_fw, sec):
            closed_sections.append(tuple(sorted(sec)))

    # enumerate all affine graphs z(x,y)=a x + b y + c
    affine_sections: Dict[Tuple[int, int, int], Tuple[int, ...]] = {}
    for a in range(3):
        for b in range(3):
            for c in range(3):
                rows: List[int] = []
                for x in range(3):
                    for y in range(3):
                        z = int((a * x + b * y + c) % 3)
                        rows.append(int(hz_to_e6[((x, y), z)]))
                affine_sections[(a, b, c)] = tuple(sorted(rows))

    affine_set = set(affine_sections.values())
    closed_set = set(closed_sections)

    # (optional) use Sage GF(3) just to assert environment is Sage-capable
    sage_ok = False
    if GF is not None:
        F = GF(3)
        sage_ok = int(F(2) + F(2)) == 1

    report = {
        "status": "ok",
        "sage_available": bool(sage_ok),
        "counts": {
            "cubic_triads_total": 45,
            "firewall_bad_triads": 9,
            "triads_remaining": 36,
            "fibers": 9,
            "sections_total_3pow9": 3**9,
            "closed_sections": int(len(closed_sections)),
            "affine_functions": 27,
            "affine_equals_closed": bool(affine_set == closed_set),
        },
        "examples": {
            "one_closed_section": (
                list(sorted(next(iter(closed_set)))) if closed_set else []
            ),
            "one_non_affine_section": [],
        },
    }

    # sanity: all closed sections fit affine, and no extra affine missing
    if (
        report["counts"]["closed_sections"] != 27
        or not report["counts"]["affine_equals_closed"]
    ):
        raise RuntimeError(f"Unexpected classification: {report['counts']}")

    # Pick an example non-affine section to show it is not closed.
    # (Choose the constant-z=0 layer then flip one fiber value.)
    base_set = set(affine_sections[(0, 0, 0)])
    # perturb one fiber choice (ensure non-affine deterministically)
    last_u = fiber_keys[-1]
    ids = fibers[last_u]
    cur = next(e for e in base_set if e6_to_hz[int(e)][0] == last_u)
    base_set.remove(cur)
    base_set.add(ids[(ids.index(cur) + 1) % 3])
    base = tuple(sorted(base_set))
    report["examples"]["one_non_affine_section"] = list(base)
    report["examples"]["one_non_affine_section_closed"] = bool(base in closed_set)

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    md: List[str] = []
    md.append("# Sage check: firewall affine sections\n")
    md.append(f"- sage_available: `{report['sage_available']}`")
    for k, v in report["counts"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## Result\n")
    md.append(
        "The firewall-filtered triads admit exactly 27 closed sections, and these are precisely the affine graphs "
        "`z(x,y)=a x + b y + c` on `F3^2`."
    )
    md.append("")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
