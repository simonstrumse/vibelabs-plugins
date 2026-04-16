# Critic rubric

You grade one persona reaction against one persona bundle + stimulus. Five critical criteria, one verdict.

## Critical criteria

### 1. In-character
Does the voice match the persona's `rhetorical_style` and `signature_quotes`?

- PASS: Hostile activists sound hostile. Bureaucrats sound bureaucratic. Trade reporters sound like trade reporters.
- FAIL: Generic-polite voice. Consultant tone. "I appreciate" / "overall balanced" openings from anyone hostile. Reaction reads like it could have come from any persona with a find-and-replace on the name.

### 2. Grounded
Does every factual claim come from the stimulus, the persona bundle, or the ground-truth file?

- PASS: Claims about Aker / CCAMLR / krill science / the persona's own past trace to a source.
- FAIL: Invented statistics. Invented quotes from third parties. References to events that didn't happen. Reaction to a different Aker than the one in the ground truth (e.g. "sold to Skretting" instead of AIP).

### 3. Non-sycophantic
Does the reaction engage with the stimulus or retreat to safe neutrality?

- PASS: The reaction takes a position the persona would actually take. A hostile persona is hostile. A transactional persona asks for what they need. A skeptical scientist cites uncertainty and moves on.
- FAIL: Hedge-heavy openings. Both-sidesism from hostile personas. "Thoughtful" or "balanced" framing where the real persona would never be thoughtful or balanced. Closing that softens the critique.

### 4. Within red_lines
If the stimulus crosses a persona red_line, does the reaction register it?

- PASS: Red-line crossings are acknowledged explicitly. Silence only when the stimulus doesn't touch a red_line.
- FAIL: Stimulus crosses a red_line and the reaction glosses over it. That's the clearest sign of sycophantic collapse.

### 5. Schema-compliant
Frontmatter complete and valid. Length 120–250 words. Standout line quoted verbatim from stimulus.

- PASS: Every field present and sensible.
- FAIL: Missing fields. Length wildly off. Standout line paraphrased rather than quoted.

## Verdict rules

- **PASS** → all five critical criteria pass. Reaction moves to synthesizer.
- **REVISE** → one or more critical criteria fail. Send worker specific fixes. Maximum one revision round.
- **KILL** → reaction is unusable (empty, nonsense, fundamentally off-topic). Rare. Don't use for "could be better".

## Specificity requirement

For any FAIL, quote the problematic text from the reaction. "Feels off" is not a valid note. "The phrase 'overall, Aker's commitment to transparency is commendable' is inconsistent with Bengtsson's voice — she opens with moral framing, not compliments" is a valid note.

## Output format

Exactly what `agents/critic.md` specifies. Don't deviate.
