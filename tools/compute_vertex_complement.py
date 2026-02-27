import pandas as pd

df=pd.read_csv('H27_CE2_FUSION_BRIDGE_BUNDLE_v01/pg_point_to_h27_vertex_coords.csv')
ids=set(df['vertex_id'])
print(len(ids),sorted(ids))
print('complement',sorted(set(range(40))-ids))
