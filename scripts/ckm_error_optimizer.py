"""Optimize CKM error alone over the active Yukawa subspace."""
from __future__ import annotations
import numpy as np
from pathlib import Path
import sys

# import path fix
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from combined_ckm_mass_landscape import build_yukawa_tensor, analyze_active_subspace
from w33_ckm_from_vev import compute_ckm_and_jarlskog

# experimental CKM target
V_CKM_exp = np.array([
    [0.97373, 0.2243,  0.00382],
    [0.2210,  0.987,   0.0410 ],
    [0.0080,  0.0388,  1.013  ],
])

# build active subspace
print('building Yukawa tensor...')
T = build_yukawa_tensor()
print('analyzing active subspace...')
rank, Vh = analyze_active_subspace(T)
print('rank', rank)
V_active = Vh[:rank, :].conj().T  # 27 x rank


def unflatten(z, rank):
    # take 2*rank reals representing complex vector
    return z[:rank] + 1j * z[rank:2*rank]


def ck_err_from_vars(x):
    # x length = 4*rank: real(alpha)+imag(alpha)+real(beta)+imag(beta)
    ar = x[:rank]; ai = x[rank:2*rank]
    br = x[2*rank:3*rank]; bi = x[3*rank:4*rank]
    alpha = ar + 1j * ai
    beta = br + 1j * bi
    # normalization constraints assumed satisfied
    alpha = alpha / np.linalg.norm(alpha)
    beta = beta / np.linalg.norm(beta)
    v = V_active @ alpha
    v = v / np.linalg.norm(v)
    w = V_active @ beta
    w = w / np.linalg.norm(w)
    params = np.concatenate([np.real(v), np.imag(v), np.real(w), np.imag(w)])
    ck = compute_ckm_and_jarlskog(params, T, V_CKM_exp,
                                  [1/500, 500/85000], [1/20, 1/40],
                                  weight_mass=0.0)
    return float(ck)

# random initialization
rng = np.random.default_rng(123)
x0 = rng.normal(size=4*rank)
# enforce norm=1 for alpha and beta
alpha0 = x0[:rank] + 1j * x0[rank:2*rank]
alpha0 /= np.linalg.norm(alpha0)
x0[:rank] = np.real(alpha0)
x0[rank:2*rank] = np.imag(alpha0)
beta0 = x0[2*rank:3*rank] + 1j * x0[3*rank:4*rank]
beta0 /= np.linalg.norm(beta0)
x0[2*rank:3*rank] = np.real(beta0)
x0[3*rank:4*rank] = np.imag(beta0)

# constraints
import scipy.optimize as opt
cons = [
    {'type': 'eq', 'fun': lambda x: np.linalg.norm(unflatten(x, rank)) - 1},
    {'type': 'eq', 'fun': lambda x: np.linalg.norm(unflatten(np.concatenate((x[2*rank:4*rank], np.zeros(0))), rank)) - 1},
]

res = opt.minimize(ck_err_from_vars, x0, method='SLSQP', constraints=cons, options={'maxiter':500,'ftol':1e-12})
print('minimization result', res)
val = res.fun if res.success else None
print('best ck_err', val)

# also do random search to verify
best = 1e9
for i in range(2000):
    alpha = rng.normal(size=rank) + 1j * rng.normal(size=rank)
    alpha /= np.linalg.norm(alpha)
    beta = rng.normal(size=rank) + 1j * rng.random(size=rank)
    beta /= np.linalg.norm(beta)
    x = np.concatenate([np.real(alpha), np.imag(alpha), np.real(beta), np.imag(beta)])
    c = ck_err_from_vars(x)
    if c < best:
        best = c
print('random best ck_err', best)
