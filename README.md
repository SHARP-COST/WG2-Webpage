# SHARP WG2 Webpage

[Website](https://sharp-cost.github.io/WG2-Webpage/) · [Deployment](https://github.com/SHARP-COST/WG2-Webpage/actions/workflows/site.yml)

Public directory of SHARP WG2 Hadron Spectroscopy members.

## Data and architecture

The authoritative membership roster is `WG2.list` in the WG2-Hadron-Spectroscopy repository.
`data/members.yaml` is this website's sanitized public snapshot, enriched with existing research profiles.
Names, affiliations, and contacts are refreshed from the roster. Research descriptions, GitHub handles,
and known countries are preserved for matching members. Missing research details and countries remain blank.

- `site/`: static HTML, CSS, and JavaScript.
- `data/members.yaml`: the only committed public member dataset.
- `scripts/sync_members.py`: explicit local import from the authoritative roster.
- `scripts/build_site.py`: builds `dist/` from public data, without private repository access.
- `scripts/check_health.py`: checks data, bundle consistency, and email privacy.
- `tests/`: import and privacy regression checks.

Generated JSON and `dist/` are not committed. The site fetches generated JSON at runtime.

## Update members

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/sync_members.py ../WG2-Hadron-Spectroscopy/WG2.list
python scripts/build_site.py
python scripts/check_health.py
python -m unittest discover -s tests
```

The importer reads only the roster above `## Emails`. It updates roster fields, adds new members,
and removes people absent from the roster. Review changes to `data/members.yaml` before committing.
For an import from a clean source checkout, use `bash scripts/update_round.sh [source-repository] [branch]`.

## Contact privacy

Only explicitly reviewed institutional domains in `scripts/member_data.py` are published.
Personal-provider and unreviewed addresses are omitted, never copied into this repository.
Retained contacts use `local (at) institution.domain`; neither the data nor the page includes a raw
address or a `mailto:` link. To publish a new institutional domain, review and add it to the allowlist.
Historical Git commits are unchanged.

## Preview and deploy

```bash
python scripts/build_site.py
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. GitHub Actions runs validation and builds on pull requests.
Pushes to `main` deploy the validated `dist/` artifact to GitHub Pages, configured with GitHub Actions as its source.
No private repository credentials are needed by deployment.
