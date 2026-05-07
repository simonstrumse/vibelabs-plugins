# Mode: `deal-comms`

**In-house names:** transaction communications; deal comms; Day 1 / 30 / 100 playbook; M&A comms pre-flight.
**Benchmark workflows:** Brunswick Capital Markets; FGS Global transaction & financial communications (legacy Sard Verbinnen); Joele Frank; Kekst CNC.

## Use when

An M&A announcement, joint venture, spin-off, significant investment, or major restructuring is ≤2 weeks from public disclosure. The comms team has a draft press release, investor presentation, CEO talking points, employee script, customer letter, regulator filing, and analyst call script. Every audience is reading a different subset. The deal needs pre-flight against: institutional investors, sell-side analysts, regulators, employees, major customers, peer companies, activists (shareholder or external), trade press.

## Use another mode if

- The announcement is a proxy fight or activist-investor defense → `activist-proxy`
- The announcement is a CEO succession → `exec-transition`
- The disclosure is routine quarterly / earnings → `earnings-rehearsal`

## Default phase composition

1. `factbase` — 14-day freshness window (deal markets move fast); budget 12 WebFetch calls (both parties' public state + any related deals + analyst model updates)
2. `cast-design` — salience scoring on; emphasis on capital-markets cluster (investors, analysts, proxy advisors)
3. `deep-research` — 12 parallel researchers
4. `initial-reactions` — 12 parallel workers
5. `critic` — 12 parallel critics
6. `social-dynamics` — 4 pairings (CEO proxy ↔ activist investor; institutional investor ↔ proxy advisor; customer ↔ competitor; employee ↔ union representative), 2 rounds
7. `memory-update` — within-run, between Day-0 reactions and Day-1/30/100 projection
8. `synthesis` — skeleton `templates/report-skeletons/deal-comms.md`; artifacts: `day-1-30-100-plan`, `qa-doc`, `message-house`, `stakeholder-heat-map`, `analyst-call-script` (embedded)

## Default cast

- **Size:** 12
- **Cluster distribution:**
    - investor: 3-4 (large institutional + sell-side analyst + one activist investor or proxy advisor)
    - regulator: 1-2 (antitrust / financial regulator depending on deal type)
    - employee / internal: 2 (at least one from each combining entity's rank-and-file)
    - customer: 1-2 (largest customer of the combining entities)
    - peer-company: 1 (direct competitor's reaction)
    - press: 2 (financial / trade press + one investigative)
    - activist (external): 0-1 (only if the deal has meaningful stakeholder impact beyond capital markets)

## Depth parameters

- Revise cycles: 2
- Social-dynamics: ON (essential — deal comms is coalitional)
- Memory: within-run (Day-0 → Day-1/30/100)
- Debate: OFF (debate frames adversarial stasis; deal comms needs coalition modeling)

## Artifacts emitted alongside `report.md`

- `artifacts/day-1-30-100-plan.md` — full readiness plan per Brunswick/FGS convention
- `artifacts/qa-doc.md` — 40-80 anticipated questions, categorized by audience (investor / regulator / employee / customer / press)
- `artifacts/message-house.md` — roof narrative + 3 pillars + proof points
- `artifacts/stakeholder-heat-map.md`
- Analyst call script section embedded in report: scripted opening + anticipated follow-ups + bridge phrases

## Expected runtime

~8-10 minutes (social-dynamics + memory phases add ~3 min).

## Expected cost

~$4 per run.

## Failure modes specific to this mode

- **MNPI warning ignored.** Deal content is almost always MNPI. Orchestrator warns once; if the user bypasses, legal exposure is on them. Log the bypass in the run-plan.
- **Investor cluster shallow.** Sell-side analysts and large institutional investors have rich public records. Named-floor (≥3 verbatim quotes) should be achievable. If researchers keep downgrading to archetype, the run-plan's cast has been miscast — surface at approval gate.
- **Activist investor missed.** If any named activist fund has a position in either entity, they must be in the cast. Scoping-designer should flag this in the factbase's stakeholder ecosystem map.
- **Day-30 and Day-100 sections empty.** If personas only react to Day-0, the memory-update phase didn't trigger. Confirm run-plan includes memory-update.

## Evidence trail

See `reference/methodology-sources.md` §deal-comms.
