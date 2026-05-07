# Factbase schema

The `ground-truth-researcher` agent writes one factbase file per run at `pre-flight-runs/<run>/factbase.md`. Every persona-worker, critic, and synthesizer reads it. Its job is to prevent factual drift — reactions to a hallucinated version of the company — and to give personas a shared ground truth so disagreements reflect worldview, not knowledge.

## File shape

```markdown
# Factbase — <company name> / <issue>

**Compiled:** <YYYY-MM-DD> · **Researcher:** ground-truth-researcher · **Source count:** <n> · **Fresh-quote window:** ≤90 days

---

## Corporate structure

- Legal entity name, listing, ticker, jurisdiction.
- Ownership and recent restructuring (acquisitions, divestitures, IPO, de-listing). Dates and named counterparties.
- Board composition (Chair, CEO, CFO at minimum). Named.
- Recent C-suite changes in the last 12 months.

## Business lines

- Each revenue-generating line: product/service, customer type, approximate scale.
- Distinguish B2B vs B2C. Note pharma/regulated vs consumer/retail where applicable.

## Operations & supply chain

- Geographic footprint. Flagged facilities and their statuses.
- Supply-chain dependencies and known chokepoints.
- Employee count and union/works-council presence where relevant.

## Regulatory baseline

- Which regulators govern this industry in the relevant jurisdictions.
- Active licenses, certifications, and their renewal/expiry status.
- Recent regulatory actions, inquiries, or settlements.

## Recent events shaping the situation

<The 3-8 events from the last 12-24 months that every stakeholder would have in mind when reading a release from this company. Each event has a date, a one-sentence summary, and a citation.>

- <YYYY-MM-DD> — <event> — source: <URL>
- <YYYY-MM-DD> — <event> — source: <URL>

## Known controversies

<Every publicly documented controversy in the last 3 years. Incident, date, source, and the specific persona-clusters that reacted.>

- <YYYY-MM-DD> — <incident> — reacting clusters: <e.g. activists, trade press> — source: <URL>

## Standard industry framings

<Two subsections: the issuing organization's preferred framings vs the critic framings. Personas use one or the other; this is the vocabulary landscape they operate in.>

**Industry self-framing:**
- "<phrase>"
- "<phrase>"

**Critic / counter-framing:**
- "<phrase>"
- "<phrase>"

## Key technical / scientific / economic facts

<Numerical anchors every persona can cite. Each with a source.>

- <fact> — source: <URL>
- <fact> — source: <URL>

## Stakeholder ecosystem map

<Named real people and institutions who will care about this stimulus. Persona-architect uses this as the starting set for cast design.>

- **Activists / NGOs:** <list of named orgs and key people, with one-line role>
- **Scientists:** <named researchers with relevant expertise>
- **Regulators:** <named bodies and key officials>
- **Press:** <trade publications and beat reporters>
- **Customers:** <named major customers or customer classes>
- **Investors:** <named institutional holders, sell-side coverage>
- **Internal:** <named comms/IR leads, sustainability officers>
- **Peer companies:** <direct competitors whose reaction matters>

## What personas should NOT do

<Drift-prevention list. Common misconceptions or out-of-date facts that Claude's background knowledge might surface but that contradict the factbase.>

- Do not assume <outdated fact>. The correct fact is <current fact>.
- Do not attribute <event> to <wrong party>. The actual actor was <correct party>.
- Do not reference events after <factbase cutoff date>. Personas live as of <date>.

## Provenance

- Source count: <n>
- Fresh-quote window: <e.g. ≤90 days — how recent the latest source quote is>
- Verified: <YYYY-MM-DD>
- Researcher's confidence note: <one-sentence self-assessment, flagging any area where sources were thin>
```

## Quality gates

- Minimum source count: 10 URLs.
- At least one source must date within 90 days of the run, or the factbase is flagged `stale`.
- Every named person in the stakeholder ecosystem map must be traceable to at least one URL in Provenance.
- "What personas should NOT do" section must be non-empty — the researcher must identify at least one common misconception to correct, because Claude's training data almost always carries at least one.

## Scope

One factbase per run. Shared across all personas. Updated only if the run is re-run — not amended mid-flight.
