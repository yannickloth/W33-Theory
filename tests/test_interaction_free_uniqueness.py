import itertools
import sympy as sp


def test_interaction_free_uniqueness_for_spectrum_0_to_7():
    # Solve for the general 3-bit Hamiltonian coefficients that reproduce the spectrum 0..7.
    # The basis is n1,n2,n3 in {0,1} and the energy model is:
    # E = c + h1*n1 + h2*n2 + h3*n3 + J12*n1*n2 + J13*n1*n3 + J23*n2*n3 + J123*n1*n2*n3

    c, h1, h2, h3, J12, J13, J23, J123 = sp.symbols('c h1 h2 h3 J12 J13 J23 J123', real=True)

    # Enumerate the 8 binary states in the same order used by the v39 code
    # and assign energies according to weights (1,2,4).
    states = list(itertools.product([0,1], repeat=3))
    energies = [s[0]*1 + s[1]*2 + s[2]*4 for s in states]

    eqs = []
    for (n1, n2, n3), E in zip(states, energies):
        expr = (
            c
            + h1*n1
            + h2*n2
            + h3*n3
            + J12*n1*n2
            + J13*n1*n3
            + J23*n2*n3
            + J123*n1*n2*n3
        )
        eqs.append(sp.Eq(expr, E))

    sol = sp.solve(eqs, [c, h1, h2, h3, J12, J13, J23, J123], dict=True)
    assert len(sol) == 1, f"Expected unique solution, got {sol}"

    sol = sol[0]
    # The unique solution should be the free dyadic Hamiltonian
    assert sol[c] == 0
    assert sol[h1] == 1
    assert sol[h2] == 2
    assert sol[h3] == 4
    assert sol[J12] == 0
    assert sol[J13] == 0
    assert sol[J23] == 0
    assert sol[J123] == 0
