# Report skeleton — core (all modes inherit)

Every mode-specific skeleton extends this file. Sections below are universal and must appear in every report in this order. Mode-specific sections (e.g. "Coalition dynamics" for crisis-tabletop, "Mock analyst Q&A" for earnings-rehearsal) are inserted at documented points.

Synthesizer follows this structure exactly. Headings unchanged. Sections may be short (one paragraph) but none may be omitted unless zero personas contributed to that section's theme — in which case write "(No material in this category)" and move on.

---

```markdown
# Stakeholder reaction report — <stimulus title>

**Run:** <run-id> · **Mode:** <mode name> · **Personas consulted:** <n> · **Stimulus:** <one-line description>

## TL;DR

- **Overall posture:** <one sentence — aggregate sentiment across clusters>
- **Largest risk:** <one sentence — the single most dangerous reaction>
- **Largest opportunity:** <one sentence — the highest-upside framing a persona surfaced>

## Reaction distribution

| Cluster | N | Sentiment mix | would_act mix | Avg trust delta |
|---|---|---|---|---|
<!-- Rows drawn from the cast-spec. Cluster labels are dynamic (activist, scientist, regulator, press, customer, investor, internal, peer-company, and mode-specific clusters like proxy-advisor or sovereign-investor). -->

Short prose summary (2-3 sentences) naming the cluster patterns. Concrete and named, e.g. "Activists uniformly hostile with [persona A] and [persona B] signaling visible retail action. Scientists split — [persona C] skeptical-critical, [persona D] neutral-technical."

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

Reactions that fit neither consensus nor expected cluster pattern. **This is often the most valuable section — do not skip.**

- <Persona (institution)>: <one-paragraph summary with a short quote>. Why it's a surprise: <one sentence>.

## Red-line warnings

Personas whose red_line the stimulus crossed. For each:

- **<Persona (institution)>** — red_line: <paraphrase of red_line from persona bundle> — crossed by: <quote from stimulus> — likely consequence: <what the persona will do>. Channel: <where they'll say it>. Quote from their reaction: "<quote>"

## Proposed revisions (≤5)

Each revision grounded in a persona reaction.

1. **<specific change>** — motivated by <persona(s)>. Before: "<stimulus line>". After: "<suggested line>". Rationale: <one sentence>.
2. ...

<!-- MODE-SPECIFIC SECTIONS INSERT HERE. See the mode's own skeleton file for what appears between "Proposed revisions" and "Coverage gaps". Examples:
- crisis-tabletop: "Coalition dynamics" (from social-dynamics phase) + "Narrative arc across rounds" (from memory-keeper)
- earnings-rehearsal: "Mock analyst Q&A" transcript (from debate phase)
- deal-comms: "Day 1 / 30 / 100 readiness" summary
- counterfactual-compare: "Side-by-side delta table" + "Per-cluster winner"
- regulatory-response: "Competitor scan" + "Coalition readiness"
-->

## Coverage gaps

Stakeholders the plan skipped or failed to simulate whose reactions might materially change the picture. Also personas whose reactions were KILLed by the critic loop and excluded from synthesis. Be honest about what we didn't learn.

- <skipped or killed persona type>: <why it matters for this stimulus>

## Appendix — Personas consulted

| ID | Name | Institution | Cluster | Sentiment | Confidence | would_act | use_constraint |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
```

---

## Formatting notes

- Quotes use inline quotation marks for short phrases, blockquotes only for multi-sentence pulls.
- Every quote that is not from the stimulus must come verbatim from a findings file. The `scripts/verify_quotes.py` step catches violations.
- Length targets: 5 personas → ~800 words. 12 personas → ~1600. 20 personas → ~2500. Do not pad to hit a target.
- For named personas whose `use_constraint` blocks public-facing attribution, quote as archetype (e.g. "a major institutional investor said...") and note the constraint in the appendix row.
- Cluster labels in the Reaction distribution table come from the cast-spec for this run — do not hardcode.
