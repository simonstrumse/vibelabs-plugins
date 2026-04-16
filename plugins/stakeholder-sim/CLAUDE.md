# stakeholder-sim

Claude Code plugin for stakeholder reaction simulation — pressure-test a press release, statement, or policy announcement against a cast of persona subagents before you publish. **Industry-agnostic** — works for any sender in any sector. The skill researches the sender, maps the stakeholder landscape, and builds the persona cast per run. Optional **presets** ship verified persona libraries for specific companies.

## Structure

```
plugins/stakeholder-sim/
├── .claude-plugin/plugin.json
├── skills/
│   └── stakeholder-sim/
│       ├── SKILL.md                    # orchestrator (Opus 4.6)
│       ├── templates/                  # reaction schema, critic rubric, report skeleton, persona-task
│       ├── reference/                  # failure modes + generic routing heuristics
│       └── presets/
│           └── aker-biomarine/         # sample preset — 20 verified personas + Aker ground truth
│               ├── README.md
│               ├── ground-truth.md
│               ├── routing-table.md
│               └── personas/
└── agents/
    # research phase (industry-agnostic)
    ├── stimulus-analyzer.md            # Sonnet 4.6 — extract sender, topic, release type, claims
    ├── client-researcher.md            # Sonnet 4.6 + WebFetch/WebSearch — build ground truth
    ├── stakeholder-mapper.md           # Sonnet 4.6 + WebSearch — propose cast of 12-20 roles
    ├── persona-builder.md              # Sonnet 4.6 + WebFetch/WebSearch — build one persona bundle
    # simulation phase
    ├── persona-worker.md               # Sonnet 4.6 — roleplay a single persona
    ├── critic.md                       # Sonnet 4.6 — quality-gate rubric pass
    ├── synthesizer.md                  # Opus 4.6 — write the stakeholder reaction report
    └── quote-verifier.md               # Sonnet 4.6 — verify every quote is real
```

## Agentic everything

Following the internal convention: **prefer Claude subagents over deterministic scripts** for any extraction, classification, research, or verification step. There is no regex parser, no hardcoded scraper, no Python script in this plugin. Every transformation is a Sonnet or Opus subagent with native tools. Orchestration (file I/O, parallel spawn, state management) is the only place deterministic code appears — and for this plugin, the orchestrator itself is a Claude agent following SKILL.md instructions.

## Architecture

```
stimulus + user request
        │
        ▼
  orchestrator (Opus, SKILL.md)
        │
   ┌────┴────┐
   │         │
preset?    research?
   │         │
   │         ▼
   │   stimulus-analyzer ─► analysis.md
   │         │
   │         ▼
   │   client-researcher  ─► ground-truth.md
   │         │                (user facts OR WebFetch research OR both)
   │         ▼
   │   stakeholder-mapper ─► cast-roster.md
   │         │                (12-20 stakeholder roles)
   │         │
   └─────────┤
             │
             ▼
        plan.md ─► USER APPROVAL (non-optional)
             │
             ▼
   persona-builder × N in parallel    (research mode; skipped in preset mode)
             │
             ▼
   persona-worker × N in parallel ─► findings/persona-<id>.md
             │
             ▼
   critic × N in parallel ─► findings/critic-<id>.md
             │
             ▼ (REVISE → re-spawn persona-worker once)
             │
   findings/persona-<id>-final.md
             │
             ▼
   synthesizer (Opus) ─► report.md
             │
             ▼
   quote-verifier ─► verification.md
             │
             ▼ (if REVISE, re-spawn synthesizer with corrections)
             │
        report.md → user
```

## Key design principles

- **Industry-agnostic by default.** Skill researches the sender and builds a cast per run via WebFetch/WebSearch. Works out of the box on any press release from any company.
- **Presets are optional shortcuts.** A preset is a verified persona library for a specific sender. Ships with `aker-biomarine` as a sample. Auto-detected from the sender identity, or requested explicitly.
- **Rich persona bundles, not demographic strings.** Each persona has verbatim signature quotes from public sources, concrete red_lines, a rhetorical_style paragraph, and a reaction_pattern. Grounded in Park et al. 2024's finding that interview-grounded personas hit 85% of human test-retest reliability.
- **Mandatory critic pass.** Every persona reaction is rubric-checked before synthesis. Defends against the dominant failure mode — sycophantic collapse to helpful-assistant voice.
- **Mandatory quote verification.** Every quoted line in the final report is checked against the findings files. No invented quotes.
- **User-facts-first.** The user can always paste facts about the client. Research is a default, not a requirement. For MNPI or sensitive releases, `user-only` mode skips web research entirely.
- **Parallel spawn.** Persona-builders, persona-workers, and critics all spawn concurrently in a single assistant turn.
- **User approves the cast.** The skill pauses after Phase 1 (plan) and cannot continue without explicit approval.

## Invoke

```
/stakeholder-sim path/to/press-release.md
```

With a preset:

```
/stakeholder-sim path/to/release.md --preset aker-biomarine
```

Or naturally:

> Simulate how journalists and activists would react to this Nordea Q4 earnings release.

> Use the Aker preset and run this against our CCAMLR statement.

## Adding a preset

1. Copy `skills/stakeholder-sim/presets/aker-biomarine/` to `presets/<new-preset>/`.
2. Replace the 20 persona files with your industry's personas (use `personas/_template.md`).
3. Rewrite `ground-truth.md` with sender-specific facts.
4. Rewrite `routing-table.md` with release-type → default-cast mapping.
5. Update the preset's `README.md` (when-to-use, cluster distribution).

Or skip all of that and let the skill build a cast on the fly from the web.

## When not to use

- Quantitative sentiment prediction — use a real poll.
- Replacing stakeholder relationships — nothing does.
- Deciding whether to publish — use humans.

This is a pressure test, not an oracle.

## References

- [Anthropic multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) — orchestrator-worker pattern with ~90% uplift
- [Park et al. 2024](https://arxiv.org/abs/2411.10109) — interview-grounded persona fidelity
- [Constitutional AI (Bai et al.)](https://arxiv.org/abs/2212.08073) — critique-and-revise loop
