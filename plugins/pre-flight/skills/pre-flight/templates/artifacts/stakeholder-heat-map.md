# Artifact: Stakeholder heat map

Per-persona Power × Legitimacy × Urgency scoring (Mitchell-Agle-Wood 1997 stakeholder salience model). Paired with the reaction data from this run (sentiment, trust_delta, would_act) to produce a visual of who matters most for this stimulus.

## Structure

```markdown
# Stakeholder heat map — <stimulus title>

**Salience framework:** Mitchell-Agle-Wood 1997 (power × legitimacy × urgency)
**Paired with:** this run's reactions

## Heat map table

| Persona | Cluster | Power | Legitimacy | Urgency | Tier | Sentiment | Trust Δ | Will act? | Channel |
|---|---|:-:|:-:|:-:|:-:|---|:-:|---|---|
| <name or archetype> | <cluster> | <0-10> | <0-10> | <0-10> | <1/2/3> | <sentiment> | <delta> | <yes/no/cond> | <channel> |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Tier-1 (definitive stakeholders)

<Personas with salience ≥ 7 on all three axes. These must be engaged. For each:>

- **<Persona>** — <one-sentence engagement note: what they need from the organization in the next 72h>

## Tier-2 (expectant stakeholders)

<Personas with ≥ 6 on two of three axes. Should be engaged. For each:>

- **<Persona>** — <one-sentence engagement note>

## Tier-3 (latent stakeholders)

<Personas with ≥ 6 on one axis. Monitor. For each:>

- **<Persona>** — <one-sentence monitor note>

## Engagement sequencing

Based on tier and urgency, the recommended sequence for the first 72 hours:

1. <Persona or cluster> — <timing, e.g. "within 2h"> — <mode, e.g. "direct call from spokesperson">
2. <Persona or cluster> — <timing> — <mode>
3. ...

## Coverage gaps on the heat map

<Personas excluded from the cast that would appear here if included. From the report's Coverage gaps section.>

- <excluded persona type>: <estimated tier if we had included them>
```

## Grounding rules

- Salience scores come from the cast-spec (architect-assigned). Do not re-score in the synthesizer.
- Sentiment / trust_delta / would_act / channel come from the final reaction files.
- Engagement sequencing is pulled from the report's red-line warnings (who must be engaged first to prevent escalation) and from urgency scores.
- Coverage gaps section mirrors the report's Coverage gaps — don't hide excluded personas.

## Visual note

For the markdown deliverable, the table format above is sufficient. For a presentation-ready visual, the PR lead can transcribe into a 3×3 grid (Power × Legitimacy axes, Urgency as color/size) in PowerPoint — that's outside the skill's output but the table data supports it directly.

## Length

Heat map table fits on one page. Tier commentary + sequencing ~300-500 words total.
