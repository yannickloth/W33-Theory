#!/usr/bin/env python3
"""
Build a full E6 root-operator dictionary on the 27-representation.

This computes the 72 one-dimensional root spaces by diagonalizing a generic Cartan
element in the *adjoint* representation (78-dim basis), then lifting each root
eigenvector back to an explicit 27×27 operator matrix.

Outputs:
  - artifacts/toe_root_operator_dictionary.json
  - artifacts/toe_root_operator_dictionary.npy

The `.npy` is a dict with:
  - keys:    (72,12) int64  (rounded weight embedding key)
  - weights: (72,6)  complex128  (α(H_k) for recovered Cartan H_k)
  - mats:    (72,27,27) complex128  (root operators)
  - key_scale: float
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


e6norm = _load_module(
    ROOT / "tools" / "chevalley_normalize_e6_from_basis_export.py",
    "chevalley_normalize_e6_from_basis_export",
)


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--export-dir",
        type=Path,
        default=Path(""),
        help="Directory containing E6_basis_78.npy. Default: use artifacts/e6_27rep_basis_export if present, else latest extracted export.",
    )
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_root_operator_dictionary.json",
    )
    p.add_argument(
        "--out-npy",
        type=Path,
        default=ROOT / "artifacts" / "toe_root_operator_dictionary.npy",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    export_dir = args.export_dir
    if not str(export_dir):
        candidate = ROOT / "artifacts" / "e6_27rep_basis_export"
        export_dir = (
            candidate
            if (candidate / "E6_basis_78.npy").exists()
            else Path(e6norm.find_latest_basis_export_dir())
        )
    export_dir = export_dir.expanduser().resolve()

    basis = e6norm.load_basis_export(export_dir)
    _v, proj = e6norm.build_projection(basis)

    cartan_mats, cartan_coeffs, cartan_stats = (
        e6norm.find_cartan_via_regular_centralizer(
            basis,
            seed=int(args.seed),
            max_tries=64,
            rcond=1e-10,
            require_commute_tol=1e-8,
        )
    )
    ad_cartan = [e6norm.ad_matrix_in_basis(hk, basis, proj) for hk in cartan_mats]
    eigvals, eigvecs, t = e6norm.diagonalize_generic_cartan(
        ad_cartan, seed=int(args.seed)
    )

    # Choose rounding scale for root keys.
    tmp_weights_embed = []
    scale0 = float(np.max(np.abs(eigvals))) if eigvals.size else 1.0
    tol0 = max(1e-10 * scale0, 1e-14)
    for idx, lam in enumerate(eigvals.tolist()):
        if abs(lam) < tol0:
            continue
        v = eigvecs[:, idx]
        nv = float(np.linalg.norm(v))
        if nv == 0.0:
            continue
        v = v / nv
        w = []
        for ak in ad_cartan:
            lk = np.vdot(v, ak @ v) / np.vdot(v, v)
            w.append(lk)
        tmp_weights_embed.append(e6norm.embed_weight(np.array(w, dtype=np.complex128)))
    key_scale = e6norm.choose_key_scale(np.array(tmp_weights_embed, dtype=np.float64))

    roots, root_stats = e6norm.extract_roots_from_eigendecomposition(
        eigvals, eigvecs, ad_cartan, key_scale=key_scale
    )
    roots_sorted = sorted(roots, key=lambda r: r.key)

    keys = np.array([list(r.key) for r in roots_sorted], dtype=np.int64)
    weights = np.array([r.weight for r in roots_sorted], dtype=np.complex128)
    mats = np.array(
        [np.tensordot(r.eigvec, basis, axes=([0], [0])) for r in roots_sorted],
        dtype=np.complex128,
    )
    norms = np.array([float(np.linalg.norm(m)) for m in mats], dtype=np.float64)

    # Determine a positive half using the same positivity rule as the normalizer.
    pos = set(r.key for r in e6norm.choose_positive_roots(roots_sorted))
    is_pos = np.array(
        [1 if tuple(k.tolist()) in pos else 0 for k in keys], dtype=np.int64
    )

    args.out_npy.parent.mkdir(parents=True, exist_ok=True)
    np.save(
        args.out_npy,
        {
            "keys": keys,
            "weights": weights,
            "mats": mats,
            "norms": norms,
            "is_positive": is_pos,
            "key_scale": float(key_scale),
        },
    )

    out: Dict[str, object] = {
        "status": "ok",
        "source": {
            "export_dir": str(export_dir),
            "basis_file": str(export_dir / "E6_basis_78.npy"),
        },
        "dims": {"roots": 72, "rank": 6, "total": 78},
        "cartan_recovery": cartan_stats,
        "root_decomposition": {"generic_cartan_coeffs_t": t.tolist(), **root_stats},
        "roots": [
            {
                "key": [int(x) for x in keys[i].tolist()],
                "weight_re": [float(x) for x in np.real(weights[i]).tolist()],
                "weight_im": [float(x) for x in np.imag(weights[i]).tolist()],
                "norm": float(norms[i]),
                "is_positive": bool(is_pos[i]),
            }
            for i in range(72)
        ],
    }
    _write_json(args.out_json, out)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_npy}")


if __name__ == "__main__":
    main()
