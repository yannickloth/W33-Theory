# Reduced Orbit Corollary (Short)

In an adapted affine gauge sending the distinguished affine flag to
((0,0), x-direction) the canonical diagonal involution A = diag(-1,1)
acts by (x,y) -> (2x,y) over F3. The vertical line L: x=0 is fixed by A
and, by the coordinate-free shifted product law, satisfies P(L) = +1.
The affine z-map z -> 2*z + 2 fixes z = 1, while the closed-form full-sign
law predicts s(L,1) = -1 for L. These conclusions are incompatible, which
provides a short algebraic contradiction ruling out z=(2,2) for any
representative invariant under such an involution. The argument is both
symbolic and machine-checked (see `tools/formal_z22_proof.py` and
`tests/test_formal_z22_module.py`).
