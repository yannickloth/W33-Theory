#!/usr/bin/env python3
"""
Analyze how the 9 firewall-forbidden Schläfli triads sit relative to the 36 double-sixes.

Inputs (existing artifacts / constructions):
  - `tools/compute_double_sixes.py`: constructs E8 roots, W(E6) orbits, and Schläfli SRG(27,16,10,8).
  - `artifacts/we6_signed_action_on_27.json`: declares the reference 27-orbit index used elsewhere.
  - `artifacts/firewall_bad_triads_mapping.json`: provides the 9 forbidden triads in Schläfli orbit-local
    indices (0..26) and in canonical E6-id indices (0..26).
  - `tools/solve_canonical_su3_gauge_and_cubic.py` + `artifacts/canonical_su3_gauge_and_cubic.json`:
    supplies the orbit-local -> canonical E6-id mapping for that 27-orbit.

For each double-six (A,B,match), we partition the 27 vertices as:
  - A (6), B (6), R (15) = remaining
and compute intersection patterns of the forbidden triads with A/B/R.

Additionally, for each double-six we build the canonical PG(3,2) structure on R by labeling the
15 remaining vertices as duads C(6,2) determined by which TWO A-vertices they fail to be adjacent to.
We then classify any forbidden triad entirely contained in R as a PG(3,2) line type:
  - triangle-line (3-subset i,j,k),
  - matching-line (perfect matching ab|cd|ef).

Writes:
  - artifacts/bad_triads_vs_double_sixes.json
  - artifacts/bad_triads_vs_double_sixes.md
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
canon = _load_module(
    ROOT / "tools" / "solve_canonical_su3_gauge_and_cubic.py",
    "solve_canonical_su3_gauge_and_cubic",
)


def _pg32_lines_on_duads() -> (
    Dict[str, List[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]]
):
    """
    PG(3,2) model via K6 edges (duads):
      points = duads C(6,2)
      lines  = 20 triangle-lines + 15 matching-lines.
    """
    triangle_lines: List[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]] = []
    for i, j, k in itertools.combinations(range(6), 3):
        triangle_lines.append(((i, j), (j, k), (i, k)))

    matching_lines: List[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]] = []
    letters = list(range(6))
    for a, b, c, d, e, f in itertools.permutations(letters, 6):
        # canonicalize to avoid duplicates: enforce a<b, c<d, e<f and ordered by first elements.
        pairs = tuple(
            sorted(
                (tuple(sorted((a, b))), tuple(sorted((c, d))), tuple(sorted((e, f))))
            )
        )
        if len(set(pairs)) != 3:
            continue
        # must be a perfect matching (disjoint pairs)
        flat = [x for p in pairs for x in p]
        if len(set(flat)) != 6:
            continue
        matching_lines.append(pairs)  # type: ignore[arg-type]
    # de-duplicate (the permutations method generates repeats)
    matching_lines = sorted(set(matching_lines))
    if len(matching_lines) != 15:
        raise RuntimeError(f"Expected 15 matching-lines, got {len(matching_lines)}")

    triangle_lines = sorted(
        tuple(tuple(sorted(p)) for p in line) for line in triangle_lines
    )
    if len(triangle_lines) != 20:
        raise RuntimeError(f"Expected 20 triangle-lines, got {len(triangle_lines)}")

    return {"triangle": triangle_lines, "matching": matching_lines}


PG32_LINES = _pg32_lines_on_duads()
PG32_LINESET = {
    "triangle": set(tuple(sorted(line)) for line in PG32_LINES["triangle"]),
    "matching": set(tuple(sorted(line)) for line in PG32_LINES["matching"]),
}


def _canonical_double_six_labeling(
    adj: np.ndarray, ds: tuple[tuple[int, ...], tuple[int, ...], dict[int, int]]
) -> tuple[list[int], list[int], dict[tuple[int, int], int]]:
    """
    Canonicalize a double-six enough to define duads on the 15 remaining vertices.

    - Order A ascending.
    - Order B by the matching from A.
    - For each remaining vertex v, define its duad (i,j) by the two A positions it is *not* adjacent to.
    """
    A, B, match = ds
    A_pos = sorted(int(x) for x in A)
    B_pos = [int(match[a]) for a in A_pos]
    A_set = set(A_pos)
    B_set = set(B_pos)
    rem = [v for v in range(adj.shape[0]) if v not in A_set and v not in B_set]
    if len(rem) != 15:
        raise RuntimeError("Expected 15 remaining vertices")

    a_index = {a: i for i, a in enumerate(A_pos)}
    rem_by_duad: Dict[tuple[int, int], int] = {}
    for v in rem:
        nonA = [a_index[a] for a in A_pos if not bool(adj[v, a])]
        if len(nonA) != 2:
            raise RuntimeError("Remaining vertex does not have 2 non-neighbors in A")
        i, j = sorted(nonA)
        key = (int(i), int(j))
        if key in rem_by_duad:
            raise RuntimeError("Duad label collision")
        rem_by_duad[key] = int(v)
    if len(rem_by_duad) != 15:
        raise RuntimeError("Expected 15 duads")
    return A_pos, B_pos, rem_by_duad


def _ds_to_e6id(
    ds: tuple[tuple[int, ...], tuple[int, ...], dict[int, int]], pos_to_e6id: list[int]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    A, B, _ = ds
    Ae = tuple(sorted(pos_to_e6id[int(v)] for v in A))
    Be = tuple(sorted(pos_to_e6id[int(v)] for v in B))
    # canonical orientation up to swapping A/B
    return (Ae, Be) if Ae <= Be else (Be, Ae)


@dataclass(frozen=True)
class DoubleSixAnalysis:
    ds_key: Tuple[
        Tuple[int, ...], Tuple[int, ...]
    ]  # (A_e6id, B_e6id) oriented canonically
    A_orbit: Tuple[int, ...]
    B_orbit: Tuple[int, ...]
    R_orbit: Tuple[int, ...]
    bad_pattern_hist: Dict[str, int]  # key like "A1B2R0"
    bad_rrr_count: int
    bad_rrr_pg32_types: Dict[str, int]  # triangle/matching/none
    bad_rrr_triads_orbit: Tuple[Tuple[int, int, int], ...]
    bad_rrr_triads_duads: Tuple[
        Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]], ...
    ]
    bad_a1b1r1_triads_orbit: Tuple[Tuple[int, int, int], ...]


def compute_bad_triads_vs_double_sixes() -> dict:
    act = json.loads(
        (ROOT / "artifacts" / "we6_signed_action_on_27.json").read_text(
            encoding="utf-8"
        )
    )
    oi_ref = int(act["reference_orbit"]["orbit_index"])

    mapping = json.loads(
        (ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text(
            encoding="utf-8"
        )
    )
    bad_triads_orbit = [
        tuple(int(x) for x in t) for t in mapping["bad_triangles_Schlafli_orbit_index"]
    ]
    bad_triads_e6id = [
        tuple(int(x) for x in t) for t in mapping["bad_triangles_Schlafli_e6id"]
    ]
    if len(bad_triads_orbit) != 9 or len(bad_triads_e6id) != 9:
        raise RuntimeError("Expected exactly 9 forbidden triads")

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    o27 = orbits[oi_ref]
    schlafli_adj, _ = cds.build_schlafli_adjacency(roots, o27)

    ok, msg = cds.verify_srg(schlafli_adj, 27, 16, 10, 8)
    if not ok:
        raise RuntimeError(f"Schläfli SRG check failed: {msg}")

    # orbit-local -> canonical E6-id mapping (used by selection/cubic artifacts)
    canon_data = json.loads(
        (ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json").read_text(
            encoding="utf-8"
        )
    )
    e6_keys_27 = [tuple(int(x) for x in k) for k in canon_data["e6_keys_27_k2"]]
    key_to_e6id = {k: i for i, k in enumerate(e6_keys_27)}
    pos_to_e6id: list[int] = []
    for pos, ridx in enumerate(o27):
        kk = canon.e6_key(roots[ridx])
        eid = key_to_e6id.get(tuple(int(x) for x in kk))
        if eid is None:
            raise RuntimeError("Failed to map orbit vertex to canonical E6 id")
        pos_to_e6id.append(int(eid))
    if sorted(pos_to_e6id) != list(range(27)):
        raise RuntimeError("orbit->E6-id mapping is not a permutation of 0..26")

    k6 = cds.find_k_cliques(schlafli_adj, 6)
    ds_list = cds.find_double_sixes(schlafli_adj, k6)
    if len(ds_list) != 36:
        raise RuntimeError(f"Expected 36 double-sixes, got {len(ds_list)}")

    analyses: List[DoubleSixAnalysis] = []
    for ds in ds_list:
        A, B, _ = ds
        A_set = set(int(x) for x in A)
        B_set = set(int(x) for x in B)
        if len(A_set) != 6 or len(B_set) != 6 or A_set & B_set:
            raise RuntimeError("Malformed double-six (sizes or overlap)")
        R = tuple(sorted(v for v in range(27) if v not in A_set and v not in B_set))

        # duad labeling / PG(3,2) structure on R
        A_pos, _, rem_by_duad = _canonical_double_six_labeling(schlafli_adj, ds)
        rem_duad_by_vertex = {v: duad for duad, v in rem_by_duad.items()}
        if set(rem_duad_by_vertex.keys()) != set(R):
            raise RuntimeError("Duad labeling did not cover exactly the remaining15")

        # forbidden triad intersection patterns
        hist = Counter()
        bad_rrr = []
        bad_a1b1r1 = []
        for t in bad_triads_orbit:
            a = sum(1 for x in t if x in A_set)
            b = sum(1 for x in t if x in B_set)
            r = 3 - a - b
            hist[f"A{a}B{b}R{r}"] += 1
            if r == 3:
                bad_rrr.append(tuple(sorted(t)))
            if (a, b, r) == (1, 1, 1):
                bad_a1b1r1.append(tuple(sorted(t)))
        bad_rrr = sorted(set(bad_rrr))
        bad_a1b1r1 = sorted(set(bad_a1b1r1))

        # PG(3,2) classification for the RRR forbidden triads
        pg32_types = Counter()
        bad_rrr_duads = []
        for t in bad_rrr:
            duads = tuple(sorted(tuple(sorted(rem_duad_by_vertex[int(v)])) for v in t))  # type: ignore[arg-type]
            bad_rrr_duads.append(duads)
            if duads in PG32_LINESET["triangle"]:
                pg32_types["triangle"] += 1
            elif duads in PG32_LINESET["matching"]:
                pg32_types["matching"] += 1
            else:
                pg32_types["none"] += 1
        bad_rrr_duads = tuple(bad_rrr_duads)

        ds_key = _ds_to_e6id(ds, pos_to_e6id)
        analyses.append(
            DoubleSixAnalysis(
                ds_key=ds_key,
                A_orbit=tuple(sorted(A_set)),
                B_orbit=tuple(sorted(B_set)),
                R_orbit=R,
                bad_pattern_hist=dict(hist),
                bad_rrr_count=len(bad_rrr),
                bad_rrr_pg32_types=dict(pg32_types),
                bad_rrr_triads_orbit=tuple(bad_rrr),
                bad_rrr_triads_duads=bad_rrr_duads,
                bad_a1b1r1_triads_orbit=tuple(bad_a1b1r1),
            )
        )

    analyses_sorted = sorted(analyses, key=lambda x: x.ds_key)

    # rank by "how much of the forbidden set can be pushed into R" (pure-remaining triads)
    ranked = sorted(
        analyses_sorted,
        key=lambda x: (
            x.bad_rrr_count,
            x.bad_rrr_pg32_types.get("triangle", 0),
            x.ds_key,
        ),
        reverse=True,
    )

    # global invariants across all 36 double-sixes
    pattern_histograms = Counter(
        tuple(sorted(x.bad_pattern_hist.items())) for x in analyses_sorted
    )
    pg32_type_histograms = Counter(
        tuple(sorted(x.bad_rrr_pg32_types.items())) for x in analyses_sorted
    )

    # sanity: bad triads are the same 9 in orbit-local and e6id; store both.
    results = {
        "status": "ok",
        "reference_orbit_index": oi_ref,
        "bad_triads": {
            "orbit_local": [list(t) for t in sorted(bad_triads_orbit)],
            "e6id": [list(t) for t in sorted(bad_triads_e6id)],
        },
        "counts": {
            "double_sixes": 36,
            "bad_triads": 9,
            "pg32_triangle_lines": len(PG32_LINES["triangle"]),
            "pg32_matching_lines": len(PG32_LINES["matching"]),
        },
        "invariants_over_all_double_sixes": {
            "bad_pattern_histograms": [
                {"hist": [[k, v] for k, v in hist], "count": int(n)}
                for hist, n in pattern_histograms.items()
            ],
            "bad_rrr_pg32_type_histograms": [
                {"types": [[k, v] for k, v in types], "count": int(n)}
                for types, n in pg32_type_histograms.items()
            ],
        },
        "ranked_by_bad_rrr": [
            {
                "ds_key_e6id": [list(x.ds_key[0]), list(x.ds_key[1])],
                "bad_pattern_hist": x.bad_pattern_hist,
                "bad_rrr_count": x.bad_rrr_count,
                "bad_rrr_pg32_types": x.bad_rrr_pg32_types,
                "bad_rrr_triads_orbit": [list(t) for t in x.bad_rrr_triads_orbit],
                "bad_rrr_triads_duads": [
                    [list(p) for p in t] for t in x.bad_rrr_triads_duads
                ],
            }
            for x in ranked
        ],
        "per_double_six": [
            {
                "ds_key_e6id": [list(x.ds_key[0]), list(x.ds_key[1])],
                "A_orbit": list(x.A_orbit),
                "B_orbit": list(x.B_orbit),
                "R_orbit": list(x.R_orbit),
                "bad_pattern_hist": x.bad_pattern_hist,
                "bad_rrr_count": x.bad_rrr_count,
                "bad_rrr_pg32_types": x.bad_rrr_pg32_types,
                "bad_rrr_triads_orbit": [list(t) for t in x.bad_rrr_triads_orbit],
                "bad_rrr_triads_duads": [
                    [list(p) for p in t] for t in x.bad_rrr_triads_duads
                ],
                "bad_a1b1r1_triads_orbit": [list(t) for t in x.bad_a1b1r1_triads_orbit],
            }
            for x in analyses_sorted
        ],
    }
    return results


def _write_md(results: dict) -> str:
    top = results["ranked_by_bad_rrr"][:10]
    inv = results["invariants_over_all_double_sixes"]
    lines = []
    lines.append("# Forbidden (firewall) triads vs double-sixes\n")
    lines.append(f"- reference 27-orbit: `{results['reference_orbit_index']}`\n")
    lines.append(f"- forbidden triads: `{results['counts']['bad_triads']}`\n")
    lines.append(f"- double-sixes: `{results['counts']['double_sixes']}`\n")
    lines.append("\n## Universal invariants (all 36 double-sixes)\n")
    for row in inv["bad_pattern_histograms"]:
        lines.append(
            f"- bad triad sector histogram: `{dict(row['hist'])}` occurs `{row['count']}` times\n"
        )
    for row in inv["bad_rrr_pg32_type_histograms"]:
        lines.append(
            f"- RRR-in-R PG(3,2) type histogram: `{dict(row['types'])}` occurs `{row['count']}` times\n"
        )
    lines.append("\n## Forbidden triads (canonical E6-id)\n")
    for t in results["bad_triads"]["e6id"]:
        lines.append(f"- `{t}`\n")
    lines.append("\n## Top double-sixes by RRR concentration\n")
    for row in top:
        A, B = row["ds_key_e6id"]
        lines.append(
            f"- A={A} B={B} :: bad_hist={row['bad_pattern_hist']} :: RRR={row['bad_rrr_count']} :: PG32={row['bad_rrr_pg32_types']}"
            f" :: RRR_triads_orbit={row['bad_rrr_triads_orbit']} :: RRR_duads={row['bad_rrr_triads_duads']}\n"
        )
    return "".join(lines)


def main() -> None:
    results = compute_bad_triads_vs_double_sixes()
    out_json = ROOT / "artifacts" / "bad_triads_vs_double_sixes.json"
    out_md = ROOT / "artifacts" / "bad_triads_vs_double_sixes.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    out_md.write_text(_write_md(results), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
