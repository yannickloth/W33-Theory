# Phase CCL - Centered Root-255 Formula

This note sharpens the centered CM square from Phase CCXLVIII and the root-255
master theorem from Phase CCXLVII.

At q = 3 the centered square gave

- g = mu^2 - 1 = 15
- mu^2 + 1 = 17

with center

- mu^2 = 16.

Therefore the CM cube root

- j(-28)^(1/3) = 255

is not just the product 15*17. It is the centered-Clifford formula

- 255 = (mu^2 - 1)(mu^2 + 1)
-     = mu^4 - 1.

Numerically,

- mu^4 - 1 = 4^4 - 1 = 256 - 1 = 255.

## Exact selector

For the full W(3,q) family,

- q*(Phi4/2)*(Phi4+Phi6) - (mu^4 - 1)
-   = q*(q-3)*(q^4 - q^3 + q^2 + 3*q + 2)/2.

So q = 3 is the unique positive integer point where

- j(-28)^(1/3) = mu^4 - 1.

## Relation to earlier forms

This single centered formula contains several earlier bridge forms at once:

- mu^4 - 1 = (mu^2 - 1)(mu^2 + 1) = 15*17
- mu^4 - 1 = g*(mu^2 + 1)
- mu^4 - 1 = g*mu^2 + g = 240 + 15.

So the root 255 is the one-step scalar extension of the exceptional packet 240,
but also the centered quartic of the 4D Clifford packet mu^2 = 16.

## Best current reading

The CM root 255 is now best viewed as the centered quartic shell around the
Clifford packet:

- center: mu^2 = 16
- neighbors: mu^2 - 1 = 15 and mu^2 + 1 = 17
- product shell: mu^4 - 1 = 255.

This is stronger than carrying the separate identities 15*17, 240+15, and
196+39+20 independently. It identifies them all as shadows of the same centered
formula around the Clifford packet.