#!/usr/bin/env python3
"""Run the full core-motif analysis chain.

This orchestration pass builds, in order:
1) rulebook-to-census motif link,
2) motif orbit polarization,
3) motif enrichment statistics,
4) motif anchor channels,
5) motif anchor-set search.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.classify_core_motif_orbit_polarization import (
    build_report as build_polarization,
)
from tools.classify_core_motif_orbit_polarization import (
    render_md as render_polarization_md,
)
from tools.core_motif_anchor_channels import build_report as build_anchors
from tools.core_motif_anchor_channels import render_md as render_anchors_md
from tools.core_motif_enrichment_stats import build_report as build_enrichment
from tools.core_motif_enrichment_stats import render_md as render_enrichment_md
from tools.link_core_rulebook_to_min_cert_census import build_report as build_link
from tools.link_core_rulebook_to_min_cert_census import render_md as render_link_md
from tools.search_core_motif_anchor_sets import build_report as build_anchor_search
from tools.search_core_motif_anchor_sets import render_md as render_anchor_search_md


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts"),
        help="Output directory for JSON artifacts.",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Output directory for markdown docs.",
    )
    parser.add_argument(
        "--rulebook-json",
        type=Path,
        default=Path("artifacts/nontrivial_core_rulebook_2026_02_11.json"),
    )
    args = parser.parse_args()

    link = build_link(rulebook_json=args.rulebook_json)
    pol = build_polarization(rulebook_json=args.rulebook_json)
    enr = build_enrichment(rulebook_json=args.rulebook_json)
    anc = build_anchors(rulebook_json=args.rulebook_json)
    search = build_anchor_search(rulebook_json=args.rulebook_json)

    _write_json(args.out_dir / "core_rulebook_min_cert_link_2026_02_11.json", link)
    _write_json(args.out_dir / "core_motif_orbit_polarization_2026_02_11.json", pol)
    _write_json(args.out_dir / "core_motif_enrichment_stats_2026_02_11.json", enr)
    _write_json(args.out_dir / "core_motif_anchor_channels_2026_02_11.json", anc)
    _write_json(args.out_dir / "core_motif_anchor_search_2026_02_11.json", search)

    _write_md(
        args.docs_dir / "CORE_RULEBOOK_MIN_CERT_LINK_2026_02_11.md",
        render_link_md(link),
    )
    _write_md(
        args.docs_dir / "CORE_MOTIF_ORBIT_POLARIZATION_2026_02_11.md",
        render_polarization_md(pol),
    )
    _write_md(
        args.docs_dir / "CORE_MOTIF_ENRICHMENT_STATS_2026_02_11.md",
        render_enrichment_md(enr),
    )
    _write_md(
        args.docs_dir / "CORE_MOTIF_ANCHOR_CHANNELS_2026_02_11.md",
        render_anchors_md(anc),
    )
    _write_md(
        args.docs_dir / "CORE_MOTIF_ANCHOR_SEARCH_2026_02_11.md",
        render_anchor_search_md(search),
    )

    print("Wrote core-motif chain artifacts and docs.")


if __name__ == "__main__":
    main()
