"""Scan combined CKM/mass objective across weight_mass parameter."""
from pathlib import Path
import json
import numpy as np
import sys

# ensure repo root and scripts are on import path
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from combined_ckm_mass_landscape import build_yukawa_tensor, analyze_active_subspace, random_active_points

# build tensor and compute active subspace
T = build_yukawa_tensor()
rank, Vh = analyze_active_subspace(T)
print('rank', rank)

weights = np.logspace(-2, 2, 9)  # 0.01 to 100
results = []
for w in weights:
    pts = random_active_points(T, Vh, rank, 1000, weight_mass=w)
    best = pts[0]
    results.append((w, best['ck_err'], best['mass_err'], best['combined']))
    print(f'w={w:.2g}: ck={best["ck_err"]:.4f}, mass={best["mass_err"]:.4f}, comb={best["combined"]:.4f}')

out = {'scan': results}
Path('data/weight_scan.json').write_text(json.dumps(out, indent=2))
print('wrote data/weight_scan.json')
