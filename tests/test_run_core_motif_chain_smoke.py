from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_core_motif_chain_smoke(tmp_path: Path) -> None:
    out_dir = tmp_path / "artifacts"
    docs_dir = tmp_path / "docs"
    cmd = [
        sys.executable,
        "tools/run_core_motif_chain.py",
        "--out-dir",
        str(out_dir),
        "--docs-dir",
        str(docs_dir),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr

    link = json.loads(
        (out_dir / "core_rulebook_min_cert_link_2026_02_11.json").read_text(
            encoding="utf-8"
        )
    )
    pol = json.loads(
        (out_dir / "core_motif_orbit_polarization_2026_02_11.json").read_text(
            encoding="utf-8"
        )
    )
    enr = json.loads(
        (out_dir / "core_motif_enrichment_stats_2026_02_11.json").read_text(
            encoding="utf-8"
        )
    )
    anc = json.loads(
        (out_dir / "core_motif_anchor_channels_2026_02_11.json").read_text(
            encoding="utf-8"
        )
    )

    assert link["status"] == "ok"
    assert pol["status"] == "ok"
    assert enr["status"] == "ok"
    assert anc["status"] == "ok"

    assert (docs_dir / "CORE_RULEBOOK_MIN_CERT_LINK_2026_02_11.md").exists()
    assert (docs_dir / "CORE_MOTIF_ORBIT_POLARIZATION_2026_02_11.md").exists()
    assert (docs_dir / "CORE_MOTIF_ENRICHMENT_STATS_2026_02_11.md").exists()
    assert (docs_dir / "CORE_MOTIF_ANCHOR_CHANNELS_2026_02_11.md").exists()
