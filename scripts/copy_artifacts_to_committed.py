#!/usr/bin/env python3
import shutil
from pathlib import Path

src = Path("artifacts/min_cert_census_medium_2026_02_10")
dst = Path("committed_artifacts/min_cert_census_medium_2026_02_10")
dst.mkdir(parents=True, exist_ok=True)
copied = 0
for p in src.iterdir():
    if p.is_file():
        shutil.copy2(p, dst / p.name)
        copied += 1
print("Copied", copied, "files to", dst)
