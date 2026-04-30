# Decision tree for project tone setup

Bruk dette flow for å avgjøre struktur når brukeren ber om "sett opp tone for dette prosjektet".

## Spørsmål 1: Hva produserer prosjektet?

- **A. E-post (broadcast eller individuelle)** → trenger tone, kanskje personas
- **B. Webside-content (blogg, landingssider)** → trenger tone, sjelden personas
- **C. Sosial media (LinkedIn, Twitter, Instagram)** → trenger tone, ofte én stemme
- **D. Teknisk dokumentasjon (API-docs, README, kode-kommentarer)** → minimal tone, mest klarhet
- **E. Salgs-/marketing-copy** → trenger tone + sannsynligvis personas (cold vs warm)

## Spørsmål 2: Hvor mange distinkte stemmer?

- **Én stemme** → kun `tone/core.md` (ingen persona-filer)
- **2-5 stemmer** → en `tone/<persona>.md` per stemme
- **5+ stemmer** → re-vurder. Sannsynligvis kan noen slås sammen, eller dere trenger å definere subkategorier under en persona.

## Spørsmål 3: Språk?

- **Ett språk** → enkelt
- **Flere språk** → spør om hver språk har samme tone eller ulik. Norge-pluss-engelsk er ofte ulik (norsk er mer fortrolig, engelsk er mer formell)

## Spørsmål 4: Eksisterer noen tone-filer allerede?

- **Ja, i `tone/` ved root** → utvid eksisterende, ikke skap parallell struktur
- **Ja, andre steder (f.eks. `content/`)** → legg pointer i `.claude/tone-pointer.md`
- **Nei** → fersk start

## Spørsmål 5: Hvor ofte oppdateres tone?

- **Sjelden** (kvartalsvis) → enkel struktur, ingen overrides-fil nødvendig
- **Ofte** (månedlig+) → overrides-fil for temporære endringer

## Output: foreslått struktur

Basert på svarene, foreslå:

### Minimal (én stemme, lite endring)
```
tone/
├── core.md
```

### Standard (én stemme, jevnlig endring)
```
tone/
├── core.md
└── overrides.md
```

### Multi-persona (flere stemmer)
```
tone/
├── core.md
├── overrides.md
├── persona-a.md
├── persona-b.md
└── persona-c.md
```

### Eksisterende non-standard
```
.claude/
└── tone-pointer.md  →  peker til content/VOICE-GUIDE.md (eller hvor enn)
```

## Eksempel-konversasjon

**Bruker:** "Sett opp tone-of-voice for dette prosjektet."

**Claude:**
1. "Hva produserer prosjektet primært? E-post, web-content, sosial, dokumentasjon, salg?"
2. (Bruker: "E-post for kursdeltakere og noen for B2B")
3. "Skiller dere mellom personlig (kurs) og B2B-tone i innholdet, eller er det samme stemme?"
4. (Bruker: "Skiller — B2B er mer profesjonell")
5. "OK. Foreslår denne strukturen:
   ```
   tone/
   ├── core.md          # Felles språkvalg, formelle valg
   ├── overrides.md     # Temporære regler
   ├── courses.md       # Kursdeltaker-tone
   └── bizdev.md        # B2B-tone
   ```
   Setter jeg opp dette og fyller med template?"
6. (Bruker: "Ja")
7. Generer filer fra templates, fyll inn med spørsmål om spesifikke fraser/avsendere.

## Antimønstre

- **Ikke duplisere** universal regler i project tone-filer
- **Ikke lage 10+ persona-filer** — restruktur til færre, bredere personas
- **Ikke pakke tone-filer inn i `.claude/skills/`** — det trigger permission-friction
- **Ikke skap parallell struktur** hvis prosjektet allerede har tone-system et annet sted
