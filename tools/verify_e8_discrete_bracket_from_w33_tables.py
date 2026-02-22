#!/usr/bin/env python3
"""
Verify the full root-space E8 bracket can be computed *purely* from W33/clock tables.

Given a root-channel label as (line i, phase p) with i∈{0..39}, p∈Z6, we already have:
  - diff→output-line for coupled pairs
  - affine-dihedral output phase: pc ≡ a*pa + b (mod 6)
  - cocycle sign signatures ε as a Z3-map pa mod3 ↦ {±1} for each (pair,diff)

This script:
  1) Builds the missing within-line signatures for A2 brackets (diff=2,4) per line.
  2) Defines a W33-table bracket on the 240 root-channels:
       [e_α, e_β] = ε(α,β) e_{α+β}   if α+β is a root
                  = 0               otherwise (Cartan case ignored here).
  3) Verifies it matches the cocycle-derived bracket computed directly from root_orbit
     coefficient vectors for *all* ordered pairs (α,β) with α+β a root.

Output:
  - artifacts/verify_e8_discrete_bracket_from_w33_tables.json
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
IN_LINES = ROOT / "artifacts" / "w33_line_fusion_law.json"
IN_DIFF_OUT = ROOT / "artifacts" / "w33_line_pair_phase_fusion_patterns.json"
IN_PHASE_OUT = ROOT / "artifacts" / "w33_line_pair_output_phase_law.json"
IN_SIGNS = ROOT / "artifacts" / "e8_cocycle_signs_on_w33_fusion.json"

OUT_JSON = ROOT / "artifacts" / "verify_e8_discrete_bracket_from_w33_tables.json"
OUT_MD = ROOT / "artifacts" / "verify_e8_discrete_bracket_from_w33_tables.md"


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


def _eps_orbit_coeffs(a: Tuple[int, ...], b: Tuple[int, ...], Cmod2: np.ndarray) -> int:
    parity = 0
    for i in range(8):
        ai = a[i] & 1
        if ai == 0:
            continue
        for j in range(i):
            bj = b[j] & 1
            if bj == 0:
                continue
            if int(Cmod2[i, j]) & 1:
                parity ^= 1
    return -1 if parity else 1


def main() -> None:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta["rows"]
    if len(rows) != 240:
        raise RuntimeError("Expected 240 rows")

    # line mapping
    lines = json.loads(IN_LINES.read_text(encoding="utf-8"))
    per_line = lines["per_line"]
    line_vertices = [tuple(ent["line"]) for ent in per_line]
    edge_to_line: Dict[Tuple[int, int], int] = {}
    for li, L in enumerate(line_vertices):
        for u, v in combinations(L, 2):
            edge_to_line[(min(u, v), max(u, v))] = li

    # root label maps
    label_to_root: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    root_to_label: Dict[Tuple[int, ...], Tuple[int, int]] = {}
    for r in rows:
        edge = tuple(sorted((int(r["edge"][0]), int(r["edge"][1]))))
        li = edge_to_line[edge]
        p = int(r["phase_z6"])
        root = tuple(int(x) for x in r["root_orbit"])
        label_to_root[(li, p)] = root
        root_to_label[root] = (li, p)
    if len(label_to_root) != 240 or len(root_to_label) != 240:
        raise RuntimeError("Label/root map size mismatch")

    # Per coupled pair tables
    diff_out = json.loads(IN_DIFF_OUT.read_text(encoding="utf-8"))["pair_summaries"]
    phase_out = json.loads(IN_PHASE_OUT.read_text(encoding="utf-8"))["pair_summaries"]
    signs = json.loads(IN_SIGNS.read_text(encoding="utf-8"))["per_case"]

    C = _cartan_unit_e8_sage_order()
    Cmod2 = (C % 2).astype(int)

    # Build within-line signatures (line i, diff in {2,4}) -> [s0,s1,s2] by pa mod3.
    within_sig: Dict[Tuple[int, int], List[int]] = {}
    for li in range(40):
        for d in (2, 4):
            by_r: Dict[int, set[int]] = {0: set(), 1: set(), 2: set()}
            for pa in range(6):
                pb = (pa - d) % 6
                a = label_to_root[(li, pa)]
                b = label_to_root[(li, pb)]
                if _ip_orbit_coeffs(a, b, C) != -1:
                    continue
                s = _eps_orbit_coeffs(a, b, Cmod2)
                by_r[pa % 3].add(int(s))
            if any(len(v) != 1 for v in by_r.values()):
                raise RuntimeError(
                    "Within-line signature not deterministic (unexpected)"
                )
            within_sig[(li, d)] = [int(next(iter(by_r[r]))) for r in range(3)]
    within_sig_export = {
        str(li): {"d2": within_sig[(li, 2)], "d4": within_sig[(li, 4)]}
        for li in range(40)
    }

    def bracket_table(
        a_lab: Tuple[int, int], b_lab: Tuple[int, int]
    ) -> Tuple[Tuple[int, int] | None, int]:
        """
        Return (out_label, coeff) for [e_a,e_b] in the root-space bracket, or (None,0) if zero.
        Cartan case (b=-a) is treated as zero here.
        """
        la, pa = a_lab
        lb, pb = b_lab

        if la == lb:
            d = (pa - pb) % 6
            if d not in (2, 4):
                return None, 0
            pc = (pa - 1) % 6 if d == 2 else (pa + 1) % 6
            coeff = within_sig[(la, d)][pa % 3]
            return (la, pc), int(coeff)

        # orient by smaller line index for table lookup
        if la < lb:
            key = f"{la},{lb}"
            d = (pa - pb) % 6
            pa_use = pa
            swap = False
        else:
            key = f"{lb},{la}"
            d = (pb - pa) % 6
            pa_use = pb
            swap = True

        out_line = diff_out[key]["diff_to_output_line"][d]
        if out_line is None:
            return None, 0
        aff = phase_out[key]["diff_to_affine_pc_of_pa_mod6"][str(d)]
        acoef = int(aff["a"])
        bcoef = int(aff["b"])
        pc = (acoef * int(pa_use) + bcoef) % 6

        sig = signs[f"{key}|d={d}"]["sign_map_sig_pa_mod3"]
        coeff = int(sig[int(pa_use) % 3])
        if swap:
            coeff = -coeff
        return (int(out_line), int(pc)), coeff

    # Verify against direct cocycle bracket from root_orbit sums.
    mismatches = 0
    checked = 0
    mismatch_examples: List[Dict[str, object]] = []

    labels = sorted(label_to_root.keys())
    for a_lab in labels:
        a = label_to_root[a_lab]
        for b_lab in labels:
            b = label_to_root[b_lab]
            s = tuple(a[k] + b[k] for k in range(8))
            if s not in root_to_label:
                continue
            if s == (0, 0, 0, 0, 0, 0, 0, 0):
                continue  # Cartan case ignored
            checked += 1
            out_lab, coeff = bracket_table(a_lab, b_lab)
            if out_lab is None:
                mismatches += 1
                if len(mismatch_examples) < 5:
                    mismatch_examples.append(
                        {"a": a_lab, "b": b_lab, "reason": "predicted_zero"}
                    )
                continue
            if out_lab != root_to_label[s]:
                mismatches += 1
                if len(mismatch_examples) < 5:
                    mismatch_examples.append(
                        {
                            "a": a_lab,
                            "b": b_lab,
                            "reason": "wrong_output",
                            "pred": out_lab,
                            "actual": root_to_label[s],
                        }
                    )
                continue
            want = _eps_orbit_coeffs(a, b, Cmod2)
            if int(coeff) != int(want):
                mismatches += 1
                if len(mismatch_examples) < 5:
                    mismatch_examples.append(
                        {
                            "a": a_lab,
                            "b": b_lab,
                            "reason": "wrong_coeff",
                            "pred": coeff,
                            "want": int(want),
                        }
                    )

    out = {
        "status": "ok" if mismatches == 0 else "fail",
        "checked_pairs_with_sum_root": checked,
        "mismatches": mismatches,
        "examples": mismatch_examples,
        "within_line_signatures": within_sig_export,
        "inputs": {
            "root_metadata": str(IN_META),
            "line_fusion_law": str(IN_LINES),
            "pair_phase_fusion_patterns": str(IN_DIFF_OUT),
            "output_phase_law": str(IN_PHASE_OUT),
            "cocycle_sign_signatures": str(IN_SIGNS),
        },
    }
    OUT_JSON.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md_lines: List[str] = []
    md_lines.append("# Verify: E8 bracket from W33 tables")
    md_lines.append("")
    md_lines.append(f"- status: `{out['status']}`")
    md_lines.append(f"- checked pairs with sum a root: **{checked}**")
    md_lines.append(f"- mismatches: **{mismatches}**")
    md_lines.append("")
    md_lines.append("## Statement")
    md_lines.append(
        "- The signed root-space bracket `[e_α,e_β]=ε(α,β)e_{α+β}` is fully determined by:"
    )
    md_lines.append("  - W33 line-pair diff→output-line table")
    md_lines.append("  - affine-dihedral output phase law `pc ≡ a*pa + b (mod 6)`")
    md_lines.append(
        "  - cocycle sign signature per (pair,diff) as a map `pa mod 3 ↦ {±1}`"
    )
    md_lines.append("  - within-line A2 signatures for diffs `2,4` (derived here)")
    md_lines.append("")
    md_lines.append(f"- JSON: `{OUT_JSON}`")
    md_lines.append(f"- Wrote: `{OUT_MD}`")
    OUT_MD.write_text("\n".join(md_lines).rstrip() + "\n", encoding="utf-8")

    print(
        f"status={out['status']} checked={checked} mismatches={mismatches} wrote={OUT_JSON}"
    )
    if out["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
