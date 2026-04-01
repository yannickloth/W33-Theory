# Phase CCLI - Centered Quartic Ladder

This note sharpens the centered root-255 formula from Phase CCL and the
heat-extension ladder from Phase CCXLIX.

At q = 3 the centered Clifford packet is

- mu^2 = 16.

The two recent promoted packets are

- E   = 240
- 255 = j(-28)^(1/3).

The new point is that both are values of the same quartic ladder in mu:

- E   = mu^4 - mu^2
- 255 = mu^4 - 1.

Numerically,

- mu^4 - mu^2 = 4^4 - 4^2 = 256 - 16 = 240
- mu^4 - 1    = 4^4 - 1   = 256 - 1  = 255.

So the gap is exactly

- 255 - 240 = mu^2 - 1 = 15 = g.

## Exact selector

For the full W(3,q) family,

- E - (mu^4 - mu^2)
-   = q*(q-3)*(q+1)*(q^2+1)/2.

So q = 3 is the unique positive integer point where

- E = mu^4 - mu^2.

Combined with the previous phase

- j(-28)^(1/3) = mu^4 - 1,

the two packets form the exact quartic ladder

- mu^4 - mu^2 -> mu^4 - 1
- 240         -> 255.

## Best current reading

The exceptional packet and the new CM root are now two consecutive shells around
the same Clifford center mu^2 = 16:

- 240 = mu^2(mu^2 - 1)
- 255 = (mu^2 - 1)(mu^2 + 1).

This is stronger than carrying the identities separately. It shows that the
exceptional packet 240 and the CM root 255 belong to one centered quartic
hierarchy around the same 4D Clifford packet.