#!/usr/bin/env python3
"""
Build an explicit Chevalley-normalized E6 Lie algebra from the E8 lattice model,
exporting a sparse commutator table on a concrete 78-dimensional basis:

  basis = (H1..H6)  ⊕  (E_α for α in Φ(E6), |Φ|=72)

Construction:
  - Identify the 72 E6 roots as the unique W(E6) orbit of size 72 inside E8 roots.
  - Use the deterministic E8 lattice cocycle ε(α,β) (tools/e8_lattice_cocycle.py).
  - Define Chevalley structure constants by the standard root-string formula:
        [E_α, E_β] = 0                        if α+β not a root and β ≠ -α
                  = N_{α,β} E_{α+β}           if α+β is a root
        [E_α, E_-α] = H_α
    with N_{α,β} = ε(α,β) * (p+1), where p is the maximal integer such that β - pα is a root.
  - Cartan action:
        [H_i, E_α] = <α, α_i> E_α   (simply-laced, coroot = root)

Verification:
  - Computes the E6 Cartan matrix for the simple roots α3..α8 (Bourbaki-in-E8).
  - Checks all Serre relations for the Chevalley generators {e_i,f_i,h_i}.

Writes:
  - artifacts/e6_chevalley_commutator_table.json
  - artifacts/e6_chevalley_commutator_table.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")

IntVec8 = Tuple[int, ...]  # doubled E8 coordinates (length 8)


def k2(r: np.ndarray) -> IntVec8:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def dot_k2(u: IntVec8, v: IntVec8) -> int:
    return sum(int(a) * int(b) for a, b in zip(u, v, strict=True))


def ip_k2(u: IntVec8, v: IntVec8) -> int:
    """
    Inner product in the undoubled normalization (roots have length^2 = 2).

    If u = 2α, v = 2β then (α,β) = <u,v>/4.
    """
    d = dot_k2(u, v)
    if d % 4 != 0:
        raise ValueError("Unexpected non-multiple-of-4 dot product for roots")
    return d // 4


def cheva_abs_N(alpha: IntVec8, beta: IntVec8, root_index: Dict[IntVec8, int]) -> int:
    """
    |N_{α,β}| = p+1 where p is max such that β - pα is a root (root-string length on the -α side).
    """
    p = 0
    while True:
        cand = tuple(beta[i] - (p + 1) * alpha[i] for i in range(8))
        if cand in root_index:
            p += 1
            continue
        break
    return p + 1


def N(alpha: IntVec8, beta: IntVec8, root_index: Dict[IntVec8, int]) -> int:
    s = tuple(alpha[i] + beta[i] for i in range(8))
    if s not in root_index:
        return 0
    eps = int(cocycle.epsilon_e8(alpha, beta))
    return int(eps * cheva_abs_N(alpha, beta, root_index))


def bracket_sparse(
    x: Dict[int, int], y: Dict[int, int], bracket_basis: List[List[Dict[int, int]]]
) -> Dict[int, int]:
    out: Dict[int, int] = {}
    for i, ci in x.items():
        for j, cj in y.items():
            for k, ck in bracket_basis[i][j].items():
                out[k] = out.get(k, 0) + ci * cj * ck
    out = {k: v for k, v in out.items() if v != 0}
    return out


def main() -> None:
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    o72 = next(o for o in orbits if len(o) == 72)
    e6_roots_k2 = [k2(roots[i]) for i in o72]
    e6_root_index = {rk: pos for pos, rk in enumerate(e6_roots_k2)}

    # E6 simple roots are α3..α8 in the Bourbaki E8 basis used throughout this repo.
    e8_basis_cols = tuple(cocycle._e8_simple_root_basis_doubled_columns())  # type: ignore[attr-defined]
    simple_k2 = list(e8_basis_cols[2:8])
    if len(simple_k2) != 6:
        raise RuntimeError("Expected 6 E6 simple roots")

    # Cartan matrix A_ij = <α_i, α_j> for simply-laced.
    cartan = [[ip_k2(simple_k2[i], simple_k2[j]) for j in range(6)] for i in range(6)]

    # Express each E6 root in the α3..α8 basis via the E8 simple-root coordinates.
    e8_solver = cocycle.E8Cocycle.standard()
    root_coeffs_e6: Dict[IntVec8, Tuple[int, ...]] = {}
    for rk in e6_roots_k2:
        coeff8 = e8_solver.coeffs_in_basis(rk)
        if coeff8[0] != 0 or coeff8[1] != 0:
            raise RuntimeError("E6 root had nonzero α1/α2 coefficients (unexpected)")
        root_coeffs_e6[rk] = tuple(int(x) for x in coeff8[2:8])

    # Choose a deterministic basis ordering:
    #   indices 0..5  : H1..H6
    #   indices 6..77 : E_root in lex order of coeffs (unique per root)
    roots_sorted = sorted(e6_roots_k2, key=lambda r: root_coeffs_e6[r])
    root_to_basis = {rk: 6 + i for i, rk in enumerate(roots_sorted)}

    basis = []
    for i in range(6):
        basis.append({"index": i, "type": "cartan", "name": f"H{i+1}"})
    for i, rk in enumerate(roots_sorted):
        coeff = root_coeffs_e6[rk]
        basis.append(
            {
                "index": 6 + i,
                "type": "root",
                "root_k2": list(rk),
                "coeffs_e6": list(coeff),
            }
        )

    # Precompute a bracket table for basis elements (sparse dict outputs).
    n_basis = 78
    bracket_basis: List[List[Dict[int, int]]] = [
        [{} for _ in range(n_basis)] for _ in range(n_basis)
    ]

    # Cartan-Cartan: 0.
    # Cartan-root: [H_i, E_α] = <α, α_i> E_α.
    for i in range(6):
        for rk in roots_sorted:
            j = root_to_basis[rk]
            val = ip_k2(rk, simple_k2[i])
            if val != 0:
                bracket_basis[i][j] = {j: int(val)}
                bracket_basis[j][i] = {j: int(-val)}

    # Root-root brackets.
    for a in roots_sorted:
        ia = root_to_basis[a]
        na = tuple(-x for x in a)
        for b in roots_sorted:
            ib = root_to_basis[b]
            if ia == ib:
                continue
            # Skew-symmetry: fill only i<j and mirror later.
            if ia > ib:
                continue
            if b == na:
                # [E_a, E_-a] = H_a = Σ coeff_i H_i
                coeff = root_coeffs_e6[a]
                term = {i: int(coeff[i]) for i in range(6) if coeff[i] != 0}
                bracket_basis[ia][ib] = term
                bracket_basis[ib][ia] = {k: -v for k, v in term.items()}
                continue

            s = tuple(a[i] + b[i] for i in range(8))
            if s not in e6_root_index:
                continue
            n = N(a, b, e6_root_index)
            if n == 0:
                continue
            isb = root_to_basis[s]
            term = {isb: int(n)}
            bracket_basis[ia][ib] = term
            bracket_basis[ib][ia] = {isb: int(-n)}

    # Export sparse commutator table (only nonzero entries for i<j).
    comm = []
    nonzero = 0
    term_count_hist = Counter()
    for i in range(n_basis):
        for j in range(i + 1, n_basis):
            terms = bracket_basis[i][j]
            if not terms:
                continue
            nonzero += 1
            term_count_hist[len(terms)] += 1
            comm.append(
                {
                    "i": i,
                    "j": j,
                    "terms": [
                        {"k": int(k), "coeff": int(v)} for k, v in sorted(terms.items())
                    ],
                }
            )

    # Serre relations for the simple roots α3..α8: e_i = E_{α_i}, f_i = E_{-α_i}, h_i = H_i.
    e_idx = []
    f_idx = []
    for i in range(6):
        a = simple_k2[i]
        e = root_to_basis.get(a)
        f = root_to_basis.get(tuple(-x for x in a))
        if e is None or f is None:
            raise RuntimeError("Simple root not found among E6 roots (unexpected)")
        e_idx.append(int(e))
        f_idx.append(int(f))

    def elem_basis(k: int) -> Dict[int, int]:
        return {int(k): 1}

    def bracket(x: Dict[int, int], y: Dict[int, int]) -> Dict[int, int]:
        return bracket_sparse(x, y, bracket_basis)

    serre_ok = True
    serre_failures = []
    # [h_i,h_j]=0 and [h_i,e_j]=A_ij e_j and [e_i,f_j]=δ_ij h_i.
    for i in range(6):
        hi = elem_basis(i)
        for j in range(6):
            hj = elem_basis(j)
            if bracket(hi, hj) != {}:
                serre_ok = False
                serre_failures.append({"rel": "[h_i,h_j]=0", "i": i, "j": j})

            ej = elem_basis(e_idx[j])
            want = {} if cartan[i][j] == 0 else {e_idx[j]: int(cartan[i][j])}
            got = bracket(hi, ej)
            if got != want:
                serre_ok = False
                serre_failures.append(
                    {
                        "rel": "[h_i,e_j]=A_ij e_j",
                        "i": i,
                        "j": j,
                        "got": got,
                        "want": want,
                    }
                )

            fj = elem_basis(f_idx[j])
            got2 = bracket(elem_basis(e_idx[i]), fj)
            want2 = {i: 1} if i == j else {}
            if got2 != want2:
                serre_ok = False
                serre_failures.append(
                    {
                        "rel": "[e_i,f_j]=δ_ij h_i",
                        "i": i,
                        "j": j,
                        "got": got2,
                        "want": want2,
                    }
                )

    # (ad e_i)^{1-A_ij} e_j = 0 for i≠j.
    for i in range(6):
        ei = elem_basis(e_idx[i])
        for j in range(6):
            if i == j:
                continue
            ej = elem_basis(e_idx[j])
            aij = int(cartan[i][j])
            if aij not in (0, -1):
                raise RuntimeError(
                    "Unexpected E6 Cartan entry (should be 0 or -1 off-diagonal)"
                )
            k = 1 - aij
            if k == 1:
                if bracket(ei, ej) != {}:
                    serre_ok = False
                    serre_failures.append(
                        {"rel": "[e_i,e_j]=0", "i": i, "j": j, "got": bracket(ei, ej)}
                    )
            elif k == 2:
                tmp = bracket(ei, ej)
                tmp2 = bracket(ei, tmp)
                if tmp2 != {}:
                    serre_ok = False
                    serre_failures.append(
                        {"rel": "ad(e_i)^2 e_j=0", "i": i, "j": j, "got": tmp2}
                    )

    out = {
        "status": "ok" if serre_ok else "failed",
        "dims": {"cartan": 6, "roots": 72, "total": 78},
        "cartan_matrix": cartan,
        "basis": basis,
        "commutators_nonzero": comm,
        "counts": {
            "nonzero_commutators": int(nonzero),
            "term_count_hist": {
                str(k): int(v) for k, v in sorted(term_count_hist.items())
            },
        },
        "serre": {
            "ok": bool(serre_ok),
            "failures": serre_failures[:10],
            "n_failures": len(serre_failures),
        },
        "simple_generators": {
            "h": list(range(6)),
            "e": e_idx,
            "f": f_idx,
        },
    }

    out_json = ROOT / "artifacts" / "e6_chevalley_commutator_table.json"
    out_md = ROOT / "artifacts" / "e6_chevalley_commutator_table.md"
    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    md = []
    md.append("# E6 Chevalley commutator table (from E8 cocycle)\n\n")
    md.append(f"- basis dim: `{out['dims']['total']}` (= 6 Cartan + 72 roots)\n")
    md.append(
        f"- nonzero commutators stored (i<j): `{out['counts']['nonzero_commutators']}`\n"
    )
    md.append(f"- term_count_hist: `{out['counts']['term_count_hist']}`\n")
    md.append(
        f"- Serre relations: `{'PASS' if serre_ok else 'FAIL'}` (failures shown in JSON)\n\n"
    )
    md.append("## Cartan matrix (α3..α8)\n\n")
    for row in cartan:
        md.append(f"- `{row}`\n")
    md.append("\n")
    out_md.write_text("".join(md), encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    if serre_ok:
        print("PASS: Serre relations")
    else:
        print("FAIL: Serre relations (see JSON)")


if __name__ == "__main__":
    main()
