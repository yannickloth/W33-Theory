import pandas as pd, os
bundle = r"c:\Repos\Theory of Everything\H27_OUTER_TWIST_ACTION_BUNDLE_v01 (1)"
print(os.listdir(bundle)[:10])
df = pd.read_csv(os.path.join(bundle,'outer_twist_action_table.csv'))
print(df.head())
print(df.columns)
print('len', len(df))
