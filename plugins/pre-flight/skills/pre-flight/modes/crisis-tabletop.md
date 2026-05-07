# Mode: `crisis-tabletop`

**In-house names:** tabletop exercise; crisis simulation; war game (M&A/IR context); full-scale crisis rehearsal.
**Benchmark workflows:** H+K Strategies FlightSchool+ full; Polpeo 3-hour live social-media crisis; Weber Shandwick FireBell; Hoover Wargaming & Crisis Simulation Initiative; Edelman social-issue simulation full-format.

## Use when

A severe or potentially severe issue is unfolding (or could unfold) and the team needs to simulate multi-day narrative dynamics — not just first reactions. Injects, timed stakeholder responses, coalition formation, memory of prior-round positions. The question is: what does the story look like on Day 3, Day 7, if each round of company response lands as intended vs. as it's likely to land?

This is the deepest and most expensive mode — 2-3 rounds of reactions with memory + social dynamics between, debate pairings on the sharpest antagonisms, and an After-Action Review (AAR) format report in the Edelman/APCO convention.

## Use another mode if

- You want a quick pre-flight, not a multi-day simulation → `crisis-pre-flight`
- The issue is centered on a specific stimulus going live in <4h → `crisis-pre-flight` with severity: high
- The driver is adversarial stakeholder activism specifically → `activist-proxy`
- The driver is regulatory → `regulatory-response`

## Default phase composition

1. `factbase` — 14-day freshness window; budget 12 WebFetch calls
2. `cast-design` — salience scoring on; severity parameter influences cast size (high / critical → 16 personas)
3. `deep-research` — 16 parallel researchers
4. `initial-reactions` (Round 1) — 16 parallel workers, each reacting to the initial stimulus / inject
5. `critic` — 16 parallel critics
6. `social-dynamics` — 5-6 pairings across the cast, 2 rounds
7. `memory-update` — within-run, between Round 1 and Round 2
8. **(Round 2)** `initial-reactions` — same 16 personas, now reacting to a new inject (or to Round 1's net state) with prior memory loaded
9. `critic` — Round 2 critic pass
10. `memory-update` — between Round 2 and Round 3
11. **(Round 3, optional)** `initial-reactions` — same 16 personas, final state projection
12. `debate` — 3-4 pairings on the sharpest antagonisms surfaced in prior rounds
13. `synthesis` — skeleton `templates/report-skeletons/crisis-tabletop.md`; artifacts: `aar-report`, `holding-statement`, `qa-doc`, `message-house`, `stakeholder-heat-map`

## Default cast

- **Size:** 16 (high-stakes crisis) or 20 (critical — enterprise-wide)
- **Cluster distribution (16):**
    - activist: 3
    - scientist / subject-matter expert: 2
    - regulator: 2
    - press: 4 (tier-1 general, trade, adversarial / investigative, enthusiast / ecosystem)
    - customer: 2
    - investor: 2
    - internal / employee: 1
    - peer-company: 1

## Depth parameters

- Revise cycles: 2 (hardcoded cap per round)
- Social-dynamics: ON (2 rounds of pairings)
- Memory: WITHIN-RUN (mandatory — this is the whole point)
- Cross-run memory: opt-in if the team wants to track the same cast across multiple tabletops over time
- Debate: ON (after Round 2 or Round 3)

## Injects

Optional feature: the user can pre-load timed injects for Round 2 and Round 3 at the scoping phase. An inject is a new piece of information that appears between rounds (a journalist's tweet, a regulator letter, a leaked memo, an activist video) that changes the information landscape. If injects are loaded, each round's personas react to the cumulative state (stimulus + any prior injects). If not loaded, Round 2 and Round 3 react to the net state of prior rounds.

MSEL (Master Scenario Events List) — a list of 12-20 timed injects — is the classical tabletop convention. We support a lightweight version: 3-6 injects, each with a time-bucket (T+1h, T+4h, T+24h, T+72h).

## Artifacts emitted alongside `report.md`

- `artifacts/aar-report.md` — full After-Action Review in Edelman/APCO format (findings, decision points, narrative arc, recommendations, playbook updates)
- `artifacts/holding-statement.md` — generated for Round 1, updated for each subsequent round
- `artifacts/qa-doc.md` — cumulative across rounds, 50-80 questions
- `artifacts/message-house.md` — evolved across rounds
- `artifacts/stakeholder-heat-map.md` — with per-round posture deltas

## Expected runtime

~15-25 minutes for a 3-round 16-persona run (most expensive mode).

## Expected cost

~$8-12 per run (memory + social-dynamics + debate + larger cast).

## Failure modes specific to this mode

- **Inject drift.** Pre-loaded injects that feel too "on-narrative" produce sanitized round outcomes. Fix: use factbase's "Known controversies" and adversarial-coverage sections to source realistic injects rather than inventing them.
- **Memory contamination across rounds.** If memory stubs carry round-specific triggers into later rounds without the "do not carry forward" discipline, Round 3 personas react to stale context. Memory-keeper hard-enforces summary-only + do-not-carry-forward.
- **Scope mismatch.** 16-persona × 3-round tabletop on a 200-word statement is absurd. Scoping-designer should default crisis-tabletop to severity: high / critical and recommend `crisis-pre-flight` for smaller stimuli.
- **Synthesis fatigue.** Reports for this mode can sprawl past 3000 words if the synthesizer doesn't enforce the AAR structure. Skeleton hard-caps at ~2800 words.

## Evidence trail

See `reference/methodology-sources.md` §crisis-tabletop.
