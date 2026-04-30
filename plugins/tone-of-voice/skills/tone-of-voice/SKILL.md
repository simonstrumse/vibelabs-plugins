---
name: tone-of-voice
description: Universal tone-of-voice rules (em-dash avoidance, anti-AI patterns, writing-assistant principle). Use when writing or reviewing emails, marketing copy, blog posts, or any user-facing text. Triggers also on "set up tone for project". Layers project-specific rules from local tone/ folder when present.
---

# Tone of Voice — Mother Skill

Universal tone-of-voice principles + bootstrapping logic for project-specific tone systems. Apply universal rules always. Layer project-specific rules on top when they exist.

## When this skill activates

- User asks to write or edit emails, marketing copy, blog posts, content for humans
- User asks to "tighten this", "make this more human", "remove AI markers", "skrive om"
- User asks to set up tone-of-voice for a new project
- User mentions "tone of voice", "anti-AI", "AI-språk", "skriveassistent"

## Workflow

### Step 1: Always apply universal rules

Before writing or reviewing anything, internalize these (read on first activation per session):

- `universal/writing-assistant-principle.md` — how to interpret user feedback
- `universal/em-dash.md` — never use em-dash (—) in human-facing text
- `universal/anti-ai-patterns.md` — 13+ markers to eliminate on sight
- `universal/rhythm-and-length.md` — vary sentence/paragraph length
- `universal/ai-hyperbole.md` — avoid revolusjonerende/game-changer/etc.

### Step 2: Detect project tone files

Look for project-specific tone files in priority order:

1. `tone/` at repo root (Vibelabs convention)
2. `content/VOICE-GUIDE-*.md` (OSE/content-driven projects)
3. `.claude/tone-pointer.md` — explicit pointer to non-standard location

If found: read and layer on top of universal. Project-specific rules override universal in conflict.

### Step 3: Detect language

If text is Norwegian, also load:
- `language/norwegian.md` — discourse particles, active voice, translation markers, "sees" vs "ses"

### Step 4: Detect domain

If writing email, also load:
- `domain/email.md` — preheader, unsubscribe footer, HTML structure, personalization patterns

### Step 5: If new project, offer bootstrap

If user says "set up tone for this project" or "lag tone-of-voice for nytt prosjekt":
- Read `bootstrap/how-to-set-up-project-tone.md`
- Run guided setup using templates in `bootstrap/templates/`

## Hierarchy and conflict resolution

```
project tone/overrides.md   (highest — temporary overrides)
project tone/<persona>.md   (persona-specific)
project tone/core.md        (project core, may override universal)
plugin universal/*.md       (lowest — fallback default)
```

When project rules conflict with universal: project wins (they're more specific). When in doubt, ask user.

## What this skill DOES NOT contain

- Project-specific personas (bizdev tone, newsletter tone, etc. — those live in project's `tone/`)
- Domain-specific vocabulary (fjord-words, technical jargon, etc.)
- Brand-specific phrases ("100% suksessrate", "Jeg pleier å ta", etc.)

The mother skill is intentionally **generic** so it carries cleanly across projects. Specifics belong in project tone files.

## File map

```
universal/      Always applies (any project, any language)
language/       Language-specific rules
domain/         Domain-specific rules (email, web, social)
bootstrap/      How to set up project-specific tone for a new project
```
