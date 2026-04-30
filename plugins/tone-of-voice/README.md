# tone-of-voice

Universell tone-of-voice-skill for Claude Code. Apply universelle anti-AI-regler på tvers av prosjekter, layer prosjekt-spesifikke regler på toppen, og bootstrap nye prosjekter med tone-of-voice-system når de trenger det.

## Hva den gir deg

**Tre lag tone-regler:**

1. **Universal** (alltid aktiv) — em-dash-forbud, anti-AI-patterns, skriveassistent-prinsipp, rytme-og-lengde, ingen AI-overdrivelse
2. **Språk-spesifikt** — diskurspartikler (jo/vel/nok/altså), aktiv vs passiv, oversettelsesmarkører, særskrivingsfeil
3. **Domene-spesifikt** — e-post (preheader, unsubscribe, personalisering, footer)

**Bootstrap-funksjon:**

Når du sier "sett opp tone for dette prosjektet" eller "lag tone-of-voice for nytt prosjekt":
- Spør om språk, antall personas, type innhold
- Foreslår mappestruktur (`tone/core.md`, evt. persona-filer)
- Genererer fra templates
- Setter opp permissions hvis prosjektet har `.claude/settings.json`

## Når den aktiveres

- Du skriver eller redigerer e-poster, marketing-copy, blogg-poster
- Du ber om "rydd opp denne teksten"
- Du sier "fjern AI-markører"
- Du setter opp tone for nytt prosjekt
- Du sjekker eksisterende tekst for tone-konsistens

## Prosjekt-konvensjon

Skillen ser etter prosjekt-spesifikk tone i denne rekkefølgen:

1. `<repo>/tone/` (Vibelabs-konvensjon — anbefalt)
2. `<repo>/content/VOICE-GUIDE-*.md` (OSE/content-prosjekt-konvensjon)
3. `<repo>/.claude/tone-pointer.md` (eksplisitt pointer-mekanisme)

Hvis ingen finnes: bruker kun universal-regler.

## Installering

Fra Vibelabs-marketplace:
```bash
claude plugin marketplace add simonstrumse/vibelabs-plugins
claude plugin install tone-of-voice
```

## Mappe-oversikt

```
skills/tone-of-voice/
├── SKILL.md           — entry point, beskriver workflow
├── universal/         — alltid aktiv
│   ├── em-dash.md
│   ├── anti-ai-patterns.md
│   ├── writing-assistant-principle.md
│   ├── rhythm-and-length.md
│   └── ai-hyperbole.md
├── language/
│   └── norwegian.md   — norsk-spesifikke anti-patterns
├── domain/
│   └── email.md       — e-post best practices
└── bootstrap/
    ├── how-to-set-up-project-tone.md
    ├── decision-tree.md
    └── templates/
        ├── tone-core-template.md
        ├── tone-overrides-template.md
        └── tone-persona-template.md
```

## Filosofi

**Universal regler bor i pluginen, prosjekt-spesifikke regler bor i prosjektet.**

Universal-reglene er hentet fra det vi har lært i Vibelabs-prosjektet (e-post-skriving) og OSE-prosjektet (web-content for fjordturer). De er **generelle** — ingenting prosjekt-spesifikt er kopiert inn.

Hvis et prosjekt har behov for spesifikke fraser, signaturer, eller persona-distinksjoner, hører de hjemme i prosjektets egen `tone/`-mappe.

## Inspirasjon

- OSE's grundige `VOICE-GUIDE-NO.md` (norsk web-writing research)
- Vibelabs' persona-system for e-postmarketing
- Aleksander Stensby (GritAI Studio) sin uformelle community-tone
- Norske blogger som Det vonde liv og Reiselykke
