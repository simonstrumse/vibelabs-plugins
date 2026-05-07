# Mode: `positioning-pressure-test`

**In-house names:** positioning review; rebrand diagnostic; pre-rebrand stress test; brand narrative pressure test.
**Benchmark workflows:** Interbrand / Lippincott / Siegel+Gale pre-rebrand workshop; RepTrak Reputation Dimensions (7-driver scorecard) as output lens; Edelman Trust Barometer narrative testing.

## Use when

A company has a positioning statement, rebrand narrative, corporate-purpose rewrite, investor-story refresh, or sustainability narrative ready to test. This is upstream of a specific announcement — the stimulus is a positioning artifact, not a press release. The pressure test: which stakeholders find it credible? Which read it as corporate-speak? Which reputation dimensions does it move? What's the specific claim that would collapse under scrutiny?

## Use another mode if

- The positioning is being tested before a specific announcement → run this first, THEN `launch-pre-mortem` or `crisis-pre-flight` on the announcement
- The positioning is purely internal / employee narrative → `internal-first`
- You want a quantitative survey result → this skill isn't the tool — use RepTrak, Kantar BrandZ, or Y&R BAV (real-respondent instruments)

**Note:** this mode requires a concrete positioning artifact. Running it against "general brand reputation" with no stimulus isn't supported — no-stimulus brand evaluation isn't a real PR workflow.

## Default phase composition

1. `factbase` — 90-day freshness window (positioning shifts slowly); budget 10 WebFetch calls (including brand-study coverage if any)
2. `cast-design` — salience scoring on; emphasis on cross-cluster credibility (positioning lands on all audiences)
3. `deep-research` — 10 parallel researchers
4. `initial-reactions` — 10 parallel workers, each reacting to the positioning artifact
5. `critic` — 10 parallel critics
6. `synthesis` — skeleton `templates/report-skeletons/positioning-pressure-test.md`; artifacts: `reputation-scorecard`, `qa-doc`, `stakeholder-heat-map`, `rebrand-risk-register` (embedded)

## Default cast

- **Size:** 10
- **Cluster distribution:**
    - press: 2 (trade + investigative — will they call it credible?)
    - customer: 2 (existing + prospect — will they find it relevant?)
    - employee / internal: 2 (will employees recognize the company in this?)
    - activist / NGO: 1 (will this be read as greenwashing / corporate-speak?)
    - investor: 1-2 (does the positioning align with their thesis?)
    - peer-company: 1 (competitive differentiation check)
    - scientist / subject-matter expert: 0-1 (only if positioning makes specific technical claims)

## Depth parameters

- Revise cycles: 2
- Social-dynamics: OFF
- Debate: OFF
- Memory: within-run only if this is part of a positioning-iteration sprint (test → revise → re-test)

## Artifacts emitted alongside `report.md`

- `artifacts/reputation-scorecard.md` — RepTrak-style scoring across the 7 dimensions (Products/Services, Innovation, Workplace, Governance, Citizenship, Leadership, Performance) based on persona reactions. Qualitative, not quantitative.
- `artifacts/qa-doc.md` — 20-40 anticipated questions (press, customer, employee, investor)
- `artifacts/stakeholder-heat-map.md`
- Rebrand risk register section embedded in report: which claims in the positioning would collapse under scrutiny from which personas, with mitigations.

## Expected runtime

~4-5 minutes.

## Expected cost

~$2 per run.

## Failure modes specific to this mode

- **Positioning too abstract.** If the stimulus is 3 high-level sentences ("we unlock human potential") with no specifics, persona reactions will be generic — every persona will find it empty. The report surfaces this as a coverage-wide signal: "the positioning needs concrete claims before it can be pressure-tested."
- **Employee cluster critical.** Internal recognition is the single strongest signal for whether positioning is credible. If the employee personas find the positioning unrecognizable, that's the headline finding regardless of other cluster reactions.
- **Activist cluster as greenwashing check.** Positioning that touches sustainability / ESG / purpose language must have an activist persona in the cast. Otherwise the report's greenwashing-risk read is blind.

## Evidence trail

See `reference/methodology-sources.md` §positioning-pressure-test.
