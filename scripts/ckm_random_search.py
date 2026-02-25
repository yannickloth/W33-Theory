"""Simple random search for minimum CKM error in active subspace."""
import numpy as np
import sys
from pathlib import Path

# import path
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from combined_ckm_mass_landscape import build_yukawa_tensor, analyze_active_subspace
from w33_ckm_from_vev import compute_ckm_and_jarlskog

V_CKM_exp = np.array([
    [0.97373, 0.2243,  0.00382],
    [0.2210,  0.987,   0.0410 ],
    [0.0080,  0.0388,  1.013  ],
])

print('building tensor...')
T = build_yukawa_tensor()
rank, Vh = analyze_active_subspace(T)
print('rank', rank)
V_active = Vh[:rank, :].conj().T

rng = np.random.default_rng(12345)
best = 1e9
best_vw = None

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
for i in range(N):
    alpha = rng.normal(size=rank) + 1j * rng.normal(size=rank)
    alpha /= np.linalg.norm(alpha)
    beta = rng.normal(size=rank) + 1j * rng.normal(size=rank)
    beta /= np.linalg.norm(beta)
    v = V_active @ alpha
    v /= np.linalg.norm(v)
    w = V_active @ beta
    w /= np.linalg.norm(w)
    params = np.concatenate([np.real(v), np.imag(v), np.real(w), np.imag(w)])
    ck = compute_ckm_and_jarlskog(params, T, V_CKM_exp,
                                  [1/500, 500/85000], [1/20, 1/40],
                                  weight_mass=0.0)
    if ck < best:
        best = ck
        best_vw = (v.copy(), w.copy())
    if i % 1000 == 0:
        print(f'i={i} best_ck={best}')

print('final best ck', best)
