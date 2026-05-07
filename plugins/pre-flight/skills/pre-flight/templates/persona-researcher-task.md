Cast entry: {cast_entry_path}
Factbase file: {factbase_path}
Persona bundle schema: {schema_path}
Write persona bundle to: {output_path}

Read the cast entry, factbase, and schema.

Source hunt, starting from cast_entry.source_candidates:
- Named personas: target 5 sources — official org page, Wikipedia, LinkedIn, 2-3 recent press, long-form profile, adversarial piece. At least one ≤90 days old.
- Archetype personas: target 3 sources — trade press on the role, 2 analogous named exemplars.

Extract signature quotes:
- Named: ≥3 verbatim, attributed, dated. Each with source URL and register.
- If you cannot find 3 for a named persona, downgrade persona_type to archetype. Never fabricate.

Compose voice (2-3 sentences, concrete register moves — pull patterns from verbatim quotes).

Write signature_opener — one sentence pre-written in the persona's voice. This is the highest-leverage drift-mitigation line. Craft it as an opening beat that anchors tone and characteristic move.

List ≥4 primary concerns, concrete and persona-specific.

Extract ≥3 talking points — shorter phrases the persona uses, verbatim where possible.

Identify ≥4 forbidden phrases — exact phrases the persona would never use. These become automatic critic FAILs. Be specific, not categorical.

Write ≥3 rhetorical constraints — hard style rules, moves they always / never make.

Map ≥3 red_lines — specific triggers from dialogue to confrontation. Ground each in public statement or factbase event.

Name channel — where they say things, drives synthesizer red-line warnings.

Write reaction pattern — one paragraph on cadence and shape of their typical response.

Write expert reflections (Park et al. 2024 multi-lens module) — three 1-2 sentence reflections from strategist / analyst / journalist lens.

Fill provenance: source URLs, last_verified: today, freshness_ttl_days: 90, refresh_triggers.

Never fabricate a quote. Never paraphrase and present as quote. Minimum source counts honored. All schema-required minima met.

use_constraint default: named → "internal rehearsal only, not for public-facing output"; archetype → "any output".

Write to output_path per the schema exactly.

Return exactly: Wrote {output_path}
