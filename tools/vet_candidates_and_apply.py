#!/usr/bin/env python3
"""Create a vetting CSV for missing-edge candidates and optionally apply selected candidates.

Usage examples:
  # generate vetting CSV with suggested_apply flags
  python tools/vet_candidates_and_apply.py --candidates-json analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.json

  # apply suggested candidates above score threshold (dry-run)
  python tools/vet_candidates_and_apply.py --candidates-json analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.json --apply --dry-run

  # apply using edited CSV (rows marked apply=yes):
  python tools/vet_candidates_and_apply.py --apply-from-csv analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates_vetting.csv --apply --force

Notes:
 - Default behavior only suggests applies for medium/high confidence or score >= threshold (default 80).
 - When applying, the script updates artifacts/edge_to_e8_root_combined.json and makes a timestamped backup.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

# default files
DEFAULT_CAND_JSON = Path(
    "analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.json"
)
DEFAULT_VET_CSV = Path(
    "analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates_vetting.csv"
)
COMBINED_MAP = Path("artifacts/edge_to_e8_root_combined.json")


def load_candidate_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Candidates JSON not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def generate_vetting_csv(
    cand_json_path: Path, out_csv: Path, score_threshold: int = 80
) -> Dict[str, Any]:
    """Flatten candidate JSON into a vetting CSV and return the report dict."""
    report = load_candidate_json(cand_json_path)
    edges = report.get("edges", [])

    rows = []
    for ent in edges:
        a_s, b_s = ent["edge"].split(",")
        a = int(a_s)
        b = int(b_s)
        for idx, cand in enumerate(ent.get("candidates", [])):
            vector = cand.get("vector")
            score = int(cand.get("score", 0))
            confidence = cand.get("confidence", "low")
            tag = cand.get("tag")
            source = cand.get("source")
            note = cand.get("note")
            derived = cand.get("derived_from")
            # suggested apply if confidence medium/high OR score >= threshold
            suggested = (
                "yes"
                if (confidence in ("high", "medium") or score >= score_threshold)
                else "no"
            )
            rows.append(
                {
                    "edge_a": a,
                    "edge_b": b,
                    "count": ent.get("count", 0),
                    "candidate_idx": idx,
                    "vector": json.dumps(vector),
                    "score": score,
                    "confidence": confidence,
                    "tag": tag,
                    "source": source,
                    "note": note or "",
                    "derived_from": json.dumps(derived) if derived else "",
                    "suggested_apply": suggested,
                    "apply": "",  # for manual marking
                    "comment": "",
                }
            )

    # write CSV
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
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
        for r in rows:
            writer.writerow(
                [
                    r["edge_a"],
                    r["edge_b"],
                    r["count"],
                    r["candidate_idx"],
                    r["vector"],
                    r["score"],
                    r["confidence"],
                    r["tag"],
                    r["source"],
                    r["note"],
                    r["derived_from"],
                    r["suggested_apply"],
                    r["apply"],
                    r["comment"],
                ]
            )

    print(f"Wrote vetting CSV to {out_csv}")
    return {"csv": str(out_csv), "rows": len(rows)}


def parse_vetting_csv(csv_path: Path) -> List[Dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Vetting CSV not found: {csv_path}")
    out = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            out.append(
                {
                    "edge_a": int(r["edge_a"]),
                    "edge_b": int(r["edge_b"]),
                    "candidate_idx": int(r["candidate_idx"]),
                    "vector": json.loads(r["vector"]) if r["vector"] else None,
                    "score": int(r["score"]) if r["score"] else 0,
                    "confidence": r.get("confidence", ""),
                    "suggested_apply": r.get("suggested_apply", "no").strip().lower()
                    in ("1", "yes", "y", "true"),
                    "apply": r.get("apply", "").strip().lower()
                    in ("1", "yes", "y", "true"),
                    "raw_row": r,
                }
            )
    return out


def backup_file(path: Path) -> Path:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    bak = path.with_suffix(path.suffix + f".bak.{ts}")
    shutil.copy(path, bak)
    print(f"Backed up {path} -> {bak}")
    return bak


def build_consensus_report(
    cand_json_path: Path,
    top_n: int = 40,
    min_occurrences: int = 3,
    out_csv: Path | None = None,
) -> Dict[str, Any]:
    """Build a consensus report of the top candidate vectors across missing edges.

    Returns a dict with keys: vector -> {occurrences, total_count, avg_score, example_edges}
    Writes CSV if out_csv is provided.
    """
    data = load_candidate_json(cand_json_path)
    edges = data.get("edges", [])[:top_n]

    tally: Dict[Tuple[int, ...], Dict[str, Any]] = {}
    for ent in edges:
        a_s, b_s = ent["edge"].split(",")
        a = int(a_s)
        b = int(b_s)
        count = int(ent.get("count", 1))
        cands = ent.get("candidates", [])
        if not cands:
            continue
        top = cands[0]
        vec = tuple(int(x) for x in top["vector"])
        score = int(top.get("score", 0))
        rec = tally.setdefault(
            vec, {"occurrences": 0, "total_count": 0, "scores": [], "edges": []}
        )
        rec["occurrences"] += 1
        rec["total_count"] += count
        rec["scores"].append(score)
        rec["edges"].append(
            {
                "edge": f"{a},{b}",
                "count": count,
                "score": score,
                "tag": top.get("tag"),
                "source": top.get("source"),
            }
        )

    # compute averages and filter by min_occurrences
    rows = []
    for vec, info in tally.items():
        occ = info["occurrences"]
        if occ < min_occurrences:
            continue
        avg = sum(info["scores"]) / len(info["scores"]) if info["scores"] else 0
        rows.append(
            {
                "vector": list(vec),
                "occurrences": occ,
                "total_count": info["total_count"],
                "avg_score": avg,
                "example_edges": [e["edge"] for e in info["edges"][:10]],
            }
        )

    rows = sorted(rows, key=lambda r: (-r["occurrences"], -r["total_count"]))

    if out_csv:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(
                ["vector", "occurrences", "total_count", "avg_score", "example_edges"]
            )
            for r in rows:
                w.writerow(
                    [
                        json.dumps(r["vector"]),
                        r["occurrences"],
                        r["total_count"],
                        r["avg_score"],
                        json.dumps(r["example_edges"]),
                    ]
                )
        print("Wrote consensus CSV to", out_csv)

    return {"rows": rows, "count": len(rows)}


def solve_greedy_matching(
    cand_json_path: Path,
    top_n: int = 40,
    candidates_per_edge: int = 3,
    priority_bonus: Dict[str, int] | None = None,
) -> Dict[str, Any]:
    """Greedy matching: assign vectors to edges ensuring unique vectors.

    Returns a dict with 'assignments' list and stats.
    """
    data = load_candidate_json(cand_json_path)
    edges = data.get("edges", [])[:top_n]
    pairs = []  # list of (score_adj, edge_a, edge_b, vector, tag, source, score)

    priority_bonus = priority_bonus or {}

    for ent in edges:
        a_s, b_s = ent["edge"].split(",")
        a = int(a_s)
        b = int(b_s)
        cands = ent.get("candidates", [])[:candidates_per_edge]
        for idx, c in enumerate(cands):
            vec = tuple(int(x) for x in c["vector"])
            score = int(c.get("score", 0))
            tag = c.get("tag", "")
            source = c.get("source", "")
            bonus = priority_bonus.get(tag, 0) + priority_bonus.get(source, 0)
            score_adj = score + bonus
            pairs.append((score_adj, a, b, vec, tag, source, score))

    # sort descending
    pairs.sort(key=lambda t: -t[0])

    assigned_edges = set()
    assigned_vectors = set()
    assignments = []

    for score_adj, a, b, vec, tag, source, score in pairs:
        if (a, b) in assigned_edges:
            continue
        if vec in assigned_vectors:
            continue
        assigned_edges.add((a, b))
        assigned_vectors.add(vec)
        assignments.append(
            {
                "edge_a": a,
                "edge_b": b,
                "vector": list(vec),
                "score": score,
                "score_adj": score_adj,
                "tag": tag,
                "source": source,
            }
        )

    stats = {
        "assigned": len(assignments),
        "total_edges": len(edges),
        "unique_vectors": len(assigned_vectors),
    }
    return {"assignments": assignments, "stats": stats}


def apply_candidates_from_csv(
    csv_path: Path,
    combined_map_path: Path = COMBINED_MAP,
    dry_run: bool = True,
    force: bool = False,
) -> Dict[str, Any]:
    candidates = parse_vetting_csv(csv_path)
    # select entries to apply: those with apply==True OR suggested_apply==True and apply not explicitly False
    to_apply = [
        c for c in candidates if c["apply"] or (c["suggested_apply"] and not c["apply"])
    ]
    if not to_apply:
        return {"applied": 0, "skipped": 0, "reason": "no candidates marked for apply"}

    # load combined map
    if not combined_map_path.exists():
        raise FileNotFoundError(
            f"Combined edge->root file not found: {combined_map_path}"
        )
    combined = json.loads(combined_map_path.read_text(encoding="utf-8"))

    # prepare actions
    actions = []
    for ent in to_apply:
        a = ent["edge_a"]
        b = ent["edge_b"]
        vec = ent["vector"]
        key = f"({a}, {b})"
        rev_key = f"({b}, {a})"
        # skip if exists and not force
        if key in combined and not force:
            # if identical mapping, mark skipped
            if combined[key] == vec:
                actions.append(("skip", key, "exists_same"))
                continue
            else:
                actions.append(("skip", key, "exists_diff"))
                continue
        # otherwise plan to add
        actions.append(("add", key, vec))

    if dry_run:
        summary = {
            "planned_add": sum(1 for a in actions if a[0] == "add"),
            "planned_skip": sum(1 for a in actions if a[0] != "add"),
        }
        print("Dry-run: planned changes:", summary)
        return {"dry_run": True, "summary": summary}

    # backup
    backup_file(combined_map_path)

    applied = 0
    skipped = 0
    for act in actions:
        if act[0] != "add":
            skipped += 1
            continue
        key = act[1]
        vec = act[2]
        a, b = [int(x.strip()) for x in key.strip("()").split(",")]
        combined[key] = vec
        combined[f"({b}, {a})"] = [-int(x) for x in vec]
        applied += 1

    # write back
    combined_map_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print(
        f"Applied {applied} candidate mappings to {combined_map_path} (skipped {skipped})"
    )
    return {"applied": applied, "skipped": skipped}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--candidates-json", type=Path, default=DEFAULT_CAND_JSON)
    p.add_argument("--vet-csv", type=Path, default=DEFAULT_VET_CSV)
    p.add_argument("--score-threshold", type=int, default=80)
    p.add_argument("--generate-csv", action="store_true")
    p.add_argument(
        "--apply-from-csv",
        type=Path,
        help="CSV path to read manual apply marks from; if specified, will use its apply column to decide which candidates to apply",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Apply proposed candidates (or those marked in CSV)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="When applying, do not write changes; just report",
    )
    p.add_argument(
        "--force", action="store_true", help="Force overwrite existing mapping entries"
    )

    # consensus options
    p.add_argument(
        "--consensus",
        action="store_true",
        help="Build a consensus report for top candidate vectors across missing edges",
    )
    p.add_argument(
        "--consensus-topn",
        type=int,
        default=40,
        help="Top N missing edges to include in consensus analysis",
    )
    p.add_argument(
        "--consensus-min-occurrences",
        type=int,
        default=3,
        help="Minimum occurrences for a candidate vector to appear in consensus report",
    )
    p.add_argument(
        "--consensus-out-csv",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates_consensus.csv"
        ),
    )
    p.add_argument(
        "--apply-consensus",
        action="store_true",
        help="Apply consensus suggestions (will generate a temp CSV and apply rows marked as suggested)",
    )
    p.add_argument(
        "--consensus-apply-min-avg",
        type=float,
        default=0.0,
        help="Minimum average score for consensus vectors to be considered for apply",
    )

    # greedy matching options
    p.add_argument(
        "--match-greedy",
        action="store_true",
        help="Run greedy matching across candidates to propose unique assignments",
    )
    p.add_argument(
        "--match-topn",
        type=int,
        default=40,
        help="Top N missing edges to include in matching",
    )
    p.add_argument(
        "--match-k",
        type=int,
        default=3,
        help="Top K candidates per edge to consider in matching",
    )
    p.add_argument(
        "--match-out-csv",
        type=Path,
        default=Path(
            "analysis/minimal_commutator_cycles/w33_uv_parser_det1_candidate_matching.csv"
        ),
    )
    p.add_argument(
        "--match-apply",
        action="store_true",
        help="Apply matching assignments (generate CSV and use apply-from-csv semantics)",
    )
    args = p.parse_args(argv)

    if args.generate_csv or (not args.apply and not args.consensus):
        # always generate CSV if requested or if not applying/doing consensus
        print("Generating vetting CSV...")
        gen = generate_vetting_csv(
            args.candidates_json, args.vet_csv, score_threshold=args.score_threshold
        )
        print("Generated:", gen)

    if args.consensus:
        print("Building consensus report...")
        cons = build_consensus_report(
            args.candidates_json,
            top_n=args.consensus_topn,
            min_occurrences=args.consensus_min_occurrences,
            out_csv=args.consensus_out_csv,
        )
        print("Consensus rows:", len(cons.get("rows", [])))

    if args.apply_consensus:
        # build consensus and find vectors that meet min avg threshold
        cons = build_consensus_report(
            args.candidates_json,
            top_n=args.consensus_topn,
            min_occurrences=args.consensus_min_occurrences,
        )
        chosen = [
            r for r in cons["rows"] if r["avg_score"] >= args.consensus_apply_min_avg
        ]
        if not chosen:
            print("No consensus vector meets the criteria for apply")
        else:
            # create a temporary vetting CSV with rows matching chosen vectors (top candidate per edge == vector)
            data = load_candidate_json(args.candidates_json)
            tmp_rows = []
            for ent in data.get("edges", [])[: args.consensus_topn]:
                a_s, b_s = ent["edge"].split(",")
                a = int(a_s)
                b = int(b_s)
                cands = ent.get("candidates", [])
                if not cands:
                    continue
                top = cands[0]
                vec = tuple(int(x) for x in top["vector"])
                if any(vec == tuple(r["vector"]) for r in chosen):
                    # create a csv-ready row with apply=yes for this top candidate
                    tmp_rows.append(
                        {
                            "edge_a": a,
                            "edge_b": b,
                            "count": ent.get("count", 0),
                            "candidate_idx": 0,
                            "vector": json.dumps(list(vec)),
                            "score": int(top.get("score", 0)),
                            "confidence": top.get("confidence", "low"),
                            "tag": top.get("tag"),
                            "source": top.get("source"),
                            "note": top.get("note", ""),
                            "derived_from": json.dumps(top.get("derived_from", "")),
                            "suggested_apply": "yes",
                            "apply": "yes",
                            "comment": "consensus-apply",
                        }
                    )
            if not tmp_rows:
                print("No top-candidate rows matched chosen consensus vectors")
            else:
                # write tmp csv
                tmp_csv = Path(
                    "analysis/minimal_commutator_cycles/w33_uv_parser_det1_consensus_apply_tmp.csv"
                )
                with tmp_csv.open("w", encoding="utf-8", newline="") as f:
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
                    for r in tmp_rows:
                        w.writerow(
                            [
                                r["edge_a"],
                                r["edge_b"],
                                r["count"],
                                r["candidate_idx"],
                                r["vector"],
                                r["score"],
                                r["confidence"],
                                r["tag"],
                                r["source"],
                                r["note"],
                                r["derived_from"],
                                r["suggested_apply"],
                                r["apply"],
                                r["comment"],
                            ]
                        )
                print("Generated temporary consensus apply CSV:", tmp_csv)
                if args.dry_run:
                    print("Dry-run: not applying changes")
                else:
                    res = apply_candidates_from_csv(
                        tmp_csv,
                        combined_map_path=COMBINED_MAP,
                        dry_run=args.dry_run,
                        force=args.force,
                    )
                    print("Apply result:", res)

    if args.match_greedy:
        print("Running greedy matching...")
        match = solve_greedy_matching(
            args.candidates_json,
            top_n=args.match_topn,
            candidates_per_edge=args.match_k,
            priority_bonus={"canon": 30, "raw": 10, "we6": 5, "e8root": 5},
        )
        print("Matching assigned:", match["stats"])
        # write CSV
        out = args.match_out_csv
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(
                ["edge_a", "edge_b", "vector", "score", "score_adj", "tag", "source"]
            )
            for a in match["assignments"]:
                w.writerow(
                    [
                        a["edge_a"],
                        a["edge_b"],
                        json.dumps(a["vector"]),
                        a["score"],
                        a["score_adj"],
                        a["tag"],
                        a["source"],
                    ]
                )
        print("Wrote matching CSV to", out)
        if args.match_apply:
            # construct a CSV that apply_candidates_from_csv can read
            apply_csv = Path(
                "analysis/minimal_commutator_cycles/w33_uv_parser_det1_matching_apply.csv"
            )
            with apply_csv.open("w", encoding="utf-8", newline="") as f:
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
                for a in match["assignments"]:
                    w.writerow(
                        [
                            a["edge_a"],
                            a["edge_b"],
                            0,
                            0,
                            json.dumps(a["vector"]),
                            a["score"],
                            "auto",
                            a["tag"],
                            a["source"],
                            "matching assignment",
                            "",
                            "yes",
                            "yes",
                            "matching",
                        ]
                    )
            print("Generated matching apply CSV", apply_csv)
            if args.dry_run:
                print("Dry-run: not applying matching")
            else:
                res = apply_candidates_from_csv(
                    apply_csv,
                    combined_map_path=COMBINED_MAP,
                    dry_run=args.dry_run,
                    force=args.force,
                )
                print("Apply result:", res)

    if args.apply:
        csv_path = args.apply_from_csv if args.apply_from_csv else args.vet_csv
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV for apply not found: {csv_path}")
        print("Applying candidates from CSV:", csv_path)
        res = apply_candidates_from_csv(
            csv_path,
            combined_map_path=COMBINED_MAP,
            dry_run=args.dry_run,
            force=args.force,
        )
        print("Apply result:", res)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
