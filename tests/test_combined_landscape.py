from __future__ import annotations

import json
import os
from pathlib import Path

def test_combined_landscape_generates_file(tmp_path):
    """Running the script creates a JSON file with expected structure."""
    from scripts import combined_ckm_mass_landscape
    # monkeypatch heavy tensor builder to a light random tensor for faster testing
    import numpy as np
    def _fake_build():
        return np.random.random((3, 3, 27))
    combined_ckm_mass_landscape.build_yukawa_tensor = _fake_build

    cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        # simulate command-line arguments
        import sys
        sys_argv_orig = sys.argv.copy()
        sys.argv = ["", "--samples", "10", "--lines", "1"]
        combined_ckm_mass_landscape.main()
        sys.argv = sys_argv_orig

        out_path = tmp_path / "data" / "combined_landscape.json"
        assert out_path.exists(), "output JSON was not created"
        payload = json.loads(out_path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        assert payload.get("rank") in (6, 7, 8)
        assert "best_random" in payload
        assert "line_results" in payload
    finally:
        os.chdir(cwd)
