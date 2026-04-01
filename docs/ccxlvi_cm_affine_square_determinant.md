# Phase CCXLVI - CM Affine Square Determinant

This note sharpens the CM affine square from Phase CCXLIV.

At q = 3 the promoted packets

- k = 12
- g = 15
- mu^2 + 1 = 17
- lambda*Phi4 = 20

fit into the exact affine square

- [ [12, 15],
-   [17, 20] ].

The new point is that this square has a nontrivial determinant identity:

- k*(lambda*Phi4) - g*(mu^2+1) = -g.

Numerically,

- 12*20 - 15*17 = 240 - 255 = -15.

So the determinant of the affine square is exactly minus the chiral Weyl-block
packet.

## Exact selector

For the full W(3,q) family,

- k*(lambda*Phi4) - g*(mu^2+1) + g
-   = q*(q^2+1)*(q-3)*(q+1)/2.

So q = 3 is the unique positive integer point where

- det([[k, g], [mu^2+1, lambda*Phi4]]) = -g.

## Best current reading

This adds a new structural layer to the CM/continuum square:

- the diagonal product is the exceptional packet 240,
- the anti-diagonal product is the new CM root 255,
- their difference is exactly one chiral Weyl block 15.

So the affine square is not just a layout of packets. Its determinant already
knows the chiral packet.
