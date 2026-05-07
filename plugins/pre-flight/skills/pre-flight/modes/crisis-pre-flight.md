# Mode: `crisis-pre-flight`

**In-house names:** pre-flight messaging review, statement stress test, red team read
**Benchmark workflows:** Edelman 2-hour crisis simulation (short-form); H+K FlightSchool+ quick pre-flight; FGS Global quarterly red-teaming of holding statements; Polpeo off-the-shelf modular simulation.
**Severity coverage:** low / medium / high / critical (high and critical add the `debate` phase).

## Use when

A comms team has a statement they plan to push in <4h. They need to know: what does this look like to the most hostile reasonable readers? Which red lines does it cross? What are the three edits that would move the needle most? What's the holding statement if things escalate?

This is the quick mode. One round. No social dynamics. No memory. Designed for speed and sharpness.

## Use another mode if

- You want to simulate how the story unfolds over a week → `crisis-tabletop`
- You want to compare two drafts A/B → `counterfactual-compare`
- The statement is pre-announcement M&A → `deal-comms`
- The statement is an earnings script → `earnings-rehearsal`
- You're stress-testing positioning rather than a specific statement → `positioning-pressure-test`

## Default phase composition

1. `factbase` — 30-day freshness window; budget 8 WebFetch calls
2. `cast-design` — salience scoring on
3. `deep-research` — 12 parallel researchers, 120s timeout each
4. `initial-reactions` — 12 parallel workers, signature_opener prepended
5. `critic` — 12 parallel critics, revise cycles capped at 2
6. (optional, if severity ≥ high) `debate` — 3 pairings, 3 exchanges each
7. `synthesis` — skeleton `templates/report-skeletons/crisis-pre-flight.md`; artifacts: `holding-statement`, `qa-doc`, `message-house`, `stakeholder-heat-map`

## Default cast

- **Size:** 12 (gut-check: 5; high-stakes: 16)
- **Cluster distribution (12):**
    - activist: 2-3
    - scientist / subject-matter expert: 1-2
    - regulator: 1
    - press: 2-3 (at least one trade-press, at least one adversarial / investigative)
    - customer: 1-2
    - investor: 1-2
    - internal: 1
- **Prefer named:** true for large public companies, false for small private firms
- **Named floor:** 3 verbatim quotes

The scoping-designer may deviate from this distribution based on the stimulus (e.g. a bycatch-incident release needs 4 activists; a consumer-product recall needs 3 customers). The run-plan documents the deviation in `cast_spec.rationale`.

## Depth parameters

- Revise cycles: 2 (hardcoded cap)
- Memory: within-run only if multi-round; default off (single-round mode)
- Cross-run memory: off by default; user opt-in flips it on
- Social-dynamics: off (use `crisis-tabletop` instead if needed)
- Debate: on only if severity ≥ high

## Artifacts emitted alongside `report.md`

- `artifacts/holding-statement.md` — fill-in-the-blank, deployable in 15 minutes
- `artifacts/qa-doc.md` — 20-50 anticipated questions with model answers
- `artifacts/message-house.md` — roof narrative + 3 pillars + proof points
- `artifacts/stakeholder-heat-map.md` — Power × Legitimacy × Urgency visual (rendered as a markdown table)

## Expected runtime

~4-6 minutes wall-clock on a 12-persona cast. Phases that dominate: factbase (~90s), cast-design (~30s), deep-research (~90s parallel), reactions + critic (~90s parallel × 2 rounds worst case), synthesis (~60s). Verify_quotes.py adds ~5s.

## Expected cost

~$0.30 orchestrator + synthesizer (Opus 4.7) + ~$0.05 × 24 subagent calls (Sonnet 4.6) ≈ ~$1.50 per run. Add ~$0.40 for 12 WebFetch-heavy persona-researcher calls. Total budget: ~$2 per run.

## Failure modes specific to this mode

- **Cast underweighted for the stimulus.** Default distribution is generic; the scoping-designer must tune it. A bycatch-incident release with 1 activist in the cast will miss the worst-case reaction.
- **Factbase misses recent event.** 30-day window is the default — for fast-moving stories, the designer should flip to a 7-day window.
- **Single-round echoes helpful-assistant voice.** In a one-round mode, the critic's revise loop is the only defense. Make sure the persona bundles have strong signature_openers and forbidden_phrases — these do more work in this mode than in multi-round modes.

## Evidence trail

Real-world anchor: see `reference/methodology-sources.md` §pre-flight-messaging-review.
