# Mode: `launch-pre-mortem`

**In-house names:** launch pre-mortem, launch messaging review, pre-launch pressure test
**Benchmark workflows:** Atlassian launch pre-mortem template; product-marketing standard pre-launch pattern; message house + FAQ + tiered media list convention.

## Use when

A product or capability launch is 1-6 weeks out and the comms + product-marketing team wants to know: what will TechCrunch / Wired / NYT / trade press / our largest customer say? What's the strongest counter-framing from our biggest competitor? What FAQ questions do we need to prepare? What edits to the message house would move the needle most?

## Use another mode if

- The launch is already public and reactions are coming in → use a retrospective tool, not this skill
- The launch is a rebrand or repositioning → `positioning-pressure-test`
- The launch has significant regulatory exposure → stack `regulatory-response` on top
- The launch is part of an M&A announcement → `deal-comms`

## Default phase composition

1. `factbase` — 60-day freshness window (launches move on quarter cycles); budget 10 WebFetch calls
2. `cast-design` — salience scoring on; emphasis on tier-1 press and customer voices
3. `deep-research` — 10 parallel researchers, 120s timeout
4. `initial-reactions` — 10 parallel workers, signature_opener prepended
5. `critic` — 10 parallel critics, revise cycles capped at 2
6. `synthesis` — skeleton `templates/report-skeletons/launch-pre-mortem.md`; artifacts: `message-house`, `qa-doc`, `stakeholder-heat-map`, `launch-runsheet` (embedded in report)

## Default cast

- **Size:** 10
- **Cluster distribution:**
    - press: 4 (at least one tier-1 general press, one trade-press beat reporter, one adversarial/skeptical voice, one enthusiast/ecosystem voice)
    - customer: 2-3 (a large existing customer and a prospect persona)
    - peer-company: 1-2 (direct competitor's comms response framing)
    - scientist / subject-matter expert: 1 (only if the launch has technical claims that a specialist would evaluate)
    - investor: 1 (sell-side analyst in the coverage)
    - internal: 0-1 (employee voice if the launch affects internal org)

The scoping-designer tunes: a consumer-facing launch pulls 2 more consumer press; a developer-tooling launch pulls 1 more tier-1 dev advocate; a B2B enterprise launch pulls 1 more procurement-customer archetype.

## Depth parameters

- Revise cycles: 2 (hardcoded cap)
- Memory: off (single-round)
- Social-dynamics: off (use `crisis-tabletop` for unfolding narratives)
- Debate: off (no adversarial exchange needed for a launch unless severity escalates — in which case stack `red-team-read`)

## Artifacts emitted alongside `report.md`

- `artifacts/message-house.md` — roof narrative + 3 pillars + proof points, drawn from consensus signals
- `artifacts/qa-doc.md` — 25-50 anticipated questions, grouped by press tier / customer / competitor angle
- `artifacts/stakeholder-heat-map.md` — Power × Legitimacy × Urgency
- Launch runsheet section embedded in report: timed cadence (embargo lift T-0 / T+1h spokesperson interviews / T+6h press-release amplification / T+24h customer comms / T+48h follow-up).

## Expected runtime

~3-5 minutes for a 10-persona cast.

## Expected cost

~$1.50 per run (smaller cast + no optional phases).

## Failure modes specific to this mode

- **Press-cluster over-weighting.** Launch pre-flights over-index on press reactions at the expense of customer voice. If the report has ≥5 press quotes and ≤1 customer quote, the cast was miscast.
- **Competitor framing absent.** Without a peer-company persona, the launch message house is untested against the most likely counter-framing. The scoping-designer should add 1 peer-company by default for any launch in a competitive category.
- **Technical claims not evaluated.** If the launch makes specific technical / scientific / capability claims, at least one scientist or subject-matter expert must be in the cast — otherwise the "is this actually true?" question goes unasked.

## Evidence trail

See `reference/methodology-sources.md` §launch-pre-mortem.
