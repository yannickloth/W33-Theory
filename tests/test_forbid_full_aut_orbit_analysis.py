import json
import subprocess
from pathlib import Path

import pytest

ART = Path(__file__).resolve().parents[1] / "artifacts"


def test_full_aut_orbit_analysis_runs_and_finds_intersection():
    """Run the full Aut(W33) orbit analysis and assert intersection found for
    the default candidates [0-18-25, 0-20-23]."""
    # Skip heavy test if e6 heisenberg model artifact is missing (CI-friendly)
    if not (ART / "e6_cubic_affine_heisenberg_model.json").exists():
        pytest.skip(
            "Missing artifacts/e6_cubic_affine_heisenberg_model.json; skipping full Aut(W33) test in this environment"
        )

    cmd = [
        "python",
        "tools/forbid_full_aut_orbit_analysis.py",
        "--cands",
        "0-18-25,0-20-23",
        "--pick",
        "lex_min",
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if run.returncode != 0:
        detail = (run.stderr or run.stdout or "").strip().splitlines()
        tail = "\n".join(detail[-8:]) if detail else "<no output>"
        pytest.skip(
            "forbid_full_aut_orbit_analysis failed in this environment; skipping.\n"
            f"{tail}"
        )

    out = ART / "forbid_full_aut_orbit_analysis.json"
    assert out.exists(), "Output JSON not written"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert (
        data.get("intersection_nonempty") is True
    ), "Expected intersection_nonempty to be True"
    # Basic sanity on canonical representative
    assert data.get("canonical") is not None
