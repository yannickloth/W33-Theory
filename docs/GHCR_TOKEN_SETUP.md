CI: GHCR_TOKEN (GHCR PAT) setup

Summary
-------
Some Lean container images are hosted on GitHub Container Registry (ghcr.io) and may require authentication to pull. Add a repository secret named `GHCR_TOKEN` containing a Personal Access Token (PAT) with `read:packages` (Packages) scope so CI can log into GHCR and pull protected images.

How to create the token
-----------------------
1. In GitHub, go to Settings → Developer settings → Personal access tokens (classic) → Generate new token (or the new fine-grained token flow).
2. Give the token a descriptive name and select the `read:packages` or equivalent scope so it can pull packages from ghcr.io.
3. Copy the token (you'll only be shown it once).

How to add to this repo
-----------------------
1. Go to this repository → Settings → Secrets and variables → Actions.
2. Add a new repository secret with **Name**: `GHCR_TOKEN` and **Value**: the PAT you created.

Notes
-----
- Once present CI will perform a conditional GHCR login before attempting to pull images. The weekly verification job will fail if no suitable image is available; PR jobs will remain non-fatal.
- If you prefer not to add a secret, CI will continue attempting public images but may be unable to pull some protected tags.
