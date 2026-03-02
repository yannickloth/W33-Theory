# Triangle scheme on 120 blocks derived from the 36-vertex E6 antipode-pair SRG

We have a 36-vertex SRG (v,k,λ,μ)=(36,20,10,12). The 120 blocks are triangles in that SRG, and the 360 SRG edges
partition into those 120 triangles (each edge lies in exactly one block).

For two distinct blocks (triangles) T,U (each a 3-set of vertices in the SRG), define:

- `|T∩U|` (intersection size)
- `c(T,U)` = number of SRG edges between T and U (cross edges, 0..9)

Then the four nontrivial relations of the rank-5 association scheme on 120 blocks are:

- **R1 (valency 2)**: |T∩U|=0 and c(T,U)=0  (these are the other two blocks on the same W33 line)
- **R2 (valency 27)**: |T∩U|=1
- **R3 (valency 36)**: |T∩U|=0 and c(T,U)=6
- **R4 (valency 54)**: |T∩U|=0 and c(T,U)=4

This classification reproduces exactly the orbit sizes (2,27,36,54) of the stabilizer action and
reconstructs the full Bose–Mesner algebra (intersection numbers p_{ij}^k).
