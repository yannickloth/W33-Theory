\
from __future__ import annotations
import os, json, time
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

def run(cmd):
    print(">", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))

def main():
    t0=time.time()
    run([sys.executable, "-m", "src.orbit_480"])
    run([sys.executable, "-m", "src.derivations_g2"])
    t1=time.time()
    print(f"Done in {t1-t0:.2f}s. See ./out/")

if __name__ == "__main__":
    main()
