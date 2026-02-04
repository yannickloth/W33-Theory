#!/usr/bin/env python3
"""
Analyze the Z3-graded E8 bracket at the level of *root channels* (not matrices):

  [g1,g1] -> g2  corresponds to the cubic E6 invariant (45 triads) tensored with SU(3) epsilon.

This script uses the exported 248-dim structure constants (from the W33-discrete engine) and
the repo's canonical cubic triads + firewall-forbidden triads to produce a clean "coupling atlas":

  - All nonzero root-brackets between grade-g1 roots (81 of them)
  - Grouped by underlying E6 triad (i27 triple, 45 total)
  - Split into firewall-allowed (36) vs firewall-forbidden (9)

Inputs:
  - artifacts/e8_structure_constants_w33_discrete.json
  - artifacts/e8_root_metadata_table.json
  - artifacts/canonical_su3_gauge_and_cubic.json
  - artifacts/firewall_bad_triads_mapping.json

Outputs:
  - artifacts/e8_g1g1_couplings_cubic_firewall.json
  - artifacts/e8_g1g1_couplings_cubic_firewall.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

IN_SC = ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json"
IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
IN_CUBIC = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
IN_FW = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"

OUT_JSON = ROOT / "artifacts" / "e8_g1g1_couplings_cubic_firewall.json"
OUT_MD = ROOT / "artifacts" / "e8_g1g1_couplings_cubic_firewall.md"


Root = Tuple[int, ...]


def _triad_key(a: int, b: int, c: int) -> Tuple[int, int, int]:
    return tuple(sorted((int(a), int(b), int(c))))


def _load_meta_by_root_orbit() -> Dict[Root, dict]:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta["rows"]
    out: Dict[Root, dict] = {}
    for r in rows:
        rt = tuple(int(x) for x in r["root_orbit"])
        out[rt] = r
    if len(out) != 240:
        raise RuntimeError(f"Expected 240 unique root_orbit rows; got {len(out)}")
    return out


def _load_cubic_triads() -> Dict[Tuple[int, int, int], int]:
    canon = json.loads(IN_CUBIC.read_text(encoding="utf-8"))
    d_sign: Dict[Tuple[int, int, int], int] = {}
    for t in canon["solution"]["d_triples"]:
        tri = _triad_key(*t["triple"])
        d_sign[tri] = int(t["sign"])
    if len(d_sign) != 45:
        raise RuntimeError(f"Expected 45 cubic triads; got {len(d_sign)}")
    return d_sign


def _load_firewall_bad_triads() -> set[Tuple[int, int, int]]:
    fw = json.loads(IN_FW.read_text(encoding="utf-8"))
    triads = fw["bad_triangles_Schlafli_e6id"]
    bad = {_triad_key(*t) for t in triads}
    if len(bad) != 9:
        raise RuntimeError(f"Expected 9 firewall triads; got {len(bad)}")
    return bad


def _parse_brackets(sc: dict) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
    brackets_raw: Dict[str, List[List[int]]] = sc["brackets"]
    table: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    for key, terms in brackets_raw.items():
        i_str, j_str = key.split(",")
        i, j = int(i_str), int(j_str)
        table[(i, j)] = [(int(k), int(c)) for k, c in terms]
    return table


def main() -> None:
    sc = json.loads(IN_SC.read_text(encoding="utf-8"))
    basis = sc["basis"]
    cartan_dim = int(basis["cartan_dim"])
    if cartan_dim != 8:
        raise RuntimeError("Expected cartan_dim=8")
    roots: List[List[int]] = basis["roots"]
    if len(roots) != 240:
        raise RuntimeError("Expected 240 roots in structure-constants basis")

    meta_by_root = _load_meta_by_root_orbit()
    d_sign = _load_cubic_triads()
    bad_triads = _load_firewall_bad_triads()
    bracket = _parse_brackets(sc)

    # Build list of grade-g1 root basis indices.
    g1_root_basis: List[int] = []
    for r_idx, rt_list in enumerate(roots):
        rt = tuple(int(x) for x in rt_list)
        row = meta_by_root.get(rt)
        if row is None:
            raise RuntimeError("Root missing from metadata table")
        if row["grade"] == "g1":
            g1_root_basis.append(cartan_dim + r_idx)

    if len(g1_root_basis) != 81:
        raise RuntimeError(f"Expected 81 g1 roots; got {len(g1_root_basis)}")

    # Extract g1×g1 nonzero brackets.
    couplings: List[dict] = []
    triad_hist: Counter[Tuple[int, int, int]] = Counter()
    triad_bad_hist: Counter[Tuple[int, int, int]] = Counter()
    su3_pair_hist: Counter[Tuple[int, int, int]] = Counter()  # (a3,b3,c3) with a3<b3
    phase_trip_hist: Counter[Tuple[int, int, int]] = Counter()  # (pa,pb,pc) in Z6
    phase_delta_hist: Counter[int] = (
        Counter()
    )  # pc - pa - pb mod 6 (ordered by basis indices)
    phase_delta_bad_hist: Counter[int] = Counter()
    coeff_hist: Counter[int] = Counter()

    triads_seen: set[Tuple[int, int, int]] = set()

    for ii, bi in enumerate(g1_root_basis):
        rt_i = tuple(int(x) for x in roots[bi - cartan_dim])
        mi = meta_by_root[rt_i]
        a27 = mi["i27"]
        a3 = mi["i3"]
        pa = mi["phase_z6"]
        if a27 is None or a3 is None or pa is None:
            raise RuntimeError("Missing i27/i3/phase_z6 for g1 root")
        for bj in g1_root_basis[ii + 1 :]:
            rt_j = tuple(int(x) for x in roots[bj - cartan_dim])
            mj = meta_by_root[rt_j]
            b27 = mj["i27"]
            b3 = mj["i3"]
            pb = mj["phase_z6"]
            if b27 is None or b3 is None or pb is None:
                raise RuntimeError("Missing i27/i3/phase_z6 for g1 root")

            # bracket stored only for i<j (but our list is increasing by construction)
            terms = bracket.get((bi, bj), [])
            if not terms:
                continue
            if len(terms) != 1:
                raise RuntimeError("Expected single-term root bracket for g1×g1")
            out_k, out_c = terms[0]
            if out_k < cartan_dim:
                raise RuntimeError("g1×g1 should not output Cartan")
            rt_k = tuple(int(x) for x in roots[out_k - cartan_dim])
            mk = meta_by_root[rt_k]
            if mk["grade"] != "g2":
                raise RuntimeError("g1×g1 nonzero bracket must land in g2")
            c27 = mk["i27"]
            c3 = mk["i3"]
            pc = mk["phase_z6"]
            if c27 is None or c3 is None or pc is None:
                raise RuntimeError("Missing i27/i3/phase_z6 for g2 root")

            tri = _triad_key(a27, b27, c27)
            triads_seen.add(tri)
            triad_hist[tri] += 1
            if tri in bad_triads:
                triad_bad_hist[tri] += 1

            aa3, bb3, cc3 = (int(a3), int(b3), int(c3))
            if aa3 == bb3:
                # SU3 epsilon implies this should not happen for a real coupling
                raise RuntimeError("Found g1×g1 coupling with equal SU3 indices")
            # normalize input pair order by SU3 index only for histogram readability
            if aa3 < bb3:
                su3_pair_hist[(aa3, bb3, cc3)] += 1
            else:
                su3_pair_hist[(bb3, aa3, cc3)] += 1

            phase_trip_hist[(int(pa), int(pb), int(pc))] += 1
            delta = (int(pc) - int(pa) - int(pb)) % 6
            phase_delta_hist[delta] += 1
            if tri in bad_triads:
                phase_delta_bad_hist[delta] += 1
            coeff_hist[int(out_c)] += 1

            couplings.append(
                {
                    "in": [
                        {
                            "basis": int(bi),
                            "root_orbit": list(rt_i),
                            "i27": int(a27),
                            "i3": int(a3),
                            "phase_z6": int(pa),
                            "edge": mi.get("edge"),
                        },
                        {
                            "basis": int(bj),
                            "root_orbit": list(rt_j),
                            "i27": int(b27),
                            "i3": int(b3),
                            "phase_z6": int(pb),
                            "edge": mj.get("edge"),
                        },
                    ],
                    "out": {
                        "basis": int(out_k),
                        "coeff": int(out_c),
                        "root_orbit": list(rt_k),
                        "i27": int(c27),
                        "i3": int(c3),
                        "phase_z6": int(pc),
                        "edge": mk.get("edge"),
                    },
                    "triad_i27": list(tri),
                    "cubic_sign": int(d_sign.get(tri, 0)),
                    "firewall_forbidden": bool(tri in bad_triads),
                }
            )

    # Sanity: triads seen should equal the 45 cubic triads (as an *unordered* set).
    triads_cubic = set(d_sign.keys())
    triad_set_ok = triads_seen == triads_cubic

    # In the root-channel basis, SU(3) indices are *attached to each root* (i27,i3), so for a
    # fixed E6 pair {a27,b27} we get 6 distinct unordered root-pairs with a3!=b3:
    #   (a3,b3) ∈ {(0,1),(0,2),(1,2)} × two ways of assigning to (a27,b27) -> 6.
    # Each E6 triad contributes 3 E6 pairs, hence 18 nonzero g1×g1 root-brackets.
    expected_couplings = 45 * 18
    counts = {
        "g1_roots": len(g1_root_basis),
        "nonzero_g1g1_brackets": len(couplings),
        "unique_i27_triads_seen": len(triads_seen),
        "expected_cubic_triads": len(triads_cubic),
        "expected_couplings_if_uniform": expected_couplings,
        "firewall_bad_triads": len(bad_triads),
        "firewall_bad_couplings": int(
            sum(1 for c in couplings if c["firewall_forbidden"])
        ),
    }

    # Is the per-triad multiplicity uniform?
    triad_multiplicities = sorted(triad_hist.values())
    multiplicity_ok = (len(triad_multiplicities) == 45) and (
        min(triad_multiplicities) == max(triad_multiplicities)
    )

    status = "ok"
    if not triad_set_ok:
        status = "fail"
    if counts["nonzero_g1g1_brackets"] != expected_couplings:
        status = "fail"
    if not multiplicity_ok:
        status = "fail"
    if counts["firewall_bad_couplings"] != len(bad_triads) * 18:
        status = "fail"

    out = {
        "status": status,
        "counts": counts,
        "checks": {
            "triad_set_matches_cubic_45": bool(triad_set_ok),
            "per_triad_multiplicity_uniform": bool(multiplicity_ok),
            "expected_total_couplings_45x18": bool(
                counts["nonzero_g1g1_brackets"] == expected_couplings
            ),
            "expected_firewall_bad_couplings_9x18": bool(
                counts["firewall_bad_couplings"] == len(bad_triads) * 18
            ),
        },
        "histograms": {
            "triad_multiplicity": {str(list(k)): int(v) for k, v in triad_hist.items()},
            "triad_bad_multiplicity": {
                str(list(k)): int(v) for k, v in triad_bad_hist.items()
            },
            "su3_pairs": {str(list(k)): int(v) for k, v in su3_pair_hist.items()},
            "phase_delta_pc_minus_pa_minus_pb_mod6": {
                str(k): int(v) for k, v in phase_delta_hist.items()
            },
            "phase_delta_pc_minus_pa_minus_pb_mod6_bad_only": {
                str(k): int(v) for k, v in phase_delta_bad_hist.items()
            },
            "coeffs": {str(k): int(v) for k, v in coeff_hist.items()},
        },
        "couplings": couplings,
    }

    OUT_JSON.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md: List[str] = []
    md.append("# E8 g1×g1 couplings vs cubic triads + firewall\n")
    md.append(f"- status: `{status}`\n")
    md.append("## Counts\n")
    for k, v in counts.items():
        md.append(f"- {k}: `{v}`")
    md.append("\n## Checks\n")
    for k, v in out["checks"].items():
        md.append(f"- {k}: `{v}`")
    md.append("\n## Notes\n")
    md.append(
        "- Each unordered E6 cubic triad contributes 18 g1×g1→g2 root-channel couplings (3 E6-pairs × 6 SU3 index assignments with a3≠b3)."
    )
    md.append("- Firewall forbids 9 of 45 triads, i.e. 162 of 810 g1×g1 couplings.\n")
    md.append(f"- JSON: `{OUT_JSON}`")
    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print(f"status={status} couplings={len(couplings)} wrote={OUT_JSON}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
