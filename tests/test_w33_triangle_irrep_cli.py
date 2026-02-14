import importlib.util
import shutil
from pathlib import Path

import pytest


@pytest.mark.skipif(
    shutil.which("gap") is None, reason="GAP not on PATH; skip CLI fallback test"
)
def test_w33_triangle_irrep_match_gap_cli(tmp_path, monkeypatch):
    """Run the GAP-CLI fallback of the triangle→PSp(4,3) irrep matcher.

    - Forces the CLI path and asserts the produced JSON contains the expected
      decomposition 160 = 10 + 30 + 30 + 90.
    - Skipped when `gap` executable isn't available on PATH.
    """
    # Locate the script and import it as a module
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "w33_triangle_irrep_match_gap.py"
    spec = importlib.util.spec_from_file_location(
        "w33_triangle_irrep_match_gap", str(script_path)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Force CLI fallback even if libgap happens to be available in the environment
    setattr(mod, "_HAS_LIBGAP", False)

    # Run in an isolated cwd so output goes to tmp_path/checks
    monkeypatch.chdir(tmp_path)

    # Execute main (this will call GAP CLI)
    mod.main()

    # Find the output file written by the CLI path
    out_files = list(
        (tmp_path / "checks").glob("PART_CVII_triangle_irrep_match_gap_cli_*.json")
    )
    assert out_files, "No CLI output JSON produced"

    out_path = sorted(out_files)[-1]
    data = out_path.read_text(encoding="utf-8")
    import json

    obj = json.loads(data)

    # Basic sanity
    assert obj["n_triangles"] == 160

    # Check irrep multiplicities: expect one 10-dim, two 30-dim, one 90-dim
    mults = obj.get("irrep_matches")
    assert mults and isinstance(mults, list)

    bydeg = {}
    for m in mults:
        d = int(m["degree"])
        bydeg[d] = bydeg.get(d, 0) + int(m["mult"])

    assert bydeg.get(10, 0) == 1
    assert bydeg.get(30, 0) == 2
    assert bydeg.get(90, 0) == 1

    # Degrees sum check
    total = sum(d * c for d, c in bydeg.items())
    assert total == obj["n_triangles"]
