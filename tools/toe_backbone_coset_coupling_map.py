#!/usr/bin/env python3
"""
Classify coupling outputs as D6-backbone vs 12-dim coset (exact).

Inputs:
  - artifacts/toe_coupling_strengths_v4.json
  - E6 root operator dictionary (generated if missing)
  - D6/coset basis export (from More New Work v3p39):
      artifacts/more_new_work_extracted/**/e6_basis_export_full/D6_basis_66.npy
      artifacts/more_new_work_extracted/**/e6_basis_export_full/coset_basis_12.npy

Method:
  - For each distinct output root, take its operator matrix E_out and solve coefficients in the
    concatenated basis [D6_basis_66, coset_basis_12] (78 total).
  - Split the reconstructed operator into backbone vs coset components using those coefficients.
  - Report backbone_frac / coset_frac by Frobenius energy.

Outputs:
  - artifacts/toe_backbone_coset_coupling_map_v3_exact.json
  - artifacts/toe_backbone_coset_coupling_map_v3_exact.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

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


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _ensure_root_dict() -> Path:
    out = ROOT / "artifacts" / "toe_root_operator_dictionary.npy"
    if out.exists():
        return out
    tool = _load_module(
        ROOT / "tools" / "toe_root_operator_dictionary.py",
        "toe_root_operator_dictionary",
    )
    tool.main([])
    if not out.exists():
        raise RuntimeError(
            "Expected toe_root_operator_dictionary.npy to be written but file missing"
        )
    return out


def _find_latest_export_full_dir() -> Path:
    search_root = ROOT / "artifacts" / "more_new_work_extracted"
    if not search_root.exists():
        raise RuntimeError(
            "Missing artifacts/more_new_work_extracted; run tools/ingest_more_new_work.py"
        )
    candidates = list(search_root.rglob("e6_basis_export_full"))
    if not candidates:
        raise RuntimeError(
            "Could not find e6_basis_export_full under artifacts/more_new_work_extracted"
        )
    # Prefer most recently modified directory.
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _prepare_solver(
    d6: np.ndarray, coset: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (Q,R,B) with B=729x78, QR factorization for fast least-squares."""
    if d6.shape != (66, 27, 27) or coset.shape != (12, 27, 27):
        raise ValueError("Unexpected D6/coset basis shapes")
    basis = np.concatenate([d6, coset], axis=0)  # (78,27,27)
    B = np.column_stack([basis[k].reshape(-1) for k in range(78)])  # (729,78)
    Q, R = np.linalg.qr(B)  # Q: (729,78), R: (78,78)
    return Q, R, basis


def _decompose(
    Q: np.ndarray, R: np.ndarray, basis: np.ndarray, x: np.ndarray
) -> Tuple[float, float, float]:
    """Return (backbone_frac, coset_frac, rel_resid) for x."""
    xv = x.reshape(-1)
    # Solve B c ≈ x via QR: c = R^{-1} Q^H x
    y = Q.conj().T @ xv
    c = np.linalg.solve(R, y)
    d6_c = c[:66]
    co_c = c[66:]
    d6_part = np.tensordot(d6_c, basis[:66], axes=([0], [0]))
    co_part = np.tensordot(co_c, basis[66:], axes=([0], [0]))
    tot = float(np.linalg.norm(xv)) ** 2
    d6n = float(np.linalg.norm(d6_part.reshape(-1))) ** 2
    con = float(np.linalg.norm(co_part.reshape(-1))) ** 2
    # Residual in full 78-basis reconstruction.
    recon = d6_part + co_part
    resid = float(np.linalg.norm((x - recon).reshape(-1)))
    rel = resid / float(np.linalg.norm(xv)) if float(np.linalg.norm(xv)) else resid
    if tot == 0.0:
        return 0.0, 0.0, rel
    return float(d6n / tot), float(con / tot), float(rel)


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_coupling_strengths_v4.json",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_backbone_coset_coupling_map_v3_exact.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_backbone_coset_coupling_map_v3_exact.md",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    coupl = _load_json(args.in_json)
    couplings = coupl.get("couplings")
    if not isinstance(couplings, list):
        raise RuntimeError("Invalid coupling strengths JSON: missing couplings list")

    root = np.load(_ensure_root_dict(), allow_pickle=True).item()
    mats = np.array(root["mats"], dtype=np.complex128)

    export_full = _find_latest_export_full_dir()
    d6 = np.load(export_full / "D6_basis_66.npy")
    coset = np.load(export_full / "coset_basis_12.npy")
    Q, R, basis = _prepare_solver(d6, coset)

    # Unique output roots.
    idxs = sorted(
        {
            int(c["output_root_index"])
            for c in couplings
            if c.get("output_root_index") is not None
        }
    )

    per_root: Dict[int, Dict[str, object]] = {}
    for k in idxs:
        bb, cc, rel = _decompose(Q, R, basis, mats[k])
        per_root[k] = {
            "output_root_index": k,
            "backbone_frac": float(bb),
            "coset_frac": float(cc),
            "rel_resid": float(rel),
            "class": (
                "backbone_major"
                if bb >= 0.60
                else ("coset_major" if cc >= 0.60 else "mixed")
            ),
        }

    # Attach per-coupling classification.
    enriched = []
    for c in couplings:
        idx = c.get("output_root_index")
        row = dict(c)
        if idx is None:
            row["backbone_coset"] = None
        else:
            row["backbone_coset"] = per_root[int(idx)]
        enriched.append(row)

    counts = {"backbone_major": 0, "coset_major": 0, "mixed": 0}
    for v in per_root.values():
        counts[v["class"]] += 1

    out: Dict[str, object] = {
        "status": "ok",
        "note": "Exact projection of coupling output root-operators into D6 (66) vs coset (12) spans.",
        "export_full_dir": str(export_full),
        "counts": {
            "total_couplings": len(couplings),
            "unique_outputs": len(per_root),
            **counts,
        },
        "couplings": sorted(
            enriched, key=lambda r: float(r.get("overlap") or 0.0), reverse=True
        ),
    }
    _write_json(args.out_json, out)

    lines: List[str] = []
    lines.append("# TOE Backbone vs Coset Map v3 (exact)")
    lines.append("")
    lines.append(f"- export_full_dir: `{export_full}`")
    lines.append(f"- total_couplings: `{len(couplings)}`")
    lines.append(f"- unique_outputs: `{len(per_root)}`")
    lines.append(
        f"- backbone_major: `{counts['backbone_major']}`  coset_major: `{counts['coset_major']}`  mixed: `{counts['mixed']}`"
    )
    lines.append("")
    lines.append("Top couplings (by overlap):")
    for c in out["couplings"][:15]:
        bc = c.get("backbone_coset")
        if not isinstance(bc, dict):
            continue
        lines.append(
            f"- pair {c['pair']} overlap={float(c.get('overlap') or 0.0):.3f} "
            f"backbone={float(bc['backbone_frac']):.2f} coset={float(bc['coset_frac']):.2f} class={bc['class']}"
        )
    lines.append("")
    lines.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, lines)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
