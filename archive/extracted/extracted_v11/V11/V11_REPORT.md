# V11 — Exact firewall-filtered Jacobiator support on g1 and deterministic cocycle testing

Computed **K3** on all `C(81,3) = 85320` g1 triples in **0.22s**.

- K3 stats: `{'zero': 84741, 'nonzero': 579, 'single': 579}`
- Output kind: `{'root': 579}`
- Output grade histogram (root outputs): `{'g1': 227, 'g2': 197, 'g0': 155}`
- Coefficients: `[(1, 300), (-1, 279)]`
- Bad-triad hit among nonzero K3: `{'good': 576, 'bad': 3}`

Top SU(3) input weight-sums (p,q):
- (0, 0): 134
- (1, 1): 84
- (-1, 2): 70
- (2, -1): 70
- (1, -2): 55
- (-2, 1): 49
- (-1, -1): 40
- (-3, 3): 39
- (3, 0): 27
- (0, -3): 11

## Cocycle test: δK3 on g1^4
- Candidate quads built from K3 support: 42231 (evaluated 42231) in 0.54s
- δK3 candidate stats: `{'zero': 42231}`
- δK3 random sample (N=50000) stats: `{'zero': 50000}` in 0.45s

### Interpretation
- **K3 is nonzero but δK3 is identically zero** on both (i) a large deterministic candidate set built from the exact K3 support, and (ii) a large random sample.
- That’s the signature of a **structured CE 3-cocycle obstruction** for the firewall-filtered bracket.
- In this discrete-basis implementation, the cocycle is **not Cartan-valued** (Cartan histogram is empty); it lands in root sectors (g0/g1/g2 split shown above).
- The obstruction is also **not localized** purely to the 9 forbidden i27 triads (only 3/579 hits were bad). That’s a real clue: the obstruction is more global than “just the forbidden triads.”
