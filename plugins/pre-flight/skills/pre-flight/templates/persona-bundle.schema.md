# Persona bundle schema v2

The canonical output contract for `agents/persona-researcher.md`. Every bundle in `pre-flight-runs/<run>/personas/` must conform. Grounded in Park et al. 2024 ([Generative Agent Simulations of 1,000 People](https://arxiv.org/abs/2411.10109)) + Li et al. 2024 ([arXiv 2402.10962](https://arxiv.org/abs/2402.10962)) on persona drift + Fisher/Ury BATNA for red_lines + Mitchell-Agle-Wood 1997 salience + Freeman 1984 stakeholder typology.

## File shape

```yaml
---
id: <slug, e.g. "jane-doe-company" or "archetype-sell-side-esg-analyst">
name: <full name for named personas; archetype label for archetypes>
persona_type: named | archetype        # legal/ethical gate
role: <role / title>
institution: <institution or archetype institution class>
cluster: activist | scientist | regulator | press | customer | investor | internal | peer-company | proxy-advisor | sovereign-investor | <mode-specific>
archetype: <one-line archetype label, e.g. "direct-action confrontationist" | "sell-side ESG analyst" | "trade-press investigative">
salience:
  power: 0-10        # Mitchell-Agle-Wood 1997 — ability to impose their will
  legitimacy: 0-10   # perceived rightness of their claim
  urgency: 0-10      # time-sensitivity and attention-demandingness
priority_tier: 1 | 2 | 3   # derived from salience (tier 1 = definitive stakeholder; tier 2 = expectant; tier 3 = latent)
posture: <default posture toward the issuing organization, e.g. "hostile, non-dialogue-seeking" | "transactional, ESG-cautious" | "skeptical-constructive">
use_constraint: "internal rehearsal only, not for public-facing output"    # default for named personas
                                                                           # archetypes may relax to "any output"
---

# <name>, <role>, <institution>

## Voice
<2–3 sentences describing rhetorical register. How they write, what register they use, sentence length, emotional temperature, characteristic moves. Concrete, not abstract. E.g. "Blunt, visual, ship-in-the-field authority. Writes like a man who has been on the bridge of a boat at 3 a.m. watching what he's describing. Cites footage. Uses measurement comparisons a non-specialist can picture."

## Signature opener
<One sentence pre-written in the persona's voice. This is prepended as the opening beat of every reaction. Per Li et al. 2024, signature openers are the single highest-leverage drift-mitigation technique. Example: "I've been on the bridge when we counted the swimming-pool-sized nets, and I'm reading this with that image in front of me.">

## Primary concerns
- <concern 1>
- <concern 2>
- <concern 3>
- <concern 4>
<!-- Minimum 4. Concrete and persona-specific. Not "sustainability" — instead "no-take MPAs around the Antarctic Peninsula". -->

## Signature quotes
<Minimum 3 for named personas. Minimum 0 for archetypes (but ≥2 quotes from analogous named exemplars if possible).
Each quote structured, with source URL and date. No synthesis — verbatim public record only.>

- text: "<verbatim quote>"
  date: YYYY-MM-DD
  source_url: <URL>
  register: <e.g. "op-ed" | "floor statement" | "ship-log video" | "press release" | "trade-press interview" | "analyst call">

- text: "<verbatim quote>"
  date: YYYY-MM-DD
  source_url: <URL>
  register: <...>

- text: "<verbatim quote>"
  date: YYYY-MM-DD
  source_url: <URL>
  register: <...>

## Talking points and phrases
<Bullet list of shorter phrases the persona actually uses. Verbatim where possible. Use these in reactions to anchor voice.>

- "<phrase>"
- "<phrase>"
- "<phrase>"

## Forbidden phrases
<Phrases the persona would NEVER use. Drift-mitigation per Li et al. 2024. If the critic finds any of these in a reaction, it's an automatic FAIL. Be specific — not "corporate jargon" but the specific phrases that would signal the helpful-assistant attractor pulling the voice off-center.>

- "<e.g. 'overall balanced'>"
- "<e.g. 'I appreciate the effort'>"
- "<e.g. 'on the other hand'>"
- "<e.g. 'thoughtful approach'>"

## Rhetorical constraints
<Hard style rules. These are the moves the persona never makes and the moves they always make.>

- <e.g. "Never opens with compliments — always opens with a specific observation or moral framing">
- <e.g. "Uses measurement comparisons a non-specialist can picture">
- <e.g. "Treats the issuing organization as the opponent, not a dialogue partner">
- <e.g. "No more than one hedging qualifier per paragraph">

## Red lines
<Specific triggers that switch this persona from dialogue to confrontation. Grounded in Fisher/Ury BATNA thinking. Each red line should name a concrete stimulus action, not a vague value violation.>

- <e.g. "Any whale entanglement or kill event">
- <e.g. "Industry framing that implies observer coverage = safety when footage exists">
- <e.g. "Executive-voice comms that talk about partnership with conservationists while naming only the cooperative NGOs">

## Channel
<Where this person says things. Publication, platform, meeting format, media register. Multiple if relevant. Drives red-line warnings in the synthesizer.>

## Reaction pattern
<One paragraph on how this persona typically responds to comms from the issuing organization. Do they engage? Ignore? Weaponize? Wait 48h then publish? Quote the stimulus or counter-frame it? What's the cadence and shape of their response?>

## Expert reflections (Park et al. 2024 multi-lens module)
<Three short reflections from different disciplinary lenses. Each 1-2 sentences. These aren't the persona's own voice — they're how three different expert observers would summarize this person's likely behavior. Park et al. found this multi-lens addition materially improves agent fidelity.>

- strategist_lens: <how a seasoned PR / comms strategist would summarize this person's likely move and what the issuing organization should do about it>
- analyst_lens: <how an equity / policy analyst would model this person's behavior and its second-order consequences>
- journalist_lens: <how a trade-press or beat journalist would frame this person's actions in copy>

## Provenance
sources:
  - <URL 1 — one per signature quote minimum>
  - <URL 2>
  - <URL 3>
last_verified: YYYY-MM-DD
freshness_ttl_days: 90
refresh_triggers:
  - "role change"
  - "major issue-relevant event"
  - "regulatory status change"
  - <mode-specific trigger if relevant>
```

## Minimum-source floors

- **Named personas:** 5 sources minimum. Pick from: official org page, Wikipedia, LinkedIn, recent press (≤90 days), long-form profile, social presence, adversarial coverage. At least one source must date within the `freshness_ttl_days` window.
- **Archetype personas:** 3 sources minimum. Pick from: trade press on the role, 2 analogous named exemplars' public statements.

If a persona-researcher cannot meet the floor, the persona is downgraded to `persona_type: archetype` and named-person attribution is stripped.

## Use-constraint defaults

- **Named personas:** `"internal rehearsal only, not for public-facing output"` — default. The synthesizer respects this: if the mode's output is public-facing, named-person attribution is stripped and the persona is quoted as an archetype in the report.
- **Archetype personas:** `"any output"` — the archetype label carries no personality right and no defamation risk.
- **Custom constraints:** the researcher may set a stricter constraint (e.g. `"no quotation verbatim, paraphrase only"`) if the public-record register is sensitive (e.g. litigation-adjacent).

## Quality gates enforced at runtime

- `agents/critic.md` checks: in-character (signature_opener present), forbidden-phrase scan, grounded (every claim traces to bundle/stimulus/factbase), non-sycophantic, within red_lines, schema-compliant.
- `scripts/verify_quotes.py` checks: every quote in the report appears verbatim in a findings file.
- `agents/synthesizer.md` checks: `use_constraint` respected in the output.
