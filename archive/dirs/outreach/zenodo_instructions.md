How to mint a Zenodo DOI for this GitHub Release

1. Ensure this repository is public and that you have admin access on GitHub.
2. Go to https://zenodo.org/account/settings/github/ and enable the GitHub integration for `wilcompute/W33-Theory`.
3. In GitHub, create a Release (choose tag `v2026-02-15-qec-mlut` or another tag). Tag must be pushed (we pushed `v2026-02-15-qec-mlut`).
4. Once the release is published on GitHub, Zenodo will automatically create a deposition and mint a DOI (you can edit metadata on Zenodo before finalizing).
5. Add the DOI to `RELEASES/DRAFT_v2026-02-15-qec-mlut.md` and update README/announcements as needed.

Notes
- Attach the executed notebook (`notebooks/w33_qec_demo.ipynb`) and any `checks/PART_CXV_qec_*.json` artifacts to the GitHub Release so they are archived by Zenodo.
- If you want help completing this step, I can prepare the release notes text and the assets to attach (already added in `RELEASES/`).