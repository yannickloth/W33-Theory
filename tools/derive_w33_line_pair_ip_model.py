#!/usr/bin/env python3
"""
Discrete inner-product model for the 240 E8 root-channels in (line,phase) coordinates.

We already have a rigid bijection:
  E8 roots (240)  <->  W33 edges (240)  <->  (W33 line index 0..39, phase k∈Z6).

This script shows something stronger than the "fusion" laws:

  The entire inner-product pattern between roots on *different* W33 lines is
  determined by the line-pair type, and (for the generic coupled pairs) by a
  tiny alignment parameter in Z2×Z3.

Line pair types:
  - orthogonal (uncoupled): cross inner products are all 0 (36/36).
  - coupled-adjacent:       cross ip depends only on diff d=(pa-pb) mod 6, constant on each d.
  - coupled-all-diffs:      cross ip depends only on (d, pa mod 3), with only 6 possible
                            patterns across all 219 such pairs; these patterns are exactly
                            Z2×Z3 transforms of a universal base table.

Outputs:
  - artifacts/w33_line_pair_ip_model.json
  - artifacts/w33_line_pair_ip_model.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
IN_LINES = ROOT / "artifacts" / "w33_line_fusion_law.json"
IN_PHASE_FUSION = ROOT / "artifacts" / "w33_line_pair_phase_fusion_patterns.json"

OUT_JSON = ROOT / "artifacts" / "w33_line_pair_ip_model.json"
OUT_MD = ROOT / "artifacts" / "w33_line_pair_ip_model.md"


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _cartan_unit_e8_sage_order() -> np.ndarray:
    return np.array(
        [
            [2, 0, -1, 0, 0, 0, 0, 0],
            [0, 2, 0, -1, 0, 0, 0, 0],
            [-1, 0, 2, -1, 0, 0, 0, 0],
            [0, -1, -1, 2, -1, 0, 0, 0],
            [0, 0, 0, -1, 2, -1, 0, 0],
            [0, 0, 0, 0, -1, 2, -1, 0],
            [0, 0, 0, 0, 0, -1, 2, -1],
            [0, 0, 0, 0, 0, 0, -1, 2],
        ],
        dtype=int,
    )


def _ip_orbit_coeffs(a: Tuple[int, ...], b: Tuple[int, ...], C: np.ndarray) -> int:
    return int(sum(a[i] * int(C[i, j]) * b[j] for i in range(8) for j in range(8)))


def _base_ip_all_diffs(d: int, r: int) -> int:
    """
    Universal base table (most common pattern), expressed formulaically.

    Inputs:
      d = (pa - pb) mod 6
      r = pa mod 3

    Output:
      inner product ∈ {-1,0,1} for the 'all-diffs' coupled pairs, in the base alignment.
    """
    t = (d // 2) % 3
    parity = d % 2
    base_even = [1, 0, -1]
    base_odd = [0, 1, -1]
    base = base_even if parity == 0 else base_odd
    return int(base[(r - t) % 3])


def _solve_alignment_all_diffs(table: List[int]) -> Tuple[int, int]:
    """
    Given a 6×3 table flattened row-major (d=0..5, r=0..2),
    find (row_shift, col_shift) in {0,1}×Z3 such that:

      table[d,r] == base_ip(d+row_shift, r+col_shift)
    """
    for row_shift in (0, 1):
        for col_shift in (0, 1, 2):
            ok = True
            for d in range(6):
                for r in range(3):
                    want = _base_ip_all_diffs((d + row_shift) % 6, (r + col_shift) % 3)
                    got = table[3 * d + r]
                    if got != want:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return row_shift, col_shift
    raise RuntimeError("No alignment in Z2×Z3 matched (unexpected)")


def main() -> None:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta.get("rows")
    if not isinstance(rows, list) or len(rows) != 240:
        raise RuntimeError("Invalid e8_root_metadata_table.json: rows")

    edge_to_root: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    edge_to_phase: Dict[Tuple[int, int], int] = {}
    for row in rows:
        e = tuple(sorted((int(row["edge"][0]), int(row["edge"][1]))))
        edge_to_root[e] = tuple(int(x) for x in row["root_orbit"])
        edge_to_phase[e] = int(row["phase_z6"])

    lines = json.loads(IN_LINES.read_text(encoding="utf-8"))
    per_line = lines.get("per_line")
    fusion_pairs = lines.get("fusion_law", {}).get("pairs")
    if not isinstance(per_line, list) or len(per_line) != 40:
        raise RuntimeError("Invalid w33_line_fusion_law.json: per_line")
    if not isinstance(fusion_pairs, dict):
        raise RuntimeError("Invalid w33_line_fusion_law.json: fusion_law.pairs")

    line_vertices: List[Tuple[int, int, int, int]] = [
        tuple(int(x) for x in e["line"]) for e in per_line
    ]

    # Line -> phase->root mapping (bijection on Z6).
    line_phase_to_root: List[Dict[int, Tuple[int, ...]]] = []
    for L in line_vertices:
        m: Dict[int, Tuple[int, ...]] = {}
        for u, v in combinations(L, 2):
            e = (min(u, v), max(u, v))
            p = edge_to_phase[e]
            r = edge_to_root[e]
            m[p] = r
        if set(m.keys()) != set(range(6)):
            raise RuntimeError("Line does not realize all phases")
        line_phase_to_root.append(m)

    # Coupled-pair diff patterns (tells us which are all-diffs vs adjacent).
    pf = json.loads(IN_PHASE_FUSION.read_text(encoding="utf-8"))
    pf_pairs = pf.get("pair_summaries")
    if not isinstance(pf_pairs, dict):
        raise RuntimeError(
            "Invalid w33_line_pair_phase_fusion_patterns.json: pair_summaries"
        )

    C8 = _cartan_unit_e8_sage_order()

    # Build model entries for all 40 choose 2 line pairs.
    model: Dict[str, Dict[str, object]] = {}
    type_counts: Counter[str] = Counter()
    alignment_counts: Counter[Tuple[int, int]] = Counter()

    total_pair_checks = 0
    total_pair_mismatches = 0

    for i in range(40):
        for j in range(i + 1, 40):
            key = f"{i},{j}"
            A = line_phase_to_root[i]
            B = line_phase_to_root[j]

            # Actual ip table for all 36 phase pairs.
            actual: Dict[Tuple[int, int], int] = {}
            for pa in range(6):
                for pb in range(6):
                    actual[(pa, pb)] = _ip_orbit_coeffs(A[pa], B[pb], C8)

            if key not in fusion_pairs:
                # Uncoupled => all zeros (verified).
                if any(v != 0 for v in actual.values()):
                    total_pair_mismatches += 1
                model[key] = {"i": i, "j": j, "type": "orthogonal"}
                type_counts["orthogonal"] += 1
                total_pair_checks += 1
                continue

            # Coupled: determine whether adjacent or all-diffs from phase-fusion patterns.
            pv = pf_pairs.get(key)
            if pv is None:
                raise RuntimeError(
                    f"Coupled pair {key} missing from phase-fusion patterns"
                )
            diff_counts = pv["diff_counts"]
            if not (isinstance(diff_counts, list) and len(diff_counts) == 6):
                raise RuntimeError("Bad diff_counts in phase-fusion patterns")
            ds6 = [d for d, c in enumerate(diff_counts) if int(c) == 6]

            predicted: Dict[Tuple[int, int], int] = {}

            if tuple(int(x) for x in diff_counts) == (2, 2, 2, 2, 2, 2):
                # all-diffs: ip depends only on (d, pa mod 3) up to a Z2×Z3 alignment.
                table: List[int] = []
                ok = True
                for d in range(6):
                    for r in range(3):
                        vals = set()
                        for pa in range(6):
                            if pa % 3 != r:
                                continue
                            pb = (pa - d) % 6
                            vals.add(actual[(pa, pb)])
                        if len(vals) != 1:
                            ok = False
                            break
                        table.append(int(next(iter(vals))))
                    if not ok:
                        break
                if not ok:
                    raise RuntimeError(
                        "all-diffs pair did not collapse to a (d,pa mod3) table (unexpected)"
                    )

                row_shift, col_shift = _solve_alignment_all_diffs(table)
                alignment_counts[(row_shift, col_shift)] += 1

                for pa in range(6):
                    for pb in range(6):
                        d = (pa - pb) % 6
                        r = pa % 3
                        predicted[(pa, pb)] = _base_ip_all_diffs(
                            (d + row_shift) % 6, (r + col_shift) % 3
                        )

                model[key] = {
                    "i": i,
                    "j": j,
                    "type": "coupled_all_diffs",
                    "alignment": {"row_shift_Z2": row_shift, "col_shift_Z3": col_shift},
                }
                type_counts["coupled_all_diffs"] += 1

            else:
                # adjacent: two diffs occur 6× among the ip=-1 interaction set.
                if len(ds6) != 2:
                    raise RuntimeError(
                        f"Coupled pair {key} is neither all-diffs nor adjacent (unexpected)"
                    )
                ds6 = sorted(ds6)
                d0 = ds6[0]
                d1 = ds6[1]
                if (d1 - d0) % 6 == 1:
                    d_start = d0
                elif (d0 - d1) % 6 == 1:
                    d_start = d1
                else:
                    raise RuntimeError(
                        f"Expected adjacent diffs; got {ds6} for pair {key}"
                    )

                d_minus = {d_start, (d_start + 1) % 6}
                d_plus = {(d_start + 3) % 6, (d_start + 4) % 6}

                for pa in range(6):
                    for pb in range(6):
                        d = (pa - pb) % 6
                        if d in d_minus:
                            predicted[(pa, pb)] = -1
                        elif d in d_plus:
                            predicted[(pa, pb)] = 1
                        else:
                            predicted[(pa, pb)] = 0

                model[key] = {
                    "i": i,
                    "j": j,
                    "type": "coupled_adjacent",
                    "d_minus": sorted(d_minus),
                    "d_plus": sorted(d_plus),
                }
                type_counts["coupled_adjacent"] += 1

            # Validate the predicted table vs actual.
            mismatch = sum(
                1 for k2, v2 in predicted.items() if int(v2) != int(actual[k2])
            )
            total_pair_checks += 1
            if mismatch:
                total_pair_mismatches += 1
            model[key]["mismatch_count"] = mismatch

    # Sanity: type counts should sum to 780 line-pairs.
    if sum(type_counts.values()) != 780:
        raise RuntimeError("Type count mismatch")

    out = {
        "inputs": {
            "e8_root_metadata_table": str(IN_META),
            "w33_line_fusion_law": str(IN_LINES),
            "w33_line_pair_phase_fusion_patterns": str(IN_PHASE_FUSION),
        },
        "counts": {
            "line_pairs_total": 780,
            "type_counts": dict(sorted(type_counts.items())),
            "all_diffs_alignment_counts": {
                f"{k[0]},{k[1]}": int(v) for k, v in sorted(alignment_counts.items())
            },
            "pair_tables_checked": total_pair_checks,
            "pairs_with_any_mismatch": total_pair_mismatches,
        },
        "theorem": {
            "discrete_ip_model_matches_all_line_pairs": total_pair_mismatches == 0,
            "all_diffs_alignment_group_is_Z2xZ3": True,
        },
        "model": model,  # 780 entries
    }

    _write_json(OUT_JSON, out)

    md: List[str] = []
    md.append("# W33 Line-Pair Discrete Inner-Product Model")
    md.append("")
    md.append(f"- Line pairs total: **780**")
    md.append(f"- Type counts: `{dict(sorted(type_counts.items()))}`")
    md.append("")
    md.append("## Theorem")
    md.append(
        f"- Discrete model matches all line-pairs: **{total_pair_mismatches == 0}**"
    )
    md.append("")
    md.append("## All-diffs alignment counts (Z2×Z3)")
    md.append(
        f"- `{ {f'{k[0]},{k[1]}': int(v) for k, v in sorted(alignment_counts.items())} }`"
    )
    md.append("")
    md.append(
        "## Base table (for coupled-all-diffs, alignment row_shift=0 col_shift=0)"
    )
    md.append("")
    md.append("Here ip depends on `d=(pa-pb) mod 6` and `r=pa mod 3` via:")
    md.append("")
    for d in range(6):
        row = [_base_ip_all_diffs(d, r) for r in range(3)]
        md.append(f"- d={d}: {row}")
    md.append("")
    md.append(f"_Wrote: `{OUT_JSON}`_")
    md.append(f"_Wrote: `{OUT_MD}`_")
    _write_md(OUT_MD, md)

    print(f"wrote={OUT_JSON}")
    print(f"wrote={OUT_MD}")
    print(f"type_counts={dict(sorted(type_counts.items()))}")
    print(f"pairs_with_any_mismatch={total_pair_mismatches}")


if __name__ == "__main__":
    main()
