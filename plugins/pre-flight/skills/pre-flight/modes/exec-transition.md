# Mode: `exec-transition`

**In-house names:** CEO succession comms; executive transition pre-flight; leadership-change announcement.
**Benchmark workflows:** Brunswick executive-transition playbook; FGS Global leadership comms; Joele Frank (CEO-change defense); Teneo CEO-succession advisory.

## Use when

A CEO, CFO, or other C-suite transition (planned or unplanned) is 1-14 days from announcement. The comms team has a press release, employee email, investor presentation, customer letter, and biographies ready. The pressure test: investor reaction (continuity story strong enough?), employee reaction (does the new leader inherit authority or have to earn it?), customer reaction (relationship risk?), trade-press framing (surprise or expected?), peer-company response.

## Use another mode if

- The transition is the result of an activist campaign → `activist-proxy`
- The transition is part of an M&A announcement → `deal-comms`
- The transition coincides with earnings → stack `earnings-rehearsal`

## Default phase composition

1. `factbase` — 30-day freshness window; budget 10 WebFetch calls (outgoing exec's public record, incoming exec's prior roles, peer-company transition outcomes)
2. `cast-design` — salience scoring with emphasis on institutional holders + board-level voices
3. `deep-research` — 10 parallel researchers
4. `initial-reactions` — 10 parallel workers
5. `critic` — 10 parallel critics
6. `synthesis` — skeleton `templates/report-skeletons/exec-transition.md`; artifacts: `qa-doc`, `message-house`, `stakeholder-heat-map`, `first-100-days-plan` (embedded)

## Default cast

- **Size:** 10
- **Cluster distribution:**
    - investor: 3 (institutional + sell-side + one activist-aware holder)
    - employee: 2 (direct-report level + rank-and-file)
    - customer: 2 (largest customers, relationship-risk sensitive)
    - press: 2 (trade + one investigative focused on governance)
    - peer-company: 1 (competitor reaction framing)

## Depth parameters

- Revise cycles: 2
- Social-dynamics: OFF (unless succession is contested, then escalate to `activist-proxy`)
- Debate: OFF (unless severity is high, e.g. unexpected ouster)
- Memory: within-run for tracking Day-0 vs Day-90 projected reactions

## Artifacts emitted alongside `report.md`

- `artifacts/qa-doc.md` — 30-50 questions (investor / employee / customer / press)
- `artifacts/message-house.md` — transition narrative: roof (continuity + evolution), 3 pillars (strategy / culture / confidence), proof points
- `artifacts/stakeholder-heat-map.md`
- First-100-days plan section embedded in report: projected stakeholder-engagement sequence for the new exec

## Expected runtime

~5-6 minutes.

## Expected cost

~$2 per run.

## Failure modes specific to this mode

- **Outgoing exec's public record ignored.** The outgoing exec's recent statements anchor stakeholder expectations of continuity. Factbase should include the outgoing exec's last 5 major public statements.
- **Incoming exec unknown to most stakeholders.** If the incoming exec has thin public record, stakeholders have nothing to react to. Coverage-gap note: "introductory comms will be first material reception; this pre-flight tests the announcement narrative, not the new exec's reception."
- **Board voice missing.** If the transition is contested or surprising, a board-chair persona is material. Add to cast if factbase reveals board-level tension.

## Evidence trail

See `reference/methodology-sources.md` §exec-transition.
