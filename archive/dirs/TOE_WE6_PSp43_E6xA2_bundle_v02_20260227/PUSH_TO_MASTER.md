# Push to master (manual, from your machine)

I can't push to GitHub directly from this environment, but this bundle is structured so you can.

From repo root:

```bash
# 1) Copy bundle contents into repo (or unzip directly into repo root)
#    (If you unzip into repo root, skip cp.)
cp -R toe_we6_decomp_bundle/* .

# 2) Quick run (optional but recommended)
python scripts/verify_orbit_decompositions.py
python scripts/classify_e8_roots_dotpair.py
python scripts/classify_w33_edges_by_rootclass.py

# 3) Commit + push
git status
git add docs/ scripts/ artifacts/line_action_orbits.json artifacts/e8_dotpair_class_summary.json artifacts/w33_edges_by_rootclass*.*
git commit -m "Add WE6 line-action decomposition + W33 root-class tagging scripts"
git push origin master
```

If you want to keep repo size down:
- commit only the scripts + docs
- put generated CSV/JSON under artifacts/ behind a .gitignore rule (or put them in outputs/)
