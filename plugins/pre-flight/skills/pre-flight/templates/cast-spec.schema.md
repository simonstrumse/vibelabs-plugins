# Cast-spec schema

The `persona-architect` agent emits a cast-spec file at `pre-flight-runs/<run>/cast-spec.md` before any persona-researcher fires. It names the personas to be built, why each was selected, and the salience scoring that drove prioritization. The user reviews and edits this before the heavy persona-research work starts.

## File shape

```yaml
---
run_id: <string>
mode: <mode name>
cast_size: <int>
architect_model: claude-opus-4-7
created_at: <ISO-8601>
---

# Cast spec — <stimulus title>

**Mode:** <mode> · **Target cast size:** <n> · **Industry key:** <string> · **Stimulus:** <one-line>

## Design rationale

<2-4 sentences: why this cast size, why this cluster distribution, what the most important stakeholder to include is and why, what the architect deliberately left out.>

## Personas

<One entry per persona. Named where public record supports ≥3 verbatim quotes; archetype otherwise.>

### 1. <persona id>

- **name:** <full name or archetype label>
- **persona_type:** named | archetype
- **role:** <role>
- **institution:** <institution or archetype institution class>
- **cluster:** <cluster label>
- **archetype:** <one-line>
- **salience:**
    - power: <0-10>
    - legitimacy: <0-10>
    - urgency: <0-10>
- **priority_tier:** 1 | 2 | 3
- **posture:** <default posture toward the issuing organization>
- **why selected:** <one sentence — the specific angle this persona opens up>
- **expected blind spot:** <one phrase — what this persona will NOT surface, to set honest coverage-gap expectations>
- **source_candidates:** <URLs the researcher should start from, 3-5 listed>

### 2. <persona id>

- ...

<...repeat for each persona in the cast...>

## Cluster distribution

| Cluster | N | Rationale |
|---|---|---|
| <cluster 1> | <n> | <why this count> |
| <cluster 2> | <n> | <why this count> |
| ... | ... | ... |

## Deliberately excluded

<Personas the architect considered but excluded. Be honest — these become coverage gaps that the synthesizer will name in the report.>

- <persona class or name>: <reason for exclusion>
- <persona class or name>: <reason for exclusion>

## Adversarial pairing suggestions

<Optional. If the mode includes a debate or social-dynamics phase, the architect suggests 3-6 natural-antagonist pairings here. The designer's run-plan may or may not adopt these.>

- <persona id A> ↔ <persona id B>: <one sentence on the tension>
- <persona id A> ↔ <persona id B>: <one sentence on the tension>

## Use-constraint summary

<Per-persona use_constraint plan. Named personas default to "internal rehearsal only"; archetypes to "any output". Any deviation is flagged here.>

- <persona id>: <use_constraint>
- <persona id>: <use_constraint>
```

## Salience scoring guidance (Mitchell-Agle-Wood 1997)

- **Power (0-10):** The persona's ability to impose their will on the issuing organization through their channel. A retail activist with 100K followers ≠ an institutional investor with a 5% stake.
- **Legitimacy (0-10):** The perceived rightness of their claim in the public sphere. A regulator claiming enforcement authority = 10; an anonymous blog commenter = 2.
- **Urgency (0-10):** Time-sensitivity and attention-demandingness. A journalist working on a 48h deadline = 9; a sustainability officer reviewing annual disclosures = 3.

**Priority tier = f(salience):**
- Tier 1 (definitive): all three attributes ≥ 7. Must be in the cast.
- Tier 2 (expectant): two of three ≥ 6. Should be in the cast unless size-constrained.
- Tier 3 (latent): one of three ≥ 6. Nice-to-have; first to drop at smaller sizes.

## Quality gates

- Cast size matches the run-plan's `cast_spec.size`.
- Cluster distribution matches the run-plan's `cast_spec.clusters`.
- Every persona has ≥3 `source_candidates` so the researcher has a starting point.
- At least one persona per priority_tier is present unless the cast is ≤5 (then tier 1 only).
- "Deliberately excluded" is non-empty — the architect must be able to articulate at least one honest gap.

## Approval gate

The user reviews this file before any persona-researcher fires. They can drop personas, add personas, retarget salience scores, or change cluster distribution. Once approved, the orchestrator spawns N persona-researcher subagents in parallel, one per entry.
