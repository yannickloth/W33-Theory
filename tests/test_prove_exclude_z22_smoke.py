from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_prove_exclude_z22_smoke(tmp_path: Path) -> None:
    out = subprocess.run(
        [sys.executable, "tools/prove_exclude_z22.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert out.returncode == 0, out.stderr
    assert "No representatives invariant under diag(-1,1) + z_map=(2,2)" in out.stdout
