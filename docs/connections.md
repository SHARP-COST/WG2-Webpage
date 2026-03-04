# Future Connections Model (Design Note)

The current webpage intentionally has **no member-to-member connection logic**.

This file describes how to add connections later in a meaningful way.

## Why It Was Removed

Simple overlap of `expertise_tags` creates shallow and potentially misleading relations.
A better model should represent real collaboration or scientifically relevant proximity.

## Recommended Data Model

Add an optional `connections` section to the combined data:

```yaml
connections:
  - source_id: "member-a"
    target_id: "member-b"
    type: "coauthor"
    weight: 0.9
    evidence: "doi:10.xxxx/xxxxx"
  - source_id: "member-a"
    target_id: "member-c"
    type: "project"
    weight: 0.7
    evidence: "WG2 task force: spectroscopy benchmarks"
```

## Connection Types

Use explicit typed edges:

- `coauthor`: shared publication history
- `project`: same task force / work package
- `method`: shared method stack (e.g., dispersion, lattice, DSE)
- `experiment-theory`: complementary role across experiment/theory
- `mentor`: supervision / training relation

## Weight Rules

Normalize to `[0, 1]` and keep rules transparent.

Example weighting:

- coauthor in last 3 years: `+0.4`
- same active WG2 task: `+0.3`
- same primary method family: `+0.2`
- explicit user-curated link: `+0.1`

Clamp max to `1.0`.

## UI Plan

When implementing lines again:

1. Render lines only when a card is selected.
2. Filter by connection type (chips/toggles).
3. Show tooltip with `type`, `weight`, and `evidence`.
4. Keep default view uncluttered (lines hidden until interaction).

## Governance

- Do not infer social/professional links from weak heuristics alone.
- Keep every displayed edge explainable by explicit evidence.
- Store provenance (`evidence`) for auditability.
