# WG2 HP Web

Public webpage repository for SHARP WG2 Hadron Spectroscopy members.

## Source Of Truth

Member profiles live in a private source repository as separate files:

- `members/*.yaml`

This public repository stores only combined synchronized data:

- `data/members.yaml`
- `data/members.json`

## Synchronization

Run locally from this repository root:

```bash
python3 scripts/sync_members.py
```

Configure source folder with env var:

```bash
WG2_SOURCE_MEMBERS=/absolute/path/to/private-repo/members python3 scripts/sync_members.py
```

If `WG2_SOURCE_MEMBERS` is not set, the script uses its default relative source path.

## Reproducible Update Round

Use the helper script to always build from a clean sandbox checkout of one exact source commit.

```bash
bash scripts/update_round.sh
```

Optional arguments:

```bash
bash scripts/update_round.sh /absolute/or/remote/path/to/WG2-Hadron-Spectroscopy main
```

What this does:
1. Clones `WG2-Hadron-Spectroscopy` into `/tmp/wg2-source-sandbox-*`.
2. Pins one source commit and uses only `members/` from that checkout.
3. Builds `data/members.yaml`, `data/members.json`, and copies them into `site/data/`.
4. Prints SHA256 checksums for reproducibility records.

Recommended before commit:

```bash
git diff -- data/members.yaml data/members.json site/data/members.yaml site/data/members.json
```

If there are changes, commit those generated files together with any workflow/doc updates.

## Health Check

Run the same consistency checks used in CI:

```bash
python3 scripts/check_health.py
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
