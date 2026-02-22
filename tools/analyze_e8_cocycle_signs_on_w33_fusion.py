#!/usr/bin/env python3
"""
Analyze the E8 lattice cocycle signs (Chevalley ε) in W33 line/phase language.

We already have a rigid identification:
  240 E8 roots  <->  240 W33 edges  <->  (W33 line i ∈ {0..39}, phase p ∈ Z6).

We also have rigid "fusion data" for α·β=-1 interactions:
  - output line is determined by diff d=(pa-pb) mod 6 for coupled line pairs.
  - output phase satisfies an affine dihedral law pc ≡ a*pa + b (mod 6), a∈{+1,-1}.

This script adds the missing "sign layer" needed to turn the fusion into a true Lie bracket:
  [e_α, e_β] = ε(α,β) e_{α+β}  when α+β is a root (E8 is simply-laced so |N|=1 here).

We compute ε(α,β) as a deterministic even-lattice cocycle on the E8 root lattice
*in the root_orbit coefficient basis used by artifacts/e8_root_metadata_table.json*:

  ε(α,β) = (-1)^{ Σ_{i>j} (α_i mod2)(β_j mod2)(C_ij mod2) }

where C is the E8 Cartan/Gram matrix in the same ordering as root_orbit.

Key empirical compression (true for this cocycle choice):
  - For every coupled pair (i<j) and every diff d that yields ip=-1 interactions,
    the sign pattern ε as a function of pa is always either:
      * constant, or
      * depends only on pa mod 3 (a Z3 signature).

Outputs:
  - artifacts/e8_cocycle_signs_on_w33_fusion.json
  - artifacts/e8_cocycle_signs_on_w33_fusion.md
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
IN_PHASE_OUT = ROOT / "artifacts" / "w33_line_pair_output_phase_law.json"
IN_IP_MODEL = ROOT / "artifacts" / "w33_line_pair_ip_model.json"

OUT_JSON = ROOT / "artifacts" / "e8_cocycle_signs_on_w33_fusion.json"
OUT_MD = ROOT / "artifacts" / "e8_cocycle_signs_on_w33_fusion.md"


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _cartan_unit_e8_sage_order() -> np.ndarray:
    # Same ordering as used throughout the W33/E8 metadata bridge.
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
    """
    Deterministic lattice cocycle in the simple-root coefficient basis:

      ε(α,β) = (-1)^{ Σ_{i>j} (α_i mod2)(β_j mod2)(C_ij mod2) }.
    """
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
    rows = meta.get("rows")
    if not isinstance(rows, list) or len(rows) != 240:
        raise RuntimeError("Invalid e8_root_metadata_table.json: rows")

    lines = json.loads(IN_LINES.read_text(encoding="utf-8"))
    per_line = lines.get("per_line")
    if not isinstance(per_line, list) or len(per_line) != 40:
        raise RuntimeError("Invalid w33_line_fusion_law.json: per_line")
    line_vertices: List[Tuple[int, int, int, int]] = [
        tuple(int(x) for x in ent["line"]) for ent in per_line
    ]

    # Edge -> line index.
    edge_to_line: Dict[Tuple[int, int], int] = {}
    for li, L in enumerate(line_vertices):
        for u, v in combinations(L, 2):
            edge_to_line[(min(u, v), max(u, v))] = li
    if len(edge_to_line) != 240:
        raise RuntimeError("Expected 240 edges in edge_to_line")

    edge_to_row = {
        tuple(sorted((int(r["edge"][0]), int(r["edge"][1])))): r for r in rows
    }

    # line_phase_to_root_orbit
    line_phase_to_root: List[Dict[int, Tuple[int, ...]]] = []
    for L in line_vertices:
        m: Dict[int, Tuple[int, ...]] = {}
        for u, v in combinations(L, 2):
            e = (min(u, v), max(u, v))
            row = edge_to_row[e]
            p = int(row["phase_z6"])
            r = tuple(int(x) for x in row["root_orbit"])
            m[p] = r
        if set(m.keys()) != set(range(6)):
            raise RuntimeError("Line does not realize all 6 phases")
        line_phase_to_root.append(m)

    # Coupled pair metadata
    pair_phase_fusion = json.loads(IN_PHASE_FUSION.read_text(encoding="utf-8"))[
        "pair_summaries"
    ]
    pair_phase_out = json.loads(IN_PHASE_OUT.read_text(encoding="utf-8"))[
        "pair_summaries"
    ]
    pair_ip_model = json.loads(IN_IP_MODEL.read_text(encoding="utf-8"))["model"]

    C = _cartan_unit_e8_sage_order()
    Cmod2 = (C % 2).astype(int)

    def classify_sign_map(pairs: List[Tuple[int, int]]) -> Dict[str, object]:
        """
        Given a list of (pa, sign) pairs (pa in 0..5), classify whether:
          - sign is constant, or
          - sign depends only on pa mod 3.
        Return a dict with:
          kind: 'constant' or 'mod3'
          signature: tuple(s0,s1,s2) where s_r is sign for pa≡r mod3 (None if never occurs)
        """
        sset = {s for _, s in pairs}
        if len(sset) == 1:
            s = int(next(iter(sset)))
            return {"kind": "constant", "signature": (s, s, s)}
        by_r: Dict[int, set[int]] = defaultdict(set)
        for pa, s in pairs:
            by_r[int(pa % 3)].add(int(s))
        if any(len(v) != 1 for v in by_r.values()):
            return {"kind": "other", "signature": None}
        sig = tuple(int(next(iter(by_r[r]))) if r in by_r else None for r in range(3))
        return {"kind": "mod3", "signature": sig}

    # Build the per-(pair,d) sign dictionaries (1956 entries).
    per_case: Dict[str, Dict[str, object]] = {}

    hist_kind = Counter()
    hist_kind_by_type = defaultdict(Counter)
    hist_sig = Counter()
    hist_sig_by_d = defaultdict(Counter)
    hist_sig_by_a = defaultdict(Counter)

    failures: List[Dict[str, object]] = []

    for key, entry in pair_ip_model.items():
        i = int(entry["i"])
        j = int(entry["j"])
        typ = str(entry["type"])
        if typ == "orthogonal":
            continue
        if key not in pair_phase_fusion or key not in pair_phase_out:
            raise RuntimeError(f"Missing phase-fusion/out data for coupled pair {key}")

        A = line_phase_to_root[i]
        B = line_phase_to_root[j]

        diff_to_out = pair_phase_fusion[key]["diff_to_output_line"]
        aff = (
            pair_phase_out[key]["pair_summaries"][key]["diff_to_affine_pc_of_pa_mod6"]
            if False
            else None
        )  # unreachable
        diff_aff = pair_phase_out[key]["diff_to_affine_pc_of_pa_mod6"]

        for d in range(6):
            # collect ip=-1 interactions at this diff
            pairs: List[Tuple[int, int]] = []
            for pa in range(6):
                pb = (pa - d) % 6
                alpha = A[pa]
                beta = B[pb]
                if _ip_orbit_coeffs(alpha, beta, C) != -1:
                    continue
                s = _eps_orbit_coeffs(alpha, beta, Cmod2)
                pairs.append((pa, int(s)))
            if not pairs:
                continue

            cls = classify_sign_map(pairs)
            if cls["kind"] == "other":
                failures.append(
                    {
                        "pair": key,
                        "diff": d,
                        "reason": "sign_map_not_constant_or_mod3",
                        "pairs": pairs,
                    }
                )
                continue

            sig = tuple(cls["signature"])
            acoef = int(diff_aff[str(d)]["a"])
            bcoef = int(diff_aff[str(d)]["b"])
            out_line = diff_to_out[d]
            case_key = f"{key}|d={d}"
            per_case[case_key] = {
                "pair": key,
                "i": i,
                "j": j,
                "type": typ,
                "diff": d,
                "output_line": out_line,
                "output_phase_affine_pc_of_pa": {"a": acoef, "b": bcoef},
                "sign_map_kind": cls["kind"],
                "sign_map_sig_pa_mod3": list(sig),
                "intersection_size": int(pair_phase_fusion[key]["intersection_size"]),
                "intersection_is_special": pair_phase_fusion[key][
                    "intersection_is_special"
                ],
            }

            hist_kind[cls["kind"]] += 1
            hist_kind_by_type[typ][cls["kind"]] += 1
            hist_sig[sig] += 1
            hist_sig_by_d[d][sig] += 1
            hist_sig_by_a[acoef][sig] += 1

    # Sanity: expect 1956 cases.
    if len(per_case) != 1956:
        raise RuntimeError(f"Expected 1956 (pair,diff) cases; got {len(per_case)}")
    if failures:
        raise RuntimeError(
            f"Unexpected failures in sign-map classification: {failures[:3]}"
        )

    out = {
        "status": "ok",
        "counts": {
            "cases_pair_diff": len(per_case),
            "sign_map_kind": dict(hist_kind),
            "sign_map_kind_by_type": {k: dict(v) for k, v in hist_kind_by_type.items()},
            "unique_sign_signatures_mod3": len(hist_sig),
        },
        "histograms": {
            "top_sign_signatures_mod3": [
                {"sig": list(sig), "count": int(c)}
                for sig, c in hist_sig.most_common(20)
            ],
            "sign_signatures_by_diff_top10": {
                str(d): [
                    {"sig": list(sig), "count": int(c)} for sig, c in ct.most_common(10)
                ]
                for d, ct in hist_sig_by_d.items()
            },
            "sign_signatures_by_output_phase_a": {
                str(a): [
                    {"sig": list(sig), "count": int(c)} for sig, c in ct.most_common(12)
                ]
                for a, ct in hist_sig_by_a.items()
            },
        },
        "per_case": per_case,
    }
    _write_json(OUT_JSON, out)

    md: List[str] = []
    md.append("# E8 cocycle signs on W33 fusion")
    md.append("")
    md.append(f"- cases (pair,diff): **{len(per_case)}** (expected 1956)")
    md.append(f"- sign-map kinds: `{dict(hist_kind)}`")
    md.append(
        f"- by line-pair type: `{ {k: dict(v) for k, v in hist_kind_by_type.items()} }`"
    )
    md.append(f"- unique Z3-signatures: **{len(hist_sig)}**")
    md.append("")
    md.append("## Top Z3 signatures")
    for sig, c in hist_sig.most_common(12):
        md.append(f"- {list(sig)}: **{c}**")
    md.append("")
    md.append("## Notes")
    md.append("- `sig=[s0,s1,s2]` means: for pa≡r (mod 3), ε takes sign `s_r`.")
    md.append("- `sig=[1,1,1]` and `sig=[-1,-1,-1]` are the constant cases.")
    md.append("")
    md.append(f"_Wrote: `{OUT_JSON}`_")
    md.append(f"_Wrote: `{OUT_MD}`_")
    _write_md(OUT_MD, md)

    print(f"wrote={OUT_JSON}")
    print(f"wrote={OUT_MD}")
    print(f"cases={len(per_case)} unique_sigs={len(hist_sig)}")


if __name__ == "__main__":
    main()
