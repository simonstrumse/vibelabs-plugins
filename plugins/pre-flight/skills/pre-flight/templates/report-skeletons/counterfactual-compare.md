# Report skeleton — `counterfactual-compare`

Extends `_core.md`. The universal sections are all rewritten to be cross-draft rather than single-stimulus. This skeleton differs more from `_core.md` than other mode skeletons because the comparison structure is fundamentally multi-draft.

## Header line

**Run:** <run-id> · **Mode:** counterfactual-compare · **Drafts compared:** <n> · **Personas consulted:** <n>

## Modified universal sections

### TL;DR (3 bullets)

- **Overall winner:** Draft <letter> — <one sentence on why>
- **Margin:** <clear / narrow / tied>
- **If no clear winner:** <alternative framing: "pick B and revise per these specific elements from A and C">

### Reaction distribution — per draft

Instead of one table, produce N tables (one per draft) showing per-cluster sentiment, would_act, trust_delta.

| Cluster | Draft A N | Sentiment mix | would_act mix | Trust Δ |
|---|---|---|---|---|
<!-- per draft -->

### Consensus signals — per draft

Consensus signals that emerged in each draft's reactions. Then a "cross-draft consensus" subsection: things ≥2 clusters said about ALL drafts (these are signals the question being tested isn't draft-sensitive).

### Disagreement axes — per draft + meta

Per-draft axes, then a meta-axis: where do drafts split the cast differently? This is the signal that the draft choice actually matters.

### Surprise signals — per draft

Surprising reactions per draft, then cross-draft: any persona whose posture swings sharply between drafts is a surprise signal — draft choice matters for that persona specifically.

### Red-line warnings — cumulative across drafts

All red-line crossings across all drafts. Mark which draft crosses which, and which drafts avoid which.

### Coverage gaps — shared across drafts

Same cast was used across drafts, so coverage gaps are shared.

## Mode-specific sections

### Side-by-side delta table — the core deliverable

See `artifacts/counterfactual-delta.md` for the full table. Summarized in the report as:

| Cluster | Winner | Margin | Headline quote |
|---|---|---|---|
| Activist | Draft <letter> | <clear / narrow / tied> | "<quote from winning draft's reaction>" |
| ... | ... | ... | ... |

### Per-dimension winners

Brief recap (full detail in the artifact):

- Highest trust-lift: Draft <letter>
- Fewest red-line crossings: Draft <letter>
- Largest supportive coalition: Draft <letter>
- Strongest message-house roof: Draft <letter>
- Clearest differentiation from competitor framing: Draft <letter>

### Recommended path forward

**Recommended:** Draft <letter>. **Why:** <2-3 sentences>. **Revisions to make before publication:**
1. <revision grounded in specific persona reaction>
2. <revision>
3. <revision>

### Elements to borrow across drafts

For a revised Draft <letter>:
- Borrow from Draft <X>: <specific phrase or framing> — because <why>.
- Borrow from Draft <Y>: <specific phrase> — because <why>.

## Artifacts emitted

- `artifacts/counterfactual-delta.md` — full delta report
- `artifacts/qa-doc.md` — composite questions across drafts
- `artifacts/stakeholder-heat-map.md`

## Length target

~2000 words for a 3-draft × 12-persona run.
