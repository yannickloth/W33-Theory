import numpy as np
import json

def test_cycle_space_properties():
    from tools.cycle_space_analysis import (
        build_W33,
        build_cycle_basis,
        intersection_matrix,
        compute_automorphisms,
        trace_under_perm,
        permute_cycle,
    )

    n, vertices, adj, edges = build_W33()
    basis = build_cycle_basis(n, adj, edges)

    # dimension should match graph cycle rank = |E|-|V|+1 = 201
    assert len(basis) == 201

    I = intersection_matrix(basis)
    # intersection form ought to be nondegenerate on this basis
    assert np.linalg.matrix_rank(I) == 201

    # we only need a few automorphisms to sanity-check behavior
    autos = compute_automorphisms(n, adj, limit=5)
    assert len(autos) == 5

    # check that trace_under_perm returns an integer for the first permutation
    perm0 = autos[0]
    tr0 = trace_under_perm(basis, perm0, edges)
    assert isinstance(tr0, int)

    # orbit size of first basis vector under the limited set should be <=201
    vec = basis[0]
    orb = set()
    frontier = [tuple(vec)]
    # using only the limited automorphisms as a proxy
    while frontier:
        w = np.array(frontier.pop())
        for perm in autos:
            w2 = permute_cycle(w, perm, edges)
            t = tuple(w2)
            if t not in orb:
                orb.add(t)
                frontier.append(t)
    size = len(orb)
    assert size <= 201 and size % 3 == 0


def test_h1_subspaces_file_exists():
    import os
    path = os.path.join("data", "h1_subspaces.json")
    assert os.path.isfile(path), "h1_subspaces.json should be produced"
    data = json.load(open(path))
    dims = data.get("subspace_dims", [])
    # there should be three 27-dim subspaces
    assert dims == [27, 27, 27]
    grams = data.get("gram_matrices", [])
    assert len(grams) == 3
    # ensure each gram matrix is 27x27 and nondegenerate
    for G in grams:
        import numpy as np
        M = np.array(G, dtype=int)
        assert M.shape == (27, 27)
        assert np.linalg.matrix_rank(M) == 27
