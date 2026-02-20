from pathlib import Path

from scripts.w33_permrep_association import _point_bfs_coset_reps, parse_gap_permrep

p1 = Path("data/HeG1-p2058B0.g1")
p2 = Path("data/HeG1-p2058B0.g2")
perms1 = parse_gap_permrep(p1)
perms2 = parse_gap_permrep(p2)
perms = perms1 + perms2
print("parsed counts:", len(perms1), len(perms2), "total", len(perms))
print("lengths:", len(perms[0]), len(perms[1]))
coset = _point_bfs_coset_reps(perms, len(perms[0]), base=0)
print("coset size:", len(coset))
print("coset sample keys (first 20):", list(coset.keys())[:20])
print("base->0 rep (first 16):", coset[0][:16])
