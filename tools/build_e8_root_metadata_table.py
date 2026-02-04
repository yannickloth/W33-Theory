#!/usr/bin/env python3
"""
Build a compact, machine-readable dictionary for all 240 E8 roots that ties together:

  - Trinification coordinates (Z^6 ⊕ Z^2 in the E6⊕A2 coroot basis used by the repo's weight proofs)
  - Orbit-basis coordinates used by the repo's Coxeter-6 orbit construction (artifacts/e8_coxeter6_orbits.json)
  - W33 edge assignment via artifacts/e8_root_to_edge.json
  - Coxeter orbit id and Z6 phase (position in canonical orbit order)
  - Trinification grade classification: g0(e6), g0(a2), g1(27⊗3), g2(27*⊗3*)

This file is the “data plane” that lets you answer questions like:
  - Which W33 edges correspond to g1 vs g2 channels?
  - What is the Z6 phase distribution by grade?
  - Which edges/root-channels sit in which Coxeter orbit vertex (W33 vertex)?

Outputs:
  - artifacts/e8_root_metadata_table.json
  - artifacts/e8_root_metadata_table.md
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _parse_root_key(k: str) -> Tuple[int, ...]:
    s = k.strip()
    if not (s.startswith("(") and s.endswith(")")):
        raise ValueError(f"Bad root key: {k}")
    body = s[1:-1].strip()
    if not body:
        return tuple()
    return tuple(int(p.strip()) for p in body.split(","))


def _canon_orbit_order(orbit: List[List[int]]) -> List[Tuple[int, ...]]:
    roots = [tuple(int(x) for x in r) for r in orbit]
    m = min(roots)
    i = roots.index(m)
    seq = roots[i:] + roots[:i]
    rev = [seq[0]] + list(reversed(seq[1:]))
    return list(min(seq, rev))


@dataclass(frozen=True)
class RootMeta:
    root_trin: Tuple[int, ...]
    root_orbit: Tuple[int, ...]
    edge: Tuple[int, int]
    orbit_id: int
    phase_z6: int
    grade: str
    i27: int | None = None
    i3: int | None = None


def main() -> None:
    root_mod = _load_module(
        "verify_e8_root_system_from_trinification",
        ROOT / "tools" / "verify_e8_root_system_from_trinification.py",
    )

    # Trinification roots in Z^8 (E6 coroot basis + A2 coroot basis).
    e6_roots = root_mod.generate_roots_from_cartan(root_mod.E6_CARTAN)
    w27 = root_mod.load_e6_27_weights_from_chevalley()
    w3 = root_mod.a2_weights_fund3()
    a2_roots = root_mod.a2_roots_from_weights(w3)

    roots_trin: List[Tuple[int, ...]] = []
    seen = set()
    for r in e6_roots:
        t = tuple(list(r) + [0, 0])
        if t not in seen:
            roots_trin.append(t)
            seen.add(t)
    for r in a2_roots:
        t = tuple([0] * 6 + list(r))
        if t not in seen:
            roots_trin.append(t)
            seen.add(t)
    # mixed
    for mu in w27:
        for nu in w3:
            t1 = tuple(list(mu.tolist()) + list(nu.tolist()))
            t2 = tuple(list((-mu).tolist()) + list((-nu).tolist()))
            if t1 not in seen:
                roots_trin.append(t1)
                seen.add(t1)
            if t2 not in seen:
                roots_trin.append(t2)
                seen.add(t2)
    roots_trin = [r for r in roots_trin if r != tuple([0] * 8)]
    roots_trin = sorted(roots_trin)
    if len(roots_trin) != 240:
        raise RuntimeError(f"Expected 240 roots; got {len(roots_trin)}")

    # Recovered E8 simple roots (in the trinification Cartan coordinate system).
    dyn = json.loads(
        (ROOT / "artifacts" / "verify_e8_dynkin_from_trinification.json").read_text(
            encoding="utf-8"
        )
    )
    simples = np.array(dyn["simples"], dtype=int)
    M = simples.T.astype(float)

    # Permutation aligning the simple-root coefficient vector with the orbit-basis convention.
    sage_close = json.loads(
        (ROOT / "artifacts" / "sage_verify_e8_trinification_closeout.json").read_text(
            encoding="utf-8"
        )
    )
    perm_to_orbit = list(sage_close["perm_to_sage_canonical"])

    # orbit-basis root -> W33 edge
    root_to_edge_raw = json.loads(
        (ROOT / "artifacts" / "e8_root_to_edge.json").read_text(encoding="utf-8")
    )
    orbit_to_edge: Dict[Tuple[int, ...], Tuple[int, int]] = {
        _parse_root_key(k): (int(v[0]), int(v[1])) for k, v in root_to_edge_raw.items()
    }

    # orbit id and phase from canonical orbit ordering
    orbits = json.loads(
        (ROOT / "artifacts" / "e8_coxeter6_orbits.json").read_text(encoding="utf-8")
    )["orbits"]
    orbit_index: Dict[Tuple[int, ...], Tuple[int, int]] = {}
    for oid, orb in enumerate(orbits):
        ordered = _canon_orbit_order(orb)
        for pos, r in enumerate(ordered):
            orbit_index[r] = (int(oid), int(pos))
    if len(orbit_index) != 240:
        raise RuntimeError("Orbit index size mismatch")

    # Mixed root index lookup for g1/g2 classification
    mu_to_i = {tuple(int(x) for x in w27[i].tolist()): i for i in range(27)}
    nu_to_a = {tuple(int(x) for x in w3[a].tolist()): a for a in range(3)}

    def to_orbit_coords(r: Sequence[int]) -> Tuple[int, ...]:
        rr = np.array(r, dtype=float).reshape(8)
        coeff = np.linalg.solve(M, rr)
        ci = np.rint(coeff).astype(int)
        if not np.allclose(coeff, ci, atol=1e-8):
            raise RuntimeError("Non-integer simple coeffs")
        if not np.array_equal(
            (M @ ci.astype(float)).astype(int), np.array(r, dtype=int)
        ):
            raise RuntimeError("Coeff solve failed exact reconstruction")
        return tuple(int(ci[p]) for p in perm_to_orbit)

    rows: List[Dict[str, object]] = []
    grade_counts: Dict[str, int] = {}
    phase_counts: Dict[str, Dict[str, int]] = {}

    for r in roots_trin:
        r_orb = to_orbit_coords(r)
        edge = orbit_to_edge.get(r_orb)
        if edge is None:
            raise RuntimeError(f"Missing edge for orbit-root {r_orb}")
        oid, pos = orbit_index[r_orb]

        # grade classification
        r6 = r[:6]
        r2 = r[6:]
        grade = "unknown"
        i27 = None
        i3 = None
        if r2 == (0, 0) and r6 != (0, 0, 0, 0, 0, 0):
            grade = "g0_e6"
        elif r6 == (0, 0, 0, 0, 0, 0) and r2 != (0, 0):
            grade = "g0_a2"
        else:
            # g1 if r=(mu,nu) with mu in W27 and nu in W3; else g2 if r=(-mu,-nu).
            mu = tuple(int(x) for x in r6)
            nu = tuple(int(x) for x in r2)
            if mu in mu_to_i and nu in nu_to_a:
                grade = "g1"
                i27 = int(mu_to_i[mu])
                i3 = int(nu_to_a[nu])
            else:
                mu2 = tuple(int(-x) for x in r6)
                nu2 = tuple(int(-x) for x in r2)
                if mu2 in mu_to_i and nu2 in nu_to_a:
                    grade = "g2"
                    i27 = int(mu_to_i[mu2])
                    i3 = int(nu_to_a[nu2])
                else:
                    raise RuntimeError(f"Could not classify root {r}")

        grade_counts[grade] = grade_counts.get(grade, 0) + 1
        phase_counts.setdefault(grade, {})
        phase_counts[grade][str(pos)] = phase_counts[grade].get(str(pos), 0) + 1

        rows.append(
            RootMeta(
                root_trin=r,
                root_orbit=r_orb,
                edge=edge,
                orbit_id=oid,
                phase_z6=pos,
                grade=grade,
                i27=i27,
                i3=i3,
            ).__dict__
        )

    out = {
        "status": "ok",
        "counts": {
            "roots_total": 240,
            "by_grade": grade_counts,
        },
        "phase_z6_by_grade": phase_counts,
        "sources": {
            "e8_root_system_trinification": "tools/verify_e8_root_system_from_trinification.py",
            "e8_simple_system_trinification": "artifacts/verify_e8_dynkin_from_trinification.json",
            "perm_to_orbit_basis": "artifacts/sage_verify_e8_trinification_closeout.json",
            "e8_orbits": "artifacts/e8_coxeter6_orbits.json",
            "root_to_edge_orbit_basis": "artifacts/e8_root_to_edge.json",
        },
        "rows": rows,
    }

    out_json = ROOT / "artifacts" / "e8_root_metadata_table.json"
    out_md = ROOT / "artifacts" / "e8_root_metadata_table.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# E8 root metadata table\n")
    md.append("- status: `ok`")
    md.append(f"- roots_total: `{out['counts']['roots_total']}`")
    md.append(f"- by_grade: `{grade_counts}`\n")
    md.append("## Phase (Z6) histogram by grade\n")
    for g in sorted(phase_counts.keys()):
        md.append(f"- {g}: {phase_counts[g]}")
    md.append(f"\n- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"ok roots={len(rows)}")


if __name__ == "__main__":
    main()
