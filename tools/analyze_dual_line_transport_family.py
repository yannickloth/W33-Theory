#!/usr/bin/env python3
"""Fit low-degree F3 transport laws for solved dual-family anchors.

This research utility loads the hard-coded anchor line tables from
``scripts/ce2_global_cocycle.py`` and tries to compress them into polynomial
maps over F3. The current default family is the vertical line
``a=(1,0,*)``, which corresponds to anchors 100, 101, and 102.

For each branch it searches the smallest total degree <= 3 whose monomial
basis fits the data exactly:
  - c = line W-support E6 id as a Heisenberg vector
  - t = line target E6 id as a Heisenberg vector
  - sign in F3 encoding (+1 -> 1, -1 -> 2)
  - overlap c/u/v target vectors
  - overlap U/V signs in the same F3 encoding
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _solve_mod3(A: np.ndarray, y: np.ndarray) -> np.ndarray | None:
    A = A.copy() % 3
    y = y.copy() % 3
    m, n = A.shape
    aug = np.concatenate([A, y.reshape(-1, 1)], axis=1) % 3
    row = 0
    pivots: list[tuple[int, int]] = []
    for col in range(n):
        pivot = None
        for r in range(row, m):
            if aug[r, col] % 3 != 0:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            aug[[row, pivot]] = aug[[pivot, row]]
        inv = 1 if aug[row, col] == 1 else 2
        aug[row] = (aug[row] * inv) % 3
        for r in range(m):
            if r == row:
                continue
            factor = aug[r, col] % 3
            if factor:
                aug[r] = (aug[r] - factor * aug[row]) % 3
        pivots.append((row, col))
        row += 1
        if row == m:
            break
    for r in range(m):
        if np.all(aug[r, :n] % 3 == 0) and aug[r, n] % 3 != 0:
            return None
    coeff = np.zeros(n, dtype=int)
    for r, c in pivots:
        coeff[c] = aug[r, n] % 3
    return coeff % 3


def _monomials(num_vars: int, max_degree: int) -> list[tuple[int, ...]]:
    return [
        exps
        for exps in itertools.product(range(3), repeat=num_vars)
        if sum(exps) <= max_degree
    ]


def _monomial_name(var_names: list[str], exps: tuple[int, ...]) -> str:
    parts: list[str] = []
    for name, exp in zip(var_names, exps):
        if exp == 0:
            continue
        if exp == 1:
            parts.append(name)
        else:
            parts.append(f"{name}^{exp}")
    return "*".join(parts) if parts else "1"


def _features(values: tuple[int, ...], monomials: list[tuple[int, ...]]) -> list[int]:
    out: list[int] = []
    for exps in monomials:
        acc = 1
        for value, exp in zip(values, exps):
            acc = (acc * (value**exp)) % 3
        out.append(acc)
    return out


@dataclass(frozen=True)
class LineSample:
    anchor_name: str
    a_vec: tuple[int, int, int]
    b_vec: tuple[int, int, int]
    c_vec: tuple[int, int, int]
    t_vec: tuple[int, int, int]
    sign_f3: int


@dataclass(frozen=True)
class OverlapSample:
    anchor_name: str
    a_vec: tuple[int, int, int]
    b_vec: tuple[int, int, int]
    c_vec: tuple[int, int, int]
    u_vec: tuple[int, int, int]
    v_vec: tuple[int, int, int]
    u_sign_f3: int
    v_sign_f3: int


def _anchor_vec_for_name(coc, anchor_name: str) -> tuple[int, int, int]:
    e6id_to_vec, _ = coc._heisenberg_vec_maps()
    active = getattr(coc, f"_anchor_{anchor_name.lower()}_active")
    for idx in range(len(e6id_to_vec)):
        if active(idx):
            return tuple(int(x) % 3 for x in e6id_to_vec[idx])
    raise RuntimeError(f"no active id found for anchor {anchor_name}")


def _collect_samples(anchor_names: list[str]) -> list[LineSample]:
    coc = _load_module(ROOT / "scripts" / "ce2_global_cocycle.py", "ce2_global_cocycle_fit")
    e6id_to_vec, _ = coc._heisenberg_vec_maps()

    def vec(i: int) -> tuple[int, int, int]:
        return tuple(int(x) % 3 for x in e6id_to_vec[int(i)])

    samples: list[LineSample] = []
    for name in anchor_names:
        table = getattr(coc, f"_ANCHOR_{name}_LINE_CASES")
        anchor_vec = _anchor_vec_for_name(coc, name)
        for b_i, (c_i, t_i, sign) in sorted(table.items()):
            samples.append(
                LineSample(
                    anchor_name=name,
                    a_vec=anchor_vec,
                    b_vec=vec(b_i),
                    c_vec=vec(c_i),
                    t_vec=vec(t_i),
                    sign_f3=1 if int(sign) == 1 else 2,
                )
            )
    return samples


def _collect_overlap_samples(anchor_names: list[str]) -> list[OverlapSample]:
    coc = _load_module(
        ROOT / "scripts" / "ce2_global_cocycle.py", "ce2_global_cocycle_fit_overlap"
    )
    e6id_to_vec, _ = coc._heisenberg_vec_maps()

    def vec(i: int) -> tuple[int, int, int]:
        return tuple(int(x) % 3 for x in e6id_to_vec[int(i)])

    samples: list[OverlapSample] = []
    for name in anchor_names:
        table = getattr(coc, f"_ANCHOR_{name}_OVERLAP_CASES")
        anchor_vec = _anchor_vec_for_name(coc, name)
        for b_i, (c_i, u_i, v_i, u_sign, v_sign) in sorted(table.items()):
            samples.append(
                OverlapSample(
                    anchor_name=name,
                    a_vec=anchor_vec,
                    b_vec=vec(b_i),
                    c_vec=vec(c_i),
                    u_vec=vec(u_i),
                    v_vec=vec(v_i),
                    u_sign_f3=1 if int(u_sign) == 1 else 2,
                    v_sign_f3=1 if int(v_sign) == 1 else 2,
                )
            )
    return samples


def _fit_outputs(records: list[dict[str, tuple[int, ...] | int]]) -> dict[str, object]:
    var_names = ["az", "bx", "by", "bz"]
    X_rows = []
    outputs: dict[str, list[int]] = {}
    for rec in records:
        az = int(rec["a_vec"][2])
        bx, by, bz = (int(v) for v in rec["b_vec"])
        X_rows.append((az, bx, by, bz))
        for key, value in rec.items():
            if key in {"a_vec", "b_vec"}:
                continue
            if isinstance(value, tuple):
                for i, entry in enumerate(value):
                    outputs.setdefault(f"{key}{i}", []).append(int(entry))
            else:
                outputs.setdefault(key, []).append(int(value))

    report: dict[str, object] = {
        "fits": {},
    }
    for degree in range(1, 4):
        monomials = _monomials(len(var_names), degree)
        names = [_monomial_name(var_names, exps) for exps in monomials]
        X = np.array([_features(row, monomials) for row in X_rows], dtype=int) % 3
        degree_report: dict[str, object] = {}
        for out_name, values in outputs.items():
            y = np.array(values, dtype=int) % 3
            coeff = _solve_mod3(X, y)
            if coeff is None:
                continue
            pred = (X @ coeff) % 3
            if not np.all(pred == y):
                continue
            degree_report[out_name] = [
                {"monomial": names[i], "coef": int(coeff[i])}
                for i in range(len(coeff))
                if coeff[i] % 3 != 0
            ]
        report["fits"][str(degree)] = degree_report
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--anchors",
        default="100,101,102",
        help="Comma-separated anchor names to analyze, e.g. 100,101,102",
    )
    args = parser.parse_args()

    anchor_names = [part.strip() for part in args.anchors.split(",") if part.strip()]
    line_samples = _collect_samples(anchor_names)
    overlap_samples = _collect_overlap_samples(anchor_names)
    report = {
        "anchors": anchor_names,
        "line": {
            "samples": len(line_samples),
            **_fit_outputs(
                [
                    {
                        "a_vec": rec.a_vec,
                        "b_vec": rec.b_vec,
                        "c": rec.c_vec,
                        "t": rec.t_vec,
                        "sign": rec.sign_f3,
                    }
                    for rec in line_samples
                ]
            ),
        },
        "overlap": {
            "samples": len(overlap_samples),
            **_fit_outputs(
                [
                    {
                        "a_vec": rec.a_vec,
                        "b_vec": rec.b_vec,
                        "c": rec.c_vec,
                        "u": rec.u_vec,
                        "v": rec.v_vec,
                        "u_sign": rec.u_sign_f3,
                        "v_sign": rec.v_sign_f3,
                    }
                    for rec in overlap_samples
                ]
            ),
        },
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
