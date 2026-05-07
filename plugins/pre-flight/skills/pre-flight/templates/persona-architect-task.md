Run-plan file: {run_plan_path}
Factbase file: {factbase_path}
Stimulus file: {stimulus_path}
Cast-spec schema: {cast_spec_schema_path}
Persona bundle schema: {persona_bundle_schema_path}
Write cast-spec to: {output_path}

Read the run-plan, factbase, stimulus, and schemas.

Start from the factbase's stakeholder ecosystem map. Score every candidate on Mitchell-Agle-Wood 1997 salience (power / legitimacy / urgency, each 0-10). Derive priority tier.

Fill the cast to the run-plan's target size and cluster distribution. Tier 1 candidates first; Tier 2 to fill; Tier 3 only if room.

Decide named vs archetype per persona:
- Named requires ≥3 verbatim quotes findable in public record within the freshness window AND presence in the factbase's stakeholder ecosystem map.
- If uncertain, mark archetype. The researcher will try to upgrade.

Write source_candidates (3-5 starting URLs) for each persona. Pull from factbase Provenance and extend with WebSearch.

Write why-selected and expected blind spot per persona.

List deliberately excluded personas and why. This must be non-empty.

If the mode includes debate or social-dynamics, suggest 3-6 adversarial pairings.

Write use-constraint summary (default: named → "internal rehearsal only"; archetype → "any output").

Compose design rationale — 2-4 sentences like a casting director's note.

Cast size exact to the run-plan. Cluster distribution exact to the run-plan. No invented people. Every persona has ≥3 source_candidates.

Write to output_path per the schema exactly.

Return exactly: Wrote {output_path}
