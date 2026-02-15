#!/usr/bin/env python3
"""Run SNF/PSLQ verification tools with an extended denominator grid (D up to 960).

Writes updated artifacts (overwrites existing artifacts where present):
 - artifacts/verify_exhaustive_failures_snf_pslq.json
 - artifacts/pslq_snf_mixed_patch_check.json

Use when you want a deeper SNF/PSLQ sweep without editing the original tools.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# helper to load-and-run a module, then optionally override module-level globals
def load_and_run(path: Path, overrides: dict | None = None):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    if overrides:
        for k, v in overrides.items():
            if hasattr(mod, k):
                setattr(mod, k, v)
    # call main()
    if hasattr(mod, "main"):
        mod.main()
    else:
        raise RuntimeError(f"Module {path} has no main()")


def main():
    tools_dir = ROOT / "tools"
    # extend denominators to include 960
    verify_path = tools_dir / "verify_exhaustive_failures_snf_pslq.py"
    pslq_path = tools_dir / "pslq_snf_mixed_patch_check.py"

    print(
        "Running verify_exhaustive_failures_snf_pslq.py with extended D_LIST (add 960)..."
    )
    load_and_run(
        verify_path, overrides={"D_LIST": [9, 18, 36, 72, 120, 240, 360, 480, 960]}
    )

    print("Running pslq_snf_mixed_patch_check.py with extended D_LIST (add 960)...")
    load_and_run(
        pslq_path, overrides={"D_LIST": [9, 72, 240, 480, 960], "MAX_DEN": 960}
    )

    print("Extended SNF/PSLQ sweep complete. Artifacts updated in artifacts/.")


if __name__ == "__main__":
    main()
