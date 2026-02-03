#!/usr/bin/env python3
"""
Firewall fragility analysis using *full operator support* (not just the dominant entry).

Interpretation (protocol proxy):
  - The protocol always allows Schläfli (skew) edges.
  - The firewall scales the 27 "bad" meet-edges by (1 - s), where s∈[0,1] is firewall_strength.

For an output channel operator E (27×27), define:
  - mass_good = Σ_{(i,j) in Schläfli edges} |E_ij|^2
  - mass_bad  = Σ_{(i,j) in firewall bad edges} |E_ij|^2
  - mass_other = remaining off-diagonal mass (diagnostic)

Define survival(s) = sqrt(mass_good + (1-s)^2 mass_bad) / sqrt(mass_good + mass_bad)
(if mass_good+mass_bad = 0, survival is 0).

Inputs:
  - artifacts/toe_backbone_coset_coupling_map_v3_exact.json
  - artifacts/toe_root_operator_dictionary.npy

Outputs:
  - artifacts/toe_firewall_fragility_v2_exact.json
  - artifacts/toe_firewall_fragility_v2_exact.md
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


toe_dynamics = _load_module(ROOT / "tools" / "toe_dynamics.py", "toe_dynamics")


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _linspace(a: float, b: float, n: int) -> List[float]:
    if n <= 1:
        return [float(a)]
    return [float(a + (b - a) * i / (n - 1)) for i in range(n)]


def _mass_by_edge_classes(
    mat: np.ndarray, skew: np.ndarray, bad_edges: set[tuple[int, int]]
) -> Tuple[float, float, float]:
    m = mat.copy()
    m[np.eye(27, dtype=bool)] = 0.0
    abs2 = np.abs(m) ** 2

    bad_mask = np.zeros((27, 27), dtype=bool)
    for u, v in bad_edges:
        bad_mask[u, v] = True
        bad_mask[v, u] = True

    good_mass = float(np.sum(abs2[skew]))
    bad_mass = float(np.sum(abs2[bad_mask]))
    total_off = float(np.sum(abs2))
    other_mass = float(total_off - good_mass - bad_mass)
    return good_mass, bad_mass, other_mass


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_backbone_coset_coupling_map_v3_exact.json",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_firewall_fragility_v2_exact.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_firewall_fragility_v2_exact.md",
    )
    p.add_argument(
        "--s-n",
        type=int,
        default=21,
        help="Number of firewall_strength samples in [0,1].",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    data = _load_json(args.in_json)
    couplings = data.get("couplings")
    if not isinstance(couplings, list):
        raise RuntimeError(
            "Invalid backbone/coset coupling map: missing couplings list"
        )

    root = np.load(
        ROOT / "artifacts" / "toe_root_operator_dictionary.npy", allow_pickle=True
    ).item()
    mats = np.array(root["mats"], dtype=np.complex128)

    skew, meet = toe_dynamics.load_schlafli_graph()
    fw = toe_dynamics.load_firewall_bad_edges()
    bad_edges = set(fw.bad_edges)

    # Unique output indices with classification.
    outputs: Dict[int, Dict[str, object]] = {}
    for c in couplings:
        idx = c.get("output_root_index")
        bc = c.get("backbone_coset")
        if idx is None or not isinstance(bc, dict):
            continue
        outputs[int(idx)] = {
            "output_root_index": int(idx),
            "class": str(bc.get("class", "mixed")),
            "backbone_frac": float(bc.get("backbone_frac", 0.0)),
            "coset_frac": float(bc.get("coset_frac", 0.0)),
        }

    s_vals = _linspace(0.0, 1.0, int(args.s_n))

    # Per-output survival curves.
    per_output = []
    for idx, meta in sorted(outputs.items(), key=lambda kv: kv[0]):
        m = mats[idx]
        good_mass, bad_mass, other_mass = _mass_by_edge_classes(m, skew, bad_edges)
        denom = good_mass + bad_mass
        surv = []
        for s in s_vals:
            if denom <= 0.0:
                surv.append(0.0)
            else:
                surv.append(
                    float(
                        np.sqrt(good_mass + (1.0 - float(s)) ** 2 * bad_mass)
                        / np.sqrt(denom)
                    )
                )
        per_output.append(
            {
                **meta,
                "mass": {
                    "good": good_mass,
                    "bad": bad_mass,
                    "other": other_mass,
                    "bad_frac": float(bad_mass / denom) if denom > 0.0 else 0.0,
                    "other_frac": (
                        float(other_mass / (good_mass + bad_mass + other_mass))
                        if (good_mass + bad_mass + other_mass) > 0.0
                        else 0.0
                    ),
                },
                "survival": surv,
            }
        )

    # Aggregate by class.
    classes = ["backbone_major", "coset_major", "mixed"]
    by_class = {k: [] for k in classes}
    for row in per_output:
        k = row["class"]
        if k in by_class:
            by_class[k].append(row)

    class_curves = {}
    for k in classes:
        rows = by_class[k]
        if not rows:
            class_curves[k] = {
                "n": 0,
                "mean_survival": [0.0 for _ in s_vals],
                "mean_bad_frac": 0.0,
            }
            continue
        surv_arr = np.array([r["survival"] for r in rows], dtype=float)
        bad_fracs = [float(r["mass"]["bad_frac"]) for r in rows]
        class_curves[k] = {
            "n": int(len(rows)),
            "mean_survival": [float(x) for x in np.mean(surv_arr, axis=0).tolist()],
            "mean_bad_frac": float(np.mean(np.array(bad_fracs, dtype=float))),
        }

    out: Dict[str, object] = {
        "status": "ok",
        "note": "Full-support firewall fragility of coupling output channels; survival(s)=sqrt(good+(1-s)^2 bad)/sqrt(good+bad).",
        "grid_s": s_vals,
        "counts": {k: int(class_curves[k]["n"]) for k in classes},
        "by_class": class_curves,
        "outputs": per_output,
    }
    _write_json(args.out_json, out)

    lines: List[str] = []
    lines.append("# TOE Firewall Fragility v2 (exact support)")
    lines.append("")
    lines.append("## Counts")
    for k in classes:
        lines.append(
            f"- {k}: `{class_curves[k]['n']}` (mean bad-frac `{class_curves[k]['mean_bad_frac']:.3f}`)"
        )
    lines.append("")
    lines.append("## Mean survival at key firewall strengths")
    for k in classes:
        curve = class_curves[k]["mean_survival"]
        if not curve:
            continue

        # Sample at s=0,0.5,1
        def at(s_target: float) -> float:
            j = int(round(s_target * (len(s_vals) - 1)))
            return float(curve[j])

        lines.append(
            f"- {k}: s=0 `{at(0.0):.3f}`  s=0.5 `{at(0.5):.3f}`  s=1 `{at(1.0):.3f}`"
        )
    lines.append("")
    lines.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, lines)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
