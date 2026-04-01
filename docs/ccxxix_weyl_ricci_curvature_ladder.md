# Phase CCXXIX - Weyl-Ricci-Curvature Ladder

This note sharpens the bivector-curvature continuum completion from Phase
CCXXVIII.

At the selected point q = 3, mu = q+1 = 4 and the exact W(3,3) packet lands on
three classical 4D curvature dimensions:

- Phi4 = 10 = dim Weyl(R^4)
- q^2 = 9 = dim S^2_0(R^4)
- lambda*Phi4 = 20 = dim Riem_alg(R^4)

where

- dim Weyl(R^4) = 10
- dim tracefree symmetric 2-tensors in 4D = 9
- dim algebraic curvature tensors in 4D = 20 = 10 + 9 + 1

So the W(3,3) transverse shell is not just a generic curvature packet. It
matches the full 4D curvature decomposition:

- Weyl part: 10
- tracefree Ricci part: 9
- scalar part: 1

## Exact q = 3 selectors

Let mu = q+1.

Then the Weyl selector is

- Phi4 - mu(mu+1)/2 = q(q-3)/2

and the tracefree-Ricci selector is

- q^2 - (mu(mu+1)/2 - 1) = q(q-3)/2.

So q = 3 is the unique positive integer point where

- Phi4 = dim Weyl(R^mu)
- q^2 = dim S^2_0(R^mu).

The curvature-shell selector is

- lambda*Phi4 - (Phi4 + q^2 + 1) = (q-3)(q^2+1)

so at q = 3 the exact W33 shell becomes

- 20 = 10 + 9 + 1.

## Higher packet reading

The exact family identity

- q*Phi3 = lambda*Phi4 + Phi4 + q^2

becomes at q = 3

- 39 = 20 + 10 + 9

so the promoted c6 packet factor q*Phi3 = 39 splits as

- full curvature shell 20
- Weyl shell 10
- tracefree Ricci shell 9.

There is also a sharp A4-side lift:

- 55 = 5*(k-1) = dim Sym^2(Weyl_4)

because dim Sym^2(R^10) = C(10+1,2) = 55. Thus the promoted factor

- a4 = 55 * 2^4 * 20

may be read as

- Sym^2(Weyl_4) * Clifford_4 * Riem_alg(R^4).

## Honest status

This still does not finish the smooth bridge theorem. But it narrows the
continuum wall further:

- the W33 packet now lands not only on bivectors and the full algebraic
  curvature shell,
- but on the full 4D curvature decomposition Weyl + tracefree Ricci + scalar,
- with the A4 packet lifting to Sym^2(Weyl_4).
