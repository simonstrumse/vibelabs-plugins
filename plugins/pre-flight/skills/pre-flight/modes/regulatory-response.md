# Mode: `regulatory-response`

**In-house names:** regulatory response playbook; public-affairs rapid response; consultation response pressure test.
**Benchmark workflows:** APCO public-affairs practice; FGS Global government-relations; Teneo and FTI Consulting regulatory comms.

## Use when

A regulator has proposed a rule, opened a consultation, issued a preliminary finding, or requested comment — and the comms + public-affairs + legal team are drafting a response (comment letter, stakeholder letter, coalition letter, press statement, op-ed). The response needs pre-flight against: the regulator itself (how they'll read it), peer-company reactions, NGO / advocacy group counter-framing, and trade press interpretation.

## Use another mode if

- The regulator has taken enforcement action and a crisis response is needed → `crisis-pre-flight` or `crisis-tabletop`
- The announcement is a proactive policy position, not a reg response → `regulatory-response` still works but with stimulus type `policy-position`
- The response is to a shareholder activist rather than a regulator → `activist-proxy`

## Default phase composition

1. `factbase` — 30-day freshness window; budget 10 WebFetch calls (regulator's public docket, peer submissions, recent trade-press coverage)
2. `cast-design` — salience scoring on; emphasis on regulator + peer-company + advocacy voices
3. `deep-research` — 12 parallel researchers
4. `initial-reactions` — 12 parallel workers
5. `critic` — 12 parallel critics, revise cycles capped at 2
6. `debate` — 3 pairings (regulator ↔ company; advocate ↔ peer-company; trade-press ↔ industry association), 3 exchanges each
7. `synthesis` — skeleton `templates/report-skeletons/regulatory-response.md`; artifacts: `comment-letter`, `qa-doc`, `stakeholder-heat-map`, `coalition-readiness-brief` (embedded)

## Default cast

- **Size:** 12
- **Cluster distribution:**
    - regulator: 2 (the specific regulator drafting the rule + one peer regulator or international counterpart)
    - peer-company: 2-3 (who else is submitting; what will they say)
    - activist / NGO: 2 (whose counter-submission will be loudest)
    - scientist / subject-matter expert: 1 (whose technical evaluation matters)
    - press: 2 (trade press that covers this regulator + one investigative journalist)
    - industry-association: 1 (if an association is coordinating)
    - internal / company: 1-2 (legal + government-relations voice)

## Depth parameters

- Revise cycles: 2
- Debate: ON (adversarial framing essential — the response will land in an adversarial docket)
- Social-dynamics: OFF (use debate instead for policy contexts)
- Memory: within-run only if the response is part of a multi-round consultation

## Artifacts emitted alongside `report.md`

- `artifacts/comment-letter.md` — full comment-letter draft grounded in the reactions
- `artifacts/qa-doc.md` — 30-60 anticipated questions from press, regulator follow-ups, and peer-company reactions
- `artifacts/stakeholder-heat-map.md` — with regulator tier-1, peer companies, advocacy groups
- Coalition-readiness brief: who would sign on to a joint letter, who would actively oppose, who's neutral

## Expected runtime

~6-8 minutes (debate phase adds ~2 min).

## Expected cost

~$3 per run.

## Failure modes specific to this mode

- **Regulator voice absent or shallow.** If the regulator persona's bundle is thin (not enough recent public statements), the whole run is undergrounded. Scoping-designer should check the factbase for fresh regulator statements before finalizing the cast.
- **Peer-company reactions generic.** Peer-company archetype personas are weaker than named ones here — the response is competitive intelligence as much as public affairs. Prefer named when possible.
- **Debate phase converges.** If the regulator ↔ company debate produces agreement, the persona bundles probably aren't distinct enough. Re-fire the weaker bundle.

## Evidence trail

See `reference/methodology-sources.md` §regulatory-response.
