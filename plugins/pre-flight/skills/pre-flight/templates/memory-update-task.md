Findings directory: {findings_dir}
Personas directory: {personas_dir}
Scope: {scope}                                # within-run | cross-run
Industry key: {industry_key}                  # required for cross-run only
Run ID: {run_id}
Consent recorded: {consent_recorded}          # must be true for cross-run
Output directory: {output_dir}

If scope is cross-run and consent_recorded is not true, refuse — write nothing, return an error string.

For each persona-<id>-final.md in findings_dir:
- Read the reaction file and the persona bundle.
- Extract sentiment, trust_delta, would_act, standout-line pull, "What would change my position" content, channel used.
- Compress into a summary stub (max 150 words within-run, max 300 words cross-run).

Each stub includes: posture summary (one sentence), sentiment trajectory (prior posture, current sentiment, trust delta this round, net trajectory if cross-run), standout framing the persona anchored on (one sentence, verbatim quote if pulled), what would move them next (one sentence from "What would change my position"), channel used, "do not carry forward" note (one line on round-specific context NOT to inherit).

Summary only. Never emit full reactions. Never paraphrase and present as quote. Posture summary is one sentence — more than one sentence means synthesizing; stop.

Cross-run stubs write to pre-flight-memory/<industry-key>/ in the user's working dir. Within-run stubs write to pre-flight-runs/<run>/memory/.

Return exactly: Wrote <n> memory stubs to {output_dir}
