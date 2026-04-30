# Tone Overrides — HØYESTE prioritet

**Status:** Aktive overstyringer som gjelder for ALL tekst-generering i dette prosjektet.

**Prioritet:**
1. Denne filen (du er her)
2. `tone/<persona>.md`
3. `tone/core.md`
4. Plugin-universal regler

**Konflikt?** Denne filen vinner.

---

## Aktive overstyringer

<!-- Legg til en linje her per overstyring, formatert slik: -->
<!-- **OVERRIDE:** [klar, handlingsorientert instruksjon] — *aktivert YYYY-MM-DD* -->

_(ingen aktive overstyringer per [DATE])_

---

## Hvordan bruke denne filen

### Legge til en overstyring
Si til Claude: "Fra nå av: bruk aldri emojis i noen persona" — Claude legger til:
```markdown
**OVERRIDE:** Bruk aldri emojis i noen persona — *aktivert YYYY-MM-DD*
```

### Fjerne en overstyring
Si: "Fjern emoji-overstyringen" — Claude sletter linjen.

### Temporært vs permanent
- Temporær override: holder for kampanjen/prosjektet, fjern når ferdig
- Permanent regel: flytt til `tone/core.md` eller relevant persona's `tone/<persona>.md`

---

## Eksempler på format

### Emoji-kontroll
```markdown
**OVERRIDE:** Ingen emojis i noen persona — *aktivert 2026-04-23*
**OVERRIDE:** Kun pizza 🍕 for newsletter, ingen andre steder — *aktivert 2026-03-15*
```

### Språk
```markdown
**OVERRIDE:** Bruk primært engelsk (internasjonal målgruppe denne måneden) — *aktivert 2026-05-01*
```

### Lengde
```markdown
**OVERRIDE:** Maks 150 ord per mail (alle personas) — *aktivert 2026-04-30*
```

### Spesifikke fraser
```markdown
**OVERRIDE:** Ikke bruk ordet "vibecoding" — bruk "bygge med AI" i stedet — *aktivert 2026-02-01*
```
