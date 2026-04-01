# Phase CCXXX - Weyl Split Completion

This note sharpens the curvature-ladder reading from Phase CCXXIX.

At q = 3 the exact W(3,3) curvature shell

- lambda*Phi4 = 20

matches the full oriented 4D algebraic curvature decomposition

- W+ : 5
- W- : 5
- S^2_0 : 9
- scalar : 1

because

- q + 2 = 5
- q^2 = 9
- 20 = 5 + 5 + 9 + 1.

## Exact selector

The family selector is

- lambda*Phi4 - (2(q+2) + q^2 + 1) = (q-3)(q^2 + q + 2)

so q = 3 is the unique positive integer point where the W33 curvature shell
lands on the oriented 4D split

- Riem_alg(R^4) = W+ + W- + S^2_0 + scalar.

## A4 lift

The promoted A4 factor is

- 55 = 5*(k-1).

At q = 3 this matches

- dim Sym^2(Weyl_4) = C(10+1,2) = 55

and, using the oriented Weyl split 10 = 5 + 5,

- 55 = 15 + 25 + 15
-    = dim Sym^2(W+) + dim(W+ tensor W-) + dim Sym^2(W-).

The corresponding selector is

- 5*(k-1) - (2*C(q+3,2) + (q+2)^2) = (q-3)(3q+5).

So the exact A4 packet now lifts from the full curvature shell to the second
symmetric power of the oriented Weyl sector.

## Best current reading

The continuum-facing packet now lands on the following oriented 4D geometry:

- bivectors: 6 = dim Lambda^2(R^4)
- Weyl split: 5 + 5
- tracefree Ricci: 9
- scalar: 1
- full algebraic curvature: 20
- quadratic Weyl packet: 55

This still does not finish the smooth bridge theorem. But it narrows the wall
further: the W33 spectral-action bridge is now pointing at the full oriented 4D
curvature decomposition together with its quadratic Weyl lift.