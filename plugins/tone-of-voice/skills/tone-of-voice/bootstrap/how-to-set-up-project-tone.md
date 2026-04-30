# How to set up project-specific tone of voice

Når brukeren sier "sett opp tone-of-voice for dette prosjektet" eller du detekter at et prosjekt mangler tone-files men trenger det.

## Når et prosjekt trenger sin egen tone

Ikke alle prosjekter trenger custom tone. Heuristikker for når det er verdt:

**JA** — sett opp project tone hvis:
- Prosjektet skriver tekst destinert for mennesker (e-post, blogg, marketing, sosial)
- Det finnes flere distinkte stemmer (personas) — f.eks. salg vs. nyhetsbrev vs. kurs
- Prosjektet har spesifikke fraser som skal gjenbrukes
- Prosjektet har bransje-spesifikt vokabular

**NEI** — universal-skillen er nok:
- Prosjektet er teknisk dokumentasjon eller kodebase uten user-facing tekst
- Det er ingen distinkte stemmer
- Tekst er sjelden eller engangs

## Decision tree for setup

Følg `decision-tree.md` for å avgjøre struktur.

## Steg-for-steg setup

### 1. Plassering

Standard er `tone/` ved repo-rot:
```
<repo>/
├── tone/
│   ├── core.md         # Project-specific universal regler (overstyrer plugin-universal hvor relevant)
│   ├── overrides.md    # Aktive temporære overstyringer
│   ├── <persona1>.md   # Persona-tone (hvis flere stemmer)
│   ├── <persona2>.md
│   └── ...
```

Hvis prosjektet bruker annen konvensjon (f.eks. OSE har `content/VOICE-GUIDE-NO.md`), legg en pointer:
```
<repo>/.claude/tone-pointer.md  →  innhold: "Tone guide: content/VOICE-GUIDE-NO.md"
```

### 2. Permissions (hvis prosjektet bruker `.claude/settings.json`)

Legg til i `permissions.allow`:
```json
"Write(tone/**)",
"Edit(tone/**)"
```

Dette er nøkkelen for frictionless oppdatering — uten den får brukeren permission-prompt på hver tone-edit.

### 3. Generer kjernen

Bruk `templates/tone-core-template.md` som starter. Tilpass:
- Hvilket språk skriver prosjektet på?
- Hva er prosjektets overordnede ethos? (uformell? profesjonell? lekent? rolig?)
- Hvilke spesifikke språkvalg gjelder? (lokale termer, foretrukne ord)
- Hva er signaturer-konvensjon? ("Vi sees!", "Mvh", "Greetings"?)

### 4. Identifiser personas (hvis relevant)

Spør brukeren: "Skriver prosjektet i flere stemmer? F.eks.:
- B2B-salg (profesjonell, varm)
- Newsletter (community-energi)
- Teknisk støtte (rolig, tydelig)
- Sponsor-pitch (data-tung)"

Hvis ja: lag én fil per persona ved å bruke `templates/tone-persona-template.md`.

### 5. Sett opp overrides-fil

`overrides.md` brukes for temporære regler (f.eks. "denne kampanjen: ingen emojis", "denne måneden: bruk engelsk"). Start tom med malen i `templates/tone-overrides-template.md`.

### 6. Oppdater router/skills (hvis prosjektet har dem)

Hvis prosjektet har `.claude/skills/router.md` eller persona-skills som tidligere refererte tone-filer på andre lokasjoner, oppdater path-referanser.

### 7. Test

Be Claude skrive en e-post for prosjektet. Verifiser:
- Universal-regler følges (ingen em-dash, ingen anti-AI patterns)
- Project-spesifikke regler følges (riktig signatur, riktige fraser)
- Persona-skille fungerer hvis multiple personas

## Hva som IKKE skal være i project tone-filer

Disse hører til mother-skillen, ikke prosjekt:
- Em-dash-regelen
- Anti-AI-patterns-tabellen (universal versjonen)
- Skriveassistent-prinsippet
- Universal rytme-og-lengde-regelen
- AI-overdrivelse generelt

Project-tone skal kun ha det som er **prosjekt-spesifikt**:
- Hvilke fraser brand bruker
- Hvilke avsenderkonvensjoner
- Hvilke personas + deres distinkte stemmer
- Bransje-spesifikt vokabular

Hvis du ser duplisering mellom project og mother, fjern fra project — la mother håndtere det.

## Hvis prosjektet har et eksisterende tone-system

Som OSE: ikke flytt det. Legg en pointer i `.claude/tone-pointer.md`:
```markdown
# Tone pointer
Tone guide: `content/VOICE-GUIDE-NO.md`
```

Mother-skillen vil lese pointeren og deretter den faktiske fila.
