#!/usr/bin/env python3
"""
Export a *complete sparse* structure-constants table for the E8 Lie algebra using the
purely discrete W33-root engine (root_orbit coeffs + deterministic cocycle signs).

Basis
-----
We use the standard Chevalley-style basis:
  - Cartan: h_1..h_8 (simple coroots; E8 is simply-laced so coroots=roots)
  - Root vectors: e_α for all 240 roots α

with roots expressed in the repo's canonical E8 simple-root coefficient basis
`root_orbit` (length-8 integer vectors). The simple roots are exactly the unit vectors.

Bracket rules
-------------
Let A be the E8 Cartan matrix (symmetric here). For α,β roots:
  [h_i, h_j] = 0
  [h_i, e_α] = α(h_i) e_α  where α(h_i) = Σ_j A[i,j] * α_j
  [e_α, e_β] = 0                 if α+β is not a root and α+β != 0
  [e_α, e_β] = ε(α,β) e_{α+β}     if α+β is a root
  [e_α, e_{-α}] = κ(α) h_α        with h_α = Σ_i α_i h_i

where κ is a (root-height) sign correction required for consistency when you fix the
root–root signs via a lattice cocycle. Concretely:
  κ(α) = (-1)^(ht(α)-1),  ht(α)=Σ_i α_i for α positive and ht(-α)=ht(α).

The sign ε is the deterministic even-lattice cocycle in the root_orbit coefficient basis:
  ε(α,β)=(-1)^{ Σ_{i>j} (α_i mod2)(β_j mod2)(A[i,j] mod2) }.

This exactly matches the verified W33-table bracket:
  - tools/verify_e8_discrete_bracket_from_w33_tables.py
  - tools/sage_verify_e8_discrete_bracket_from_w33_tables.sage

Conceptually, ε is the same kind of sign-choice data as an "asymmetry function" in
Chevalley-basis constructions (common in lattice/VOA presentations of simply-laced algebras).

Outputs
-------
  - artifacts/e8_structure_constants_w33_discrete.json
  - artifacts/e8_structure_constants_w33_discrete.md
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

IN_META = ROOT / "artifacts" / "e8_root_metadata_table.json"
OUT_JSON = ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json"
OUT_MD = ROOT / "artifacts" / "e8_structure_constants_w33_discrete.md"


Root = Tuple[int, ...]  # length 8


def _canonical_cartan() -> List[List[int]]:
    return [
        [2, 0, -1, 0, 0, 0, 0, 0],
        [0, 2, 0, -1, 0, 0, 0, 0],
        [-1, 0, 2, -1, 0, 0, 0, 0],
        [0, -1, -1, 2, -1, 0, 0, 0],
        [0, 0, 0, -1, 2, -1, 0, 0],
        [0, 0, 0, 0, -1, 2, -1, 0],
        [0, 0, 0, 0, 0, -1, 2, -1],
        [0, 0, 0, 0, 0, 0, -1, 2],
    ]


def _eps_orbit_coeffs(a: Root, b: Root, Amod2: List[List[int]]) -> int:
    parity = 0
    for i in range(8):
        if (a[i] & 1) == 0:
            continue
        for j in range(i):
            if (b[j] & 1) == 0:
                continue
            if (Amod2[i][j] & 1) != 0:
                parity ^= 1
    return -1 if parity else 1


def _alpha_on_hi(alpha: Root, i: int, A: List[List[int]]) -> int:
    return int(sum(int(A[i][j]) * int(alpha[j]) for j in range(8)))


def _height(alpha: Root) -> int:
    """
    Height in the simple-root basis:
      ht(α) = Σ_i α_i for α positive,
      ht(α) = ht(-α) for α negative.

    For E8 roots in simple-root coordinates, every root is either all-≥0 or all-≤0.
    """

    if all(x >= 0 for x in alpha):
        return int(sum(alpha))
    if all(x <= 0 for x in alpha):
        return int(sum(-x for x in alpha))
    # Should not happen for a genuine root in this coordinate system.
    raise ValueError(f"Not a sign-coherent root vector: {alpha}")


def _kappa_height_sign(alpha: Root) -> int:
    """
    Sign correction needed for the *Cartan* bracket [e_α, e_-α] when using a lattice cocycle
    sign convention on [e_α,e_β] for α+β a root.

    Empirically (and matches the A2 subalgebra test), the consistent choice is:
      [e_α, e_-α] = κ(α) * h_α,   κ(α) = (-1)^(ht(α)-1)

    i.e. κ(α)=+1 for odd height, κ(α)=-1 for even height.
    """

    ht = _height(alpha)
    return -1 if (ht % 2) == 0 else 1


@dataclass(frozen=True)
class BasisIndex:
    kind: str  # "h" or "e"
    payload: object


def main() -> None:
    meta = json.loads(IN_META.read_text(encoding="utf-8"))
    rows = meta["rows"]
    roots: List[Root] = sorted({tuple(int(x) for x in r["root_orbit"]) for r in rows})
    if len(roots) != 240:
        raise RuntimeError(f"Expected 240 roots; got {len(roots)}")

    # Basis ordering: 8 Cartan + 240 roots
    root_to_idx: Dict[Root, int] = {rt: 8 + i for i, rt in enumerate(roots)}

    A = _canonical_cartan()
    Amod2 = [[int(x) & 1 for x in row] for row in A]

    # Sparse bracket table for ordered pairs (i<j). Each entry is list[(k, coeff)].
    # Indices: 0..7 for h_i, 8..247 for e_root
    brackets: Dict[str, List[List[int]]] = {}

    nonzero = 0
    nonzero_cartan_terms = 0
    nonzero_root_terms = 0

    # Precompute roots as list for fast lookup.
    root_set = set(roots)

    # Cartan–Cartan: all zero (omit)

    # Cartan–root
    for hi in range(8):
        for rt in roots:
            j = root_to_idx[rt]
            coeff = _alpha_on_hi(rt, hi, A)
            if coeff == 0:
                continue
            key = f"{hi},{j}"
            brackets[key] = [[j, int(coeff)]]
            nonzero += 1
            nonzero_root_terms += 1

    # Root–root
    for a in roots:
        ia = root_to_idx[a]
        for b in roots:
            ib = root_to_idx[b]
            if ia >= ib:
                continue
            s = tuple(int(a[t] + b[t]) for t in range(8))
            if s == (0, 0, 0, 0, 0, 0, 0, 0):
                # [e_a,e_-a] = h_a = Σ_i a_i h_i
                terms: List[List[int]] = []
                kappa = _kappa_height_sign(a)
                for i in range(8):
                    c = int(kappa * int(a[i]))
                    if c != 0:
                        terms.append([i, c])
                if terms:
                    brackets[f"{ia},{ib}"] = terms
                    nonzero += 1
                    nonzero_cartan_terms += 1
                continue
            if s not in root_set:
                continue
            isc = root_to_idx[s]
            coeff = _eps_orbit_coeffs(a, b, Amod2)
            brackets[f"{ia},{ib}"] = [[isc, int(coeff)]]
            nonzero += 1
            nonzero_root_terms += 1

    out = {
        "status": "ok",
        "basis": {
            "n": 248,
            "cartan_dim": 8,
            "root_dim": 240,
            "root_order": "lex(root_orbit)",
            "roots": [list(r) for r in roots],
        },
        "cartan_matrix": A,
        "brackets": brackets,
        "counts": {
            "nonzero_brackets_i_lt_j": int(nonzero),
            "nonzero_root_terms": int(nonzero_root_terms),
            "nonzero_cartan_terms": int(nonzero_cartan_terms),
        },
        "notes": {
            "meaning": "brackets['i,j'] gives [basis_i, basis_j] for i<j in the (h_i, e_root) basis.",
            "antisymmetry": "Recover [j,i] by negating coefficients.",
        },
    }

    OUT_JSON.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sha = hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()

    md: List[str] = []
    md.append("# E8 structure constants from W33-discrete root engine\n")
    md.append(f"- status: `{out['status']}`")
    md.append(f"- basis: `{out['basis']['n']}` = 8 Cartan + 240 roots")
    md.append(f"- nonzero brackets (i<j): `{out['counts']['nonzero_brackets_i_lt_j']}`")
    md.append("- Cartan bracket uses `κ(α)=(-1)^(ht(α)-1)` in this cocycle gauge.")
    md.append(f"- sha256(json): `{sha}`\n")
    md.append("## Indexing\n")
    md.append("- `0..7` are `h_1..h_8`.")
    md.append("- `8..247` are `e_α` in lex order of `root_orbit`.\n")
    md.append(f"- JSON: `{OUT_JSON}`")
    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print(f"status=ok wrote={OUT_JSON}")
    print(f"sha256={sha}")


if __name__ == "__main__":
    main()
