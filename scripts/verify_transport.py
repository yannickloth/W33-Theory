import json
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_r=[axis_adj[f'r{i}'] for i in range(4)]
trans=json.load(open('transported_r_generators.json'))
print([axis_r[i]==trans[f'r{i}'] for i in range(4)])
