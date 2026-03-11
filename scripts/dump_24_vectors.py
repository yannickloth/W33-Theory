"""Compute the 24-dimensional invariant subspace for automorphism 582 and dump its basis."""

import sys
from pathlib import Path
import numpy as np
from sympy import Matrix

sys.path.append('.')
from e8_embedding_group_theoretic import build_w33
from tools.cycle_space_analysis import build_cycle_basis
from tools.cycle_space_decompose import build_clique_complex, boundary_matrix, permute_cycle, compute_automorphisms

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
H1_BASIS_CACHE = DATA_DIR / "h1_basis.npz"
AUTOMORPHISM_CACHE = DATA_DIR / "automorphisms.pkl"
KNOWN_24_BASIS_CACHE = DATA_DIR / "24_basis.npz"
KNOWN_24_INDEX = 1410


def construct_H1_basis(n, adj, edges):
    if H1_BASIS_CACHE.exists():
        arr = np.load(H1_BASIS_CACHE)["arr_0"]
        if arr.shape == (81, 240):
            print("loading cached H1 basis")
            return [arr[i].astype(int, copy=True) for i in range(arr.shape[0])]

    full_basis = build_cycle_basis(n, adj, edges)
    simplices = build_clique_complex(n, adj)
    B2 = boundary_matrix(simplices[2], simplices[1])
    M2 = Matrix(B2.tolist())
    im_basis_sym = M2.columnspace()
    im_basis = [np.array([int(x) for x in v], dtype=int).flatten() for v in im_basis_sym]

    H1_basis = []
    def in_span(v, vecs):
        if not vecs:
            return False
        M = Matrix(np.column_stack(vecs + [v]))
        return M.rank() <= Matrix(np.column_stack(vecs)).rank()

    for v in full_basis:
        if not in_span(v, H1_basis + im_basis):
            H1_basis.append(v.copy())
        if len(H1_basis) == 81:
            break
    DATA_DIR.mkdir(exist_ok=True)
    np.savez(H1_BASIS_CACHE, np.stack(H1_basis))
    return H1_basis


def action_matrix_on_H1(perm, basis, edges):
    dim = len(basis)
    Bmat = np.column_stack(basis)  # 240x81
    pinv = np.linalg.pinv(Bmat)
    M = Matrix.zeros(dim, dim)
    for i, b in enumerate(basis):
        b_permuted = permute_cycle(b, perm, edges)
        coeffs = pinv @ b_permuted
        coeffs = np.rint(coeffs).astype(int)
        for j, c in enumerate(coeffs):
            M[j, i] = c
    return M


import argparse

def main():
    parser = argparse.ArgumentParser(description='Dump 24-vector basis for a given automorphism index')
    parser.add_argument('--index', type=int, default=1410,
                        help='automorphism index (default 1410)')
    parser.add_argument('--output', type=str, default=None,
                        help='optional file to save the 24x? basis as numpy .npz')
    args = parser.parse_args()

    if args.index == KNOWN_24_INDEX and KNOWN_24_BASIS_CACHE.exists():
        mat = np.load(KNOWN_24_BASIS_CACHE)["arr_0"]
        print("loaded cached 24-basis", mat.shape)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            np.savez(args.output, mat)
            print('saved basis to', args.output)
        else:
            np.set_printoptions(threshold=100, edgeitems=5)
            print(mat)
        return

    n, verts, adj, edges = build_w33()
    H1_basis = construct_H1_basis(n, adj, edges)
    # only compute enough automorphisms to reach index
    if AUTOMORPHISM_CACHE.exists():
        import pickle
        with open(AUTOMORPHISM_CACHE, "rb") as f:
            autos = pickle.load(f)
    else:
        autos = compute_automorphisms(n, adj, limit=args.index + 1)
    if len(autos) <= args.index:
        raise RuntimeError(f"automorphism {args.index} not generated; increase limit")
    perm = autos[args.index]
    M_sym = action_matrix_on_H1(perm, H1_basis, edges)

    # convert to numpy for numeric eigendecomposition
    M = np.array(M_sym.tolist(), dtype=float)
    eigvals, eigvecs = np.linalg.eig(M)
    # print eigenvalue summary
    from collections import Counter
    ev_rounded = [round(v.real,6) for v in eigvals]
    cnt = Counter(ev_rounded)
    print('eigenvalue counts (rounded real parts):')
    for val, c in cnt.items():
        print(val, c)
    # cluster eigenvalues with tolerance
    unique = {}
    for i, val in enumerate(eigvals):
        # round to nearest rational by tolerance
        r = round(val.real, 6)
        unique.setdefault(r, []).append(i)

    for val, indices in unique.items():
        if len(indices) == 24:
            print('numeric eigenvalue', val, 'multiplicity', len(indices))
            # compute nullspace symbolically for exact basis
            # convert value to rational if possible
            from sympy import Rational
            try:
                exact_val = Rational(val).limit_denominator()
            except Exception:
                exact_val = val
            print('computing nullspace of M -', exact_val, 'I')
            symM = M_sym - exact_val * Matrix.eye(M_sym.shape[0])
            null = symM.nullspace()
            mat = np.column_stack([np.array(v, dtype=int).flatten() for v in null])
            print('24-basis shape', mat.shape)
            np.set_printoptions(threshold=100, edgeitems=5)
            print(mat)
            if args.output:
                np.savez(args.output, mat)
                print('saved basis to', args.output)
            break

if __name__ == '__main__':
    main()
