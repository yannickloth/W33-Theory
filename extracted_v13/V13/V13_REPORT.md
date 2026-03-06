# V13 — Closed form for the firewall-filtered Jacobiator K3 as a coboundary of the deleted 2-cochain m

We define the firewall-filtered bracket by deleting one term from each of 162 forbidden g1×g1 brackets:

- Full bracket: `[ , ]`
- Deleted 2-cochain: `m(i,j)` is the removed single-term output for each forbidden pair.
- Filtered bracket: `[i,j]' = [i,j] - m(i,j)`.

Since `[ , ]` satisfies Jacobi, the filtered Jacobiator on g1 triples can be expanded exactly as:

**K3(a,b,c) = J'(a,b,c) = Part1 + Part2 + Part3** where:

- **Part1** = `-([m(a,b),c] + [m(b,c),a] + [m(c,a),b])`
- **Part2** = `-(m([a,b],c) + m([b,c],a) + m([c,a],b))` (full bracket inside m)
- **Part3** = `+(m(m(a,b),c) + cyc)` (quadratic term)

## Verification
- g1 triples total: 85,320
- nonzero K3 triples: 579
- exact match rate (computed K3 vs expanded Part1+Part2+Part3): **100%**

Mechanism split:
- direct Part1-only: 259
- indirect Part2-only: 320
- Part3 ever nonzero: 0

## Why V11 saw δK3 = 0 (cocycle)
Here K3 is *exactly* the linear CE-style expression in the 2-cochain m with no quadratic terms.
So δK3=0 follows from δ²=0. This gives a structural proof of the cocycle behavior.

## Why K3 can be nonzero even when no input pair is forbidden
In the 320 indirect cases, none of (a,b),(b,c),(c,a) is a forbidden pair, but the full bracket [a,b] (etc.) contains intermediate g1 terms u such that (u,c) is a forbidden pair.
Those contributions appear through Part2.

## Direct mechanism (Part1)
Top forbidden input pairs (unordered):
- (166, 189): 22
- (64, 142): 22
- (189, 195): 21
- (16, 222): 20
- (30, 185): 18
- (165, 195): 17
- (166, 194): 17
- (38, 132): 17
- (142, 180): 16
- (86, 153): 15

Top removed outputs in Part1:
- out=229: 34
- out=32: 26
- out=226: 22
- out=75: 22
- out=237: 21
- out=79: 20
- out=88: 18
- out=41: 17
- out=191: 16
- out=107: 15

## Indirect mechanism (Part2)
Source term frequencies:
- ab->c: 136
- bc->a: 110
- ca->b: 74

Distinct forbidden pairs used indirectly: 90 / 162
Top intermediate u terms:
- u=180 grade=g1 count=18
- u=197 grade=g2 count=18
- u=18 grade=g0 count=15
- u=22 grade=g1 count=12
- u=30 grade=g1 count=12
- u=26 grade=g0 count=12
- u=167 grade=g0 count=12
- u=176 grade=g0 count=9
- u=159 grade=g2 count=9
- u=147 grade=g2 count=8

Top forbidden (u,z) pairs used in Part2:
- (22, 222): 10
- (30, 184): 10
- (24, 197): 9
- (185, 197): 9
- (13, 180): 8
- (22, 158): 8
- (30, 185): 8
- (38, 132): 8
- (142, 180): 7
- (64, 180): 7
