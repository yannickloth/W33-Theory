import json, os, pprint
bundle = r"c:\Repos\Theory of Everything\H27_OUTER_TWIST_ACTION_BUNDLE_v01 (1)"
with open(os.path.join(bundle, "outer_twist_action_on_H27.json")) as f:
    d = json.load(f)
pprint.pprint(d)
