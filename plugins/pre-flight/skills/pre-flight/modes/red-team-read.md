# Mode: `red-team-read`

**In-house names:** red team read; adversarial pass; hostile-reader review.
**Benchmark workflows:** US DoD / RAND red-teaming origin (1960s); post-9/11 Defense Science Board formalization; Wag The Dog corporate adaptation; FGS Global quarterly red-teaming; specialist shops (Red Team Thinking, Bryghtpath).

## Use when

A statement, policy, announcement, or campaign concept is ready for a dedicated adversarial pass. This is a focused, deliberately hostile read — not a balanced stakeholder simulation. The cast is adversarial-only: short-seller, adversary journalist, regulator-skeptic, competitor comms team, hostile activist, litigation-adjacent reporter. The question is: where are the vulnerabilities? What headline would hostile readers write? What claim would they challenge and what evidence would they demand?

Red-team-read is designed for pre-publication when the team believes the material is ready and wants explicit vulnerability testing — not for general pressure tests (which is `crisis-pre-flight`).

## Use another mode if

- You want balanced stakeholder simulation → `crisis-pre-flight`
- The material is policy-facing and needs regulator + peer modeling → `regulatory-response`
- The material is an M&A announcement → `deal-comms`

## Default phase composition

1. `factbase` — 30-day freshness window; budget 10 WebFetch calls (emphasis on adversarial coverage archives)
2. `cast-design` — salience scoring on; cast is **adversarial-only** (no neutral or supportive personas)
3. `deep-research` — 8 parallel researchers
4. `initial-reactions` — 8 parallel workers (each instructed to lift the worst pull-quote, write the hostile headline, identify the specific claim to challenge)
5. `critic` — 8 parallel critics (stricter threshold — red-team-read requires sharp adversarial takes, not balanced ones)
6. `debate` — 2 pairings (short-seller ↔ CFO proxy; hostile journalist ↔ spokesperson proxy), 3 exchanges each
7. `synthesis` — skeleton `templates/report-skeletons/red-team-read.md`; artifacts: `vulnerability-memo`, `qa-doc`, `stakeholder-heat-map`

## Default cast

- **Size:** 8
- **Cluster distribution (adversarial-only):**
    - activist / NGO (hostile): 2
    - press (adversarial / investigative): 2
    - investor (short-seller / activist-short): 1
    - peer-company (competitor comms): 1
    - regulator (skeptic / enforcement-oriented): 1
    - litigation-adjacent: 1 (plaintiff-side attorney archetype or class-action journalist)

All personas pre-identified as adversarial. The cast deliberately excludes supportive or neutral voices — red-team-read is about worst-case reading, not aggregate reception.

## Depth parameters

- Revise cycles: 2
- Debate: ON (adversarial debate phase sharpens vulnerabilities)
- Social-dynamics: OFF
- Memory: OFF

## Artifacts emitted alongside `report.md`

- `artifacts/vulnerability-memo.md` — top 5 vulnerabilities ranked by severity × probability, each with a suggested edit or reframe (format adapted from `research/pre-ai-methods/distilled-protocols.md` Protocol 3)
- `artifacts/qa-doc.md` — 20-40 hostile questions with model answers that don't cross any documented red_line
- `artifacts/stakeholder-heat-map.md` — adversarial cluster only
- Hostile-headline catalog section embedded in report: 5-10 headlines hostile personas would write about this material

## Expected runtime

~5-7 minutes.

## Expected cost

~$2.50 per run.

## Failure modes specific to this mode

- **Red-team light.** Hostile personas sound reasonable instead of hostile. Persona bundles need explicit adversarial priming in the voice section ("your career is built on catching corporate spin"). Critic's non-sycophantic criterion is stricter in this mode.
- **Balanced coverage creeps in.** If the scoping-designer adds any neutral/supportive personas to the cast, surface and reject — the mode's definition is adversarial-only.
- **Debate converges.** If the short-seller ↔ CFO debate produces agreement, the CFO proxy bundle has drifted helpful. Either regenerate or pair with a harder short-seller.
- **Vulnerability memo generic.** Vulnerabilities must be specific to the material, not generic ("transparency concerns"). The synthesizer's vulnerability-memo quality is the key deliverable.

## Evidence trail

See `reference/methodology-sources.md` §red-team-read.
