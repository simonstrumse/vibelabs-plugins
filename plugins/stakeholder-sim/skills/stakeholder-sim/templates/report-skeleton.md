# Report skeleton

Synthesizer follows this structure exactly. Headings unchanged. Sections may be short (one paragraph) but none may be omitted unless N=0 personas contributed to that section's theme — in which case write "(No material in this category)" and move on.

---

```markdown
# Stakeholder reaction report — <stimulus title>

**Run:** <run-id> · **Personas consulted:** <n> · **Stimulus:** <one-line description> · **Release type:** <product-launch | ccamlr-policy | financial | bycatch-incident | sustainability-report | m-and-a | general>

## TL;DR

- **Overall posture:** <one sentence — aggregate sentiment across clusters>
- **Largest risk:** <one sentence — the single most dangerous reaction>
- **Largest opportunity:** <one sentence — the highest-upside framing a persona surfaced>

## Reaction distribution

| Cluster | N | Sentiment mix | would_act mix | Avg trust delta |
|---|---|---|---|---|
| Activists | | | | |
| Scientists | | | | |
| Regulators | | | | |
| Press | | | | |
| Customers | | | | |
| Investors | | | | |
| Internal | | | | |

Short prose summary (2-3 sentences) naming the cluster patterns. E.g. "Activists uniformly hostile with Hammarstedt and Allan threatening visible retail action. Scientists split — Savoca skeptical-critical, Kawaguchi neutral-technical. Press transactional except Bøe, who flagged a Brennpunkt angle."

## Consensus signals

Things ≥2 personas from **different clusters** noticed independently. Each as a subsection:

### <concise finding>

- <Persona A (institution)>: "<quote from reaction>"
- <Persona B (institution)>: "<quote from reaction>"

Why it matters: <one sentence on the PR implication>

## Disagreement axes

Each axis as a subsection. Name the axis concretely. Both sides with quotes.

### <axis — e.g. "Is this a pharma-grade launch or a consumer supplement?">

- **Side A:** <Persona (institution)>: "<quote>"
- **Side B:** <Persona (institution)>: "<quote>"

Resolution advice: <one sentence — which side to pick, or how to disambiguate in the copy>

## Surprise signals

Reactions that fit neither consensus nor expected cluster. **This is often the most valuable section — do not skip.**

- <Persona (institution)>: <one-paragraph summary with a short quote>. Why it's a surprise: <one sentence>.

## Red-line warnings

Personas whose red_line the release crossed. For each:

- **<Persona (institution)>** — red_line: <paraphrase of red_line from persona bundle> — crossed by: <quote from stimulus> — likely consequence: <what the persona will do>. Channel: <where they'll say it>. Quote from their reaction: "<quote>"

## Proposed revisions (≤5)

Each revision grounded in a persona reaction.

1. **<specific change>** — motivated by <persona(s)>. Before: "<stimulus line>". After: "<suggested line>". Rationale: <one sentence>.
2. ...

## Coverage gaps

Stakeholders the plan skipped or failed to simulate whose reactions might materially change the picture. Be honest about what we didn't learn.

- <skipped persona type>: <why it matters for this release>

## Appendix — Personas consulted

| ID | Name | Institution | Sentiment | Confidence | would_act |
|---|---|---|---|---|---|
| | | | | | |
```

---

## Formatting notes

- Quotes use inline quotation marks for short phrases, blockquotes only for multi-sentence pulls.
- Every quote that is not from the stimulus must come verbatim from a findings file. The verify_quotes.py step will catch violations.
- Length targets: 5 personas → ~800 words. 12 personas → ~1600. 20 personas → ~2500. Do not pad to hit a target.
