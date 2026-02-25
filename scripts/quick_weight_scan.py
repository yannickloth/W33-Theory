"""Quick weight scan with light sampling for exploratory analysis."""
from pathlib import Path
import json
import numpy as np
import sys

# set up import path
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from combined_ckm_mass_landscape import build_yukawa_tensor, analyze_active_subspace, random_active_points

print('building tensor...')
T = build_yukawa_tensor()
rank, Vh = analyze_active_subspace(T)
print('rank', rank)

weights = np.logspace(-2, 2, 7)
for w in weights:
    pts = random_active_points(T, Vh, rank, 200, weight_mass=w)
    best = pts[0]
    print(f'w={w:.2g}: ck={best["ck_err"]:.4f}, mass={best["mass_err"]:.4f}, comb={best["combined"]:.4f}')
