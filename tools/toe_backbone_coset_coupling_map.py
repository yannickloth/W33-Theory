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


def _find_latest_export_full_dir(preferred_basis_file: Path | None = None) -> Path:
    """
    Locate an extracted 'e6_basis_export_full' folder by searching for E6_basis_78.npy.
    If `preferred_basis_file` is provided (path to an E6_basis_78.npy used to build the
    current root-operator dictionary), attempt to find a matching export whose
    E6_basis_78.npy is numerically equal (within tolerance). Otherwise fall back to
    the lexicographically/most-recently-modified candidate.
    """
    search_root = ROOT / "artifacts" / "more_new_work_extracted"
    if not search_root.exists():
        raise RuntimeError(
            "Missing artifacts/more_new_work_extracted; run tools/ingest_more_new_work.py"
        )

    # Try matching a preferred basis file if supplied.
    if preferred_basis_file is not None and preferred_basis_file.exists():
        try:
            pref = np.load(preferred_basis_file)
            # Search for exported E6_basis_78.npy files and compare numerically.
            candidates = sorted(
                search_root.rglob("E6_basis_78.npy"), key=lambda p: str(p).lower()
            )
            for cand in candidates:
                try:
                    cand_mat = np.load(cand)
                except Exception:
                    continue
                if cand_mat.shape != pref.shape:
                    continue
                if np.allclose(pref, cand_mat, rtol=1e-10, atol=1e-12):
                    full_dir = cand.parent
                    if (full_dir / "D6_basis_66.npy").exists() and (
                        full_dir / "coset_basis_12.npy"
                    ).exists():
                        print(
                            f"Using e6_basis_export_full matching root-dict basis: {full_dir}"
                        )
                        return full_dir
            print(
                "No matching e6_basis_export_full found for root-dict basis; falling back to latest export_full dir"
            )
        except Exception:
            print(
                "Warning: failed to load preferred basis file for matching; falling back to latest export_full dir"
            )

    # Fallback: prefer the most recently modified "e6_basis_export_full" dir.
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

    # Prefer using an e6_basis_export_full that matches the root-operator dictionary
    # if one is available. This avoids basis-mismatch that causes large reconstruction
    # residuals when decomposing root operators into D6 vs coset spans.
    preferred_basis = None
    root_json = ROOT / "artifacts" / "toe_root_operator_dictionary.json"
    if root_json.exists():
        try:
            rd = _load_json(root_json)
            preferred_basis = rd.get("source", {}).get("basis_file", None)
            if preferred_basis is not None:
                preferred_basis = Path(preferred_basis)
        except Exception:
            preferred_basis = None

    export_full = _find_latest_export_full_dir(preferred_basis)

    # If the chosen export_full provides an `e6_basis_export/E6_basis_78.npy`, prefer
    # regenerating the root-operator dictionary from that export to ensure the
    # root `mats` are computed in the same basis as the D6/coset files.
    bundle_export_dir = export_full.parent / "e6_basis_export"
    if bundle_export_dir.exists() and (bundle_export_dir / "E6_basis_78.npy").exists():
        root_json_path = ROOT / "artifacts" / "toe_root_operator_dictionary.json"
        rebuild = True
        if root_json_path.exists():
            try:
                rd = _load_json(root_json_path)
                basis_file = rd.get("source", {}).get("basis_file")
                if (
                    basis_file is not None
                    and Path(basis_file).expanduser().resolve()
                    == (bundle_export_dir / "E6_basis_78.npy").resolve()
                ):
                    rebuild = False
            except Exception:
                rebuild = True
        if rebuild:
            # Backup existing root dict files before rebuilding.
            npy_path = ROOT / "artifacts" / "toe_root_operator_dictionary.npy"
            json_path = ROOT / "artifacts" / "toe_root_operator_dictionary.json"
            try:
                if npy_path.exists():
                    npy_path.rename(npy_path.with_suffix(npy_path.suffix + ".bak"))
                if json_path.exists():
                    json_path.rename(json_path.with_suffix(json_path.suffix + ".bak"))
            except Exception as e:
                print(f"Warning: failed to backup root dict files: {e}")
            print(f"Regenerating root-operator dictionary from {bundle_export_dir}")
            tool = _load_module(
                ROOT / "tools" / "toe_root_operator_dictionary.py",
                "toe_root_operator_dictionary",
            )
            tool.main(["--export-dir", str(bundle_export_dir)])

    # Load (or reloaded) root dictionary and mats.
    try:
        root_dict_path = _ensure_root_dict()
        root_dict = np.load(root_dict_path, allow_pickle=True).item()
        weights = root_dict.get("weights", None)
        mats = np.array(root_dict["mats"], dtype=np.complex128)
    except Exception:
        weights = None
        mats = np.zeros((0, 27, 27), dtype=np.complex128)

    d6 = np.load(export_full / "D6_basis_66.npy")
    coset = np.load(export_full / "coset_basis_12.npy")
    Q, R, basis = _prepare_solver(d6, coset)

    # Ensure root operator dictionary exists and attempt to match couplings with explicit output vectors
    try:
        root_dict_path = _ensure_root_dict()
        root_dict = np.load(root_dict_path, allow_pickle=True).item()
        weights = root_dict.get("weights", None)
    except Exception:
        weights = None

    # If couplings contain output_root vectors but not indices, match by nearest weight
    matched = 0
    if weights is not None:
        for c in couplings:
            if c.get("output_root_index") is None and c.get("output_root") is not None:
                out_vec = np.array(c.get("output_root"), dtype=float)
                dists = np.linalg.norm(weights - out_vec.reshape(1, -1), axis=1)
                best = int(np.argmin(dists))
                c["output_root_index"] = best
                c["output_root_match_dist"] = float(dists[best])
                matched += 1
    if matched:
        print(f"Matched {matched} couplings to nearest root weights by vector distance")

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
            bc = per_root[int(idx)]
            row["backbone_coset"] = bc
            # Backwards-compatible `decomp` summary used by `toe_coupling_atlas_sweep.py`.
            row["decomp"] = {
                "backbone_frac": float(bc.get("backbone_frac", 0.0)),
                "coset_frac": float(bc.get("coset_frac", 0.0)),
            }
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
