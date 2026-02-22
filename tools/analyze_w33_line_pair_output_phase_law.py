#!/usr/bin/env python3
"""
Output-phase law for W33 line fusion (next compression step).

Background (already verified elsewhere in this repo):
  - W33 has 40 lines (K4 cliques). Each line has 6 edges.
  - Each line's 6 edge-channels are exactly an A2 root subsystem, and the global
    Coxeter "clock" provides a phase label k∈Z6 on each edge.
  - For every coupled line pair (i<j), the 12 interactions (α,β) with α·β=-1
    split into two full output lines (two A2 subsystems).
  - Moreover, the choice of output line is determined solely by the phase-difference
      d = (phase(α) - phase(β)) mod 6.

This tool asks the remaining natural question:

  Given an interaction α (phase pa on line i) and β (phase pb on line j) with α·β=-1,
  their output root is γ = α+β. We already know its output line L_out is diff-determined.

  What is the output phase pc = phase(γ)?

Naive attempt: is `pc-pa` constant (mod 6) per output line or per phase-difference?
Answer: not always (fails precisely in the “adjacent-diff” coupled pairs).

Actual closed law (this script proves it from the repo’s fixed bijection):
  For every coupled pair (i,j) and every occurring diff d, the map pa↦pc is always
  *affine dihedral*:

      either  pc ≡  (+1)*pa + b   (mod 6)    [rotation]
      or      pc ≡  (-1)*pa + b   (mod 6)    [reflection]

  with b∈Z6 depending on (i,j,d).  There are no other cases.

Outputs:
  - artifacts/w33_line_pair_output_phase_law.json
  - artifacts/w33_line_pair_output_phase_law.md
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

OUT_JSON = ROOT / "artifacts" / "w33_line_pair_output_phase_law.json"
OUT_MD = ROOT / "artifacts" / "w33_line_pair_output_phase_law.md"


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _cartan_unit_e8_sage_order() -> np.ndarray:
    # Gram in the same simple-root coefficient basis used by root_orbit.
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


def main() -> None:
    if not IN_LINES.exists():
        raise RuntimeError(f"Missing required input: {IN_LINES}")

    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta.get("rows")
    if not isinstance(rows, list) or len(rows) != 240:
        raise RuntimeError("Invalid e8_root_metadata_table.json: rows")

    edge_to_row: Dict[Tuple[int, int], Dict[str, object]] = {}
    root_orbit_to_row: Dict[Tuple[int, ...], Dict[str, object]] = {}
    for row in rows:
        e = tuple(sorted((int(row["edge"][0]), int(row["edge"][1]))))
        r = tuple(int(x) for x in row["root_orbit"])
        edge_to_row[e] = row
        root_orbit_to_row[r] = row
    if len(edge_to_row) != 240 or len(root_orbit_to_row) != 240:
        raise RuntimeError("Expected bijection for edge/root mappings")

    lines = json.loads(IN_LINES.read_text(encoding="utf-8"))
    per_line = lines.get("per_line")
    fusion_pairs = lines.get("fusion_law", {}).get("pairs")
    if not isinstance(per_line, list) or len(per_line) != 40:
        raise RuntimeError("Invalid w33_line_fusion_law.json: per_line")
    if not isinstance(fusion_pairs, dict):
        raise RuntimeError("Invalid w33_line_fusion_law.json: fusion_law.pairs")

    line_vertices: List[Tuple[int, int, int, int]] = []
    for entry in per_line:
        i = int(entry["i"])
        if i != len(line_vertices):
            raise RuntimeError("Unexpected line indexing; expected i=0..39")
        L = tuple(int(x) for x in entry["line"])
        if len(L) != 4:
            raise RuntimeError("Expected 4 points per line")
        line_vertices.append(L)

    # Edge -> line index.
    edge_to_line: Dict[Tuple[int, int], int] = {}
    for li, L in enumerate(line_vertices):
        for u, v in combinations(L, 2):
            e = (min(u, v), max(u, v))
            if e in edge_to_line and edge_to_line[e] != li:
                raise RuntimeError(f"Edge {e} appears in multiple lines")
            edge_to_line[e] = li
    if len(edge_to_line) != 240:
        raise RuntimeError(f"Expected 240 unique edges; got {len(edge_to_line)}")

    # For each line, build phase->root mapping (bijection on Z6).
    line_phase_to_root: List[Dict[int, Tuple[int, ...]]] = []
    for L in line_vertices:
        phase_to_root: Dict[int, Tuple[int, ...]] = {}
        for u, v in combinations(L, 2):
            e = (min(u, v), max(u, v))
            row = edge_to_row[e]
            p = int(row["phase_z6"])
            r = tuple(int(x) for x in row["root_orbit"])
            if p in phase_to_root and phase_to_root[p] != r:
                raise RuntimeError("Phase collision within a line")
            phase_to_root[p] = r
        if set(phase_to_root.keys()) != set(range(6)):
            raise RuntimeError(f"Line {L} does not realize all 6 phases")
        line_phase_to_root.append(phase_to_root)

    C8 = _cartan_unit_e8_sage_order()

    failures: List[Dict[str, object]] = []
    pair_summaries: Dict[str, Dict[str, object]] = {}

    # Global histograms for the affine law.
    affine_hist: Counter[Tuple[int, int, int]] = Counter()  # (diff d, a in {+1,-1}, b)
    affine_hist_by_pattern: Dict[str, Counter[Tuple[int, int, int]]] = defaultdict(
        Counter
    )
    affine_a_counts: Counter[int] = Counter()

    # Diagnostics for the naive hypotheses.
    naive_pc_minus_pa_constant_per_out_line = True
    naive_pc_minus_pa_constant_per_diff = True

    # Reconstruct diff_counts as we go so we can partition patterns.
    def pattern_name(diff_counts: List[int]) -> str:
        patt = tuple(diff_counts)
        if patt == (2, 2, 2, 2, 2, 2):
            return "all_diffs"
        ds = [d for d, c in enumerate(diff_counts) if c == 6]
        if len(ds) == 2:
            return f"adjacent_{tuple(ds)}"
        return f"other_{patt}"

    for key, outs_raw in fusion_pairs.items():
        i, j = (int(x) for x in str(key).split(","))
        outs = sorted(int(x) for x in outs_raw)
        if len(outs) != 2:
            raise RuntimeError(f"Expected 2 outputs for pair {key}; got {outs}")
        out0, out1 = outs

        A = line_phase_to_root[i]
        B = line_phase_to_root[j]

        # For each diff, collect (pa,pc) and output-line (should be unique per diff).
        pairs_by_diff: Dict[int, List[Tuple[int, int]]] = {d: [] for d in range(6)}
        out_by_diff: Dict[int, set[int]] = {d: set() for d in range(6)}
        diff_counts = [0] * 6

        interaction_count = 0
        for pa in range(6):
            ra = A[pa]
            for pb in range(6):
                rb = B[pb]
                if _ip_orbit_coeffs(ra, rb, C8) != -1:
                    continue
                interaction_count += 1
                d = (pa - pb) % 6
                diff_counts[d] += 1

                rc = tuple(ra[k] + rb[k] for k in range(8))
                row_out = root_orbit_to_row.get(rc)
                if row_out is None:
                    failures.append(
                        {
                            "pair": key,
                            "reason": "missing_sum_root",
                            "pa": pa,
                            "pb": pb,
                            "diff": d,
                        }
                    )
                    continue

                e_out = tuple(
                    sorted((int(row_out["edge"][0]), int(row_out["edge"][1])))
                )
                out_line = edge_to_line.get(e_out)
                if out_line is None:
                    failures.append(
                        {
                            "pair": key,
                            "reason": "missing_output_edge_line",
                            "edge": list(e_out),
                        }
                    )
                    continue
                if out_line not in (out0, out1):
                    failures.append(
                        {
                            "pair": key,
                            "reason": "output_line_not_expected",
                            "got": out_line,
                            "expected": outs,
                        }
                    )
                    continue

                pc = int(row_out["phase_z6"])
                pairs_by_diff[d].append((pa, pc))
                out_by_diff[d].add(out_line)

        if interaction_count != 12:
            failures.append(
                {
                    "pair": key,
                    "reason": "bad_interaction_count",
                    "got": interaction_count,
                }
            )

        # Determine affine law per occurring diff and check naive hypotheses.
        diff_affine: Dict[int, Dict[str, int]] = {}
        pc_minus_pa_shift_sets_by_out: Dict[int, set[int]] = {out0: set(), out1: set()}
        pc_minus_pa_shift_sets_by_diff: Dict[int, set[int]] = {}
        patt_name = pattern_name(diff_counts)
        for d in range(6):
            if diff_counts[d] == 0:
                continue
            lst = pairs_by_diff[d]
            if len(lst) != diff_counts[d]:
                raise RuntimeError("Internal mismatch: pairs_by_diff count")
            shifts = {(pc - pa) % 6 for pa, pc in lst}
            sums = {(pc + pa) % 6 for pa, pc in lst}
            if len(shifts) == 1:
                a = 1
                b = int(next(iter(shifts)))
            elif len(sums) == 1:
                a = -1
                b = int(next(iter(sums)))
            else:
                failures.append(
                    {
                        "pair": key,
                        "reason": "non_affine_phase_map",
                        "diff": d,
                        "count": len(lst),
                        "shift_set": sorted(shifts),
                        "sum_set": sorted(sums),
                    }
                )
                continue
            diff_affine[d] = {"a": a, "b": b}
            affine_hist[(d, a, b)] += 1
            affine_hist_by_pattern[patt_name][(d, a, b)] += 1
            affine_a_counts[a] += 1

            # For naive diagnostics:
            pc_minus_pa_shift_sets_by_diff[d] = shifts
            # Aggregate by output line as well.
            for pa, pc in lst:
                # For this diff, output-line should be unique (checked below).
                out_line = (
                    next(iter(out_by_diff[d])) if len(out_by_diff[d]) == 1 else None
                )
                if out_line in pc_minus_pa_shift_sets_by_out:
                    pc_minus_pa_shift_sets_by_out[out_line].add((pc - pa) % 6)

        # Also record the (diff -> out_line) parity subset for all-diff patterns.
        diff_to_out_list: List[int | None] = [None] * 6
        for d in range(6):
            if diff_counts[d] == 0:
                continue
            if len(out_by_diff[d]) != 1:
                failures.append(
                    {
                        "pair": key,
                        "reason": "nonunique_output_line_for_diff",
                        "diff": d,
                        "out_lines": sorted(out_by_diff[d]),
                    }
                )
                continue
                diff_to_out_list[d] = next(iter(out_by_diff[d]))

        # Naive checks for this pair:
        # - per diff: shift-set size must be 1
        # - per output line: union over diffs landing in that out-line must have shift-set size 1
        if any(
            len(pc_minus_pa_shift_sets_by_diff[d]) != 1
            for d in pc_minus_pa_shift_sets_by_diff
        ):
            naive_pc_minus_pa_constant_per_diff = False
        if any(len(sset) != 1 for sset in pc_minus_pa_shift_sets_by_out.values()):
            naive_pc_minus_pa_constant_per_out_line = False

        pair_summaries[str(key)] = {
            "i": i,
            "j": j,
            "outputs": outs,
            "diff_counts": diff_counts,
            "diff_to_output_line": diff_to_out_list,
            "diff_to_affine_pc_of_pa_mod6": {
                str(d): diff_affine[d] for d in sorted(diff_affine)
            },
            "pattern": patt_name,
        }

    # Compact top-level summary (affine law).
    affine_top = affine_hist.most_common(15)
    affine_by_pattern_top = {
        k: v.most_common(8) for k, v in affine_hist_by_pattern.items()
    }

    out = {
        "inputs": {
            "e8_root_metadata_table": str(IN_META),
            "w33_line_fusion_law": str(IN_LINES),
        },
        "counts": {"coupled_pairs": len(pair_summaries), "failures": len(failures)},
        "theorems": {
            "naive_pc_minus_pa_constant_per_output_line_for_all_pairs": naive_pc_minus_pa_constant_per_out_line,
            "naive_pc_minus_pa_constant_per_diff_for_all_pairs": naive_pc_minus_pa_constant_per_diff,
            "affine_dihedral_law_per_(pair,diff)": len(failures) == 0,
        },
        "histograms": {
            "affine_(diff,a,b)_top15": [
                {"diff": d, "a": a, "b": b, "count": c} for (d, a, b), c in affine_top
            ],
            "affine_a_counts": dict(
                sorted((int(k), int(v)) for k, v in affine_a_counts.items())
            ),
            "affine_by_pattern_top8": {
                k: [{"diff": d, "a": a, "b": b, "count": c} for (d, a, b), c in top]
                for k, top in affine_by_pattern_top.items()
            },
        },
        "failures": failures[:50],
        "pair_summaries": pair_summaries,  # 540 items; JSON is large but manageable
    }

    _write_json(OUT_JSON, out)

    md: List[str] = []
    md.append("# W33 Line-Pair Output Phase Law")
    md.append("")
    md.append(f"- Coupled line pairs: **{len(pair_summaries)}** (expected 540)")
    md.append(f"- Failures recorded: **{len(failures)}**")
    md.append("")
    md.append("## Global theorems checked")
    md.append(
        f"- Naive `pc - pa` constant per output line (all pairs): **{naive_pc_minus_pa_constant_per_out_line}**"
    )
    md.append(
        f"- Naive `pc - pa` constant per diff (all pairs): **{naive_pc_minus_pa_constant_per_diff}**"
    )
    md.append(f"- **Affine dihedral law per (pair,diff)**: **{len(failures)==0}**")
    md.append("")
    md.append("## Most common affine templates")
    md.append("")
    md.append(
        "Each occurring diff `d` yields an affine law `pc ≡ a*pa + b (mod 6)` with `a∈{+1,-1}`."
    )
    md.append("")
    md.append("Top 15 `(d,a,b)` classes:")
    for (d, a, b), c in affine_top:
        md.append(f"- `(d,a,b)=({d},{a},{b})`: **{c}** cases")
    md.append("")
    md.append(
        f"`a`-counts: {dict(sorted((int(k), int(v)) for k, v in affine_a_counts.items()))}"
    )
    md.append("")
    if failures:
        md.append("## Failures (first 10)")
        md.append("")
        for f in failures[:10]:
            md.append(f"- {f}")
        md.append("")
    md.append(f"_Wrote: `{OUT_JSON}`_")
    md.append(f"_Wrote: `{OUT_MD}`_")
    _write_md(OUT_MD, md)

    print(f"wrote={OUT_JSON}")
    print(f"wrote={OUT_MD}")
    print(f"pairs={len(pair_summaries)} failures={len(failures)}")
    print(
        f"naive theorem pc-pa constant per out-line: {naive_pc_minus_pa_constant_per_out_line}"
    )
    print(
        f"naive theorem pc-pa constant per diff: {naive_pc_minus_pa_constant_per_diff}"
    )
    print(f"affine dihedral law per (pair,diff): {len(failures)==0}")


if __name__ == "__main__":
    main()
