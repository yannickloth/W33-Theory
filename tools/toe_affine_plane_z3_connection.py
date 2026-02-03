#!/usr/bin/env python3
"""
TOE: Affine-plane (AG(2,3)) + Z3 lift "connection" model.

This script is a *compression layer* over existing verified artifacts:

- The firewall quotient of the 27 cubic-triad vertices produces:
    9 blocks (bad triads) = 9 points
    12 block-triples from allowed triads = 12 lines
  i.e. the affine plane AG(2,3) (aka the Hesse (9_4, 12_3) configuration).

- The Z3 kernel element acts as 9 disjoint 3-cycles on the 27 vertices, giving
  "3 lifts per line". The `toe_z3_lift_constraint` computation finds block-wise
  offsets that gauge-fix the lift coordinate so every triad satisfies
      t'(u) + t'(v) + t'(w) == 0  (mod 3).

Here we:
  1) build a canonical coordinate model for the 9 blocks as F3^2 using two
     parallel classes (deterministic choice),
  2) compute per-line lift patterns (t'-vectors) and their Z3-translation orbits,
  3) compute the induced affine "slope" lambda per line along its canonical
     parameterization.

Outputs:
  - artifacts/toe_affine_plane_z3_connection.json
  - artifacts/toe_affine_plane_z3_connection.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mod3(x: int) -> int:
    return int(x) % 3


def _sorted_tuple(xs: Iterable[int]) -> Tuple[int, ...]:
    return tuple(sorted(int(x) for x in xs))


def _parallel_classes(
    lines: List[Tuple[int, int, int]]
) -> List[List[Tuple[int, int, int]]]:
    """All parallel classes: 3 disjoint lines covering all 9 points."""
    lines = sorted(set(lines))
    classes = []
    for comb in combinations(lines, 3):
        a, b, c = map(set, comb)
        if (a & b) or (a & c) or (b & c):
            continue
        if len(a | b | c) != 9:
            continue
        classes.append(frozenset(comb))

    uniq = sorted(set(classes), key=lambda fs: tuple(sorted(tuple(l) for l in fs)))
    return [sorted(list(fs)) for fs in uniq]


def _choose_axes(
    parallel: List[List[Tuple[int, int, int]]]
) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
    """
    Deterministically pick two parallel classes to define x- and y- axes.

    Any pair of distinct classes works; we pick the first two in canonical order.
    """
    if len(parallel) != 4:
        raise RuntimeError(f"Expected 4 parallel classes, got {len(parallel)}")
    return parallel[0], parallel[1]


def _coords_from_axes(
    x_class: List[Tuple[int, int, int]],
    y_class: List[Tuple[int, int, int]],
) -> Dict[int, Tuple[int, int]]:
    x_class = sorted(x_class)
    y_class = sorted(y_class)
    x_line_to_val = {line: i for i, line in enumerate(x_class)}
    y_line_to_val = {line: i for i, line in enumerate(y_class)}

    coords: Dict[int, Tuple[int, int]] = {}
    for b in range(9):
        x = next((val for line, val in x_line_to_val.items() if b in line), None)
        y = next((val for line, val in y_line_to_val.items() if b in line), None)
        if x is None or y is None:
            raise RuntimeError("Axis classes do not cover all 9 blocks")
        coords[b] = (int(x), int(y))
    if len(set(coords.values())) != 9:
        raise RuntimeError("Coordinate assignment is not bijective on 9 blocks")
    return coords


def _classify_line_equation(
    line: Tuple[int, int, int],
    coords: Dict[int, Tuple[int, int]],
) -> dict:
    pts = [coords[b] for b in line]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if len(set(xs)) == 1:
        return {"type": "x", "c": xs[0]}
    if len(set(ys)) == 1:
        return {"type": "y", "c": ys[0]}
    for m in (1, 2):
        cs = {(_mod3(y - m * x)) for x, y in pts}
        if len(cs) == 1:
            return {"type": "y=mx+c", "m": m, "c": next(iter(cs))}
    return {"type": "unknown"}


def _ordered_blocks_on_line(
    line: Tuple[int, int, int],
    coords: Dict[int, Tuple[int, int]],
    eq: dict,
) -> Tuple[int, int, int]:
    pts = [(b, coords[b]) for b in line]
    if eq["type"] == "x":
        return tuple(b for b, _ in sorted(pts, key=lambda kv: kv[1][1]))  # sort by y
    if eq["type"] in {"y", "y=mx+c"}:
        return tuple(b for b, _ in sorted(pts, key=lambda kv: kv[1][0]))  # sort by x
    return line


def main() -> None:
    dual_path = ROOT / "artifacts" / "toe_affine_plane_duality.json"
    z3_path = ROOT / "artifacts" / "toe_z3_lift_constraint.json"
    dual = _load_json(dual_path)
    z3 = _load_json(z3_path)

    if dual.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_duality.json status != ok")
    if z3.get("status") != "ok":
        raise RuntimeError("toe_z3_lift_constraint.json status != ok")

    bad_triads = [_sorted_tuple(t) for t in dual["firewall"]["bad_triads"]]
    kernel_cycles = [
        [int(v) for v in cyc] for cyc in dual["kernel_z3"]["cycle_decomposition"]
    ]
    offsets = [int(x) for x in z3["blocks"]["offsets_z3"]]
    if len(bad_triads) != 9:
        raise RuntimeError(f"Expected 9 bad triads, got {len(bad_triads)}")
    if len(kernel_cycles) != 9 or any(len(c) != 3 for c in kernel_cycles):
        raise RuntimeError("Expected 9 kernel cycles of length 3")
    if len(offsets) != 9:
        raise RuntimeError(f"Expected 9 offsets, got {len(offsets)}")

    block_of: Dict[int, int] = {}
    t_raw: Dict[int, int] = {}
    for bi, cyc in enumerate(kernel_cycles):
        for t, v in enumerate(cyc):
            if v in block_of:
                raise RuntimeError("Vertex appears in multiple kernel cycles")
            block_of[v] = bi
            t_raw[v] = t
    if len(block_of) != 27:
        raise RuntimeError("Expected 27 vertices covered by cycles")

    def t_shifted(v: int) -> int:
        return _mod3(t_raw[v] + offsets[block_of[v]])

    # Invert (block, t_shifted) -> vertex (unique within each block).
    vertex_by_block_t: Dict[int, Dict[int, int]] = {b: {} for b in range(9)}
    for v in range(27):
        b = block_of[v]
        t = t_shifted(v)
        if t in vertex_by_block_t[b]:
            raise RuntimeError("Duplicate t_shifted label in a block")
        vertex_by_block_t[b][t] = v
    if any(len(m) != 3 for m in vertex_by_block_t.values()):
        raise RuntimeError("Each block must realize all 3 t_shifted labels")

    # Lines from duality file (block triples) with their allowed triads.
    line_rows = dual["duality_by_line"]
    if not (isinstance(line_rows, list) and len(line_rows) == 12):
        raise RuntimeError("Expected duality_by_line list of length 12")

    line_blocks_sorted: List[Tuple[int, int, int]] = []
    line_blocks_given: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
    line_to_triads: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]] = {}

    for row in line_rows:
        blocks_g = tuple(int(x) for x in row["line_blocks"])
        blocks = _sorted_tuple(blocks_g)
        if len(blocks) != 3 or len(set(blocks)) != 3:
            raise RuntimeError("Each line_blocks must be 3 distinct blocks")
        line_blocks_sorted.append(blocks)
        line_blocks_given[blocks] = blocks_g
        tris = [tuple(int(v) for v in tri) for tri in row["allowed_triads_cycle"]]
        if len(tris) != 3:
            raise RuntimeError("Expected 3 allowed triads per line")
        line_to_triads[blocks] = tris

    line_blocks_sorted = sorted(set(line_blocks_sorted))
    if len(line_blocks_sorted) != 12:
        raise RuntimeError(f"Expected 12 distinct lines, got {len(line_blocks_sorted)}")

    parallel = _parallel_classes(line_blocks_sorted)
    x_class, y_class = _choose_axes(parallel)
    coords = _coords_from_axes(x_class, y_class)

    # Assemble block metadata.
    blocks_out = []
    for b in range(9):
        vs = kernel_cycles[b]
        blocks_out.append(
            {
                "id": b,
                "coord_f3_2": list(coords[b]),
                "offset_z3": offsets[b],
                "vertices": [
                    {
                        "v": int(v),
                        "t_raw": int(t_raw[int(v)]),
                        "t_shifted": int(t_shifted(int(v))),
                    }
                    for v in vs
                ],
            }
        )

    # Per-line lift patterns and affine parameterization.
    lines_out = []
    orbit_type_hist = Counter()
    lambda_hist = Counter()
    # For discovering a closed-form lambda(c) per direction family.
    lam_samples_by_family: Dict[Tuple[str, int | None], Dict[int, int]] = defaultdict(
        dict
    )
    for line in line_blocks_sorted:
        eq = _classify_line_equation(line, coords)
        ordered_blocks = _ordered_blocks_on_line(line, coords, eq)
        tris = line_to_triads[line]

        # Helper: t-vector along specified block order for this triad.
        def triad_tvec(
            tri: Tuple[int, int, int], block_order: Tuple[int, int, int]
        ) -> Tuple[int, int, int]:
            by_block: Dict[int, int] = {}
            for v in tri:
                b = block_of[v]
                if b in by_block:
                    raise RuntimeError("Triad contains two vertices from same block")
                by_block[b] = v
            if set(by_block) != set(block_order):
                raise RuntimeError("Triad does not match its line blocks")
            return tuple(t_shifted(by_block[b]) for b in block_order)

        # Triad vectors in the (given) line-block order.
        blocks_given = line_blocks_given.get(line, line)
        triad_vectors_given = [triad_tvec(tri, blocks_given) for tri in tris]

        # Z3-translation orbit invariant: differences relative to first component.
        diffs = {(_mod3(v[1] - v[0]), _mod3(v[2] - v[0])) for v in triad_vectors_given}
        if len(diffs) != 1:
            raise RuntimeError(
                "Expected line lift vectors to be Z3 translates (diff-invariant)"
            )
        d1, d2 = next(iter(diffs))
        orbit_type = (0, d1, d2)
        orbit_type_hist[orbit_type] += 1

        # Along the canonical line parameterization, each lift is an affine line in Z3 with slope lambda.
        triad_vectors_param = [triad_tvec(tri, ordered_blocks) for tri in tris]
        diffs_param = {
            (_mod3(v[1] - v[0]), _mod3(v[2] - v[0])) for v in triad_vectors_param
        }
        if len(diffs_param) != 1:
            raise RuntimeError(
                "Expected parameterized lift vectors to be Z3 translates (diff-invariant)"
            )
        lam = diffs_param.pop()[0]
        # Must satisfy v2-v0 = 2*lam (mod 3)
        for v in triad_vectors_param:
            if _mod3(v[2] - v[0]) != _mod3(2 * lam):
                raise RuntimeError(
                    "Parameterized lift vectors are not affine-linear in the line parameter"
                )
        lambda_hist[int(lam)] += 1
        # Record samples keyed by (family, slope) with intercept c -> lambda.
        if eq["type"] == "y=mx+c":
            fam = ("y=mx+c", int(eq["m"]))
            c = int(eq["c"])
        else:
            fam = (str(eq["type"]), None)
            c = int(eq["c"]) if "c" in eq else 0
        lam_samples_by_family[fam][c] = int(lam)

        lines_out.append(
            {
                "blocks": list(line),
                "blocks_given_order": list(blocks_given),
                "coord_f3_2": [list(coords[b]) for b in line],
                "equation": eq,
                "ordered_blocks": list(ordered_blocks),
                "lift_orbit_type": list(orbit_type),
                "lambda": int(lam),
                "allowed_triads_cycle": [
                    {
                        "vertices": list(tri),
                        "t_shifted_given_order": list(vec_g),
                        "t_shifted_param_order": list(vec_p),
                    }
                    for tri, vec_g, vec_p in zip(
                        tris, triad_vectors_given, triad_vectors_param
                    )
                ],
            }
        )

    # Fit lambda(c) = a*c + b over F3 for each family (three samples at c=0,1,2).
    lambda_laws = {}
    for fam, samples in sorted(lam_samples_by_family.items()):
        if set(samples.keys()) != {0, 1, 2}:
            raise RuntimeError(f"Incomplete lambda samples for {fam}: {samples}")
        b = _mod3(samples[0])
        a = _mod3(samples[1] - b)
        # sanity check at c=2
        if _mod3(a * 2 + b) != _mod3(samples[2]):
            raise RuntimeError(f"Bad F3 fit for {fam}: a={a}, b={b}, samples={samples}")
        lambda_laws[str(fam)] = {"a": int(a), "b": int(b), "samples": dict(samples)}

    # Compile allowed triads using ONLY (blocks coords + fitted lambda laws + block t_shifted labels).
    compiled_allowed = set()
    for line_obj in lines_out:
        eq = line_obj["equation"]
        ordered_blocks = [int(x) for x in line_obj["ordered_blocks"]]
        if eq["type"] == "y=mx+c":
            fam_key = str(("y=mx+c", int(eq["m"])))
        else:
            fam_key = str((str(eq["type"]), None))
        law = lambda_laws[fam_key]
        c = int(eq.get("c", 0))
        lam = _mod3(law["a"] * c + law["b"])
        for k in range(3):
            tvals = [_mod3(k + i * lam) for i in range(3)]
            tri = tuple(
                sorted(vertex_by_block_t[b][t] for b, t in zip(ordered_blocks, tvals))
            )
            compiled_allowed.add(tri)

    actual_allowed = set()
    for tris in line_to_triads.values():
        for tri in tris:
            actual_allowed.add(tuple(sorted(int(v) for v in tri)))

    if compiled_allowed != actual_allowed:
        missing = sorted(actual_allowed - compiled_allowed)
        extra = sorted(compiled_allowed - actual_allowed)
        raise RuntimeError(
            "Compiled triads do not match reference allowed triads "
            f"(missing={len(missing)}, extra={len(extra)})."
        )

    # Summarize parallel classes and line-type distribution per class.
    line_type_by_line = {
        tuple(l["blocks"]): tuple(l["lift_orbit_type"]) for l in lines_out
    }
    parallel_out = []
    for cls in parallel:
        cls_types = [line_type_by_line[line] for line in cls]
        parallel_out.append(
            {
                "lines": [list(line) for line in cls],
                "lift_orbit_types": [list(t) for t in cls_types],
                "lift_orbit_type_hist": {
                    str(k): int(v) for k, v in sorted(Counter(cls_types).items())
                },
            }
        )

    out = {
        "status": "ok",
        "sources": {
            "toe_affine_plane_duality": str(dual_path),
            "toe_z3_lift_constraint": str(z3_path),
        },
        "counts": {
            "blocks": 9,
            "vertices": 27,
            "affine_lines": 12,
            "parallel_classes": 4,
            "orbit_type_hist": {
                str(k): int(v) for k, v in sorted(orbit_type_hist.items())
            },
            "lambda_hist": {str(k): int(v) for k, v in sorted(lambda_hist.items())},
        },
        "lambda_laws_f3": lambda_laws,
        "compiled_allowed_triads_match_reference": True,
        "axes": {
            "x_parallel_class": [list(line) for line in x_class],
            "y_parallel_class": [list(line) for line in y_class],
        },
        "blocks": blocks_out,
        "parallel_classes": parallel_out,
        "lines": sorted(lines_out, key=lambda d: tuple(d["blocks"])),
    }

    json_path = ROOT / "artifacts" / "toe_affine_plane_z3_connection.json"
    md_path = ROOT / "artifacts" / "toe_affine_plane_z3_connection.md"
    _write_json(json_path, out)

    md = []
    md.append("# TOE affine-plane + Z3 lift connection (derived artifact)")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Orbit-type histogram (t'-vectors modulo global Z3 shift)")
    for k, v in out["counts"]["orbit_type_hist"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Lambda histogram (slope along canonical line parameter)")
    for k, v in out["counts"]["lambda_hist"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Closed-form lambda laws (per affine-line family)")
    md.append(
        "Each family is fitted as `lambda(c) = a*c + b (mod 3)` in our coordinate gauge."
    )
    for fam, law in out["lambda_laws_f3"].items():
        md.append(f"- {fam}: a={law['a']}, b={law['b']}, samples={law['samples']}")
    md.append("")
    md.append("## Compiler check")
    md.append(
        "- Using only the fitted lambda laws + (block,t') labels, we exactly reconstruct the 36 allowed triads."
    )
    md.append("")
    md.append("## Axes (chosen parallel classes)")
    md.append(f"- x: {out['axes']['x_parallel_class']}")
    md.append(f"- y: {out['axes']['y_parallel_class']}")
    md.append("")
    md.append("## Notes")
    md.append(
        "- `t_shifted = t_raw + offset[block] (mod 3)` is the gauge-fixed Z3 lift label."
    )
    md.append(
        "- Each affine line has 3 lifted triads, forming a Z3 orbit under the kernel action."
    )
    _write_md(md_path, "\n".join(md) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
