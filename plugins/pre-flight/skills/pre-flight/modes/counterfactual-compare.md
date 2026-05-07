# Mode: `counterfactual-compare`

**In-house names:** A/B message test; counterfactual draft review; side-by-side comparison.
**Benchmark workflows:** Political-consulting dial tests (GQR / Lake Research / Public Opinion Strategies); emerging practice in corporate PR per Cision 2025 "AI persona-based chatbots to simulate stakeholder qualities" framing.

## Use when

Two or more drafts of the same statement / release / positioning exist, and the team needs a grounded comparison: which draft lands best per cluster, which crosses fewest red lines, which surfaces the largest supportive coalition, which has the strongest message-house roof. Frequently used after an initial `crisis-pre-flight` or `launch-pre-mortem` when the team has iterated into a handful of candidate drafts.

## Use another mode if

- Only one draft exists → run `crisis-pre-flight` / `launch-pre-mortem` / etc. first
- The drafts are significantly different announcements, not variants → run each in its appropriate mode
- You want to validate a single draft is ready → one of the single-draft modes

## Default phase composition

1. `factbase` — same freshness as the single-draft equivalent; budget 8-10 WebFetch calls (one factbase for all drafts — shared context)
2. `cast-design` — salience scoring on; cast held constant across drafts
3. `deep-research` — 12 parallel researchers (persona bundles reused across drafts)
4. `initial-reactions` — **per draft**, 12 parallel workers reading each draft independently. For 3 drafts × 12 personas = 36 worker spawns total. Workers do not see other drafts' reactions.
5. `critic` — per draft, 12 parallel critics each. REVISE loops per draft.
6. `counterfactual` — runs the `counterfactual-comparator` agent over the full N-draft × 12-persona matrix
7. `synthesis` — skeleton `templates/report-skeletons/counterfactual-compare.md`; artifacts: `counterfactual-delta`, `qa-doc` (composite across drafts), `stakeholder-heat-map`

## Default cast

- **Size:** 12 (same as the underlying single-draft mode — cast quality matters more than quantity for discrimination)
- **Cluster distribution:** matches whatever mode the drafts are for. A counterfactual-compare of crisis-pre-flight drafts uses crisis-pre-flight cluster distribution. A counterfactual-compare of launch-pre-mortem drafts uses launch distribution.

## Depth parameters

- Revise cycles: 2 per draft
- Social-dynamics: OFF (comparison is about single-shot reactions across drafts; adding social-dynamics confuses the signal)
- Debate: OFF
- Memory: OFF (within-draft; each draft is independent)

## Number of drafts

- **Minimum:** 2
- **Maximum:** 4 — beyond this the delta table is unreadable and runtime/cost balloons.
- **Sweet spot:** 3 drafts.

## Artifacts emitted alongside `report.md`

- `artifacts/counterfactual-delta.md` — full delta report with side-by-side tables, per-dimension winners, cluster-by-cluster narratives, quote comparison, recommended draft with revision notes
- `artifacts/qa-doc.md` — composite across drafts, identifying questions that would surface regardless of which draft is chosen
- `artifacts/stakeholder-heat-map.md` — cast-level (shared across drafts since cast is constant)

## Expected runtime

~8-12 minutes for 3 drafts × 12 personas. Runtime scales linearly with draft count.

## Expected cost

~$5 per 3-draft run.

## Failure modes specific to this mode

- **Drafts too similar.** If the drafts differ only in phrasing of 1-2 lines, personas will produce near-identical reactions and the delta signal is weak. Scoping-designer should warn if drafts are <15% different at the word level.
- **Drafts too different.** If the drafts are genuinely different announcements, not variants, counterfactual-compare produces confused output. The scoping-designer should check drafts are the same underlying stimulus type, and reject if they're not.
- **Cast disagreement on dimensions.** If every cluster has a different winner, the report may appear inconclusive. Surface this honestly — "no draft wins across the cast; revisions should pull specific elements from each" is a valid outcome, not a failure.
- **Hidden winner.** If one draft has a slight edge on every dimension but nothing strongly, the comparator should name it as the winner with margin-honest caveats rather than declining to recommend.

## Evidence trail

See `reference/methodology-sources.md` §counterfactual-compare.
