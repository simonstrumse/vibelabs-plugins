# Report skeleton — `red-team-read`

Extends `_core.md`. Universal sections inherited. Mode-specific sections insert between "Proposed revisions" and "Coverage gaps."

## Header line

**Run:** <run-id> · **Mode:** red-team-read · **Personas consulted:** <n> (adversarial-only) · **Stimulus:** <one-line>

## Mode-specific sections

### Hostile-headline catalog

5-10 headlines hostile personas would write about this material. Each attributed.

1. "<headline>" — from <adversarial press persona>'s reaction
2. "<headline>" — from <activist persona>'s reaction
3. "<headline>" — from <short-seller persona>'s reaction
4. ...

### Worst pull-quotes

The quotes from the stimulus that hostile readers will lift and use. Each with a one-sentence explanation of why.

- **"<verbatim from stimulus>"** — why it's a pull: <one line> — who will lift it: <persona>.
- ...

### Claims likely to be challenged

Specific claims that will draw adversarial scrutiny. Grounded in red-line warnings.

- **Claim:** "<exact phrase>" — **challenger:** <persona> — **challenge:** "<quote from reaction>" — **evidence they would demand:** <one line> — **do we have it?** <yes/no/partial> — **recommended revise:** <one line>.
- ...

### Debate phase — short-seller ↔ CFO proxy

Condensed transcript:
- **SS1:** <quote>
- **CFO1:** <quote>
- **SS2:** <quote>
- **CFO2:** <quote>
- **SS3:** <quote>
- **CFO3:** <quote>

Did the CFO narrative hold? Where did it weaken?

### Debate phase — hostile journalist ↔ spokesperson proxy

Condensed transcript:
- **J1:** <quote>
- **SP1:** <quote>
- **J2:** <quote>
- **SP2:** <quote>
- **J3:** <quote>
- **SP3:** <quote>

Did the spokesperson's framing survive follow-up pressure?

### Vulnerability memo — top 5 ranked

For each vulnerability:
1. **<vulnerability title>** (severity <high/medium/low> × probability <high/medium/low>) — **surfaced by:** <personas> — **suggested edit / reframe:** <concrete line>.
2. ...
3. ...
4. ...
5. ...

## Artifacts emitted

- `artifacts/vulnerability-memo.md` (expands on the top-5 ranking above)
- `artifacts/qa-doc.md` (hostile questions only with model answers)
- `artifacts/stakeholder-heat-map.md` (adversarial cluster only)

## Length target

~1600 words (8-persona adversarial cast + debate).
