#!/usr/bin/env python3
"""
Canonicalize a Chevalley certificate to the repo's standard E6 node ordering.

Why:
  `tools/chevalley_normalize_e6_from_basis_export.py` recovers a valid E6 Cartan matrix
  up to permutation, recorded as `cartan.perm_to_canonical`.  Downstream "physics
  dictionary" work is easier if the simple-root generators are stored in the same
  node order everywhere.

Inputs (default):
  - artifacts/e6_basis_export_chevalley_27rep.json
  - artifacts/e6_basis_export_chevalley_27rep_generators.npy

Writes:
  - artifacts/e6_basis_export_chevalley_27rep_canonical.json
  - artifacts/e6_basis_export_chevalley_27rep_canonical_generators.npy
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def invert_perm(perm_current_to_canon: List[int]) -> List[int]:
    if sorted(perm_current_to_canon) != list(range(len(perm_current_to_canon))):
        raise ValueError("perm_to_canonical is not a permutation")
    inv = [0] * len(perm_current_to_canon)
    for cur, can in enumerate(perm_current_to_canon):
        inv[int(can)] = int(cur)
    return inv


def permute_square(a: List[List[int]], inv: List[int]) -> List[List[int]]:
    n = len(inv)
    return [[int(a[inv[i]][inv[j]]) for j in range(n)] for i in range(n)]


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_basis_export_chevalley_27rep.json",
    )
    p.add_argument(
        "--in-npy",
        type=Path,
        default=ROOT / "artifacts" / "e6_basis_export_chevalley_27rep_generators.npy",
    )
    p.add_argument(
        "--out-stem",
        type=str,
        default="e6_basis_export_chevalley_27rep_canonical",
        help="Writes artifacts/<stem>.json and artifacts/<stem>_generators.npy",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    data = _load_json(args.in_json)
    cart = data.get("cartan", {})
    if not isinstance(cart, dict):
        raise RuntimeError("Invalid input JSON: missing cartan object")

    perm = cart.get("perm_to_canonical")
    if not isinstance(perm, list) or len(perm) != 6:
        raise RuntimeError("Invalid input JSON: cartan.perm_to_canonical missing")
    # NOTE: despite the name, `chevalley_normalize_e6_from_basis_export.py` defines
    # this permutation as:
    #   canonical[i,j] == computed[perm[i], perm[j]]
    # i.e. perm maps canonical-index -> computed-index.
    perm_from_canonical = [int(x) for x in perm]
    perm_to_canonical = invert_perm(perm_from_canonical)

    # Reorder certificate fields.
    cartan_matrix = cart.get("cartan_matrix")
    if not isinstance(cartan_matrix, list) or len(cartan_matrix) != 6:
        raise RuntimeError("Invalid input JSON: cartan.cartan_matrix missing")
    cartan_matrix = [[int(x) for x in row] for row in cartan_matrix]

    canon_cartan = cart.get("canonical_matrices", {}).get("E6")
    if not isinstance(canon_cartan, list) or len(canon_cartan) != 6:
        raise RuntimeError("Invalid input JSON: cartan.canonical_matrices.E6 missing")

    cartan_matrix_reordered = permute_square(cartan_matrix, perm_from_canonical)

    simple_roots = data.get("simple_roots")
    if not isinstance(simple_roots, list) or len(simple_roots) != 6:
        raise RuntimeError("Invalid input JSON: simple_roots missing")
    simple_roots_reordered = [simple_roots[perm_from_canonical[i]] for i in range(6)]

    # Reorder generator arrays.
    payload = np.load(args.in_npy, allow_pickle=True).item()
    e = np.array(payload["e"])
    f = np.array(payload["f"])
    h = np.array(payload["h"])
    if e.shape != (6, 27, 27) or f.shape != (6, 27, 27) or h.shape != (6, 27, 27):
        raise RuntimeError("Unexpected generator array shapes in input npy")

    e2 = np.array([e[perm_from_canonical[i]] for i in range(6)], dtype=np.complex128)
    f2 = np.array([f[perm_from_canonical[i]] for i in range(6)], dtype=np.complex128)
    h2 = np.array([h[perm_from_canonical[i]] for i in range(6)], dtype=np.complex128)

    out_json = ROOT / "artifacts" / f"{args.out_stem}.json"
    out_npy = ROOT / "artifacts" / f"{args.out_stem}_generators.npy"

    # Build output.
    out = dict(data)
    out["simple_roots"] = simple_roots_reordered
    out_cart = dict(cart)
    out_cart["perm_from_canonical"] = list(range(6))  # now canonical
    out_cart["perm_to_canonical"] = list(range(6))  # now canonical
    out_cart["perm_from_canonical_original"] = perm_from_canonical
    out_cart["perm_to_canonical_original"] = perm_to_canonical
    out_cart["cartan_matrix_original"] = cartan_matrix
    out_cart["cartan_matrix"] = cartan_matrix_reordered
    out_cart["cartan_matrix_matches_canonical"] = (
        cartan_matrix_reordered == canon_cartan
    )
    out["cartan"] = out_cart

    _write_json(out_json, out)
    np.save(
        out_npy,
        {
            "e": e2,
            "f": f2,
            "h": h2,
            "perm_from_canonical_original": np.array(perm_from_canonical, dtype=int),
            "perm_to_canonical_original": np.array(perm_to_canonical, dtype=int),
        },
    )

    print(f"Wrote {out_json}")
    print(f"Wrote {out_npy}")
    if out_cart["cartan_matrix_matches_canonical"]:
        print("PASS: Cartan matrix matches canonical E6 ordering")
    else:
        print("WARN: Cartan matrix does not match canonical after reordering")


if __name__ == "__main__":
    main()
