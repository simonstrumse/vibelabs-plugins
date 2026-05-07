# Mode: `earnings-rehearsal`

**In-house names:** earnings rehearsal; mock analyst Q&A; investor day dry run; pre-call Q&A prep.
**Benchmark workflows:** NIRI (National Investor Relations Institute) playbook; 30-day pre-event cadence; Corbin Advisors Voice of Investor®; ICR institutional-investor perception studies.

## Use when

An earnings call, investor day, dividend announcement, guidance update, or material investor-facing release is 1-30 days out. The IR team has an earnings script, guidance figures, and an initial Q&A prep doc. The rehearsal needs to pressure-test: what will sell-side analysts ask that isn't on the prep doc? What's the hardest buy-side question? What does the trade press pick up? Which competitor reaction changes the model?

## Use another mode if

- The release includes an M&A announcement → `deal-comms`
- The release is a CEO succession during earnings → stack with `exec-transition`
- The release is in response to a regulatory inquiry → `regulatory-response`

## Default phase composition

1. `factbase` — 14-day freshness window (quarterly cycle + recent analyst notes); budget 10 WebFetch calls
2. `cast-design` — salience scoring on; emphasis on sell-side analysts, buy-side institutions
3. `deep-research` — 8 parallel researchers (smaller cast)
4. `initial-reactions` — 8 parallel workers
5. `critic` — 8 parallel critics
6. `debate` — 3 pairings (sell-side ↔ CFO proxy; buy-side ↔ sell-side; short-seller ↔ IR lead), 3 exchanges each (this IS the mock Q&A)
7. `synthesis` — skeleton `templates/report-skeletons/earnings-rehearsal.md`; artifacts: `mock-analyst-qa`, `qa-doc`, `message-house`, `stakeholder-heat-map`

## Default cast

- **Size:** 8
- **Cluster distribution:**
    - investor: 5 (3 sell-side — ideally named from actual coverage; 2 buy-side — largest institutional holders or vocal activists)
    - press: 2 (one trade/financial press, one investigative)
    - peer-company: 1 (one direct competitor's IR voice for model-reaction framing)

## Depth parameters

- Revise cycles: 2
- Debate: ON (the debate phase IS the mock Q&A rehearsal)
- Social-dynamics: OFF
- Memory: OFF unless this earnings is part of a multi-call tracking engagement (then cross-run memory opt-in)

## Artifacts emitted alongside `report.md`

- `artifacts/mock-analyst-qa.md` — full transcript of debate phase: each analyst asks their 3 questions, CEO/CFO proxy answers, analyst follow-ups. 20-40 questions total.
- `artifacts/qa-doc.md` — anticipated Q&A grouped by easy / medium / hard / hostile (NIRI convention)
- `artifacts/message-house.md` — earnings narrative: roof = one-sentence quarter headline, 3 pillars (performance / strategy / guidance), proof points
- `artifacts/stakeholder-heat-map.md` — investor coverage with salience

## Expected runtime

~6-8 minutes (debate phase adds ~2 min; smaller cast keeps it manageable).

## Expected cost

~$2.50 per run.

## Failure modes specific to this mode

- **Named sell-side impossible.** Many sell-side analysts publish under bank research-house brands without individual public quote records; the researcher downgrades to archetype. Acceptable — archetype sell-side captures the role behavior; what matters is the ANGLE, not the named individual.
- **Buy-side quiet.** Large institutions rarely speak publicly. Buy-side personas are almost always archetypes. That's fine.
- **Mock Q&A feels too soft.** Debate phase with default "take turns" framing may produce polite exchanges. If so, add "analyst is under pressure to justify a downgrade recommendation; CFO proxy is under pressure from the CEO to protect guidance" framing — this is encoded in the earnings-rehearsal debate-task template.
- **Short-seller absent.** If short-interest is elevated, a short-seller persona (activist short) must be in the cast. Scoping-designer should check factbase for short-interest data.

## Evidence trail

See `reference/methodology-sources.md` §earnings-rehearsal.
