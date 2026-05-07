Persona A file: {persona_a_file}
Persona B file: {persona_b_file}
A's first-round reaction: {reaction_a_path}
B's first-round reaction: {reaction_b_path}
Stimulus file: {stimulus_path}
Factbase file: {factbase_path}
Pairing frame: {pairing_frame}
Exchanges: {exchanges}                # default 3
Write debate transcript to: {output_path}

Read both bundles, both reactions, the stimulus, the factbase, and the pairing_frame.

Identify each persona's strongest claim (most grounded, most central to their posture) and their weakest claim (most vulnerable to challenge).

Write a debate transcript with exactly {exchanges} exchanges per side:
- Opening statements (A1, B1): 80-120 words each. Persona's strongest claim framed as opening. Prepend signature_opener or close paraphrase.
- Direct challenge (A2, B2): 100-150 words each. Each persona addresses the OTHER's opening claim head-on. Not pivoting to their own points — engaging what was actually said.
- Closing (A3, B3): 80-120 words each. Name the claim you consider weakest and the condition under which you could move.

Then a moderator's read (2-3 sentences, third-person analyst voice, synthesizer-facing): whose case was sharper and why; where each weakened under pressure; what this means for the issuing organization.

Both personas stay in their own voice throughout. Honor each persona's signature_opener, forbidden_phrases, rhetorical_constraints, red_lines. No voice-melding.

Engage, don't pivot. No straw-manning. Restate the other's claim accurately before challenging it.

No invented facts. Grounded in bundles, first-round reactions, stimulus, factbase.

No artificial convergence if the pairing is genuinely adversarial — sharpen the divide, don't find a middle.

Return exactly: Wrote {output_path}
