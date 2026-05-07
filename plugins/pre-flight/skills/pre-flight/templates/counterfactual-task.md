Drafts: {drafts}                      # list of 2-4 draft stimulus paths, labeled A/B/C/D
Reaction sets: {reaction_sets}        # one directory per draft, each containing all persona reactions
Factbase file: {factbase_path}
Cast-spec file: {cast_spec_path}
Write delta report to: {output_path}

Read all drafts, all reaction sets, factbase, and cast-spec.

For each draft build a summary profile: per-cluster sentiment distribution, per-cluster trust_delta average, per-cluster would_act proportion, red-line warnings crossed, consensus signals (≥2 cross-cluster), disagreement axes, surprise signals.

Build the cross-draft delta table — one row per cluster, one column per draft, with sentiment/trust-delta reading and a winner column.

Identify per-dimension winners: highest trust-lift across cast, fewest red-line crossings, largest supportive coalition, strongest message-house roof, clearest differentiation from competitor framing.

Write cluster-by-cluster narratives (one paragraph per draft per cluster, with at least one verbatim quote per paragraph).

Write quote-comparison highlights: strongest supporting quote per draft + worst hostile quote per draft.

Write recommended-draft section: which draft wins, why in 2-3 sentences, weaknesses the next revision must address (grounded in specific persona reactions).

Optionally sketch a proposed synthesized draft IF the pattern of wins suggests a clean combination. If not, omit — a forced combined draft is worse than "pick B and revise."

Coverage gaps: dimensions where all drafts produced similar reactions — not discriminated between drafts.

Every per-cluster reading quotes at least one persona from that cluster for each draft. Winners are declared, not hedged. Grounded in reaction quotes, not in your prose preferences for the draft text.

No invented quotes — every quote traces verbatim to a specific reaction file.

Return exactly: Wrote {output_path}
