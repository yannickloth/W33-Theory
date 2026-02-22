# TOE Kernel Spec v0.1 — W33 as an Information-Field Firewalled Gauge Network

This spec compresses the *verified* structural results from our W33/Witting work into a single coherent architecture: keys, authenticated transport, curvature-as-syndrome, phase clocking, and an E6 firewall carving a code subspace.

---

## 0) Primitive objects

### Universe \(\mathcal{U}\)
A finite information geometry with **40 atomic states** \(S=\{0,\dots,39\}\).

### Orthogonality graph \(G_{\perp}\)
A strongly regular graph on \(S\) with parameters **SRG(40,12,2,4)**.

- **Orthogonal / perfectly hidden:** \(u\perp v\) iff \((u,v)\) is an edge in \(G_{\perp}\)
- **Nonorth / potentially coupled:** \(u\not\perp v\) otherwise

> Encryption axiom: perfect secrecy = orthogonality (zero overlap); coupling requires nonorthogonality (partial key match).

---

## 1) Encapsulation: 10 “objects” with 2-bit private keyspaces

Partition \(S\) into **10 blocks** (“objects/contexts”) \(B_0,\dots,B_9\), each of size 4.

Each state \(s\in B_i\) carries a **2-bit internal key**
\[
x(s)\in \mathbb{Z}_2^2=\{00,01,10,11\}.
\]

Interpretation (Pauli frame / crypto key):
- \(x=(a,b)\leftrightarrow X^a Z^b\) (Pauli exponent key)
- \(11\) corresponds to \(XZ\sim iY\) (composite/fermion channel)

---

## 2) Authenticated interaction channel: N180 as unique handshake

Define an authenticated interaction relation \(N_{180}\subset S\times S\) with the **unique handshake property**:

For any ordered block pair \((A,B)\), and any \(x\in\mathbb{Z}_2^2\), there exists a **unique** partner key
\[
T_{AB}(x)\in\mathbb{Z}_2^2
\]
such that the corresponding states interact:
\[
s=(A,x),\quad s'=(B,T_{AB}(x))\quad\Rightarrow\quad (s,s')\in N_{180}.
\]

So each ordered pair has a **unique key-exchange map** \(T_{AB}\).

---

## 3) Transport field: affine gauge connection on keys

Each \(T_{AB}\) is affine:
\[
T_{AB}(x) = M_{AB}x + t_{AB},
\quad (M_{AB},t_{AB})\in AGL(2,2).
\]

- \(t_{AB}\in\mathbb{Z}_2^2\) is a “Pauli translation” (session-key translation).
- \(M_{AB}\in GL(2,2)\) is a “Clifford router” action on Pauli exponents.

> **Field A (transport/gauge):** the connection \((M_{AB},t_{AB})\).

---

## 4) Curvature / syndrome: holonomy on triples is a parity-check design

For any block triple \((A,B,C)\), define holonomy:
\[
H_{ABC} = T_{CA}\circ T_{BC}\circ T_{AB}\in AGL(2,2).
\]

Its **matrix class** (identity vs swap) is an orientation-independent **Z\(_2\)** syndrome on unordered triples.

Unordered triples split 60/60, and the “odd” triples form a **2-(10,3,4)** design:
- 60 triples of size 3
- every pair of blocks occurs in exactly 4 odd triples

> **Field B (syndrome/curvature):** the Z\(_2\) holonomy class on triangles (a MAC/parity-check structure).

---

## 5) Phase field: quantized interference clock

Each directed interaction edge carries a **phase tick**
\[
k_6(A\to B; x)\in\mathbb{Z}_6
\]
derived from gauge-invariant Bargmann / overlap phases.

This yields a local “session key / clock” per interaction:
\[
(\Delta x, k_6)\in \mathbb{Z}_2^2\times \mathbb{Z}_6 \quad\text{(24-state clock)}.
\]

> **Field C (phase/U(1)-like):** the \(\mathbb{Z}_6\) phase 1-form and its loop holonomies.

---

## 6) E6 kernel: firewall / admissibility constraint

Pick an embedding vertex \(v_0\in S\). Let:
- \(H_{12}=N(v_0)\) (12 orth neighbors)
- \(H_{27}\) = non-neighbors of \(v_0\)

For any nonorth pair \(\{u,v\}\subset H_{27}\), define witness set:
\[
W(u,v)=N(u)\cap N(v)
\quad\text{(size 4)}.
\]

### Firewall rule (theorem-level)
\[
\boxed{\text{bad}(u,v)\iff W(u,v)\subset H_{12}}
\]

The allowed E6 kernel edges are the complement:
\[
S_{\text{Schläfli}} = \text{nonorth}(H_{27}) \setminus \text{bad}.
\]

### Composite-channel prohibition (corollary)
On **bad** edges, the Pauli translation channel \(t=11\) (\(XZ\sim iY\)) never occurs.

Interpretation:
- \(W(u,v)\subset H_{12}\) = local-only transcript (vulnerable handshake).
- Firewall deletes those transitions and forbids the composite/fermion channel in vulnerable configurations.

> Constraint field: **bad** is a hard admissibility/causality rule; the E6 kernel is the surviving code subspace.

---

## 7) Sectors (“particle types”): idempotent decomposition of coupling algebra

The rank-6 association scheme yields idempotents \(E_0,\dots,E_5\) defining **sector planes**.

From selection-rule deltas we extracted three effective modes:
- **G**: authenticated router/gauge-like mode
- **M**: endpoint/matter-like mode
- **C**: constraint/firewall mode

Sectors carry charges under \((G,M,C)\); couplings are low-rank products of charges (effective field theory on sectors).

---

## Minimal physical reading

- **Interaction** occurs iff partial key match exists (nonorth) and handshake authenticates (N180), unless forbidden by firewall (bad).
- **Gauge field** = key transport \((M,t)\).
- **Curvature** = syndrome/parity design on triples.
- **Phase** = interference clock \(k_6\).
- **Mass/causality** = firewall constraint carving the E6 kernel.
- **Particles** = sector patterns with charges under \((G,M,C)\).
