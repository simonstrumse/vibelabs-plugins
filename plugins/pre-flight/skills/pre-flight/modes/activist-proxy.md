# Mode: `activist-proxy`

**In-house names:** activist defense; proxy fight pre-flight; shareholder activism response.
**Benchmark workflows:** Brunswick and FGS Global shareholder-activism practices; Joele Frank (activist defense specialist); MacKenzie Partners / Okapi Partners proxy-solicitation models.

## Use when

An activist investor has taken a position, published a letter, filed a 13D with intent, nominated a dissident slate, or launched a public campaign — and the company is drafting a response (press release, shareholder letter, proxy statement, ISS/Glass Lewis submission). The pressure test: how will institutional holders, proxy advisors, sell-side, and trade press read the response? What coalition does the activist build? Where does the company's narrative win the argument?

## Use another mode if

- The activist is external (NGO / advocacy) rather than a shareholder → `crisis-pre-flight` or `crisis-tabletop` depending on severity
- The response is tied to an M&A transaction (defensive or offensive) → `deal-comms` (with activist-proxy overlay)
- The focus is earnings rather than proxy-specific → `earnings-rehearsal`

## Default phase composition

1. `factbase` — 14-day freshness window (activist campaigns move fast); budget 12 WebFetch calls (activist's prior campaigns, ISS/Glass Lewis recent recommendations in this industry, peer proxy-fight outcomes)
2. `cast-design` — salience scoring with emphasis on proxy-advisor + institutional-holder power scores
3. `deep-research` — 10 parallel researchers
4. `initial-reactions` — 10 parallel workers
5. `critic` — 10 parallel critics
6. `debate` — 3 pairings (activist ↔ CEO proxy; ISS ↔ Glass Lewis; institutional holder ↔ sell-side), 3 exchanges each
7. `synthesis` — skeleton `templates/report-skeletons/activist-proxy.md`; artifacts: `proxy-response-letter`, `qa-doc`, `message-house`, `stakeholder-heat-map`, `coalition-map` (embedded)

## Default cast

- **Size:** 10
- **Cluster distribution:**
    - investor — activist: 1 (the named activist investor)
    - investor — institutional: 3 (top-5 holders by voting power — named where possible)
    - investor — proxy advisor: 2 (ISS analyst + Glass Lewis analyst for this industry)
    - investor — sell-side: 1 (named analyst covering the stock)
    - press: 2 (Dealreporter / Activist Insight / 13D Monitor + mainstream financial press)
    - peer-company: 0-1 (only if peer activist outcomes are instructive)

## Depth parameters

- Revise cycles: 2
- Debate: ON (ISS vs Glass Lewis pairing particularly valuable)
- Social-dynamics: OFF (coalition modeling happens via debate pairings)
- Memory: within-run for multi-step activist campaigns (initial letter → 13D → nomination)

## Artifacts emitted alongside `report.md`

- `artifacts/proxy-response-letter.md` — shareholder letter draft grounded in the reactions
- `artifacts/qa-doc.md` — 30-50 questions from investors, proxy advisors, trade press
- `artifacts/message-house.md` — anti-activist narrative: roof + 3 pillars (strategy / performance / governance) + proof points
- `artifacts/stakeholder-heat-map.md` — voting-power × urgency
- Coalition map section embedded in report: who votes with the company, who votes with the activist, who's persuadable

## Expected runtime

~7-9 minutes.

## Expected cost

~$3 per run.

## Failure modes specific to this mode

- **Proxy advisor voice shallow.** ISS and Glass Lewis publish recommendations on the record; bundles should hit named-floor. If not, the factbase's stakeholder ecosystem map was under-researched.
- **Institutional holder personas weak.** Large institutions rarely speak publicly on specific votes, so personas default to archetype-by-role (e.g. "top-3 holder passive-index voting team"). This is fine — what matters is the voting model, not the named individual.
- **Activist underestimated.** Scoping-designer should pull the activist's 3-5 most recent campaign letters; persona-architect should not let tier-1 salience drop.

## Evidence trail

See `reference/methodology-sources.md` §activist-proxy.
