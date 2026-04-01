# Phase CCXLVIII - Centered CM Square

This note sharpens the CM affine square from Phase CCXLIV.

At q = 3 the promoted packets

- k = 12
- g = 15
- mu^2 + 1 = 17
- lambda*Phi4 = 20

are not just an affine square. They are exactly the four neighbors of the same
center

- mu^2 = 16.

Indeed,

- k          = mu^2 - lambda^2 = 16 - 4 = 12
- g          = mu^2 - 1        = 16 - 1 = 15
- mu^2 + 1   = 16 + 1          = 17
- lambda*Phi4 = mu^2 + lambda^2 = 16 + 4 = 20.

So the four packets form the centered square

- mu^2 ± 1
- mu^2 ± lambda^2.

## Exact selectors

For the full W(3,q) family,

- k - (mu^2 - lambda^2) = q(q-3)
- g - (mu^2 - 1) = q(q-3)(q+1)/2
- lambda*Phi4 - (mu^2 + lambda^2) = (q-3)(q^2+1)
- (mu^2 + 1) - (mu^2 + 1) = 0.

So q = 3 is the unique positive integer point where all four promoted packets
collapse onto the centered form around mu^2.

## Consequences

1. Opposite corners sum to the same value:
   - k + lambda*Phi4 = 2*mu^2 = 32
   - g + (mu^2 + 1) = 2*mu^2 = 32.

2. The determinant identity from the previous phase becomes transparent:
   - k*(lambda*Phi4) - g*(mu^2+1)
   - = (mu^2-lambda^2)(mu^2+lambda^2) - (mu^2-1)(mu^2+1)
   - = 1 - lambda^4
   - = 1 - mu^2 = -15 = -g.

So the affine-square determinant is really a centered-Clifford identity.

## Best current reading

The CM / continuum packets 12, 15, 17, 20 are now organized by a single center
mu^2 = 16. This is stronger than the earlier affine-square picture because the
packets are no longer just connected by steps q and q+2: they are the exact
plus/minus neighbors of the 4D Clifford packet.