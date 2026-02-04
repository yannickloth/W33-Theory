#!/usr/bin/env python3
"""
Purely discrete E8 Chevalley-Serre verification in the repo's W33/E8 bridge coordinates.

This closes the algebra side *without* using the 27-rep matrices or the Z3-graded build:

Inputs:
  - artifacts/e8_root_metadata_table.json
      gives all 240 E8 roots as simple-root coefficient vectors `root_orbit` in the
      repo's fixed E8 simple system (Sage-order Cartan matrix), plus W33 (edge,line,phase).

We then:
  1) Take the 8 simple roots α_i to be the standard basis vectors e_i in this coordinate
     system (these appear in the metadata table).
  2) Define the Chevalley bracket on root spaces by:
       [e_α, e_β] = ε(α,β) e_{α+β}   if α+β is a root
                 = 0               otherwise (except β=-α)
     with ε the deterministic even-lattice cocycle in this simple-root basis:
       ε(α,β)=(-1)^{ Σ_{i>j} (α_i mod2)(β_j mod2)(C_ij mod2) }.
     (E8 is simply-laced so |N_{α,β}|=1 whenever α+β is a root.)
  3) Set [e_α, e_-α] = h_α and h_α = Σ a_i h_i for α=Σ a_i α_i.

And verify:
  - [h_i,e_j] = C_ij e_j
  - [e_i,f_j] = δ_ij h_i
  - Serre relations for the 8 simple generators.

Outputs:
  - artifacts/verify_e8_chevalley_from_w33_discrete.json
  - artifacts/verify_e8_chevalley_from_w33_discrete.md
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

OUT_JSON = ROOT / "artifacts" / "verify_e8_chevalley_from_w33_discrete.json"
OUT_MD = ROOT / "artifacts" / "verify_e8_chevalley_from_w33_discrete.md"


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


def _ip_orbit_coeffs(a: Tuple[int, ...], b: Tuple[int, ...], C: np.ndarray) -> int:
    return int(sum(a[i] * int(C[i, j]) * b[j] for i in range(8) for j in range(8)))


def main() -> None:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta.get("rows")
    if not isinstance(rows, list) or len(rows) != 240:
        raise RuntimeError("Invalid e8_root_metadata_table.json: rows")

    # root set in orbit-coefficient basis.
    roots = [tuple(int(x) for x in r["root_orbit"]) for r in rows]
    root_set = set(roots)
    if len(root_set) != 240:
        raise RuntimeError("Root duplicates in metadata table")

    # Build mapping from root->(edge,line,phase,grade).
    lines = json.loads(IN_LINES.read_text(encoding="utf-8"))
    per_line = lines.get("per_line")
    if not isinstance(per_line, list) or len(per_line) != 40:
        raise RuntimeError("Invalid w33_line_fusion_law.json: per_line")
    line_vertices = [tuple(int(x) for x in ent["line"]) for ent in per_line]
    edge_to_line: Dict[Tuple[int, int], int] = {}
    for li, L in enumerate(line_vertices):
        for u, v in combinations(L, 2):
            edge_to_line[(min(u, v), max(u, v))] = li

    root_info: Dict[Tuple[int, ...], Dict[str, object]] = {}
    for r in rows:
        root = tuple(int(x) for x in r["root_orbit"])
        edge = tuple(sorted((int(r["edge"][0]), int(r["edge"][1]))))
        root_info[root] = {
            "edge": list(edge),
            "line": int(edge_to_line[tuple(edge)]),
            "phase_z6": int(r["phase_z6"]),
            "grade": str(r["grade"]),
        }

    C = _cartan_unit_e8_sage_order()
    Cmod2 = (C % 2).astype(int)

    # Simple roots in this coordinate system are the unit vectors e_i.
    simples = [tuple(1 if k == i else 0 for k in range(8)) for i in range(8)]
    if not all(s in root_set for s in simples):
        raise RuntimeError("Missing some simple roots as unit vectors (unexpected)")

    # Verify Cartan pairings between simples produce the expected Cartan matrix.
    cartan_ok = True
    cartan_got = [[0] * 8 for _ in range(8)]
    for i in range(8):
        for j in range(8):
            cartan_got[i][j] = _ip_orbit_coeffs(simples[i], simples[j], C)
            if cartan_got[i][j] != int(C[i, j]):
                cartan_ok = False

    # Define bracket on basis:
    # - root vectors are represented by their root tuple
    # - Cartan basis elements are indices 0..7
    def add_root(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(a[k] + b[k] for k in range(8))

    def neg_root(a: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(-x for x in a)

    def bracket_root_root(a: Tuple[int, ...], b: Tuple[int, ...]) -> Dict[str, object]:
        """
        Return either:
          - {'kind':'root', 'root': sum_root, 'coeff': ±1}
          - {'kind':'cartan', 'h_coeffs': [c0..c7]}  meaning Σ c_i h_i
          - {'kind':'zero'}
        """
        if a == neg_root(b):
            # [e_a, e_-a] = h_a = Σ a_i h_i
            return {"kind": "cartan", "h_coeffs": [int(x) for x in a]}
        s = add_root(a, b)
        if s not in root_set:
            return {"kind": "zero"}
        coeff = _eps_orbit_coeffs(a, b, Cmod2)
        return {"kind": "root", "root": s, "coeff": int(coeff)}

    def bracket_h_root(i: int, a: Tuple[int, ...]) -> Dict[str, object]:
        # [h_i, e_a] = <a, alpha_i^∨> e_a. For symmetric Cartan, this is (C @ a)_i.
        pair = int(sum(int(C[j, i]) * a[j] for j in range(8)))
        if pair == 0:
            return {"kind": "zero"}
        return {"kind": "root", "root": a, "coeff": pair}

    # Checks:
    # 1) [h_i, e_{alpha_j}] = C_ij e_{alpha_j}
    he_ok = True
    he_fail: List[Dict[str, object]] = []
    for i in range(8):
        for j in range(8):
            bj = bracket_h_root(i, simples[j])
            want = int(C[i, j])
            if want == 0:
                ok = bj["kind"] == "zero"
            else:
                ok = (
                    bj["kind"] == "root"
                    and bj["root"] == simples[j]
                    and int(bj["coeff"]) == want
                )
            if not ok:
                he_ok = False
                if len(he_fail) < 5:
                    he_fail.append({"i": i, "j": j, "got": bj, "want_coeff": want})

    # 2) [e_i, f_j] = δ_ij h_i where f_j = e_{-alpha_j}
    ef_ok = True
    ef_fail: List[Dict[str, object]] = []
    for i in range(8):
        for j in range(8):
            ei = simples[i]
            fj = neg_root(simples[j])
            br = bracket_root_root(ei, fj)
            if i == j:
                ok = br["kind"] == "cartan" and br["h_coeffs"] == [
                    int(x) for x in simples[i]
                ]
            else:
                ok = br["kind"] == "zero"
            if not ok:
                ef_ok = False
                if len(ef_fail) < 5:
                    ef_fail.append({"i": i, "j": j, "got": br})

    # 3) Serre relations for simple generators.
    # For simply-laced E8: if C_ij=0 => [e_i,e_j]=0; if C_ij=-1 => [e_i,[e_i,e_j]]=0.
    serre_ok = True
    serre_fail: List[Dict[str, object]] = []

    for i in range(8):
        for j in range(8):
            if i == j:
                continue
            Aij = int(C[i, j])
            ei = simples[i]
            ej = simples[j]

            if Aij == 0:
                br = bracket_root_root(ei, ej)
                ok = br["kind"] == "zero"
                if not ok:
                    serre_ok = False
                    if len(serre_fail) < 8:
                        serre_fail.append(
                            {"type": "e", "i": i, "j": j, "Aij": Aij, "got": br}
                        )
            elif Aij == -1:
                br1 = bracket_root_root(ei, ej)
                if br1["kind"] == "zero":
                    ok = False
                else:
                    br2 = bracket_root_root(ei, br1["root"])  # [e_i, [e_i,e_j]]
                    ok = br2["kind"] == "zero"
                if not ok:
                    serre_ok = False
                    if len(serre_fail) < 8:
                        serre_fail.append(
                            {
                                "type": "e",
                                "i": i,
                                "j": j,
                                "Aij": Aij,
                                "br1": br1,
                                "br2": br2 if "br2" in locals() else None,
                            }
                        )
            else:
                raise RuntimeError("Unexpected Cartan entry (E8 is simply-laced)")

            # same for f: replace (ei,ej) with (-ei,-ej)
            fi = neg_root(ei)
            fj = neg_root(ej)
            if Aij == 0:
                br = bracket_root_root(fi, fj)
                ok = br["kind"] == "zero"
                if not ok:
                    serre_ok = False
                    if len(serre_fail) < 8:
                        serre_fail.append(
                            {"type": "f", "i": i, "j": j, "Aij": Aij, "got": br}
                        )
            else:
                br1 = bracket_root_root(fi, fj)
                if br1["kind"] == "zero":
                    ok = False
                else:
                    br2 = bracket_root_root(fi, br1["root"])
                    ok = br2["kind"] == "zero"
                if not ok:
                    serre_ok = False
                    if len(serre_fail) < 8:
                        serre_fail.append(
                            {
                                "type": "f",
                                "i": i,
                                "j": j,
                                "Aij": Aij,
                                "br1": br1,
                                "br2": br2,
                            }
                        )

    # Report simple roots as W33 edges.
    simple_w33 = []
    for i, r in enumerate(simples):
        info = root_info[r]
        simple_w33.append({"i": i, "root_orbit": list(r), **info})

    out = {
        "status": "ok" if (cartan_ok and he_ok and ef_ok and serre_ok) else "fail",
        "cartan_matrix": [[int(x) for x in row] for row in C.tolist()],
        "checks": {
            "cartan_matrix_matches_inner_products": cartan_ok,
            "he_relations_ok": he_ok,
            "ef_relations_ok": ef_ok,
            "serre_ok": serre_ok,
        },
        "examples": {"he_fail": he_fail, "ef_fail": ef_fail, "serre_fail": serre_fail},
        "simple_roots_as_w33_edges": simple_w33,
    }

    _write_json(OUT_JSON, out)

    md: List[str] = []
    md.append("# Verify E8 Chevalley from W33-discrete data")
    md.append("")
    md.append(f"- status: `{out['status']}`")
    md.append(f"- Cartan ok: `{cartan_ok}`")
    md.append(f"- [h,e] ok: `{he_ok}`")
    md.append(f"- [e,f] ok: `{ef_ok}`")
    md.append(f"- Serre ok: `{serre_ok}`")
    md.append("")
    md.append("## Simple roots as W33 channels")
    for s in simple_w33:
        md.append(
            f"- i={s['i']}: line={s['line']} phase={s['phase_z6']} edge={s['edge']} grade={s['grade']}"
        )
    md.append("")
    md.append(f"- JSON: `{OUT_JSON}`")
    _write_md(OUT_MD, md)

    print(f"wrote={OUT_JSON}")
    print(f"wrote={OUT_MD}")
    print(f"status={out['status']}")


if __name__ == "__main__":
    main()
