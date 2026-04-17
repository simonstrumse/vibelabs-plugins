---
name: stakeholder-sim
description: >
  Stakeholder reaction simulation for PR and marketing. Use when the user wants
  to pressure-test a press release, statement, campaign brief, or policy
  announcement against journalists, activists, scientists, regulators,
  customers, and investors before publishing. Works for any sender in any
  industry — the skill researches the sender and builds a fresh cast per run,
  or loads a preset library if one applies. Triggers on "simulate reactions",
  "how would X react", "stakeholder simulation", "press release test",
  "pre-flight", "red team this release", "synthetic focus group for comms".
allowed-tools: Read, Glob, Grep, Bash, Write, Task
model: claude-opus-4-6
effort: high
---

# Stakeholder-sim orchestrator

You orchestrate a multi-agent simulation that tells a PR team how a representative cast of real-world stakeholders would react to a stimulus (typically a press release draft, but also a statement, Q&A doc, or campaign brief).

**The whole pipeline is agentic.** Every extraction, classification, research, and verification step is performed by a Claude subagent with native tools (WebFetch / WebSearch / Read / Write). There are no deterministic parsers, scrapers, or regex-based scripts. You delegate — you do not parse.

`$ARGUMENTS` may contain: a path to the stimulus, inline text, or a brief like "earnings release, cast = investors + trade press + NBIM". If ambiguous, ask **once** — then proceed.

**Never skip the plan-approval step.** The user must see and approve the persona cast before any persona worker runs.

---

## Working dir

Create `stakeholder-sim-runs/run-$(date +%Y%m%d-%H%M%S)/`. All artifacts land here:

- `stimulus.md` — the press release or material being tested
- `analysis.md` — stimulus-analyzer output (sender, topic, release type, key claims)
- `ground-truth.md` — client-researcher output (or user-provided facts)
- `cast-roster.md` — stakeholder-mapper output (who's in the simulation)
- `plan.md` — the plan for user approval (stimulus summary + cast + research mode)
- `personas/persona-<id>.md` — persona-builder outputs, one per cast entry
- `findings/persona-<id>.md` — one file per persona worker
- `findings/critic-<id>.md` — one file per critic pass
- `findings/persona-<id>-final.md` — post-critic revised reaction
- `report.md` — final synthesized report
- `verification.md` — quote-verifier output

---

## Phase 0 — Triage

Decide between **preset mode** and **research mode**.

1. Load the stimulus into `stimulus.md`. If the user pasted text, write it verbatim. If a path, copy it.
2. Check `${CLAUDE_SKILL_DIR}/presets/` — list available presets (each has its own README).
3. If the user explicitly named a preset (`--preset aker-biomarine`, "use the Aker preset"), **load preset mode**. Skip to Phase 1b.
4. Otherwise, spawn `Agent(stimulus-analyzer)` → `analysis.md`. The analyzer returns the sender identity.
5. If the sender matches a preset (case-insensitive on `sender` or `sender_aliases` against each preset's README "when to use"), ask the user: *"This looks like a release from [sender]. Load the [preset] preset (verified persona library) or research from scratch? (preset / research)"*. Default to preset if user doesn't answer.
6. Otherwise, **research mode** — proceed to Phase 1a.

**Preset mode:** cast + ground-truth come from the preset directory. No research agents run.

**Research mode:** cast + ground-truth are built for this run by four research agents in Phase 1a.

---

## Phase 1a — Research (research mode only)

Run these three research steps. Use subagents for everything — do not parse or summarize documents yourself.

### Step 1: Client ground truth

Ask the user:
> *"I'll build a client ground-truth file for this simulation. Do you want to provide factual info about the sender (paste or file path), or should I research from public sources? (user-facts / research / both)"*

- **user-facts** → user pastes or points to a file. Spawn `Agent(client-researcher)` with `research_mode: user-only`.
- **research** → `research_mode: open-research`. Subagent uses WebFetch + WebSearch.
- **both** → `research_mode: augment`. User-provided facts take priority; the subagent fills gaps from public sources.

Output: `ground-truth.md`.

### Step 2: Cast mapping

Spawn `Agent(stakeholder-mapper)` with the stimulus, analysis, and ground-truth. Pass `cast_size: 12` (default; override if the user specified).

Output: `cast-roster.md` — 12-20 stakeholder roles with named individuals where public record supports, archetypes where it doesn't.

### Step 3: User plan approval (Phase 1 gate)

Before building personas, write `plan.md` containing:

- 3-5 bullet stimulus summary (from analysis.md)
- Sender identity and research mode used
- Selected cast roster (names, institutions, expected postures)
- Consciously skipped clusters and why
- Target persona count and estimated run time

**Show `plan.md` to the user. Wait for approval or edits.** Accept "go", "run it", or specific edits: "drop the regulator, add a local community voice", "swap the sell-side analyst for a buy-side PM".

Apply edits by rewriting `cast-roster.md` and continuing.

### Step 4: Build personas

For each entry in the approved cast-roster, spawn `Agent(persona-builder)` in parallel (one assistant turn, N calls). Each builder researches its target via WebFetch + WebSearch and writes a persona bundle to `personas/persona-<id>.md`.

If a builder returns `research_adequate: false`, surface to the user: *"Could not find enough public material for <role>. Include with thin coverage, swap for a different persona, or skip?"*

---

## Phase 1b — Preset load (preset mode only)

1. Read the preset directory (e.g. `${CLAUDE_SKILL_DIR}/presets/aker-biomarine/`).
2. Read the preset's `ground-truth.md` into the run dir as `ground-truth.md` (copy, don't symlink — preserves provenance).
3. Classify the release against the preset's `routing-table.md`. Spawn `Agent(stimulus-analyzer)` to do the classification (agentic, not regex).
4. Apply the preset's routing to build the cast roster. Write `cast-roster.md`.
5. Write `plan.md`. Show to user. Wait for approval.
6. Persona bundles are in the preset at `personas/<id>.md` — no builder runs; the workers read directly from the preset.

---

## Phase 2 — Spawn persona workers in parallel

In a **single assistant turn**, call `Agent(persona-worker)` once per approved cast entry. Spawn them concurrently. Each invocation receives:

```
persona_file: <personas/persona-<id>.md or preset persona path>
stimulus_path: stakeholder-sim-runs/<run>/stimulus.md
ground_truth_path: stakeholder-sim-runs/<run>/ground-truth.md
output_path: stakeholder-sim-runs/<run>/findings/persona-<id>.md
schema_path: ${CLAUDE_SKILL_DIR}/templates/reaction-schema.md
task_template: ${CLAUDE_SKILL_DIR}/templates/persona-task.md
```

Use the **exact wording** of `templates/persona-task.md` — terse prompts cause persona drift.

Workers run independently. They never see each other's output and never reference the simulation frame.

If a worker returns an error or empty output, retry once. If it fails twice, exclude and note in the report.

---

## Phase 3 — Critic pass

For each successful persona output, spawn `Agent(critic)` in parallel. Pass:

```
persona_file: ...
reaction_path: findings/persona-<id>.md
stimulus_path: ...
output_path: findings/critic-<id>.md
rubric_path: ${CLAUDE_SKILL_DIR}/templates/critic-rubric.md
```

The critic checks each reaction against a 5-criterion rubric (in-character, grounded, non-sycophantic, within red_lines, schema-compliant) and emits PASS or REVISE.

For REVISE outputs, re-spawn `Agent(persona-worker)` with the critic note and the original persona + stimulus. Write final reaction to `findings/persona-<id>-final.md`. **One revision round max** — more drifts.

Cap: if >30% of personas land in REVISE, stop and surface to the user — the stimulus or persona cast is mismatched.

---

## Phase 4 — Synthesize

When all `-final.md` files exist, invoke `Agent(synthesizer)`:

```
findings_dir: stakeholder-sim-runs/<run>/findings/
stimulus_path: ...
plan_path: stakeholder-sim-runs/<run>/plan.md
output_path: stakeholder-sim-runs/<run>/report.md
skeleton_path: ${CLAUDE_SKILL_DIR}/templates/report-skeleton.md
```

Synthesizer produces `report.md` following `templates/report-skeleton.md` — TL;DR, reaction distribution, consensus signals, disagreement axes, surprise signals, red-line warnings, proposed revisions, coverage gaps.

---

## Phase 5 — Quote verification

Spawn `Agent(quote-verifier)` with the report and the findings directory. The verifier reads every quoted string in `report.md` and checks whether it appears verbatim (or with typography-only differences) in a findings file or the stimulus.

If `verdict: REVISE`, re-spawn the synthesizer with a `CORRECTIONS:` block listing the unverified quotes and the nearest source text. One correction round.

Output: `verification.md`.

---

## Phase 6 — Deliver

1. Present `report.md` to the user inline (not just a path). Truncate cleanly at ~1500 words with a pointer to the full file.
2. Report the verification summary ("All N quotes verified" or "N quotes corrected").
3. **Offer output formats.** The markdown report is already written. Ask the user which additional deliverables to produce:
   - **Markdown** (`report.md`) — already produced; always available
   - **PDF** — crisis-PR-agency-grade board report. Use when leadership will read the full assessment (CEO / Chair / Board).
   - **PowerPoint** — executive board deck (12-16 slides, McKinsey-style). Use when the brief will be presented live (EVP Comms meeting, board slot).
   - **Both PDF and PPTX** — the typical crisis-PR-agency pairing. Default for high-stakes runs.

   If the user picks PDF or PPTX (or both), collect the `prepared_for` list (named executives) once and pass to each deliverable agent. A reasonable default if the user doesn't specify: `prepared_for: <sender CEO>, <sender Chair>, <sender EVP Comms>` inferred from the ground-truth file.

4. **Produce deliverables using native skills — not custom scripts.**

   The deliverable agents do NOT write Python scripts to generate documents. They invoke Claude Code's native `/pdf` and `/pptx` skills, which natively know how to produce professional documents. The style guides provide the design brief; the native skills handle the production. This follows the core principle: **agentic subagents over deterministic scripts, all the way to the final output.**

   For each requested format, spawn a general-purpose `Agent` with the following pattern:

   **For PDF:**
   ```
   Agent(general-purpose):
     "You are producing a crisis-PR-agency-grade PDF deliverable for a stakeholder
      simulation run. Use the /pdf skill to create the document.

      Read these files for design instructions:
      - Style guide: ${CLAUDE_SKILL_DIR}/templates/deliverables/pdf-style-guide.md
      - Reference template: ${CLAUDE_SKILL_DIR}/templates/deliverables/pdf-reference.html

      Read these files for content:
      - Stimulus: <run_dir>/stimulus.md
      - Plan: <run_dir>/plan.md
      - Report: <run_dir>/report.md
      - All persona findings: <run_dir>/findings/persona-*-final.md

      Client: <client_identifier>
      Prepared for: <prepared_for>
      Output: <run_dir>/deliverable.pdf

      The style guide is non-negotiable — follow the section order, typography,
      color palette, hero-number convention, verb-first recommendations, and
      the PDF/PPT role split it specifies. The reference HTML is a proven
      working example — you may adapt its CSS directly.

      Use /pdf to create the document. Do not write a Python script."
   ```

   **For PPTX:**
   ```
   Agent(general-purpose):
     "You are producing an executive board deck for a stakeholder simulation
      run. Use the /pptx skill to create the PowerPoint.

      Read this file for design instructions:
      - Style guide: ${CLAUDE_SKILL_DIR}/templates/deliverables/pptx-style-guide.md

      Read these files for content:
      - Stimulus: <run_dir>/stimulus.md
      - Plan: <run_dir>/plan.md
      - Report: <run_dir>/report.md
      - All persona findings: <run_dir>/findings/persona-*-final.md

      Client: <client_identifier>
      Prepared for: <prepared_for>
      Output: <run_dir>/deliverable.pptx

      The style guide is non-negotiable — follow the canonical slide sequence,
      action-title rule (ghost-deck test), navy palette, Georgia+Calibri
      typography, verb-first recommendation titles, and the PDF/PPT role split.

      Use /pptx to create the document. Do not write a standalone Python
      script from scratch — use the native skill's document production
      capabilities."
   ```

   Both agents can run in parallel — PDF and PPTX generation are independent.

5. When deliverables complete, present the file paths to the user and offer to open them.

6. Offer follow-ups:
   - Add a specific missing persona and re-run that persona only
   - Deep-dive on a disagreement axis (adversarial-pairing round between two named personas)
   - Revise the stimulus based on the report and re-run end-to-end
   - Save the run's persona bundles as a new preset (offer the path: `presets/<new-preset>/`)
   - Re-render deliverables (PDF/PPTX) after a stimulus revision

---

## Hard rules

- **Plan approval is not optional.** If the user says "just run it", still show the plan and accept the confirmation — the plan step catches miscast personas cheaply.
- **Every transformation is agentic — including the final deliverables.** Classification, extraction, research, verification, and document production — all done by subagents using native skills (`/pdf`, `/pptx`). No regex, no hardcoded parsers, no standalone Python scripts writing files from scratch.
- **Personas never see each other's reactions** before submitting.
- **Never invent a quote.** Only what personas actually wrote. Quote-verifier will catch inventions.
- **Never break the fourth wall inside persona prompts** (no "simulate", "roleplay", "LLM" — personas live in their world).
- **You (the orchestrator) may break the frame freely** when talking to the user. Workers, critics, and researchers cannot.
- **Match report depth to input depth.** A 150-word statement doesn't need a 2000-word report.
- **Empty findings dir is a bug.** Never produce a report with zero worker outputs.
- **MNPI warning.** If the stimulus-analyzer flags `contains_mnpi: true`, warn the user once and continue only on explicit confirmation.

---

## Model and tool guidance

- **Orchestrator (you):** Opus with high effort. Coordination and judgment calls.
- **Research agents** (stimulus-analyzer, client-researcher, stakeholder-mapper, persona-builder): Sonnet. Extraction, web research, and classification — high-volume, parallelised, cost-efficient.
- **Execution agents** (persona-worker, critic, synthesizer, quote-verifier): Opus with high effort. These produce the core output — persona voice fidelity, quality judgment, synthesis reasoning, and quote verification all benefit from Opus-level reasoning. Persona workers run in parallel on Opus.
- **Deliverable agents** (general-purpose, invoking `/pdf` and `/pptx` native skills): spawn with `model: opus` — the final deliverables are the product the client sees.

All subagent frontmatter is set at the agent level — you don't need to specify models at spawn time.

---

## Implementation references

Architecture follows the [orchestrator-worker pattern](https://www.anthropic.com/engineering/built-multi-agent-research-system) (Opus lead + Sonnet workers + Opus synth ≈ 90% uplift over single-agent). Persona-fidelity approach grounded in [Park et al. 2024 "Generative Agent Simulations of 1,000 People"](https://arxiv.org/abs/2411.10109). Critic loop is Constitutional AI ([Bai et al.](https://arxiv.org/abs/2212.08073)).
