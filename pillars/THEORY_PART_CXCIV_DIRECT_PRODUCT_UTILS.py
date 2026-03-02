#!/usr/bin/env python3
"""Utility functions exploiting the \(\Gamma\times H\) direct product.

Several of the newly written pillars have shown that the monodromy group
\(\Gamma\) and the tomotope automorphism set \(H\) commute and intersect
trivially.  In the closure \(<\Gamma,H>\subseteq S_{192}\) this means the
combined group is isomorphic to the direct product of the two factors.

The only computation required to build the closure is therefore the
pairwise multiplication of every element of \(\Gamma\) with every element of
\(H\), a task of size \(|\Gamma|\times|H|\) rather than an expensive
BFS through the symmetric group.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple


def compose(p: Tuple[int, ...], q: Tuple[int, ...]) -> Tuple[int, ...]:
    """Return permutation p\circ q."""
    return tuple(p[q[i]] for i in range(len(p)))


def direct_product_closure(
    Gamma: Iterable[Tuple[int, ...]], H: Iterable[Tuple[int, ...]]
) -> List[Tuple[int, ...]]:
    """Return list of permutations representing the closure of Gamma and H.

    Because every element of Gamma commutes with every element of H and their
    intersection is trivial, the map

        (g,h) \mapsto g\circ h

    is injective and its image has size |Gamma|*|H|.  This function simply
    computes that image.
    """
    return [compose(g, h) for g in Gamma for h in H]
