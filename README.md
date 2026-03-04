# WG2 HP Web

Public webpage repository for SHARP WG2 Hadron Spectroscopy members.

## Source Of Truth

Member profiles live in the private repository:

- `/Users/mikhailmikhasenko/Documents/SHARP.CAT/WG2-Hadron-Spectroscopy/members/*.yaml`

This public repository stores only combined synchronized data:

- `data/members.yaml`
- `data/members.json`

## Synchronization

Run locally from this repository root:

```bash
python3 scripts/sync_members.py
```

Optional override for source folder:

```bash
WG2_SOURCE_MEMBERS=/absolute/path/to/private-repo/members python3 scripts/sync_members.py
```

## Local Build

```bash
python3 scripts/build_site.py
```

This will:
1. Sync member YAML files from the private repository.
2. Generate combined `data/members.yaml` and `data/members.json`.
3. Copy data into `site/data/` for static hosting.

## Deployment

GitHub Actions workflow `.github/workflows/site.yml` deploys the content of `site/` to GitHub Pages.
