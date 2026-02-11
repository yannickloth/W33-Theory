#!/usr/bin/env python3
"""Swap-based candidate impact analysis.

For each top problem edge, test nearest canonical root replacements (including
roots already assigned elsewhere) and compute how many problem cycles would
change to have s_mod3 == k (i.e., become matches) after substitution. Emit a
vet CSV with suggested_apply='yes' for candidates exceeding the threshold.

The baseline per-A2 extraction outputs must correspond to the current
`artifacts/edge_to_e8_root_combined.json`. After applying a vetted CSV and
re-extracting per-A2 results, use `--baseline-kind postapply` (or `auto`).
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def load_combined_map(path: Path) -> Dict[Tuple[int, int], Tuple[int, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    m: Dict[Tuple[int, int], Tuple[int, ...]] = {}
    for k, coords in data.items():
        if isinstance(k, str) and k.startswith("("):
            s = k.strip()[1:-1]
            a_s, b_s = s.split(",")
            a = int(a_s.strip())
            b = int(b_s.strip())
            m[(a, b)] = tuple(int(x) for x in coords)
    return m


def load_cycles_with_k(path: Path) -> List[Dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    if isinstance(data, dict):
        rows = data.get("rows", [])
    else:
        rows = data
    for r in rows:
        cyc = None
        if isinstance(r, dict) and "cycle" in r:
            cyc = [int(x) for x in r["cycle"]]
        elif isinstance(r, dict) and "cycle_vertices" in r:
            cyc = [int(x) for x in r["cycle_vertices"].split(",") if x.strip()]
        if cyc is None:
            continue
        out.append({"idx": r.get("idx"), "cycle": cyc, "k": r.get("k")})
    return out


def build_edge_to_cycle_index(
    cycles: List[List[int]],
) -> Dict[Tuple[int, int], List[int]]:
    edge_to_cycles: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for idx, cyc in enumerate(cycles):
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            edge_to_cycles[(a, b)].append(idx)
    return edge_to_cycles


def load_canonical_roots(path: Path) -> List[Tuple[int, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    roots: List[Tuple[int, ...]] = []
    if isinstance(data, list):
        for ent in data:
            coords = ent.get("root_coords")
            if coords:
                roots.append(tuple(int(x) for x in coords))
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict) and "root_coords" in v:
                coords = v["root_coords"]
                roots.append(tuple(int(x) for x in coords))
            else:
                s = k.strip()
                if s.startswith("(") or s.startswith("["):
                    inner = s.strip("()[]")
                    parts = [p.strip() for p in inner.split(",") if p.strip()]
                    try:
                        coords = tuple(int(x) for x in parts)
                        roots.append(coords)
                    except Exception:
                        continue
    return roots


def _dot_int(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return sum(int(a) * int(b) for a, b in zip(u, v, strict=True))


def inner_prod_doubled(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return _dot_int(u, v) // 4


def find_simple_roots_in_a2(
    a2_indices: List[int], root_index_to_coords: Dict[int, Tuple[int, ...]]
):
    roots = {i: root_index_to_coords[i] for i in a2_indices}
    for i, a in roots.items():
        for j, b in roots.items():
            if i >= j:
                continue
            ip = inner_prod_doubled(a, b)
            if ip == -1:
                return a, b, i, j
    raise RuntimeError("No simple root pair found in A2 indices")


def dist2(u: Tuple[int, ...], v: Tuple[int, ...]) -> int:
    return sum((int(a) - int(b)) ** 2 for a, b in zip(u, v))


def load_root_index_map(path: Path) -> Dict[int, Tuple[int, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    m = {}
    if isinstance(data, list):
        for ent in data:
            idx = int(ent.get("root_index"))
            coords = tuple(int(x) for x in ent.get("root_coords"))
            m[idx] = coords
    elif isinstance(data, dict):
        # try parsing keyed entries
        for k, v in data.items():
            if isinstance(k, str) and (k.startswith("(") or k.startswith("[")):
                continue
    return m


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--top-edges-json",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/problem_cycle_edge_tally.json"
        ),
    )
    p.add_argument(
        "--combined-map",
        type=Path,
        default=Path("artifacts/edge_to_e8_root_combined.json"),
    )
    p.add_argument(
        "--cycles-json",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/w33_uv_parser_det1_results_cycles_for_e8.json"
        ),
    )
    p.add_argument(
        "--canonical-root-file",
        type=Path,
        default=Path("artifacts/edge_root_bijection_canonical.json"),
    )
    p.add_argument(
        "--a2-solution-json",
        type=Path,
        default=Path("artifacts/a2_4_decomposition.json"),
    )
    p.add_argument(
        "--baseline-kind",
        choices=["auto", "combined", "postapply"],
        default="auto",
        help="Baseline per-A2 outputs to use (default: auto)",
    )
    p.add_argument(
        "--score-mode",
        choices=["fixed", "net"],
        default="fixed",
        help="Score candidates by fixed matches or net (fixed-regressed)",
    )
    p.add_argument(
        "--recompute-top-edges",
        action="store_true",
        help="Ignore --top-edges-json and recompute from baseline problem cycles",
    )
    p.add_argument("--top-n", type=int, default=20)
    p.add_argument("--candidate-nearest", type=int, default=100)
    p.add_argument("--apply-threshold", type=int, default=3)
    p.add_argument(
        "--out-json",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates.json"
        ),
    )
    p.add_argument(
        "--out-csv",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates.csv"
        ),
    )
    p.add_argument(
        "--out-apply-csv",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/w33_uv_parser_det1_swap_candidates_vetting.csv"
        ),
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # load current mapping and cycles
    combined_map = load_combined_map(args.combined_map)
    cycles_list = load_cycles_with_k(args.cycles_json)
    cycles = [r["cycle"] for r in cycles_list]
    cycle_k_map = {idx: r.get("k") for idx, r in enumerate(cycles_list)}

    edge_to_cycles = build_edge_to_cycle_index(cycles)

    # load canonical roots
    canonical_roots = load_canonical_roots(args.canonical_root_file)

    # prepare A2 simple roots
    root_index_map = {}
    try:
        er_data = json.loads(
            Path("artifacts/edge_root_bijection_canonical.json").read_text(
                encoding="utf-8"
            )
        )
        if isinstance(er_data, list):
            for ent in er_data:
                idx = int(ent["root_index"])
                coords = tuple(int(x) for x in ent["root_coords"])
                root_index_map[idx] = coords
    except Exception:
        pass
    # load a2 solutions
    a2_sols = json.loads(
        Path("artifacts/a2_4_decomposition.json").read_text(encoding="utf-8")
    )["a2_4_solution"]
    a2_pairs = [sol for sol in a2_sols]

    # Load baseline per-A2 outputs (must correspond to the current combined map)
    baseline_kind = args.baseline_kind
    if baseline_kind == "auto":
        postapply_ok = all(
            Path(
                f"analysis/minimal_commutator_cycles/e8_det1_postapply_a2_{i}/e8_rootword_cocycle.json"
            ).exists()
            for i in range(4)
        )
        baseline_kind = "postapply" if postapply_ok else "combined"

    per_a2_rows = []
    for i in range(4):
        pth = Path(
            f"analysis/minimal_commutator_cycles/e8_det1_{baseline_kind}_a2_{i}/e8_rootword_cocycle.json"
        )
        if not pth.exists():
            raise FileNotFoundError(f"Missing baseline per-A2 file: {pth}")
        j = json.loads(pth.read_text(encoding="utf-8"))
        per_a2_rows.append(j["rows"])

    ncycles = len(per_a2_rows[0]) if per_a2_rows else 0
    if ncycles != len(cycles):
        raise RuntimeError(
            f"Baseline cycle count mismatch: per_a2_rows={ncycles} vs cycles_json={len(cycles)}"
        )

    baseline_any_match = [False] * ncycles
    baseline_any_divisible = [False] * ncycles
    for idx in range(ncycles):
        any_div = False
        any_match = False
        for a in range(len(per_a2_rows)):
            r = per_a2_rows[a][idx]
            if r.get("divisible"):
                any_div = True
                if r.get("k") is not None and r.get("s_mod3") == r.get("k"):
                    any_match = True
        baseline_any_match[idx] = any_match
        baseline_any_divisible[idx] = any_div

    problem_cycle_set = {
        i
        for i in range(ncycles)
        if baseline_any_divisible[i] and not baseline_any_match[i]
    }

    # Determine top edges to analyze
    if args.recompute_top_edges:
        edge_counter = Counter()
        for idx in sorted(problem_cycle_set):
            cyc = cycles[idx]
            for i in range(len(cyc)):
                ea = cyc[i]
                eb = cyc[(i + 1) % len(cyc)]
                edge_counter[(ea, eb)] += 1
        top = edge_counter.most_common(args.top_n)
        top_edges = [(ea, eb, c) for (ea, eb), c in top]
    else:
        top_j = json.loads(args.top_edges_json.read_text(encoding="utf-8"))
        top = top_j.get("top_edges", [])[: args.top_n]
        top_edges = [(e["edge_a"], e["edge_b"], e["count"]) for e in top]

    # Precompute A2 simple roots (alpha,beta) for each A2 selection
    a2_simple_roots: List[Tuple[Tuple[int, ...], Tuple[int, ...]] | None] = []
    for a2_idxs in a2_pairs:
        try:
            alpha, beta, _ai_idx, _bi_idx = find_simple_roots_in_a2(
                a2_idxs, root_index_map
            )
        except Exception:
            a2_simple_roots.append(None)
        else:
            a2_simple_roots.append((alpha, beta))

    print("Baseline kind:", baseline_kind)
    print("Problem cycle count (baseline):", len(problem_cycle_set))

    # analyze each top edge
    out_rows = []
    vet_rows = []
    for a, b, count in top_edges:
        key = (a, b)
        rev_key = (b, a)
        current = combined_map.get(key)
        candidates_tested = 0
        candidates = []
        # pick canonical nearest neighbors (including those already assigned)
        neighbors = sorted(
            canonical_roots, key=lambda r: dist2(r, current) if current else 0
        )[: args.candidate_nearest]
        for r in neighbors:
            if current and tuple(r) == tuple(current):
                continue

            improved_cycles: List[int] = []
            regressed_cycles: List[int] = []
            affected_cycle_indices = sorted(
                set(edge_to_cycles.get(key, [])) | set(edge_to_cycles.get(rev_key, []))
            )
            for idx in affected_cycle_indices:
                if args.score_mode == "fixed" and idx not in problem_cycle_set:
                    continue

                cyc = cycles[idx]

                # Gather rlist with substitution
                rlist = []
                missing = False
                for i in range(len(cyc)):
                    x = cyc[i]
                    y = cyc[(i + 1) % len(cyc)]
                    if (x, y) == key:
                        rlist.append(tuple(r))
                    elif (x, y) == rev_key:
                        rlist.append(tuple(-int(t) for t in r))
                    else:
                        v = combined_map.get((x, y))
                        if v is None:
                            missing = True
                            break
                        rlist.append(tuple(v))
                if missing:
                    continue

                # Determine if substituted cycle has ANY A2 match
                any_match_after = False
                k_val = cycle_k_map.get(idx)
                if k_val is not None:
                    for simple in a2_simple_roots:
                        if simple is None:
                            continue
                        alpha, beta = simple
                        tvals = [
                            inner_prod_doubled(rr, alpha) - inner_prod_doubled(rr, beta)
                            for rr in rlist
                        ]
                        S = sum(tvals)
                        if S % 3 != 0:
                            continue
                        s_mod3 = (S // 3) % 3
                        if s_mod3 == k_val:
                            any_match_after = True
                            break

                was_match = baseline_any_match[idx]
                if (not was_match) and any_match_after:
                    improved_cycles.append(idx)
                elif was_match and (not any_match_after):
                    regressed_cycles.append(idx)

            fixed_matches = len(set(improved_cycles))
            regressed_matches = len(set(regressed_cycles))
            net_matches = fixed_matches - regressed_matches
            score = fixed_matches if args.score_mode == "fixed" else net_matches
            if score > 0:
                candidates.append(
                    {
                        "vector": list(r),
                        "fixed_matches": fixed_matches,
                        "regressed_matches": regressed_matches,
                        "net_matches": net_matches,
                        "fixed_cycles": sorted(set(improved_cycles)),
                        "regressed_cycles": sorted(set(regressed_cycles)),
                    }
                )
            candidates_tested += 1
            if candidates_tested >= args.candidate_nearest:
                break
        # sort candidates by selected score mode
        if args.score_mode == "fixed":
            candidates.sort(
                key=lambda c: (
                    -c["fixed_matches"],
                    c.get("regressed_matches", 0),
                    -c.get("net_matches", 0),
                )
            )
        else:
            candidates.sort(
                key=lambda c: (
                    -c.get("net_matches", 0),
                    -c["fixed_matches"],
                    c.get("regressed_matches", 0),
                )
            )
        out_rows.append(
            {"edge": f"{a},{b}", "count": count, "candidates": candidates[:10]}
        )
        for c in candidates:
            score = (
                c["fixed_matches"]
                if args.score_mode == "fixed"
                else c.get("net_matches", 0)
            )
            if score >= args.apply_threshold:
                comment = f"fixed={c['fixed_matches']} regressed={c.get('regressed_matches', 0)} net={c.get('net_matches', 0)} mode={args.score_mode}"
                vet_rows.append(
                    {
                        "edge_a": a,
                        "edge_b": b,
                        "vector": json.dumps(c["vector"]),
                        "score": score,
                        "comment": comment,
                    }
                )

    # write outputs
    out_json = args.out_json
    out_csv = args.out_csv
    out_json.write_text(
        json.dumps(
            {"top_edges_analyzed": len(top_edges), "out_rows": out_rows}, indent=2
        ),
        encoding="utf-8",
    )
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "edge",
                "count",
                "top_candidate_vector",
                "top_fixed_matches",
                "top_regressed_matches",
                "top_net_matches",
                "score_mode",
            ]
        )
        for ent in out_rows:
            topc = ent["candidates"][0] if ent["candidates"] else None
            w.writerow(
                [
                    ent["edge"],
                    ent["count"],
                    json.dumps(topc["vector"]) if topc else "",
                    topc["fixed_matches"] if topc else 0,
                    topc.get("regressed_matches", 0) if topc else 0,
                    topc.get("net_matches", 0) if topc else 0,
                    args.score_mode,
                ]
            )

    vet_csv = args.out_apply_csv
    with vet_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "edge_a",
                "edge_b",
                "count",
                "candidate_idx",
                "vector",
                "score",
                "confidence",
                "tag",
                "source",
                "note",
                "derived_from",
                "suggested_apply",
                "apply",
                "comment",
            ]
        )
        for r in vet_rows:
            w.writerow(
                [
                    r["edge_a"],
                    r["edge_b"],
                    0,
                    0,
                    r["vector"],
                    r["score"],
                    "auto",
                    "swap-canon",
                    "swap",
                    r.get("comment", ""),
                    "",
                    "yes",
                    "",
                    r.get("comment", ""),
                ]
            )

    print("Wrote swap candidates JSON/CSV and vet CSV (suggest-only)")


if __name__ == "__main__":
    try:
        import argparse

        main()
    except Exception:
        import traceback
        from pathlib import Path as _P

        _P("tmp").mkdir(exist_ok=True)
        _P("tmp/swap_candidate_impact_error.txt").write_text(
            traceback.format_exc(), encoding="utf-8"
        )
        traceback.print_exc()
        raise
