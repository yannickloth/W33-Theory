# W(3,3) ↔ Q(4,3) via Klein correspondence (explicit, computed)

This bundle constructs:
- W(3,3): points = PG(3,3) points; lines = totally isotropic lines w.r.t. the symplectic form
  B(u,v) = u0*v3 - u3*v0 + u1*v2 - u2*v1  (mod 3).
- The Klein correspondence: each (projective) line in PG(3,3) maps to Plücker coords (p01,p02,p03,p12,p31,p23)
  satisfying the Klein quadric equation: p01*p23 + p02*p31 + p03*p12 = 0.
- The isotropic condition B(u,v)=0 becomes the hyperplane constraint p03 + p12 = 0 for our chosen B.

Intersecting Klein quadric with that hyperplane yields a parabolic quadric Q(4,3) in PG(4,3):
  p01*p23 + p02*p31 + 2*p03^2 = 0,
in 5 coordinates (p01,p02,p03,p31,p23).

Outputs:
- `Klein_map_line_to_Qpoint.json`: a bijection from the 40 isotropic lines of W(3,3) to the 40 points of Q(4,3).
- `Duality_point_to_Qline.json`: maps each W-point to a Q-line (a 4-point set in Q).
  This gives an explicit incidence-preserving isomorphism W(3,3) ≅ (Q(4,3))^dual.

Run:
  python verify_klein_duality.py
