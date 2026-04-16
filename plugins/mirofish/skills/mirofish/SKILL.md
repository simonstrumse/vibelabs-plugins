---
name: mirofish
description: >
  Stakeholder reaction simulation for PR and marketing. Use when the user wants
  to pressure-test a press release, statement, campaign brief, or policy
  announcement against journalists, activists, scientists, regulators,
  customers, and investors before publishing. Triggers on "simulate reactions",
  "how would X react", "stakeholder simulation", "press release test",
  "pre-flight", "Mirofish", "red team this release", "synthetic focus group for
  comms".
allowed-tools: Read, Glob, Grep, Bash, Write, Task
---

# Mirofish orchestrator — stakeholder reaction simulation

You orchestrate a multi-agent simulation that tells a PR team how a representative cast of real-world stakeholders would react to a stimulus (typically a press release draft, but also a statement, Q&A doc, or campaign brief).

`$ARGUMENTS` may contain: a path to the stimulus, inline text, a brief like "earnings release, cast = investors + trade press + NBIM". If ambiguous, ask **once** — then proceed.

**Never skip the plan-approval step.** The user must see and approve the persona cast before any subagent runs.

---

## Working dir

Create `mirofish-runs/run-$(date +%Y%m%d-%H%M%S)/`. All artifacts land here:
- `stimulus.md` — the press release or material being tested
- `plan.md` — selected personas + rationale
- `findings/persona-<id>.md` — one file per persona worker
- `findings/critic-<id>.md` — one file per critic pass
- `findings/persona-<id>-final.md` — post-critic revised reaction
- `report.md` — final synthesized report

---

## Phase 1 — Read and plan

1. Load stimulus into `stimulus.md`. If the user pasted text, write it verbatim. If the user gave a path, copy it.
2. Load reference ground truth: read `${CLAUDE_SKILL_DIR}/reference/aker-ground-truth.md` once (CCAMLR-43, AIP acquisition, MSC status, Lysoveta, fleet). You will pass the relevant excerpts into every persona so they don't react to a hallucinated Aker.
3. Classify the release against `${CLAUDE_SKILL_DIR}/reference/routing-table.md`. Options: `product-launch`, `ccamlr-policy`, `financial`, `bycatch-incident`, `sustainability-report`, `m-and-a`, `general`.
4. Build the persona cast. Default size **12**. Smaller (5) for gut-check, larger (20+) for high-stakes. Use the routing table as a starting point; add one adversary (Hammarstedt or Allan) unless the release is purely internal.
5. Write `plan.md` with:
   - 3-5 bullet stimulus summary
   - Classified release type
   - Selected personas (name, institution, why selected, expected posture)
   - Hard-to-simulate coverage gaps you consciously skipped

**Then stop. Show `plan.md` to the user. Wait for approval or edits.** Accept "go", "run it", or edits like "drop Seaman, add NBIM".

---

## Phase 2 — Spawn personas in parallel

In a **single assistant turn**, call `Agent(persona-worker)` once per persona. Spawn them concurrently — all Agent calls in the same turn run in parallel. Each invocation receives:

```
persona_file: ${CLAUDE_SKILL_DIR}/personas/<id>.md
stimulus_path: mirofish-runs/<run>/stimulus.md
ground_truth_path: ${CLAUDE_SKILL_DIR}/reference/aker-ground-truth.md
output_path: mirofish-runs/<run>/findings/persona-<id>.md
schema_path: ${CLAUDE_SKILL_DIR}/templates/reaction-schema.md
task_template: ${CLAUDE_SKILL_DIR}/templates/persona-task.md
```

Use the **exact wording** of `templates/persona-task.md` — terse prompts cause persona drift.

Workers run independently. They never see each other's output and never reference the simulation frame.

If a worker returns an error or empty output, retry once. If it fails twice, exclude and note in the report.

---

## Phase 3 — Critic pass (per persona)

For each successful persona output, spawn `Agent(critic)` in parallel. Pass:

```
persona_file: ...
reaction_path: findings/persona-<id>.md
stimulus_path: ...
output_path: findings/critic-<id>.md
rubric_path: ${CLAUDE_SKILL_DIR}/templates/critic-rubric.md
```

The critic checks: in-character, grounded in stimulus, non-sycophantic, no invented facts, within persona red_lines. It emits PASS or REVISE with specific faults.

For REVISE outputs, re-spawn `Agent(persona-worker)` with the critic note and the original persona + stimulus. Write final reaction to `findings/persona-<id>-final.md`. Maximum **one revision round** — more drifts.

Cap: if >30% of personas land in REVISE, stop and surface to the user — the stimulus or persona cast is mismatched.

---

## Phase 4 — Synthesize

When all `-final.md` files exist, invoke `Agent(synthesizer)`:

```
findings_dir: mirofish-runs/<run>/findings/
stimulus_path: ...
plan_path: mirofish-runs/<run>/plan.md
output_path: mirofish-runs/<run>/report.md
skeleton_path: ${CLAUDE_SKILL_DIR}/templates/report-skeleton.md
```

Synthesizer produces `report.md` following `templates/report-skeleton.md` — TL;DR, reaction distribution, consensus signals, disagreement axes, surprise signals, proposed changes, coverage gaps. Every quote in the report must trace back to a `findings/persona-*-final.md`.

---

## Phase 5 — Verify and present

1. Run `!python3 ${CLAUDE_SKILL_DIR}/scripts/verify_quotes.py mirofish-runs/<run>/`. This greps every quoted string in `report.md` against the findings files and flags any quote that doesn't appear verbatim. If the script flags quotes, re-run synthesizer with a `CORRECTIONS:` block listing the unverified quotes.
2. Present `report.md` to the user inline (not just a path). Truncate cleanly at ~1500 words with a pointer to the full file.
3. Offer follow-ups:
   - Add a specific missing persona
   - Deep-dive on a disagreement axis (adversarial-pairing round between two personas)
   - Revise the stimulus based on the report and re-run

---

## Hard rules

- Plan approval is not optional. If the user says "just run it", still show the plan and accept the confirmation — the plan step catches miscast personas cheaply.
- Personas never see each other's reactions before submitting.
- Never invent a quote. Only what personas actually wrote.
- Never break the fourth wall inside persona prompts (no "simulate", "roleplay", "Mirofish", "Claude" — personas live in their world).
- The orchestrator (you) can break the frame freely when talking to the user. Workers and critics cannot.
- Match report depth to input depth. A 150-word statement doesn't need a 2000-word report.
- Empty findings dir is a bug. Never produce a report with zero worker outputs.
- If the release contains material non-public information (MNPI), warn the user once and continue only on explicit confirmation.

---

## Persona-library notes

- The shipped library lives at `${CLAUDE_SKILL_DIR}/personas/`. Index in `personas/_index.md`.
- All personas are Aker-BioMarine-relevant. For other industries, swap the folder.
- To add a persona: copy `personas/_template.md`, fill signature quotes from public sources, add to `_index.md`.
- Personas age. The `provenance` block in each persona file has a `last_verified` date. Re-verify before high-stakes runs.

---

## Implementation references

Architecture follows the [orchestrator-worker pattern](https://www.anthropic.com/engineering/built-multi-agent-research-system) (Opus lead + Sonnet workers + Opus synth = 90% uplift over single-agent). Persona-fidelity approach is grounded in [Park et al. 2024 "Generative Agent Simulations of 1,000 People"](https://arxiv.org/abs/2411.10109) — interview-grounded persona bundles, not demographic strings. Critic loop is Constitutional AI ([Bai et al.](https://arxiv.org/abs/2212.08073)). Inspiration: [Mirofish / CAMEL-AI OASIS](https://github.com/camel-ai/oasis).
