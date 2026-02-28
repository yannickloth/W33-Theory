#!/usr/bin/env python3
"""Relate flag-level Heisenberg qids to qutrit Pauli/Clifford operators.

Using the six distinguished qids from the triality bridge, we map the
coordinate (x,y,z) \in F3^3 to the unitary
    P(x,y,z) = \omega^z X^x Z^y,
where \omega = e^{2\pi i/3}, and X,Z are the standard qutrit shift/clock.

We then compute the multiplication table for the six operators (mod phases)
and inspect whether they generate a small Clifford algebra-like structure.
"""
import json, zipfile, csv
import numpy as np

# load six qids
report = json.load(open('data/w33_triality_bridge.json'))
block_qids = {int(k): set(v) for k, v in report['T4b_block_qids'].items()}
six = set()
for qs in block_qids.values():
    six.update(qs)
six = sorted(six)
print('six qids', six)

# load coords
with zipfile.ZipFile('TOE_K27_HEISENBERG_S3_v01_20260228_bundle.zip') as zf:
    coords_csv = zf.read('TOE_K27_HEISENBERG_S3_v01_20260228/K27_heisenberg_coords.csv').decode()
qid2coords = {int(r['qid']):(int(r['x']),int(r['y']),int(r['z']))
               for r in csv.DictReader(coords_csv.splitlines())}

# primitive qutrit X,Z
omega = np.exp(2j*np.pi/3)
X = np.roll(np.eye(3,dtype=complex), -1, axis=1)
Z = np.diag([1, omega, omega**2])

# build operator for each qid
ops = {}
for q in six:
    x,y,z = qid2coords[q]
    ops[q] = (omega**z) * np.linalg.matrix_power(X, x) @ np.linalg.matrix_power(Z, y)

# function to reduce matrix up to phase (divide by one element)
def mod_phase(mat):
    # find nonzero entry
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if abs(mat[i,j])>1e-6:
                phase = mat[i,j]/abs(mat[i,j])
                return mat/phase
    return mat

# compute multiplication table (qid_a * qid_b => qid_c or None)
mult = {}
for a in six:
    mult[a]={}
    for b in six:
        prod = ops[a] @ ops[b]
        prod = mod_phase(prod)
        # compare to each ops[c]
        found=None
        for c in six:
            if np.allclose(prod, mod_phase(ops[c]), atol=1e-6):
                found=c
                break
        mult[a][b]=found
print('multiplication table:')
for a in six:
    print(a, mult[a])

# identify any central elements (commute with all defined products)
central=[]
for a in six:
    if all((mult[a].get(b) == b or mult[a].get(b) is None) and
           (mult[b].get(a) == b or mult[b].get(a) is None)
           for b in six):
        central.append(a)
print('central qids (mod-phase) among the six:', central)

# compute orders of each operator (mod phase) up to 3
orders = {}
for a in six:
    m=ops[a]
    orders[a] = np.linalg.matrix_power(m, 3)
    orders[a] = mod_phase(orders[a])
print('orders at power 3 (should equal I if order divides 3):')
for a,mat in orders.items():
    print(a, np.allclose(mat, np.eye(3)))

# check if closure under multiplication yields small set
closure=set(six)
changed=True
while changed:
    changed=False
    for a in list(closure):
        for b in list(closure):
            c = mult[a][b]
            if c is not None and c not in closure:
                closure.add(c); changed=True
print('closure size',len(closure))
