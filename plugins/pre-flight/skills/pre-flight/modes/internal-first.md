# Mode: `internal-first`

**In-house names:** internal-first announcement; cascade comms; workforce-change comms pre-flight.
**Benchmark workflows:** IABC (International Association of Business Communicators) Handbook cascade methodology; Mercer workforce-comms; layoff / RTO / restructuring comms playbooks.

## Use when

An announcement is primarily internal — layoffs, RTO mandate, restructuring, leadership reorg, comp / benefits change, organizational culture shift — but leak risk to external audiences is material. The comms team has an all-hands script, manager toolkit, team-level talking points, and FAQ drafts. The pressure test: employee reception (primary), leaked-to-press reception (secondary), customer and investor reception if the leak travels, activist reception if layoffs / workforce impact is significant.

## Use another mode if

- The announcement is fully public-first → `launch-pre-mortem` or `crisis-pre-flight`
- The announcement is a CEO transition → `exec-transition`
- The announcement is M&A-driven workforce impact → `deal-comms` with internal-first overlay

## Default phase composition

1. `factbase` — 30-day freshness window; budget 10 WebFetch calls (peer-company comparable announcements, recent employee-leak coverage in this industry, union / works-council activity)
2. `cast-design` — salience scoring with emphasis on employee + union + investigative press
3. `deep-research` — 12 parallel researchers
4. `initial-reactions` — 12 parallel workers
5. `critic` — 12 parallel critics
6. `synthesis` — skeleton `templates/report-skeletons/internal-first.md`; artifacts: `cascade-pack`, `qa-doc`, `message-house`, `stakeholder-heat-map`, `leak-response-triggers` (embedded)

## Default cast

- **Size:** 12
- **Cluster distribution:**
    - employee: 4 (senior manager + individual contributor + early-career + affected-vs-unaffected mix)
    - union / works-council: 1 (only if the workforce is organized; otherwise archetype employee-advocate)
    - press: 2 (industry trade + one investigative focused on workforce / labor)
    - customer: 1 (largest customer, continuity-risk framing)
    - investor: 1 (sell-side analyst watching headcount)
    - activist: 1 (labor-rights or worker-advocacy, if workforce impact is significant)
    - peer-company: 1 (how competitors will frame their own position in response)
    - internal comms / IR lead: 1 (self-check — does this sound like us?)

## Depth parameters

- Revise cycles: 2
- Social-dynamics: OFF (cascade is hierarchical, not networked)
- Debate: OFF
- Memory: within-run for tracking initial → 24h leak-wave → 72h settled reception

## Artifacts emitted alongside `report.md`

- `artifacts/cascade-pack.md` — full cascade: exec email → manager toolkit (talking points + Q&A for manager 1:1s) → town-hall script → team-level talking points → written follow-up. Per IABC Handbook convention.
- `artifacts/qa-doc.md` — 40-60 questions (employee / manager / press if leaked / customer if escalates / investor)
- `artifacts/message-house.md` — internal narrative: roof (the why) + 3 pillars (business rationale / impact on you / what comes next) + proof points
- `artifacts/stakeholder-heat-map.md`
- Leak-response triggers section embedded in report: if the announcement leaks before cascade completes, which external comms fire when — derived from press and investor personas' urgency scores

## Expected runtime

~5-6 minutes.

## Expected cost

~$2.50 per run.

## Failure modes specific to this mode

- **Employee cluster too generic.** "The employees will not like this" is not a useful finding. The cast must differentiate: affected vs unaffected, early-career vs senior, direct-report-of-exec vs rank-and-file. The scoping-designer should push on this in the cast-spec.
- **Leak risk underestimated.** Internal announcements with workforce impact leak to trade press within 24-48h. Press cluster must include an investigative workforce beat reporter. If not, coverage-gap entry: "leak risk not modeled."
- **Union voice missing for organized workforce.** If the factbase reveals union or works-council presence, their reaction is material and legally relevant. Must be in the cast.
- **Cascade pack generic.** The cascade artifact is the primary deliverable in this mode — it must reflect the persona reactions (manager Q&A grounded in employee-persona questions; town-hall script grounded in rank-and-file concerns).

## Evidence trail

See `reference/methodology-sources.md` §internal-first.
