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

    # build index-based lookup maps for numeric U/V from CE2 artifact
    # (avoid O(N^2) `allclose` scans by using stored integer indices)
    U_map: Dict[Tuple[Tuple[int, int], Tuple[int, int]], np.ndarray] = {}
    V_map: Dict[Tuple[Tuple[int, int], Tuple[int, int]], np.ndarray] = {}
    for k, e in raw.items():
        a = tuple(e["a"])  # (i,j)
        b = tuple(e["b"])
        c = tuple(e["c"])
        U_rats = e.get("U_rats", [])
        V_rats = e.get("V_rats", [])
        U_fracs = [Fraction(s) if s != "0" else None for s in U_rats]
        V_fracs = [Fraction(s) if s != "0" else None for s in V_rats]
        U_num = np.array(
            [float(fr) if fr is not None else 0.0 for fr in U_fracs],
            dtype=np.complex128,
        )
        V_num = np.array(
            [float(fr) if fr is not None else 0.0 for fr in V_fracs],
            dtype=np.complex128,
        )
        # accumulate numeric flat arrays keyed by index pairs for O(1) lookup later
        # (multiple local CE2 solutions may share the same (a,c) or (b,c) keys)
        if (b, c) in U_map:
            U_map[(b, c)] = U_map[(b, c)] + U_num
        else:
            U_map[(b, c)] = U_num
        if (a, c) in V_map:
            V_map[(a, c)] = V_map[(a, c)] + V_num
        else:
            V_map[(a, c)] = V_num

    def alpha_global(A, B):
        """Assemble numeric alpha on-the-fly using index lookups (cheap)."""
        acc = toe.E8Z3.zero()
        # only g1 x g2 pairs produce CE2 contributions in our artifact
        if np.any(A.g1) and np.any(B.g2):
            idxA = tuple(np.argwhere(np.abs(A.g1) > 0.5)[0].tolist())
            idxB = tuple(np.argwhere(np.abs(B.g2) > 0.5)[0].tolist())

            # U contributions: +U[(idxA,idxB)]  and -U[(idxB,idxA)]
            Um = U_map.get((idxA, idxB))
            if Um is not None:
                acc = acc + flat_to_E8Z3_numeric(toe, Um)
            Um2 = U_map.get((idxB, idxA))
            if Um2 is not None:
                acc = acc - flat_to_E8Z3_numeric(toe, Um2)

            # V contributions: +V[(idxA,idxB)] and -V[(idxB,idxA)]
            Vm = V_map.get((idxA, idxB))
            if Vm is not None:
                acc = acc + flat_to_E8Z3_numeric(toe, Vm)
            Vm2 = V_map.get((idxB, idxA))
            if Vm2 is not None:
                acc = acc - flat_to_E8Z3_numeric(toe, Vm2)

        return acc

    # `alpha_global` is implemented above using index-based U_map/V_map lookups
    # (previous all-pairs summation removed for performance on large CE2 artifacts)

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
        for d_elem in (x, y, z):
            val = l4_fn(x, y, z, d_elem)
            flat = e8_to_flat(val)
            # skip all-zero results
            if np.allclose(flat, 0.0):
                continue
            # construct canonical key for the fourth element (match loader key_for_elem)
            if np.any(d_elem.g1):
                idx = np.argwhere(np.abs(d_elem.g1) > 0.5)
                di, dj = int(idx[0, 0]), int(idx[0, 1])
                kd = f"g1:{di}:{dj}"
            elif np.any(d_elem.g2):
                idx = np.argwhere(np.abs(d_elem.g2) > 0.5)
                di, dj = int(idx[0, 0]), int(idx[0, 1])
                kd = f"g2:{di}:{dj}"
            else:
                # unsupported sector for symbolic entry
                continue
            key = f"g1:{a[0]}:{a[1]}|g1:{b[0]}:{b[1]}|g2:{c[0]}:{c[1]}|{kd}"
            sparse[key] = fracize_array(flat)

    OUT.write_text(json.dumps(sparse, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    return sparse


if __name__ == "__main__":
    main()
