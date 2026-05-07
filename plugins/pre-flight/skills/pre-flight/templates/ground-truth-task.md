Stimulus file: {stimulus_path}
Run-plan file: {run_plan_path}
Factbase schema: {factbase_schema_path}
Write factbase to: {output_path}

Read the stimulus and run-plan. Identify: which company, which industry, which issue, which stakeholder clusters need grounding.

Search and fetch per the schema's section order:
- Corporate structure (official site → Wikipedia → annual report → recent trade press)
- Business lines
- Operations & supply chain
- Regulatory baseline (relevant regulator's site + recent actions)
- Recent events (12-24 month window, trade press + adversarial coverage)
- Known controversies (NGO reports + critical press + litigation if any)
- Standard framings (both the company's preferred phrasing and the counter-framing)
- Key technical / scientific / economic facts (numerical anchors, each cited)
- Stakeholder ecosystem map (named candidates per cluster)
- What personas should NOT do (drift-prevention list — at least one common misconception)

Every fact needs a source URL. Minimum 10 sources total. At least one ≤90 days old.

Prefer primary sources. Pull adversarial coverage explicitly — the factbase's job is to prevent personas from being anchored in the company's own framing.

Date-stamp every event as YYYY-MM-DD. No "recently."

If a fact matters but you can't source it, drop it. Never invent.

Write a one-sentence self-assessment in "Researcher's confidence note" flagging any thin sections.

Write to output_path per the schema exactly.

Return exactly: Wrote {output_path}
