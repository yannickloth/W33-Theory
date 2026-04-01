# Phase CCXXXIV - Sym^2 Bivector Bianchi Split

This note sharpens the Bianchi-hyperplane reading from Phase CCXXXIII into an
actual construction.

Earlier phases identified the continuum-facing packet

- dim Lambda^2(R^4) = 6
- dim Sym^2(Lambda^2(R^4)) = 21
- dim Riem_alg(R^4) = 20

The new point is that the full passage

- 21 -> 20

comes from the oriented chiral split itself.

## Chiral quadratic decomposition

In oriented 4D,

- Lambda^2 = Lambda^2_+ (+) Lambda^2_-
- dim Lambda^2_+ = dim Lambda^2_- = 3.

Therefore

- Sym^2(Lambda^2)
- = Sym^2(Lambda^2_+) (+) (Lambda^2_+ tensor Lambda^2_-) (+) Sym^2(Lambda^2_-)

with dimensions

- 6 + 9 + 6 = 21.

Now each 6-dimensional symmetric square splits as

- Sym^2(R^3) = Sym^2_0(R^3) (+) R
- 6 = 5 + 1.

So the full quadratic bivector packet becomes

- 21 = (5+1) + 9 + (5+1).

The algebraic curvature shell is obtained by imposing the Bianchi scalar cut,
which removes one scalar combination of the two chiral trace lines. What
remains is

- 20 = 5 + 9 + 5 + 1.

This is exactly the oriented 4D curvature decomposition already matched in the
previous phases.

## Exact W33 landing

At q = 3 the W33 packet lands on every stage of this construction:

- 2q = 6
- lambda*Phi4 = 20
- 2(q+2) + q^2 + 1 = 20

and the chiral blocks are

- q + 2 = 5
- q^2 = 9
- q + 2 = 5
- scalar = 1.

So the W33 continuum-facing shell does not merely match the end result 20. It
matches the entire construction

- Sym^2(3 (+) 3) = (5+1) + 9 + (5+1) -> 5 + 9 + 5 + 1.

## Best current reading

The smooth-bridge target is now sharper still:

- start from the oriented bivector split 3 + 3,
- form the quadratic bivector packet 6 + 9 + 6,
- impose the single Bianchi scalar cut,
- recover the exact W33 curvature shell 5 + 9 + 5 + 1.

This does not finish the smooth bridge theorem. But it identifies the exact
finite packet with the standard construction of the 4D algebraic curvature
operator from the quadratic bivector space, not merely with matching dimensions.