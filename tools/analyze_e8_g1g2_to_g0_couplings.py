#!/usr/bin/env python3
"""
Analyze the Z3-graded E8 bracket on root channels:

  [g1, g2] -> g0 = (g0_e6 ⊕ g0_a2)  plus the Cartan terms when roots are opposite.

This is the clean "interaction semantics" of trinification at the level of E8 root spaces:
  - e6 outputs should preserve the SU3 index i3 (delta contraction in the 3-factor),
  - a2 outputs should preserve the E6 index i27 (delta contraction in the 27-factor),
  - opposite roots give Cartan.

Inputs:
  - artifacts/e8_structure_constants_w33_discrete.json
  - artifacts/e8_root_metadata_table.json

Outputs:
  - artifacts/e8_g1g2_to_g0_couplings.json
  - artifacts/e8_g1g2_to_g0_couplings.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
IN_SC = ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json"
IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
OUT_JSON = ROOT / "artifacts" / "e8_g1g2_to_g0_couplings.json"
OUT_MD = ROOT / "artifacts" / "e8_g1g2_to_g0_couplings.md"

Root = Tuple[int, ...]
Pair = Tuple[int, int]
Terms = List[Tuple[int, int]]


def _load_meta_by_root_orbit() -> Dict[Root, dict]:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    out: Dict[Root, dict] = {}
    for r in meta["rows"]:
        rt = tuple(int(x) for x in r["root_orbit"])
        out[rt] = r
    if len(out) != 240:
        raise RuntimeError("Expected 240 unique root_orbit rows")
    return out


def _parse_brackets(sc: dict) -> Dict[Pair, Terms]:
    table: Dict[Pair, Terms] = {}
    for key, terms in sc["brackets"].items():
        i_str, j_str = key.split(",")
        i, j = int(i_str), int(j_str)
        table[(i, j)] = [(int(k), int(c)) for k, c in terms]
    return table


def main() -> None:
    sc = json.loads(IN_SC.read_text(encoding="utf-8"))
    basis = sc["basis"]
    n = int(basis["n"])
    cartan_dim = int(basis["cartan_dim"])
    roots: List[List[int]] = basis["roots"]
    if n != 248 or cartan_dim != 8 or len(roots) != 240:
        raise RuntimeError("Unexpected basis sizing")

    meta_by_root = _load_meta_by_root_orbit()
    bracket = _parse_brackets(sc)

    g1 = []
    g2 = []
    g0_e6 = []
    g0_a2 = []
    for r_idx, rt_list in enumerate(roots):
        rt = tuple(int(x) for x in rt_list)
        row = meta_by_root[rt]
        bi = cartan_dim + r_idx
        if row["grade"] == "g1":
            g1.append(bi)
        elif row["grade"] == "g2":
            g2.append(bi)
        elif row["grade"] == "g0_e6":
            g0_e6.append(bi)
        elif row["grade"] == "g0_a2":
            g0_a2.append(bi)
    if len(g1) != 81 or len(g2) != 81 or len(g0_e6) != 72 or len(g0_a2) != 6:
        raise RuntimeError("Unexpected grade sizes")

    # Analyze all g1×g2 pairs (unordered by basis index), but record input (i27,i3) for each.
    out_kind = Counter()  # cartan / g0_e6 / g0_a2 / other / zero
    e6_preserve_i3 = 0
    e6_total = 0
    a2_preserve_i27 = 0
    a2_total = 0
    cartan_opposites = 0

    first_violation: dict | None = None

    for bi in g1:
        rt_i = tuple(int(x) for x in roots[bi - cartan_dim])
        mi = meta_by_root[rt_i]
        a27 = mi["i27"]
        a3 = mi["i3"]
        if a27 is None or a3 is None:
            raise RuntimeError("Missing i27/i3 for g1 root")
        for bj in g2:
            # ensure i<j for lookup
            i, j = (bi, bj) if bi < bj else (bj, bi)
            terms = bracket.get((i, j), [])
            if not terms:
                out_kind["zero"] += 1
                continue

            rt_j = tuple(int(x) for x in roots[bj - cartan_dim])
            mj = meta_by_root[rt_j]
            b27 = mj["i27"]
            b3 = mj["i3"]
            if b27 is None or b3 is None:
                raise RuntimeError("Missing i27/i3 for g2 root")

            # Two cases:
            # - root+(-root)=0 => Cartan combination (multiple terms, all k<8)
            # - root+root' is root => single root term (k>=8)
            if all(k < cartan_dim for k, _c in terms):
                out_kind["cartan"] += 1
                cartan_opposites += 1
                continue
            if len(terms) != 1:
                out_kind["other"] += 1
                if first_violation is None:
                    first_violation = {
                        "kind": "multi_term_non_cartan",
                        "pair": [bi, bj],
                        "terms": terms[:12],
                    }
                continue
            out_k, _out_c = terms[0]
            if out_k < cartan_dim:
                out_kind["other"] += 1
                if first_violation is None:
                    first_violation = {
                        "kind": "mixed_cartan_root",
                        "pair": [bi, bj],
                        "terms": terms[:12],
                    }
                continue
            rt_k = tuple(int(x) for x in roots[out_k - cartan_dim])
            mk = meta_by_root[rt_k]
            gk = mk["grade"]
            if gk == "g0_e6":
                out_kind["g0_e6"] += 1
                e6_total += 1
                if int(a3) == int(b3):
                    e6_preserve_i3 += 1
                else:
                    if first_violation is None:
                        first_violation = {
                            "kind": "e6_output_but_i3_mismatch",
                            "in": [mi, mj],
                            "out": mk,
                        }
            elif gk == "g0_a2":
                out_kind["g0_a2"] += 1
                a2_total += 1
                if int(a27) == int(b27):
                    a2_preserve_i27 += 1
                else:
                    if first_violation is None:
                        first_violation = {
                            "kind": "a2_output_but_i27_mismatch",
                            "in": [mi, mj],
                            "out": mk,
                        }
            else:
                out_kind["other"] += 1
                if first_violation is None:
                    first_violation = {
                        "kind": "unexpected_output_grade",
                        "out_grade": gk,
                        "pair": [bi, bj],
                    }

    checks = {
        "e6_outputs_preserve_i3": bool(e6_total == e6_preserve_i3),
        "a2_outputs_preserve_i27": bool(a2_total == a2_preserve_i27),
    }
    status = "ok"
    if not all(checks.values()):
        status = "fail"

    out = {
        "status": status,
        "counts": {
            "g1_roots": len(g1),
            "g2_roots": len(g2),
            "g1_g2_pairs": len(g1) * len(g2),
            "nonzero_pair_outputs": {k: int(v) for k, v in out_kind.items()},
            "e6_outputs": int(e6_total),
            "a2_outputs": int(a2_total),
            "cartan_opposites": int(cartan_opposites),
        },
        "checks": checks,
        "first_violation": first_violation,
    }

    OUT_JSON.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md: List[str] = []
    md.append("# E8 g1×g2 → g0 coupling analysis\n")
    md.append(f"- status: `{status}`\n")
    md.append("## Counts\n")
    for k, v in out["counts"].items():
        md.append(f"- {k}: `{v}`")
    md.append("\n## Checks\n")
    for k, v in checks.items():
        md.append(f"- {k}: `{v}`")
    md.append("\n## Interpretation\n")
    md.append(
        "- Outputs in `g0_e6` preserve `i3` (generation index) ⇒ E6 gauge bosons do not mix generations."
    )
    md.append(
        "- Outputs in `g0_a2` preserve `i27` (E6 index) ⇒ SU(3) family gauge bosons do not change the E6 state, only the generation label.\n"
    )
    md.append(f"- JSON: `{OUT_JSON}`")
    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print(f"status={status} wrote={OUT_JSON}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
