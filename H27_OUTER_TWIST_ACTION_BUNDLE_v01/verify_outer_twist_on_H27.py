\
import pandas as pd, json
import numpy as np

df = pd.read_csv("outer_twist_action_table.csv")
# verify formula from JSON
dat = json.load(open("outer_twist_action_on_H27.json"))
A = np.array(dat["induced_map_on_H27_coords"]["u_map_affine"]["A"], dtype=int) % 3
b = np.array(dat["induced_map_on_H27_coords"]["u_map_affine"]["b"], dtype=int).reshape(2,1) % 3

for r in df.itertuples(index=False):
    u = np.array([[r.x],[r.y]],dtype=int)%3
    u2 = (A@u + b) % 3
    t2 = (2*r.t + 2 + 2*r.x + r.y) % 3
    if (int(u2[0,0]), int(u2[1,0]), int(t2)) != (r.x2,r.y2,r.t2):
        raise SystemExit("FAIL: formula mismatch at row "+str((r.x,r.y,r.t)))
print("ALL CHECKS PASSED: affine u-map and t-map reproduce the full table.")
