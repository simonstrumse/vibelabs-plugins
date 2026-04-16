# Reaction output schema

Every persona-worker writes a file in this exact shape. Frontmatter keys are mandatory.

```
---
persona_id: <id-from-persona-file>
persona_name: <full name>
institution: <institution>
sentiment: hostile | skeptical | neutral | supportive | transactional
confidence: 0.0-1.0           # how confident this persona is in their own take
would_act: yes | no | conditional   # will they say something publicly?
trust_in_aker_delta: -2 | -1 | 0 | +1 | +2   # shift in persona's trust after reading
channel: <where they'd say it — "Mongabay comment request" / "X thread" / "CCAMLR floor statement" / "internal memo">
---

## Reaction

<120–250 words in the persona's first-person voice. Addresses the release directly.
Uses signature phrases from the persona bundle where they fit. Preserves the persona's
rhetorical register — dry/moral/bureaucratic/trade-press/whatever the bundle says.
No bullet lists unless the persona actually writes that way (e.g. sell-side analyst).
No references to the simulation or to any LLM. No both-sidesism from hostile personas.>

## Standout line

> <one sentence or phrase copied verbatim from the stimulus>

Why it stood out: <one sentence in persona's voice explaining why this line, specifically>

## What would change my position

<1–3 sentences in persona's voice: what Aker would have to do, say, remove, add, or prove
for this persona's stance to shift meaningfully. If nothing would — say that.>
```

## Field guidance

- **sentiment** vs **trust_in_aker_delta**: sentiment is about the release; trust delta is about Aker as an institution. A persona can be hostile to a specific release while trust stays neutral (they expected it).
- **would_act = conditional**: flag what the condition is in "What would change my position".
- **confidence < 0.4** is a sign the reaction is thin or the persona doesn't have enough to go on. That's useful information, not a bug.
- **channel** drives the synthesizer's red-line warnings. A quote that would land in NRK Brennpunkt is different from one in a closed NBIM engagement meeting.
