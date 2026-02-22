#!/usr/bin/env python3
"""
Verify a fully discrete E8 root-channel engine in (W33 line, Z6 phase) coordinates.

Inputs (all produced inside this repo):
  - artifacts/e8_root_metadata_table.json
      provides the rigid bijection: 240 roots <-> 240 W33 edges, with phase_z6 labels.
  - artifacts/w33_line_fusion_law.json
      canonical numbering of the 40 W33 lines (K4 cliques).
  - artifacts/w33_line_pair_ip_model.json
      *discrete* inner product model between any two lines (orthogonal / adjacent / all-diffs),
      including the tiny Z2×Z3 alignment parameter for the generic coupled pairs.
  - artifacts/w33_line_pair_phase_fusion_patterns.json
      diff -> output line determinism for coupled pairs (this is a data table).
  - artifacts/w33_line_pair_output_phase_law.json
      affine-dihedral output phase law per (pair,diff): pc ≡ a*pa + b (mod 6).

What this script verifies:
  1) The discrete inner-product model reproduces the actual E8 inner product for all
     240×240 root pairs (in the simple-root coefficient basis used in the metadata table).
  2) For every pair with inner product -1, the discrete fusion engine predicts the
     correct sum root (as a (line,phase) label), matching actual root addition.

This is the “compression” milestone: root inner products + root addition close entirely
inside the W33+clock data, without having to look at the 8D Euclidean embedding.
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
IN_IP_MODEL = ROOT / "artifacts" / "w33_line_pair_ip_model.json"
IN_DIFF_OUT = ROOT / "artifacts" / "w33_line_pair_phase_fusion_patterns.json"
IN_PHASE_OUT = ROOT / "artifacts" / "w33_line_pair_output_phase_law.json"


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


def _a2_ip_by_phase_diff(d: int) -> int:
    # Verified per-line (A2 hexagon law).
    return {0: 2, 1: 1, 2: -1, 3: -2, 4: -1, 5: 1}[d % 6]


def _base_ip_all_diffs(d: int, r: int) -> int:
    # Same base formula as tools/derive_w33_line_pair_ip_model.py.
    t = (d // 2) % 3
    parity = d % 2
    base_even = [1, 0, -1]
    base_odd = [0, 1, -1]
    base = base_even if parity == 0 else base_odd
    return int(base[(r - t) % 3])


def main() -> None:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta.get("rows")
    if not isinstance(rows, list) or len(rows) != 240:
        raise RuntimeError("Invalid e8_root_metadata_table.json: rows")

    # root label = (line_index, phase_z6) (240 total).
    # map label -> root_orbit and reverse.
    label_to_root: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    root_to_label: Dict[Tuple[int, ...], Tuple[int, int]] = {}
    edge_to_row: Dict[Tuple[int, int], Dict[str, object]] = {}
    for r in rows:
        e = tuple(sorted((int(r["edge"][0]), int(r["edge"][1]))))
        edge_to_row[e] = r

    lines = json.loads(IN_LINES.read_text(encoding="utf-8"))
    per_line = lines.get("per_line")
    if not isinstance(per_line, list) or len(per_line) != 40:
        raise RuntimeError("Invalid w33_line_fusion_law.json: per_line")
    line_vertices = [tuple(int(x) for x in ent["line"]) for ent in per_line]

    # Edge -> line index.
    edge_to_line: Dict[Tuple[int, int], int] = {}
    for li, L in enumerate(line_vertices):
        for u, v in combinations(L, 2):
            edge_to_line[(min(u, v), max(u, v))] = li

    # Build label<->root bijection.
    for e, r in edge_to_row.items():
        li = edge_to_line[e]
        phase = int(r["phase_z6"])
        root = tuple(int(x) for x in r["root_orbit"])
        lab = (li, phase)
        if lab in label_to_root and label_to_root[lab] != root:
            raise RuntimeError("Label collision (unexpected)")
        label_to_root[lab] = root
        root_to_label[root] = lab
    if len(label_to_root) != 240 or len(root_to_label) != 240:
        raise RuntimeError("Expected 240 labels")

    # Load line-pair ip model.
    ip_model = json.loads(IN_IP_MODEL.read_text(encoding="utf-8"))
    model = ip_model.get("model")
    if not isinstance(model, dict) or len(model) != 780:
        raise RuntimeError("Invalid w33_line_pair_ip_model.json: model")

    # Load diff->out_line mapping and output-phase affine parameters.
    diff_out = json.loads(IN_DIFF_OUT.read_text(encoding="utf-8"))["pair_summaries"]
    phase_out = json.loads(IN_PHASE_OUT.read_text(encoding="utf-8"))["pair_summaries"]

    # Verify full 240×240 inner products via discrete model.
    C8 = _cartan_unit_e8_sage_order()
    labels = sorted(label_to_root.keys())  # 240

    ip_mismatches = 0
    for a in labels:
        for b in labels:
            la, pa = a
            lb, pb = b

            # predicted ip
            if la == lb:
                pred = _a2_ip_by_phase_diff((pa - pb) % 6)
            else:
                key = f"{min(la, lb)},{max(la, lb)}"
                entry = model[key]
                typ = entry["type"]
                if typ == "orthogonal":
                    pred = 0
                elif typ == "coupled_adjacent":
                    d_minus = set(int(x) for x in entry["d_minus"])
                    d_plus = set(int(x) for x in entry["d_plus"])
                    d = (pa - pb) % 6 if la < lb else (pb - pa) % 6
                    if d in d_minus:
                        pred = -1
                    elif d in d_plus:
                        pred = 1
                    else:
                        pred = 0
                elif typ == "coupled_all_diffs":
                    align = entry["alignment"]
                    rs = int(align["row_shift_Z2"])
                    cs = int(align["col_shift_Z3"])
                    d = (pa - pb) % 6 if la < lb else (pb - pa) % 6
                    r = pa % 3 if la < lb else pb % 3
                    pred = _base_ip_all_diffs((d + rs) % 6, (r + cs) % 3)
                else:
                    raise RuntimeError(f"Unknown line-pair type {typ}")

            # actual ip from root coefficients
            ra = label_to_root[a]
            rb = label_to_root[b]
            actual = _ip_orbit_coeffs(ra, rb, C8)
            if pred != actual:
                ip_mismatches += 1
                if ip_mismatches < 5:
                    print("ip mismatch", a, b, "pred", pred, "actual", actual)

    if ip_mismatches != 0:
        raise RuntimeError(f"Discrete ip mismatches: {ip_mismatches}")

    # Verify fusion for all ip=-1 pairs.
    fusion_mismatches = 0
    fusion_checked = 0
    for a in labels:
        for b in labels:
            ra = label_to_root[a]
            rb = label_to_root[b]
            if _ip_orbit_coeffs(ra, rb, C8) != -1:
                continue
            fusion_checked += 1

            la, pa = a
            lb, pb = b
            # Compute predicted sum label.
            if la == lb:
                # Within A2: ip=-1 iff diff is 2 or 4.
                d = (pa - pb) % 6
                if d == 2:
                    pc = (pa - 1) % 6
                elif d == 4:
                    pc = (pa + 1) % 6
                else:
                    raise RuntimeError("Unexpected within-line ip=-1 diff")
                pred_label = (la, pc)
            else:
                key = f"{min(la, lb)},{max(la, lb)}"
                if key not in diff_out or key not in phase_out:
                    raise RuntimeError(f"Missing fusion tables for coupled pair {key}")
                d = (pa - pb) % 6 if la < lb else (pb - pa) % 6

                out_line = diff_out[key]["diff_to_output_line"][d]
                if out_line is None:
                    raise RuntimeError(
                        "ip=-1 but diff_to_output_line is None (unexpected)"
                    )
                aff = phase_out[key]["diff_to_affine_pc_of_pa_mod6"][str(d)]
                acoef = int(aff["a"])
                bcoef = int(aff["b"])
                pa_use = (
                    pa if la < lb else pb
                )  # affine law is in terms of the 'first' line's pa
                pc = (acoef * pa_use + bcoef) % 6
                pred_label = (int(out_line), int(pc))

            # Actual sum root.
            rc = tuple(ra[k] + rb[k] for k in range(8))
            act_label = root_to_label.get(rc)
            if act_label is None:
                raise RuntimeError("ip=-1 but sum is not a root (unexpected)")
            if pred_label != act_label:
                fusion_mismatches += 1
                if fusion_mismatches < 10:
                    print(
                        "fusion mismatch", a, b, "pred", pred_label, "actual", act_label
                    )

    if fusion_mismatches != 0:
        raise RuntimeError(
            f"Discrete fusion mismatches: {fusion_mismatches} / {fusion_checked}"
        )

    print("PASS: discrete inner product matches all 240x240 pairs")
    print(f"PASS: discrete fusion matches all ip=-1 pairs ({fusion_checked})")


if __name__ == "__main__":
    main()
