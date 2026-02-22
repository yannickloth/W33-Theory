#!/usr/bin/env sage
"""
Sage cross-check: signed E8 root-space bracket from W33 tables.

Goal
----
Verify that the *full* signed root-space bracket can be computed purely from:
  - W33 line-pair diff→output-line table
  - affine-dihedral output phase law pc ≡ a*pa + b (mod 6)
  - cocycle sign signatures per (pair,diff) as a map pa mod 3 ↦ {±1}
  - within-line A2 signatures for diffs 2 and 4 (derived here)

and that this matches the standard cocycle bracket computed directly from the
E8 Cartan matrix on the 240 roots (given as simple-root coefficient vectors).

Inputs
------
  - artifacts/e8_root_metadata_table.json
  - artifacts/w33_line_fusion_law.json
  - artifacts/w33_line_pair_phase_fusion_patterns.json
  - artifacts/w33_line_pair_output_phase_law.json
  - artifacts/e8_cocycle_signs_on_w33_fusion.json

Outputs
-------
  - artifacts/sage_verify_e8_discrete_bracket_from_w33_tables.json
  - artifacts/sage_verify_e8_discrete_bracket_from_w33_tables.md
"""

from sage.all import *  # noqa: F401,F403
import json
import os
from datetime import datetime
from itertools import combinations

IN_META = "artifacts/e8_root_metadata_table.json"
IN_LINES = "artifacts/w33_line_fusion_law.json"
IN_DIFF_OUT = "artifacts/w33_line_pair_phase_fusion_patterns.json"
IN_PHASE_OUT = "artifacts/w33_line_pair_output_phase_law.json"
IN_SIGNS = "artifacts/e8_cocycle_signs_on_w33_fusion.json"

OUT_JSON = "artifacts/sage_verify_e8_discrete_bracket_from_w33_tables.json"
OUT_MD = "artifacts/sage_verify_e8_discrete_bracket_from_w33_tables.md"


def load_meta():
    obj = json.load(open(IN_META, "r"))
    edge_to_root = {}
    edge_to_phase = {}
    root_to_edge = {}
    for row in obj["rows"]:
        u, v = row["edge"]
        e = (min(u, v), max(u, v))
        r = tuple(int(x) for x in row["root_orbit"])
        p = int(row["phase_z6"])
        edge_to_root[e] = r
        edge_to_phase[e] = p
        root_to_edge[r] = e
    if len(edge_to_root) != 240 or len(root_to_edge) != 240:
        raise RuntimeError("expected 240 roots/edges")
    return edge_to_root, edge_to_phase, root_to_edge


def load_lines():
    obj = json.load(open(IN_LINES, "r"))
    per_line = obj["per_line"]
    if len(per_line) != 40:
        raise RuntimeError("expected 40 lines")
    return [tuple(int(x) for x in ent["line"]) for ent in per_line]


def cartan_e8():
    E8 = RootSystem(["E", 8])
    return matrix(ZZ, E8.cartan_type().cartan_matrix())


def ip(a, b, C):
    return int(vector(ZZ, a) * C * vector(ZZ, b))


def eps_orbit_coeffs(a, b, Cmod2):
    # deterministic even-lattice cocycle in the simple-root coeff basis
    parity = 0
    for i in range(8):
        if (a[i] & 1) == 0:
            continue
        for j in range(i):
            if (b[j] & 1) == 0:
                continue
            if int(Cmod2[i, j]) & 1:
                parity = 1 - parity
    return -1 if parity else 1


def main():
    edge_to_root, edge_to_phase, root_to_edge = load_meta()
    line_vertices = load_lines()

    # Edge -> line idx.
    edge_to_line = {}
    for li, L in enumerate(line_vertices):
        for u, v in combinations(L, 2):
            edge_to_line[(min(u, v), max(u, v))] = li
    if len(edge_to_line) != 240:
        raise RuntimeError("expected 240 edges in edge_to_line")

    # label <-> root maps, where label = (line, phase)
    label_to_root = {}
    root_to_label = {}
    for e, r in edge_to_root.items():
        li = edge_to_line[e]
        p = edge_to_phase[e]
        label_to_root[(li, p)] = r
        root_to_label[r] = (li, p)
    if len(label_to_root) != 240:
        raise RuntimeError("expected 240 (line,phase) labels")

    diff_out = json.load(open(IN_DIFF_OUT, "r"))["pair_summaries"]
    phase_out = json.load(open(IN_PHASE_OUT, "r"))["pair_summaries"]
    signs = json.load(open(IN_SIGNS, "r"))["per_case"]

    C = cartan_e8()
    Cmod2 = C % 2

    # within-line signatures: (line i, diff in {2,4}) -> [s0,s1,s2] by pa mod3
    within_sig = {}
    for li in range(40):
        for d in (2, 4):
            by_r = {0: set(), 1: set(), 2: set()}
            for pa in range(6):
                pb = (pa - d) % 6
                a = label_to_root[(li, pa)]
                b = label_to_root[(li, pb)]
                if ip(a, b, C) != -1:
                    continue
                s = eps_orbit_coeffs(a, b, Cmod2)
                by_r[pa % 3].add(int(s))
            if any(len(v) != 1 for v in by_r.values()):
                raise RuntimeError("within-line signature not deterministic")
            within_sig[(li, d)] = [int(next(iter(by_r[r]))) for r in range(3)]

    def bracket_table(a_lab, b_lab):
        la, pa = a_lab
        lb, pb = b_lab

        if la == lb:
            d = (pa - pb) % 6
            if d not in (2, 4):
                return None, 0
            pc = (pa - 1) % 6 if d == 2 else (pa + 1) % 6
            coeff = within_sig[(la, d)][pa % 3]
            return (la, pc), int(coeff)

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
        law = phase_out[key]["diff_to_affine_pc_of_pa_mod6"][str(d)]
        acoef = int(law["a"])
        bcoef = int(law["b"])
        pc = int((acoef * pa_use + bcoef) % 6)

        sig = signs[f"{key}|d={d}"]["sign_map_sig_pa_mod3"]
        coeff = int(sig[int(pa_use) % 3])
        if swap:
            coeff = -coeff
        return (int(out_line), int(pc)), int(coeff)

    mismatches = 0
    checked = 0
    examples = []

    labels = sorted(label_to_root.keys())
    for a_lab in labels:
        a = label_to_root[a_lab]
        for b_lab in labels:
            b = label_to_root[b_lab]
            s = tuple(a[k] + b[k] for k in range(8))
            out = root_to_label.get(s)
            if out is None:
                continue
            if s == (0, 0, 0, 0, 0, 0, 0, 0):
                continue
            checked += 1
            pred_out, pred_coeff = bracket_table(a_lab, b_lab)
            if pred_out is None:
                mismatches += 1
                if len(examples) < 5:
                    examples.append({"a": a_lab, "b": b_lab, "reason": "predicted_zero"})
                continue
            if pred_out != out:
                mismatches += 1
                if len(examples) < 5:
                    examples.append({"a": a_lab, "b": b_lab, "reason": "wrong_output", "pred": pred_out, "want": out})
                continue
            want = eps_orbit_coeffs(a, b, Cmod2)
            if int(pred_coeff) != int(want):
                mismatches += 1
                if len(examples) < 5:
                    examples.append({"a": a_lab, "b": b_lab, "reason": "wrong_coeff", "pred": int(pred_coeff), "want": int(want)})

    status = "ok" if mismatches == 0 else "fail"

    report = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "checked_pairs_with_sum_root": checked,
        "mismatches": mismatches,
        "examples": examples,
    }

    def to_py(o):
        if isinstance(o, Integer):
            return int(o)
        if isinstance(o, (list, tuple)):
            return [to_py(x) for x in o]
        if isinstance(o, dict):
            return {str(k): to_py(v) for k, v in o.items()}
        return o

    os.makedirs("artifacts", exist_ok=True)
    json.dump(to_py(report), open(OUT_JSON, "w"), indent=2, sort_keys=True)

    md = []
    md.append("# Sage verify: E8 bracket from W33 tables")
    md.append("")
    md.append(f"- status: `{status}`")
    md.append(f"- checked pairs with sum a root: **{checked}**")
    md.append(f"- mismatches: **{mismatches}**")
    md.append("")
    md.append(f"_Wrote: `{OUT_JSON}`_")
    md.append(f"_Wrote: `{OUT_MD}`_")
    open(OUT_MD, "w").write("\n".join(md).rstrip() + "\n")

    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
