import json
import subprocess
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"


def test_full_aut_orbit_analysis_runs_and_finds_intersection():
    """Run the full Aut(W33) orbit analysis and assert intersection found for
    the default candidates [0-18-25, 0-20-23]."""
    cmd = [
        "python",
        "tools/forbid_full_aut_orbit_analysis.py",
        "--cands",
        "0-18-25,0-20-23",
        "--pick",
        "lex_min",
    ]
    subprocess.run(cmd, check=True)
    out = ART / "forbid_full_aut_orbit_analysis.json"
    assert out.exists(), "Output JSON not written"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert (
        data.get("intersection_nonempty") is True
    ), "Expected intersection_nonempty to be True"
    # Basic sanity on canonical representative
    assert data.get("canonical") is not None
