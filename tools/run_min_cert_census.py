#!/usr/bin/env python3
"""Run or plan exact minimal-certificate censuses and derived analyses.

Default behavior is dry-run planning. With `--execute`, this tool runs:
1) exact minimal-certificate enumeration,
2) canonical representative classification,
3) involution-rule checking,
4) reduced-orbit closed-form equivalence checking,
5) markdown gallery and summary generation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALID_SPACES = ("hessian", "agl")


def _normalize_candidate_spaces(candidate_spaces: list[str]) -> list[str]:
    out: list[str] = []
    seen = set()
    for raw in candidate_spaces:
        space = str(raw).strip().lower()
        if space not in VALID_SPACES:
            raise ValueError(
                f"Unsupported candidate space '{raw}'. Use one of: {', '.join(VALID_SPACES)}"
            )
        if space not in seen:
            out.append(space)
            seen.add(space)
    return out


def _cmd_preview(cmd: list[str]) -> str:
    return subprocess.list2cmdline([str(part) for part in cmd])


def _run_checked(cmd: list[str]) -> None:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        stdout = proc.stdout.strip()
        details = stderr if stderr else stdout
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {_cmd_preview(cmd)}\n{details}"
        )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_run_plan(
    in_json: Path,
    out_dir: Path,
    candidate_spaces: list[str],
    max_exact_solutions: int,
    time_limit_sec: float,
) -> dict[str, Any]:
    runs = []
    for space in candidate_spaces:
        enum_out = out_dir / f"e6_f3_trilinear_min_cert_exact_{space}_full.json"
        classified_out = out_dir / f"{enum_out.stem}_with_geotypes.json"
        rule_out = (
            out_dir
            / f"e6_f3_trilinear_min_cert_orbit_involution_rule_check_{space}_exact_full.json"
        )
        reduced_out = (
            out_dir
            / f"e6_f3_trilinear_reduced_orbit_closed_form_equiv_{space}_exact_full.json"
        )
        gallery_out = (
            out_dir / f"e6_f3_trilinear_min_cert_gallery_{space}_exact_full.md"
        )
        enum_cmd = [
            sys.executable,
            str(ROOT / "tools" / "enumerate_minimal_certificates.py"),
            "--in-json",
            str(in_json),
            "--candidate-space",
            space,
            "--mode",
            "exact",
            "--max-exact-solutions",
            str(max_exact_solutions),
            "--time-limit-sec",
            str(time_limit_sec),
            "--out-json",
            str(enum_out),
        ]
        classify_cmd = [
            sys.executable,
            str(ROOT / "tools" / "classify_canonical_reps.py"),
            "--in-json",
            str(enum_out),
            "--out-json",
            str(classified_out),
        ]
        rule_cmd = [
            sys.executable,
            str(ROOT / "tools" / "check_min_cert_orbit_involution_rule.py"),
            "--in-json",
            str(classified_out),
            "--out-json",
            str(rule_out),
        ]
        reduced_cmd = [
            sys.executable,
            str(ROOT / "tools" / "check_reduced_orbit_closed_form_equiv.py"),
            "--in-json",
            str(classified_out),
            "--out-json",
            str(reduced_out),
        ]
        gallery_cmd = [
            sys.executable,
            str(ROOT / "tools" / "make_min_cert_gallery.py"),
            "--in-json",
            str(classified_out),
            "--out-md",
            str(gallery_out),
            "--title",
            f"Minimal-Certificate Gallery ({space})",
        ]
        runs.append(
            {
                "candidate_space": space,
                "limits": {
                    "max_exact_solutions": int(max_exact_solutions),
                    "time_limit_sec": float(time_limit_sec),
                },
                "outputs": {
                    "enumeration_json": str(enum_out),
                    "classified_json": str(classified_out),
                    "involution_rule_json": str(rule_out),
                    "reduced_orbit_closed_form_json": str(reduced_out),
                    "gallery_md": str(gallery_out),
                },
                "commands": {
                    "enumerate": enum_cmd,
                    "classify": classify_cmd,
                    "rule_check": rule_cmd,
                    "reduced_check": reduced_cmd,
                    "gallery": gallery_cmd,
                    "enumerate_preview": _cmd_preview(enum_cmd),
                    "classify_preview": _cmd_preview(classify_cmd),
                    "rule_check_preview": _cmd_preview(rule_cmd),
                    "reduced_check_preview": _cmd_preview(reduced_cmd),
                    "gallery_preview": _cmd_preview(gallery_cmd),
                },
            }
        )
    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "source_map_json": str(in_json),
        "planned_runs": runs,
    }


def _build_orbit_histograms(
    representatives: list[dict[str, Any]]
) -> dict[str, dict[str, int]]:
    raw = Counter()
    weighted = Counter()
    for entry in representatives:
        orbit_size = str(int(entry.get("orbit_size", 0)))
        raw[orbit_size] += 1
        weighted[orbit_size] += int(entry.get("hit_count", 1))
    return {
        "raw": dict(sorted(raw.items(), key=lambda item: int(item[0]))),
        "weighted_by_hit_count": dict(
            sorted(weighted.items(), key=lambda item: int(item[0]))
        ),
    }


def _write_summary_md(summary: dict[str, Any], out_md: Path) -> None:
    lines = []
    lines.append("# Minimal-Certificate Census Summary")
    lines.append("")
    lines.append(f"- Generated: `{summary['generated_utc']}`")
    lines.append(f"- Source map: `{summary['source_map_json']}`")
    lines.append("")
    lines.append(
        "| Candidate Space | k_min | Exact Solutions | Distinct Reps | Rule Holds | Reduced Eq | Reduced Profile | z-map Restriction |"
    )
    lines.append("|---|---:|---:|---:|---|---|---|---|")
    for run in summary.get("runs", []):
        lines.append(
            "| {} | {} | {} | {} | {} | {} | {} | {} |".format(
                run.get("candidate_space", ""),
                run.get("k_min", ""),
                run.get("exact_solutions_count", ""),
                run.get("distinct_representatives", ""),
                "yes" if run.get("involution_rule_holds", False) else "no",
                "yes" if run.get("reduced_closed_form_equivalent", False) else "no",
                (
                    "yes"
                    if run.get("reduced_closed_form_strict_profile_holds", False)
                    else "no"
                ),
                (
                    "yes"
                    if run.get("reduced_closed_form_zmap_restriction_holds", False)
                    else "no"
                ),
            )
        )
    lines.append("")
    for run in summary.get("runs", []):
        lines.append(f"## {run['candidate_space']}")
        lines.append("")
        lines.append(f"- Enumeration: `{run['outputs']['enumeration_json']}`")
        lines.append(f"- Classified: `{run['outputs']['classified_json']}`")
        lines.append(f"- Rule check: `{run['outputs']['involution_rule_json']}`")
        lines.append(
            "- Reduced closed-form check: "
            f"`{run['outputs']['reduced_orbit_closed_form_json']}`"
        )
        lines.append(f"- Gallery: `{run['outputs']['gallery_md']}`")
        lines.append(
            "- Rule mismatch count: `{}`".format(
                run.get("involution_mismatch_count", "n/a")
            )
        )
        lines.append(
            "- Reduced-form mismatch count: `{}`".format(
                run.get("reduced_closed_form_mismatch_count", "n/a")
            )
        )
        lines.append(
            "- Reduced match-count hist: `{}`".format(
                run.get("reduced_closed_form_match_count_histogram", {})
            )
        )
        lines.append(
            "- Reduced strict profile holds: `{}`".format(
                run.get("reduced_closed_form_strict_profile_holds", "n/a")
            )
        )
        lines.append(
            "- Reduced z-map restriction holds: `{}`".format(
                run.get("reduced_closed_form_zmap_restriction_holds", "n/a")
            )
        )
        lines.append(
            "- Reduced matching z-maps: `{}`".format(
                run.get("reduced_closed_form_observed_matching_z_maps", [])
            )
        )
        lines.append(
            "- Orbit hist (raw): `{}`".format(
                run.get("orbit_histograms", {}).get("raw", {})
            )
        )
        lines.append(
            "- Orbit hist (weighted): `{}`".format(
                run.get("orbit_histograms", {}).get("weighted_by_hit_count", {})
            )
        )
        lines.append("")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_map.json",
    )
    parser.add_argument(
        "--candidate-spaces",
        nargs="+",
        default=["hessian", "agl"],
        help="Candidate spaces to run (hessian, agl).",
    )
    parser.add_argument("--max-exact-solutions", type=int, default=0)
    parser.add_argument("--time-limit-sec", type=float, default=0.0)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "artifacts")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write only the execution plan (default behavior when --execute is omitted).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run the planned census commands.",
    )
    parser.add_argument(
        "--skip-classify",
        action="store_true",
        help="Skip canonical representative classification.",
    )
    parser.add_argument(
        "--skip-involution-check",
        action="store_true",
        help="Skip involution-rule checker.",
    )
    parser.add_argument(
        "--skip-gallery",
        action="store_true",
        help="Skip markdown gallery generation.",
    )
    parser.add_argument(
        "--skip-reduced-closed-form-check",
        action="store_true",
        help="Skip reduced-orbit closed-form equivalence checker.",
    )
    parser.add_argument("--summary-json", type=Path, default=None)
    parser.add_argument("--summary-md", type=Path, default=None)
    args = parser.parse_args()

    if args.execute and args.dry_run:
        parser.error("Use either --execute or --dry-run, not both.")
    execute = bool(args.execute)

    candidate_spaces = _normalize_candidate_spaces(list(args.candidate_spaces))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = _build_run_plan(
        in_json=args.in_json,
        out_dir=args.out_dir,
        candidate_spaces=candidate_spaces,
        max_exact_solutions=int(args.max_exact_solutions),
        time_limit_sec=float(args.time_limit_sec),
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out_dir / "min_cert_census_plan.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    mode = "execute" if execute else "dry-run"
    print(f"Wrote {mode} manifest: {manifest_path}")

    if not execute:
        return

    summary_runs = []
    for plan in manifest["planned_runs"]:
        outputs = plan["outputs"]
        commands = plan["commands"]
        _run_checked(list(commands["enumerate"]))
        enum_payload = _load_json(Path(outputs["enumeration_json"]))
        run_summary: dict[str, Any] = {
            "candidate_space": plan["candidate_space"],
            "outputs": outputs,
            "k_min": enum_payload.get("k_min"),
            "exact_solutions_count": int(enum_payload.get("exact_solutions_count", 0)),
            "distinct_representatives": int(
                enum_payload.get("distinct_canonical_representatives_found", 0)
            ),
            "truncated_by_max_solutions": bool(
                enum_payload.get("truncated_by_max_solutions", False)
            ),
            "truncated_by_time_limit": bool(
                enum_payload.get("truncated_by_time_limit", False)
            ),
            "involution_rule_holds": None,
            "involution_mismatch_count": None,
            "reduced_closed_form_equivalent": None,
            "reduced_closed_form_mismatch_count": None,
            "reduced_closed_form_match_count_histogram": {},
            "reduced_closed_form_strict_profile_holds": None,
            "reduced_closed_form_zmap_restriction_holds": None,
            "reduced_closed_form_observed_matching_z_maps": [],
            "orbit_histograms": {"raw": {}, "weighted_by_hit_count": {}},
        }

        classified_payload = None
        if not args.skip_classify:
            _run_checked(list(commands["classify"]))
            classified_payload = _load_json(Path(outputs["classified_json"]))
            reps = list(classified_payload.get("representatives", []))
            run_summary["orbit_histograms"] = _build_orbit_histograms(reps)

        if (not args.skip_involution_check) and (classified_payload is not None):
            _run_checked(list(commands["rule_check"]))
            rule_payload = _load_json(Path(outputs["involution_rule_json"]))
            run_summary["involution_rule_holds"] = bool(rule_payload.get("rule_holds"))
            run_summary["involution_mismatch_count"] = int(
                rule_payload.get("mismatch_count", 0)
            )

        if (not args.skip_reduced_closed_form_check) and (
            classified_payload is not None
        ):
            _run_checked(list(commands["reduced_check"]))
            reduced_payload = _load_json(
                Path(outputs["reduced_orbit_closed_form_json"])
            )
            run_summary["reduced_closed_form_equivalent"] = bool(
                reduced_payload.get("equivalent")
            )
            run_summary["reduced_closed_form_mismatch_count"] = int(
                reduced_payload.get("mismatch_count", 0)
            )
            run_summary["reduced_closed_form_match_count_histogram"] = dict(
                reduced_payload.get("match_count_histogram", {})
            )
            run_summary["reduced_closed_form_strict_profile_holds"] = bool(
                reduced_payload.get("symmetry_profile", {}).get("strict_profile_holds")
            )
            run_summary["reduced_closed_form_zmap_restriction_holds"] = bool(
                reduced_payload.get("zmap_restriction_holds")
            )
            run_summary["reduced_closed_form_observed_matching_z_maps"] = list(
                reduced_payload.get("observed_matching_z_maps", [])
            )

        if (not args.skip_gallery) and (classified_payload is not None):
            _run_checked(list(commands["gallery"]))

        summary_runs.append(run_summary)

    summary_json = args.summary_json or (args.out_dir / "min_cert_census_summary.json")
    summary_md = args.summary_md or (args.out_dir / "min_cert_census_summary.md")
    summary = {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "source_map_json": str(args.in_json),
        "mode": "execute",
        "run_count": len(summary_runs),
        "runs": summary_runs,
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_md(summary, summary_md)
    print(f"Wrote summary json: {summary_json}")
    print(f"Wrote summary md: {summary_md}")


if __name__ == "__main__":
    main()
