# TOE: Pocket(20) completion bit under full PSp(4,3) stabilizer — and the Sp(4,3) lift

This report is computed from the uploaded bundles in `/mnt/data` and is fully reproducible via `recompute_pocket20_deck_lift.py` (included).

## 1. The ambient group and the stabilizer

* The 10 given generators `sp43_generators_on_e6pairs_36.json` generate a permutation group of size **25920** on the 36 SRG vertices (this is **PSp(4,3)** in its 36-point action).
* The stabilizer of vertex **20** inside that group has size **720**.

So we have:
\[
|PSp(4,3)| = 25920,\qquad |\mathrm{Stab}(20)| = 720.
\]

## 2. The “edgepair completion” 2-cover at center 20

From `pocket20_edgepair_cover.csv`:

* There are **45** unordered pairs of orbit10 K5-edges.
* Each pair has **2** pocket completions.
* Total pockets in this cover: **90**.

So the cover is a clean 2-sheeted fibration:
\[
\text{Pockets}_20 \cong \binom{10}{2}\times \mathbb{Z}_2.
\]

The involution that swaps the two completions inside each fiber is the **deck flip** `F`
(see `edgepair_fiber_pairs_45.csv`, `deck_flip_perm_on_90.json`).

## 3. How the completion bit transforms under the *full* stabilizer

Let `completion(p)∈{0,1}` be the bit from the CSV.

**Key fact:** the stabilizer `Stab(20)` preserves the 90-pocket cover *as a set* (no element sends a covered pocket outside the 90-set).

But the completion bit is **not** globally invariant (nor globally flipped) under `Stab(20)`:

* For most elements, some edgepair fibers are swapped and others are not.
* I also tried to gauge-change the labeling by flipping fibers (a 0-cochain) to reduce the action to a *global* ± character; the linear system is inconsistent (see code).

So: the completion bit is a genuinely **nontrivial 2-lift** structure, not reducible to “all + / all −” at the stabilizer level.

## 4. The breakthrough: you get the **Sp(4,3) central double cover** for free

Even though the completion bit is not a global character, the deck flip **commutes with every stabilizer element**:

> `F g = g F` for all `g ∈ Stab(20)`.

This means adjoining the deck flip produces a **central extension**:
\[
\langle \mathrm{Stab}(20), F\rangle
\]
of size **1440**, i.e.
\[
|\langle \mathrm{Stab}(20), F\rangle| = 1440 = 2\cdot 720.
\]

So the 90-pocket cover is literally a place where the **hidden central Z₂** (the one you *cannot see* on the 36 SRG vertices) becomes **visible**.

Interpretation:

* On SRG36 vertices you only see **PSp(4,3)**.
* On this canonical 2-cover you see the **lift to Sp(4,3)**, because the center acts as the deck flip.

This matches the “two global glue solutions” phenomenon in your pocket-sign gluing: central sign data is invisible in the base but real in the lifted object.

## 5. Files

* `SUMMARY.json` — all counts and confirmations
* `stab20_generators_and_induced_actions.json` — two explicit stabilizer generators (36-action + induced 90-action) and the deck flip on 90
* `edgepair_fiber_pairs_45.csv` — explicit fiber pairing (the deck flip)
* `COMMUTATION_CHECK.txt` — commutation verified for all 720 stabilizer elements

