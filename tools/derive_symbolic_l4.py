#!/usr/bin/env python3
"""Derive a sparse symbolic l4 from rational CE2 local solutions.

- Loads `artifacts/ce2_rational_local_solutions.json` produced by
  `assemble_exact_l4_from_local_ce2.py`.
- Builds the global `alpha_global` by summing local rational alphas.
- Computes `l4(a,b,c,d) = (1/6) * antisym_sum(alpha)` on a small set of
  representative 4-tuples (those involving the failing triples' basis elems).
- Rationalizes all nonzero flattened entries and writes
  `artifacts/l4_symbolic_constants.json` containing sparse mapping.

The output is a compact symbolic description of the thin l4 prototype.
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
OUT = ROOT / "artifacts" / "l4_symbolic_constants.json"
MAX_DEN = 720


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flat_to_E8Z3_numeric(toe, flat_vals: List[float]):
    N = 27 * 27
    e6 = np.array(flat_vals[:N]).reshape((27, 27)).astype(np.complex128)
    off = N
    sl3 = np.array(flat_vals[off : off + 9]).reshape((3, 3)).astype(np.complex128)
    off += 9
    g1 = np.array(flat_vals[off : off + 81]).reshape((27, 3)).astype(np.complex128)
    off += 81
    g2 = np.array(flat_vals[off : off + 81]).reshape((27, 3)).astype(np.complex128)
    return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)


def e8_to_flat(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def fracize_array(arr: np.ndarray) -> List[str]:
    res = []
    for v in arr.flatten():
        if abs(v) < 1e-15:
            res.append("0")
        else:
            fr = Fraction(float(v)).limit_denominator(MAX_DEN)
            res.append(str(fr))
    return res


def main() -> Dict[str, Any]:
    assert IN.exists(), "Run assemble_exact_l4_from_local_ce2.py first"
    raw = json.loads(IN.read_text(encoding="utf-8"))

    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    exh = _load_module(
        ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py", "exh"
    )

    # build local alpha functions (from rational arrays in artifact)
    local_alphas = []
    for k, e in raw.items():
        a = tuple(e["a"])  # (i,j)
        b = tuple(e["b"])
        c = tuple(e["c"])
        U_rats = e.get("U_rats", [])
        V_rats = e.get("V_rats", [])
        U_fracs = [Fraction(s) if s != "0" else None for s in U_rats]
        V_fracs = [Fraction(s) if s != "0" else None for s in V_rats]

        def make_alpha(Uf, Vf, a_ref=a, b_ref=b, c_ref=c):
            def alpha(A, B):
                # compare by basis-element identity
                if np.allclose(A.g1, exh.basis_elem_g1(toe, b_ref).g1) and np.allclose(
                    B.g2, exh.basis_elem_g2(toe, c_ref).g2
                ):
                    return flat_to_E8Z3_numeric(
                        toe, [float(fr) if fr is not None else 0.0 for fr in Uf]
                    )
                if np.allclose(A.g1, exh.basis_elem_g1(toe, a_ref).g1) and np.allclose(
                    B.g2, exh.basis_elem_g2(toe, c_ref).g2
                ):
                    return flat_to_E8Z3_numeric(
                        toe, [float(fr) if fr is not None else 0.0 for fr in Vf]
                    )
                # skew-symmetric matches
                if np.allclose(A.g1, exh.basis_elem_g1(toe, c_ref).g1) and np.allclose(
                    B.g2, exh.basis_elem_g2(toe, b_ref).g2
                ):
                    return flat_to_E8Z3_numeric(
                        toe, [-(float(fr) if fr is not None else 0.0) for fr in Uf]
                    )
                if np.allclose(A.g1, exh.basis_elem_g1(toe, c_ref).g1) and np.allclose(
                    B.g2, exh.basis_elem_g2(toe, a_ref).g2
                ):
                    return flat_to_E8Z3_numeric(
                        toe, [-(float(fr) if fr is not None else 0.0) for fr in Vf]
                    )
                return toe.E8Z3.zero()

            return alpha

        local_alphas.append(make_alpha(U_fracs, V_fracs))

    # assemble global alpha
    def alpha_global(A, B):
        acc = toe.E8Z3.zero()
        for alpha in local_alphas:
            acc = acc + alpha(A, B)
        return acc

    # thin l4 definition (same as attach_l4_from_ce2)
    def l4_fn(a, b, c, d):
        s = toe.E8Z3.zero()
        s = s + alpha_global(a, b)
        s = s + alpha_global(c, d)
        s = s - alpha_global(a, c)
        s = s - alpha_global(b, d)
        s = s + alpha_global(a, d)
        s = s + alpha_global(b, c)
        return s.scale(1.0 / 6.0)

    # compute sparse structure constants on representative 4-tuples
    sparse: Dict[str, List[str]] = {}
    for k, e in raw.items():
        a = tuple(e["a"])  # (i,j)
        b = tuple(e["b"])
        c = tuple(e["c"])
        x = exh.basis_elem_g1(toe, a)
        y = exh.basis_elem_g1(toe, b)
        z = exh.basis_elem_g2(toe, c)

        # compute l4 on (x,y,z,*) for * in {x,y,z}
        for d_elem, d_label in [(x, "x"), (y, "y"), (z, "z")]:
            val = l4_fn(x, y, z, d_elem)
            flat = e8_to_flat(val)
            # skip all-zero results
            if np.allclose(flat, 0.0):
                continue
            key = f"g1:{a[0]}:{a[1]}|g1:{b[0]}:{b[1]}|g2:{c[0]}:{c[1]}|{d_label}"
            sparse[key] = fracize_array(flat)

    OUT.write_text(json.dumps(sparse, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    return sparse


if __name__ == "__main__":
    main()
