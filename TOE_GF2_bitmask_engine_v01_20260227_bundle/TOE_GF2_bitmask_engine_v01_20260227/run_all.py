#!/usr/bin/env python3
import subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]

def run(cmd):
    print("\n$ " + " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    run([sys.executable, str(ROOT/"examples"/"triangle_complex_homology.py")])
    run([sys.executable, str(ROOT/"examples"/"fixed_subspace_H1.py")])
