# Failure modes and their signatures

Read this when a simulation output feels off. Each failure has a signature the orchestrator can detect and a corrective action.

---

## Sycophantic collapse

**Signature.** All personas land in the "skeptical" or "neutral" sentiment bucket regardless of the stimulus. Reactions open with "I appreciate…", "Overall…", "While there are some concerns…". Hostile personas sound reasonable. Transactional personas sound enthusiastic.

**Root cause.** Claude's helpful-assistant attractor pulls personas toward politeness. Most common with hostile activist personas (Hammarstedt, Allan) on first-pass.

**Fix.** (a) Critic catches this with the "non-sycophantic" criterion. (b) If >30% of a run fails non-sycophantic, rerun with the persona prompt prepended by the persona's strongest signature quote to anchor voice.

---

## Factual drift

**Signature.** Personas reference facts that don't appear in the stimulus or ground truth. Invented statistics. Invented Aker history. Wrong acquisition history (Skretting instead of AIP).

**Root cause.** Ground-truth file wasn't read by the worker, or the stimulus ambiguity forced speculation.

**Fix.** (a) Confirm ground_truth_path is in the spawn message. (b) Add the specific drifted fact to `aker-ground-truth.md` with an explicit correction.

---

## Cross-contamination

**Signature.** Personas quote each other. Reactions converge on identical phrasings. The persona cast reaches consensus too cleanly.

**Root cause.** Workers are reading other findings files (bug in output paths). Or the orchestrator passed one worker's output to another.

**Fix.** Confirm each worker's system message doesn't include sibling findings. Workers should only see persona + stimulus + ground truth + schema.

---

## Persona bleed

**Signature.** Same-archetype personas (e.g. two activists) produce indistinguishable reactions. Shuffling names wouldn't change the report.

**Root cause.** Persona bundles too thin or too similar. Relying on role rather than signature_quotes + rhetorical_style.

**Fix.** Enrich the bundles. Each persona needs ≥3 signature quotes the others don't have and a specific rhetorical_style line that differentiates them.

---

## Invented quotes in the report

**Signature.** A quote attributed to a persona in `report.md` doesn't match any text in `findings/persona-<id>-final.md`.

**Root cause.** Synthesizer paraphrasing and presenting as quotation.

**Fix.** `scripts/verify_quotes.py` catches this. Synthesizer reruns with a CORRECTIONS block. If it happens twice, the synthesizer prompt needs an additional "quotes must be bytewise identical" instruction.

---

## Coverage-gap silence

**Signature.** Report reads as complete. No "Coverage gaps" section, or it's empty.

**Root cause.** Synthesizer over-confident. The plan consciously skipped personas and the synthesizer didn't carry that forward.

**Fix.** The synthesizer reads `plan.md` and must list the "personas skipped" section in the coverage-gap section. Non-negotiable.

---

## Scope mismatch

**Signature.** Report is longer and deeper than the stimulus warrants. 2,500-word report on a 150-word statement. Findings feel over-fitted.

**Root cause.** Default cast was too large for the stimulus.

**Fix.** Orchestrator chooses cast size by stimulus length and stakes. A single-line quote from a CEO doesn't need 16 personas.

---

## Red-line silence

**Signature.** The stimulus crosses a persona's stated red_line but the reaction glosses over it. E.g., a persona named as an MSC objector doesn't mention MSC when the stimulus celebrates MSC recertification.

**Root cause.** Signature variant of sycophantic collapse.

**Fix.** Critic's "within red_lines" criterion should catch this. If it doesn't, the persona bundle's red_lines field is probably too abstract — rewrite it with concrete trigger phrases.

---

## Confidence inflation

**Signature.** All personas report `confidence: 0.8+`. No "I'd need to see more" or "this is my gut read but I'd check with my team" reactions.

**Root cause.** Prompt framing pushed personas toward strong takes even when a real human wouldn't have one.

**Fix.** The persona-worker prompt explicitly allows low confidence. If every run is high-confidence, add an example of a low-confidence reaction to the template.

---

## Timezone / recency drift

**Signature.** Personas reference events that happened after the simulation date. Anachronisms.

**Fix.** Ground-truth file includes a "personas live on <date>" stamp. Orchestrator includes the date in every spawn.
