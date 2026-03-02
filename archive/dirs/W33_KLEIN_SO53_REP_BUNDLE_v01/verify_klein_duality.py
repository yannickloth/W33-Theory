#!/usr/bin/env python3
# Verify the Klein correspondence duality between W(3,3) and Q(4,3) for our chosen symplectic form.
import json, itertools
MOD=3
def det2(a,b,c,d): return (a*d-b*c)%MOD
def norm(coords):
    for a in coords:
        if a%MOD!=0:
            inv=1 if a%MOD==1 else 2
            return tuple((inv*x)%MOD for x in coords)
    raise ValueError("zero")
def quadric_eq(c5):
    p01,p02,p03,p31,p23=c5
    return (p01*p23 + p02*p31 + 2*(p03*p03))%MOD

with open("W33_points_PG33.json","r") as f:
    pts=json.load(f)["points40"]
with open("W33_isotropic_lines_W33.json","r") as f:
    lines=json.load(f)["lines40"]
with open("Klein_map_line_to_Qpoint.json","r") as f:
    km=json.load(f)
Q_points=[tuple(v) for v in km["Q_points40"]]
line_to_Qid=km["line_id_to_Q_point_id"]
pt_to_Qline=None
with open("Duality_point_to_Qline.json","r") as f:
    pt_to_Qline=json.load(f)["point_id_to_Q_line_point_ids"]

# check: 40 points, 40 lines of size 4
assert len(pts)==40
assert len(lines)==40
assert all(len(s)==4 for s in lines)

# check: mapping is bijection
assert sorted(line_to_Qid)==sorted(set(line_to_Qid))==list(range(40))
# check: quadric eq
assert all(quadric_eq(Q_points[i])==0 for i in range(40))

# build incidence: point->incident lines in W
inc_point=[set() for _ in range(40)]
for lid,pset in enumerate(lines):
    for pid in pset:
        inc_point[pid].add(lid)
assert all(len(s)==4 for s in inc_point)

# duality incidence check:
# For any incidence (pid on lid), image Qpoint(line) is on image Qline(point)
for pid in range(40):
    qline=set(pt_to_Qline[pid])
    assert len(qline)==4
    for lid in inc_point[pid]:
        qpid=line_to_Qid[lid]
        assert qpid in qline
print("ALL CHECKS PASSED: Klein duality W(3,3) -> Q(4,3) (q=3, odd, so not self-dual).")
