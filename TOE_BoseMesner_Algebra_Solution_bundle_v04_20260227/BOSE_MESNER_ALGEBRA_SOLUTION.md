# Bose–Mesner Algebra Solution for the 120-duad (edgepair) Scheme

This is a **complete algebraic solution** of the rank‑5 commutant / association‑scheme algebra coming from the degree‑120 action (your `sp43_edgepair_generators.json`).

We work in the adjacency‑algebra basis $\{A_0,A_1,A_2,A_3,A_4\}$ where $A_0=I$ and $\sum_i A_i = J$ (all‑ones).

Valencies: $(k_0,k_1,k_2,k_3,k_4)=(1, 2, 27, 36, 54)$, so $n=120$.

## 1) Multiplication table (structure constants)

The algebra is determined by intersection numbers $p_{ij}^k$ via

$$A_i A_j = \sum_{k=0}^4 p_{ij}^k\, A_k.$$

Key products (everything else follows by commutativity + symmetry):

- $A_1A_1 = 2A_0 + A_1$
- $A_1A_2 = A_4$
- $A_1A_3 = 2A_3$
- $A_1A_4 = 2A_2 + A_4$
- $A_2A_2 = 27A_0 + 10A_2 + 6A_3 + 4A_4$
- $A_2A_3 = 8A_2 + 9A_3 + 8A_4$
- $A_2A_4 = 27A_1 + 8A_2 + 12A_3 + 14A_4$
- $A_3A_3 = 36A_0 + 36A_1 + 12A_2 + 6A_3 + 12A_4$
- $A_3A_4 = 16A_2 + 18A_3 + 16A_4$
- $A_4A_4 = 54A_0 + 27A_1 + 28A_2 + 24A_3 + 22A_4$

### Rewrite rules you can use immediately

- $A_1^2 = A_1 + 2A_0$  (relation‑1 graph = **40 disjoint triangles**)
- $A_1A_2 = A_4$
- $A_1A_3 = 2A_3$
- $A_1A_4 = 2A_2 + A_4$

## 2) Eigenmatrices P and Q (complete diagonalization)

Because the commutant is commutative (rank‑5 scheme), the permutation module $\mathbb{C}^{120}$ is **multiplicity‑free**.

### P eigenmatrix (eigenvalues of $A_i$ on $E_r$)

| E_r   |   A0 |   A1 |   A2 |   A3 |   A4 |   mult |
|:------|-----:|-----:|-----:|-----:|-----:|-------:|
| E0    |    1 |    2 |   27 |   36 |   54 |      1 |
| E1    |    1 |   -1 |    9 |    0 |   -9 |     20 |
| E2    |    1 |    2 |   -3 |    6 |   -6 |     24 |
| E3    |    1 |    2 |    3 |  -12 |    6 |     15 |
| E4    |    1 |   -1 |   -3 |    0 |    3 |     60 |

### Q dual eigenmatrix (idempotents in the A‑basis)

Defined by $E_r = \frac1{n}\sum_i Q_{i,r}A_i$ and $PQ=nI$.

| A_i   |   E0 |        E1 |       E2 |       E3 |        E4 |
|:------|-----:|----------:|---------:|---------:|----------:|
| A0    |    1 |  20       | 24       | 15       |  60       |
| A1    |    1 | -10       | 24       | 15       | -30       |
| A2    |    1 |   6.66667 | -2.66667 |  1.66667 |  -6.66667 |
| A3    |    1 |   0       |  4       | -5       |   0       |
| A4    |    1 |  -3.33333 | -2.66667 |  1.66667 |   3.33333 |

## 3) Primitive idempotents (closed form)

- $E_0$ (rank $m_0=1$):  $E_0 = \frac{1}{120}\,(A_0 + A_1 + A_2 + A_3 + A_4)$
- $E_1$ (rank $m_1=20$):  $E_1 = \frac{1}{36}\,(6A_0 - 3A_1 + 2A_2 - A_4)$
- $E_2$ (rank $m_2=24$):  $E_2 = \frac{1}{90}\,(18A_0 + 18A_1 - 2A_2 + 3A_3 - 2A_4)$
- $E_3$ (rank $m_3=15$):  $E_3 = \frac{1}{72}\,(9A_0 + 9A_1 + A_2 - 3A_3 + A_4)$
- $E_4$ (rank $m_4=60$):  $E_4 = \frac{1}{36}\,(18A_0 - 9A_1 - 2A_2 + A_4)$

## 4) Minimal polynomials

- $A_1$:  `x**2 - x - 2`
- $A_2$:  `x**4 - 36*x**3 + 234*x**2 + 324*x - 2187`
- $A_3$:  `x**4 - 30*x**3 - 288*x**2 + 2592*x`
- $A_4$:  `x**5 - 48*x**4 - 387*x**3 + 3186*x**2 + 12636*x - 52488`

## 5) Representation-theoretic meaning (group algebra view)

Let $G=PSp(4,3)$ (order 25920) act on the 120 duads (line perfect‑matchings). Let $\mathcal{A}=\mathrm{End}_G(\mathbb{C}^{120})$.

- $\dim \mathcal{A}=5$ ⇒ **multiplicity‑free** decomposition of $\mathbb{C}^{120}$.
- Irreducible constituent dimensions are exactly the idempotent ranks: **1, 20, 24, 15, 60**.
- The $A_i$ are double‑coset operators for a stabilizer $H$ of size 216, so $(G,H)$ is a **Gelfand pair** and the rows of $P$ are spherical functions.
