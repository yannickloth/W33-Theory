Paper alignment (Wilmot, 2025/2026)
==================================

The Springer open-access version (published Feb 14, 2026) states:

- "Section 5 provides the transformations to uncover all 480 representations of octonions and G2."
- The abstract: "... provides a direct construction of G2 for each of the 480 representations of the octonions."
- Section 6 summary reiterates that ρ_O^2=-1 is invariant under Pin(7) and that 480 representations can be enumerated.

This bundle reproduces the *same cardinality 480* by a direct discrete computation:
take the standard octonion multiplication table in a Cayley–Dickson basis and orbit it
under the full signed-permutation group of the 7 imaginary basis units.

Result:
- signed-permutation group size = 2^7 * 7! = 645120
- stabilizer inside signed perms has size 1344 = 168 * 8
- orbit size = 645120 / 1344 = 480

We also compute Der(O) via derivation equations (D(xy)=D(x)y+xD(y)) and get:
- dim Der(O) = 14 (g2)
- dim {D in Der(O): D(e7)=0} = 8 (sl3 core)

These align with the standard representation-theoretic inclusion g2 ⊃ sl3 and 7 = 1 ⊕ 3 ⊕ 3̄.
