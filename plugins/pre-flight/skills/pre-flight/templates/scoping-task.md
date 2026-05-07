Stimulus file: {stimulus_path}
User answers file: {user_answers_path}
Modes directory: {modes_dir}
Modes index: {modes_index_path}
Phase library: {phase_library_path}
Run-plan schema: {run_plan_schema_path}
Methodology sources: {methodology_sources_path}
Write run-plan to: {output_path}

Read the stimulus, user answers, modes index, phase library, and run-plan schema.

Classify the mode. Map the stimulus + user answers onto the published mode catalog. If the user answer names a mode, use it. If not, infer from the stimulus. Ambiguous cases: pick the closest — the user can override at the approval gate.

Compose phases from the mode's default list in modes/<mode>.md. Adjust based on user answers (severity, depth preference, memory opt-in).

Design the cast: size, cluster distribution, prefer_named flag. Match the mode defaults but tune to the stimulus.

Set depth parameters. Respect published caps (revise cycles ≤ 2; cast size ≤ 20).

Select the report skeleton. Always templates/report-skeletons/<mode>.md. List the artifacts the mode requires.

Write designer_reasoning — 2-4 sentences explaining your key choices.

Emit run-plan.yaml conforming to the schema exactly. Every required field populated.

Do not invent mode names or phase names. Only use published enums. If you believe a new phase is needed, pick the closest published phase and flag it in designer_reasoning.

Never enable cross_run_enabled without explicit user consent in the user answers file.

Return exactly: Wrote {output_path}
