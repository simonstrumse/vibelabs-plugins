# Reaction output schema

Every persona-worker writes a file in this exact shape. Frontmatter keys are mandatory.

```
---
persona_id: <id-from-persona-file>
persona_name: <full name or archetype label>
persona_type: named | archetype
institution: <institution>
cluster: <cluster label from the cast-spec, e.g. activist | scientist | regulator | press | customer | investor | internal | peer-company>
sentiment: hostile | skeptical | neutral | supportive | transactional
confidence: 0.0-1.0           # how confident this persona is in their own take
would_act: yes | no | conditional   # will they say something publicly?
trust_delta: -2 | -1 | 0 | +1 | +2   # shift in this persona's trust in the issuing organization after reading
channel: <where they'd say it — trade-press interview / X thread / closed-door meeting / comment letter / internal memo / op-ed / floor statement>
revision_round: 0 | 1 | 2     # 0 on first write; 1 or 2 after critic-driven revise
---

## Reaction

<120–250 words in the persona's first-person voice. Must open with the persona's signature_opener (or a close paraphrase in the same beat). Addresses the stimulus directly.
Uses signature phrases from the persona bundle where they fit. Preserves the persona's
rhetorical register per the bundle. No bullet lists unless the persona actually writes
that way (e.g. sell-side analyst). No references to simulation, AI, Claude, Pre-Flight.
No both-sidesism from hostile personas. No forbidden_phrases.>

## Standout line

> <one sentence or phrase copied verbatim from the stimulus>

Why it stood out: <one sentence in persona's voice explaining why this line, specifically>

## What would change my position

<1–3 sentences in persona's voice: what the issuing organization would have to do, say,
remove, add, or prove for this persona's stance to shift meaningfully. If nothing would —
say that.>
```

## Field guidance

- **persona_type** determines downstream handling. `named` personas carry a `use_constraint` from their bundle; the synthesizer respects it. `archetype` personas can always be quoted without naming a real individual.
- **cluster** is drawn from the cast-spec produced by the persona-architect — it's not a fixed enum. Typical clusters: activist, scientist, regulator, press, customer, investor, internal, peer-company — but modes may introduce others (e.g. `proxy-advisor` for activist-proxy mode, `sovereign-investor` for deal-comms).
- **sentiment** vs **trust_delta**: sentiment is about the stimulus; trust_delta is about the issuing organization as an institution. A persona can be hostile to a specific release while trust stays neutral (they expected it).
- **would_act = conditional**: flag what the condition is in "What would change my position".
- **confidence < 0.4** is a sign the reaction is thin or the persona doesn't have enough to go on. That's useful information, not a bug.
- **channel** drives the synthesizer's red-line warnings. A quote that would land in a public broadcast is different from one in a closed investor-engagement meeting.
- **revision_round** is set by the worker: 0 on first write, 1 after a first critic REVISE, 2 after a second. Critic KILLs on round-2 failure.
