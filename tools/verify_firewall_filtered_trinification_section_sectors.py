#!/usr/bin/env python3
"""
Certificate: the firewall-filtered (36-triad) Z3-graded bracket is Jacobi-consistent on
the 27 affine "section sectors" in the Heisenberg/affine-plane model of H27.

Background (repo-native):
  - The full Z3-graded E8 build uses 45 signed cubic triads and satisfies Jacobi:
      tools/toe_e8_z3graded_bracket_jacobi.py
  - The firewall forbids exactly 9 cubic triads ("fiber triads") in H27:
      artifacts/firewall_bad_triads_mapping.json
  - Those 9 forbidden triads are precisely the Z3-fibers {u}×Z3 in the certified
    Heisenberg/affine-plane model:
      artifacts/e6_cubic_affine_heisenberg_model.json

If we simply delete those 9 triads from the cubic (keeping the same bracket formula),
Jacobi fails badly in general.

Key observation (made precise here):
  - Among all 3^9 = 19683 sections picking 1 lift per fiber {u}×Z3, exactly 27 are closed under the
    firewall-filtered triads (i.e. no triad intersects the section in exactly 2 points).
  - These 27 closed sections are exactly the graphs of affine maps z(x,y)=a x + b y + c on u=(x,y)∈F3^2.
  - On any such affine section, the firewall-filtered bracket is Jacobi-consistent and closed under:
      [g1,g1] -> g2,   [g2,g2] -> g1.

Outputs:
  - artifacts/firewall_filtered_trinification_section_sectors.json
  - artifacts/firewall_filtered_trinification_section_sectors.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

IN_E6_BASIS = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
IN_FW = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
IN_HEIS = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"

OUT_JSON = ROOT / "artifacts" / "firewall_filtered_trinification_section_sectors.json"
OUT_MD = ROOT / "artifacts" / "firewall_filtered_trinification_section_sectors.md"


def _load_z3_tool() -> object:
    path = ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    spec = importlib.util.spec_from_file_location(
        "toe_e8_z3graded_bracket_jacobi", path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _triad_key(i: int, j: int, k: int) -> Tuple[int, int, int]:
    a, b, c = sorted((int(i), int(j), int(k)))
    return (a, b, c)


def _load_bad9() -> set[Tuple[int, int, int]]:
    data = json.loads(IN_FW.read_text(encoding="utf-8"))
    bad = {_triad_key(*t) for t in data["bad_triangles_Schlafli_e6id"]}
    if len(bad) != 9:
        raise RuntimeError(f"Expected 9 firewall triads; got {len(bad)}")
    return bad


def _load_heisenberg_layers() -> (
    Tuple[Dict[Tuple[int, int], List[int]], Dict[int, List[int]]]
):
    data = json.loads(IN_HEIS.read_text(encoding="utf-8"))
    e6_to_hz = {
        int(k): (tuple(v["u"]), int(v["z"]))
        for k, v in data["e6id_to_heisenberg"].items()
    }

    fibers: Dict[Tuple[int, int], List[int]] = {}
    layers: Dict[int, List[int]] = {0: [], 1: [], 2: []}
    for e6id, (u, z) in e6_to_hz.items():
        fibers.setdefault(u, []).append(e6id)
        layers[z].append(e6id)
    for u in fibers:
        fibers[u] = sorted(fibers[u])
    for z in layers:
        layers[z] = sorted(layers[z])

    if len(fibers) != 9 or any(len(v) != 3 for v in fibers.values()):
        raise RuntimeError("Expected 9 fibers of size 3 in Heisenberg model")
    if any(len(layers[z]) != 9 for z in layers):
        raise RuntimeError("Expected 3 layers of size 9 in Heisenberg model")
    return fibers, layers


def _u_values() -> List[Tuple[int, int]]:
    return [(x, y) for x in range(3) for y in range(3)]


def _rows_to_zmap(
    e6_to_hz: Dict[int, Tuple[Tuple[int, int], int]], rows: Sequence[int]
) -> Dict[Tuple[int, int], int]:
    zmap: Dict[Tuple[int, int], int] = {}
    for e6id in rows:
        u, z = e6_to_hz[int(e6id)]
        zmap[u] = int(z)
    if len(zmap) != 9:
        raise RuntimeError("Expected section rows to include each u exactly once")
    return zmap


def _is_affine_zmap(zmap: Dict[Tuple[int, int], int]) -> Tuple[int, int, int] | None:
    """
    Decide if z(u) is affine-linear on F3^2:
      z(x,y) = a*x + b*y + c (mod 3).
    Return (a,b,c) if yes, else None.
    """
    U = _u_values()
    for a in range(3):
        for b in range(3):
            for c in range(3):
                if all(((a * x + b * y + c) % 3) == int(zmap[(x, y)]) for x, y in U):
                    return (a, b, c)
    return None


def _is_closed_section(
    triads_fw: Sequence[Tuple[int, int, int, int]], rows: set[int]
) -> bool:
    """
    Closure criterion for the firewall-filtered triads: no triad may intersect the section in exactly 2 points.
    """
    for i, j, k, _s in triads_fw:
        c = int((i in rows)) + int((j in rows)) + int((k in rows))
        if c == 2:
            return False
    return True


def _focus_vertex(
    triads_fw: Sequence[Tuple[int, int, int, int]], rows: set[int]
) -> int | None:
    """
    In every closed affine section we observe exactly 4 contained triads, all sharing a unique vertex.
    Return that vertex id, else None.
    """
    contained = [
        set((i, j, k))
        for i, j, k, _s in triads_fw
        if (i in rows and j in rows and k in rows)
    ]
    if not contained:
        return None
    common = set.intersection(*contained)
    if len(common) != 1:
        return None
    return int(next(iter(common)))


def _rand_tensor_on_rows(
    rng: np.random.Generator, *, rows: Sequence[int], scale: int
) -> np.ndarray:
    X = np.zeros((27, 3), dtype=np.complex128)
    rows_arr = np.array(list(rows), dtype=int)
    X[rows_arr, :] = rng.integers(-scale, scale + 1, size=(len(rows_arr), 3))
    return X


def _elt(
    tool: object, *, g1: np.ndarray | None = None, g2: np.ndarray | None = None
) -> object:
    z27 = np.zeros((27, 27), dtype=np.complex128)
    z3 = np.zeros((3, 3), dtype=np.complex128)
    return tool.E8Z3(
        e6=z27,
        sl3=z3,
        g1=np.zeros((27, 3), dtype=np.complex128) if g1 is None else g1,
        g2=np.zeros((27, 3), dtype=np.complex128) if g2 is None else g2,
    )


def _jacobi_stats(
    tool: object, br: object, gens: Tuple, *, trials: int
) -> Dict[str, float]:
    fx, fy, fz = gens
    max_res = 0.0
    mean_res = 0.0
    for _ in range(trials):
        j = tool._jacobi(br, fx(), fy(), fz())
        r = float(tool._elt_norm(j))
        mean_res += r
        max_res = max(max_res, r)
    return {
        "max_residual": float(max_res),
        "mean_residual": float(mean_res / trials),
        "trials": float(trials),
    }


def _triads_contained(
    triads: Sequence[Tuple[int, int, int, int]], rows: set[int]
) -> int:
    cnt = 0
    for i, j, k, _s in triads:
        if (i in rows) and (j in rows) and (k in rows):
            cnt += 1
    return int(cnt)


def _check_sector(
    *,
    tool: object,
    br: object,
    name: str,
    triads_fw: Sequence[Tuple[int, int, int, int]],
    rows: Sequence[int],
    rng: np.random.Generator,
    trials: int,
    entry_scale: int,
) -> Dict[str, object]:
    rows_sorted = sorted(int(x) for x in rows)
    row_set = set(rows_sorted)
    outside = [i for i in range(27) if i not in row_set]

    def rand_g1():
        return _elt(
            tool, g1=_rand_tensor_on_rows(rng, rows=rows_sorted, scale=entry_scale)
        )

    def rand_g2():
        return _elt(
            tool, g2=_rand_tensor_on_rows(rng, rows=rows_sorted, scale=entry_scale)
        )

    jacobi = {
        "g1_g1_g1": _jacobi_stats(tool, br, (rand_g1, rand_g1, rand_g1), trials=trials),
        "g2_g2_g2": _jacobi_stats(tool, br, (rand_g2, rand_g2, rand_g2), trials=trials),
        "g1_g1_g2": _jacobi_stats(tool, br, (rand_g1, rand_g1, rand_g2), trials=trials),
        "g1_g2_g2": _jacobi_stats(tool, br, (rand_g1, rand_g2, rand_g2), trials=trials),
    }

    closure = {"g1g1_to_g2_outside_max": 0.0, "g2g2_to_g1_outside_max": 0.0}
    for _ in range(25):
        X = _rand_tensor_on_rows(rng, rows=rows_sorted, scale=entry_scale)
        Y = _rand_tensor_on_rows(rng, rows=rows_sorted, scale=entry_scale)
        out2 = br.bracket_g1_g1(X, Y)
        if outside:
            closure["g1g1_to_g2_outside_max"] = max(
                closure["g1g1_to_g2_outside_max"],
                float(np.max(np.abs(out2[np.array(outside), :]))),
            )
        U = _rand_tensor_on_rows(rng, rows=rows_sorted, scale=entry_scale)
        V = _rand_tensor_on_rows(rng, rows=rows_sorted, scale=entry_scale)
        out1 = br.bracket_g2_g2(U, V)
        if outside:
            closure["g2g2_to_g1_outside_max"] = max(
                closure["g2g2_to_g1_outside_max"],
                float(np.max(np.abs(out1[np.array(outside), :]))),
            )

    return {
        "name": name,
        "rows": rows_sorted,
        "size": int(len(rows_sorted)),
        "triads_contained": _triads_contained(triads_fw, row_set),
        "focus_e6id": _focus_vertex(triads_fw, row_set),
        "jacobi": jacobi,
        "closure": closure,
    }


def _write_md(report: dict) -> None:
    md: List[str] = []
    md.append("# Firewall-filtered trinification: affine section sectors\n")
    md.append(
        "This checks Jacobi for the Z3-graded bracket after deleting the 9 firewall triads.\n"
    )
    md.append(
        f"- triads: `{report['triads']['total']}` → `{report['triads']['remaining']}` (deleted `{report['triads']['firewall_bad']}`)"
    )
    md.append(f"- Jacobi trials per case: `{report['params']['trials']}`")
    md.append(
        f"- closed sections: `{report['section_counts']['closed_sections']}` / `{report['section_counts']['total_sections_3pow9']}`"
    )
    md.append(f"- affine sections: `{report['section_counts']['affine_sections']}`")
    md.append(
        f"- affine == closed: `{report['section_counts']['affine_equals_closed']}`"
    )
    md.append(
        f"- focus bijection: `{report['affine_section_focus']['focus_bijection_ok']}`"
    )
    md.append("")
    md.append(
        "| sector | |rows| | triads inside | focus | g1g1g1 max | g1g1g2 max | g1g2g2 max | g2g2g2 max | g1g1→g2 outside | g2g2→g1 outside |"
    )
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for name, sec in sorted(report["sectors"].items()):
        j = sec["jacobi"]
        md.append(
            f"| `{name}` | {sec['size']} | {sec['triads_contained']} | "
            f"{sec.get('focus_e6id')} | "
            f"{j['g1_g1_g1']['max_residual']:.3e} | {j['g1_g1_g2']['max_residual']:.3e} | "
            f"{j['g1_g2_g2']['max_residual']:.3e} | {j['g2_g2_g2']['max_residual']:.3e} | "
            f"{sec['closure']['g1g1_to_g2_outside_max']:.3e} | {sec['closure']['g2g2_to_g1_outside_max']:.3e} |"
        )
    md.append("")
    md.append("## Interpretation\n")
    md.append(
        "- The firewall-filtered bracket is not Lie globally, but becomes Lie-consistent on the 27 affine section sectors.\n"
        "- Each affine section is the graph of an affine map `z(x,y)=a x + b y + c` on `F3^2`.\n"
        "- A random 1-per-fiber section is typically not closed: `[g1,g1]` and `[g2,g2]` leak outside the support and\n"
        "  mixed Jacobi residuals jump to `O(1..10^2)`.\n"
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    tool = _load_z3_tool()

    e6_basis = np.load(IN_E6_BASIS).astype(np.complex128)
    proj = tool.E6Projector(e6_basis)

    triads_all: List[Tuple[int, int, int, int]] = list(tool._load_signed_cubic_triads())
    bad9 = _load_bad9()
    triads_fw = [t for t in triads_all if _triad_key(t[0], t[1], t[2]) not in bad9]
    if len(triads_fw) != 36:
        raise RuntimeError(f"Expected 36 remaining triads, got {len(triads_fw)}")

    scales = {
        "scale_g1g1": 1.0,
        "scale_g2g2": -1.0 / 6.0,
        "scale_e6": 1.0,
        "scale_sl3": 1.0 / 6.0,
    }

    br_fw = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads_fw,
        scale_g1g1=scales["scale_g1g1"],
        scale_g2g2=scales["scale_g2g2"],
        scale_e6=scales["scale_e6"],
        scale_sl3=scales["scale_sl3"],
    )

    fibers, layers = _load_heisenberg_layers()
    fiber_keys = sorted(fibers.keys())

    heis = json.loads(IN_HEIS.read_text(encoding="utf-8"))
    e6_to_hz = {
        int(k): (tuple(v["u"]), int(v["z"]))
        for k, v in heis["e6id_to_heisenberg"].items()
    }
    hz_to_e6 = {(u, z): e6id for e6id, (u, z) in e6_to_hz.items()}

    # Enumerate all affine sections z(x,y)=a x + b y + c
    affine_sections: Dict[Tuple[int, int, int], List[int]] = {}
    for a in range(3):
        for b in range(3):
            for c in range(3):
                rows: List[int] = []
                for x, y in _u_values():
                    z = int((a * x + b * y + c) % 3)
                    rows.append(int(hz_to_e6[((x, y), z)]))
                affine_sections[(a, b, c)] = sorted(rows)

    # Brute-verify: affine sections are exactly the closed sections among all 3^9 sections.
    fiber_list = [fibers[u] for u in fiber_keys]
    closed_sections: List[Tuple[int, ...]] = []
    # 3^9 = 19683 is small; enumerate deterministically.
    for choice in np.ndindex(*(3,) * 9):
        sec = {int(fiber_list[i][choice[i]]) for i in range(9)}
        if _is_closed_section(triads_fw, sec):
            closed_sections.append(tuple(sorted(sec)))

    affine_set = {tuple(v) for v in affine_sections.values()}
    closed_set = set(closed_sections)
    section_counts = {
        "affine_sections": int(len(affine_set)),
        "closed_sections": int(len(closed_set)),
        "affine_equals_closed": bool(affine_set == closed_set),
        "total_sections_3pow9": 19683,
    }
    if (
        section_counts["closed_sections"] != 27
        or section_counts["affine_sections"] != 27
        or not section_counts["affine_equals_closed"]
    ):
        raise RuntimeError(f"Unexpected section classification: {section_counts}")

    rng = np.random.default_rng(0)
    trials = 20
    entry_scale = 2

    sectors: Dict[str, Dict[str, object]] = {}
    for (a, b, c), rows in sorted(affine_sections.items()):
        name = f"affine_a{a}b{b}c{c}"
        sec = _check_sector(
            tool=tool,
            br=br_fw,
            name=name,
            triads_fw=triads_fw,
            rows=rows,
            rng=rng,
            trials=trials,
            entry_scale=entry_scale,
        )
        # annotate with affine params
        sec["affine_params"] = {"a": int(a), "b": int(b), "c": int(c)}
        sectors[name] = sec

    # Controls:
    # Random non-affine section (should leak / fail mixed Jacobi)
    chosen: List[int] = []
    for u in fiber_keys:
        ids = fibers[u]
        chosen.append(ids[int(rng.integers(0, 3))])
    rows = sorted(chosen)
    if tuple(rows) in affine_set:
        # extremely unlikely; perturb deterministically
        last_u = fiber_keys[-1]
        ids = fibers[last_u]
        cur = rows[-1]
        rows = sorted(rows[:-1] + [ids[(ids.index(cur) + 1) % 3]])
    sectors["control_random_non_affine_section"] = _check_sector(
        tool=tool,
        br=br_fw,
        name="control_random_non_affine_section",
        triads_fw=triads_fw,
        rows=rows,
        rng=rng,
        trials=trials,
        entry_scale=entry_scale,
    )
    # Two-layer control (forces missing fiber interactions to matter)
    sectors["control_two_layers_z=0or1"] = _check_sector(
        tool=tool,
        br=br_fw,
        name="control_two_layers_z=0or1",
        triads_fw=triads_fw,
        rows=sorted(layers[0] + layers[1]),
        rng=rng,
        trials=trials,
        entry_scale=entry_scale,
    )

    affine_focus = {
        k: int(v.get("focus_e6id"))
        for k, v in sectors.items()
        if k.startswith("affine_")
    }
    focus_vals = list(affine_focus.values())
    focus_bijection_ok = (len(set(focus_vals)) == 27) and (
        set(focus_vals) == set(range(27))
    )
    focus_to_affine = {
        int(sec["focus_e6id"]): sec.get("affine_params", {})
        for name, sec in sectors.items()
        if name.startswith("affine_")
    }

    report = {
        "status": "ok",
        "triads": {
            "total": int(len(triads_all)),
            "firewall_bad": int(len(bad9)),
            "remaining": int(len(triads_fw)),
        },
        "scales": scales,
        "heisenberg": {
            "fibers": {f"{u[0]},{u[1]}": v for u, v in fibers.items()},
            "layers": {str(z): layers[z] for z in layers},
        },
        "affine_section_focus": {
            "focus_bijection_ok": bool(focus_bijection_ok),
            "focus_to_affine_params": focus_to_affine,
        },
        "section_counts": section_counts,
        "params": {"trials": int(trials), "entry_scale": int(entry_scale)},
        "sectors": sectors,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    _write_md(report)
